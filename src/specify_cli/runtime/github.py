"""
specify_cli.runtime.github - GitHub API Operations
===================================================

Runtime layer for GitHub API operations including release fetching
and template downloading.

This module isolates all GitHub API I/O operations with comprehensive
OpenTelemetry instrumentation. All side effects are contained here.

Key Features
-----------
* **Release Fetching**: Get latest release information
* **Asset Downloads**: Download release assets with progress
* **Rate Limit Handling**: Parse and format rate limit errors
* **Authentication**: GitHub token management
* **Telemetry**: Full OTEL instrumentation

Security
--------
* Token sanitization before use
* No credential logging
* Secure SSL context via truststore

Examples
--------
    >>> from specify_cli.runtime.github import fetch_latest_release, download_asset
    >>>
    >>> release = fetch_latest_release("github", "spec-kit")
    >>> asset = find_matching_asset(release, "claude", "sh")
    >>> download_asset(asset, Path("/tmp"))

See Also
--------
- :mod:`specify_cli.runtime.template` : Template extraction
- :mod:`specify_cli.core.telemetry` : Telemetry utilities
"""

from __future__ import annotations

import os
import ssl
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import httpx

try:
    import truststore

    _ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
except ImportError:
    # Fallback to standard SSL if truststore not available
    _ssl_context = ssl.create_default_context()

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.semconv import GitHubAttributes, GitHubOperations
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "GitHubError",
    "RateLimitError",
    "download_asset",
    "fetch_latest_release",
    "find_matching_asset",
    "format_rate_limit_error",
    "github_auth_headers",
    "github_token",
    "parse_rate_limit_headers",
]


class GitHubError(Exception):
    """Base exception for GitHub API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(GitHubError):
    """GitHub API rate limit exceeded."""

    def __init__(
        self, message: str, reset_time: datetime | None = None, retry_after: int | None = None
    ) -> None:
        super().__init__(message, status_code=403)
        self.reset_time = reset_time
        self.retry_after = retry_after


def github_token(cli_token: str | None = None) -> str | None:
    """Get sanitized GitHub token from CLI argument or environment.

    Priority:
    1. CLI argument (if provided)
    2. GH_TOKEN environment variable
    3. GITHUB_TOKEN environment variable

    Parameters
    ----------
    cli_token : str, optional
        Token passed via CLI argument.

    Returns
    -------
    str | None
        Sanitized token or None if not available.
    """
    token = (cli_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or "").strip()
    return token or None


def github_auth_headers(cli_token: str | None = None) -> dict[str, str]:
    """Get Authorization headers for GitHub API requests.

    Parameters
    ----------
    cli_token : str, optional
        Token passed via CLI argument.

    Returns
    -------
    dict[str, str]
        Headers dict with Authorization if token is available.
    """
    token = github_token(cli_token)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def parse_rate_limit_headers(headers: httpx.Headers) -> dict[str, Any]:
    """Extract and parse GitHub rate-limit headers.

    Parameters
    ----------
    headers : httpx.Headers
        Response headers from GitHub API.

    Returns
    -------
    dict[str, Any]
        Parsed rate limit information.
    """
    info: dict[str, Any] = {}

    # Standard GitHub rate-limit headers
    if "X-RateLimit-Limit" in headers:
        info["limit"] = int(headers.get("X-RateLimit-Limit", "0"))
    if "X-RateLimit-Remaining" in headers:
        info["remaining"] = int(headers.get("X-RateLimit-Remaining", "0"))
    if "X-RateLimit-Reset" in headers:
        reset_epoch = int(headers.get("X-RateLimit-Reset", "0"))
        if reset_epoch:
            reset_time = datetime.fromtimestamp(reset_epoch, tz=UTC)
            info["reset_epoch"] = reset_epoch
            info["reset_time"] = reset_time
            info["reset_local"] = reset_time.astimezone()

    # Retry-After header
    if "Retry-After" in headers:
        retry_after = headers.get("Retry-After", "")
        try:
            info["retry_after_seconds"] = int(retry_after)
        except ValueError:
            info["retry_after"] = retry_after

    return info


def format_rate_limit_error(status_code: int, headers: httpx.Headers, url: str) -> str:
    """Format a user-friendly error message with rate-limit information.

    Parameters
    ----------
    status_code : int
        HTTP status code.
    headers : httpx.Headers
        Response headers.
    url : str
        Request URL.

    Returns
    -------
    str
        Formatted error message.
    """
    rate_info = parse_rate_limit_headers(headers)

    lines = [f"GitHub API returned status {status_code} for {url}"]
    lines.append("")

    if rate_info:
        lines.append("Rate Limit Information:")
        if "limit" in rate_info:
            lines.append(f"  * Rate Limit: {rate_info['limit']} requests/hour")
        if "remaining" in rate_info:
            lines.append(f"  * Remaining: {rate_info['remaining']}")
        if "reset_local" in rate_info:
            reset_str = rate_info["reset_local"].strftime("%Y-%m-%d %H:%M:%S %Z")
            lines.append(f"  * Resets at: {reset_str}")
        if "retry_after_seconds" in rate_info:
            lines.append(f"  * Retry after: {rate_info['retry_after_seconds']} seconds")
        lines.append("")

    lines.append("Troubleshooting Tips:")
    lines.append("  * If on shared CI/corporate environment, you may be rate-limited.")
    lines.append("  * Use --github-token or set GH_TOKEN/GITHUB_TOKEN environment variable.")
    lines.append("  * Authenticated: 5,000/hour vs 60/hour for unauthenticated.")

    return "\n".join(lines)


def fetch_latest_release(
    owner: str,
    repo: str,
    *,
    token: str | None = None,
    client: httpx.Client | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Fetch the latest release from a GitHub repository.

    Parameters
    ----------
    owner : str
        Repository owner.
    repo : str
        Repository name.
    token : str, optional
        GitHub token for authentication.
    client : httpx.Client, optional
        HTTP client to use.
    timeout : float, optional
        Request timeout in seconds.

    Returns
    -------
    dict[str, Any]
        Release data including tag_name, assets, etc.

    Raises
    ------
    GitHubError
        If the API request fails.
    RateLimitError
        If rate limit is exceeded.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    start_time = time.time()

    with span(
        GitHubOperations.FETCH_RELEASE,
        **{
            GitHubAttributes.OWNER: owner,
            GitHubAttributes.REPO: repo,
        },
    ):
        add_span_event("github.fetch.starting", {"url": api_url})

        should_close_client = False
        if client is None:
            client = httpx.Client(verify=_ssl_context)
            should_close_client = True

        try:
            headers = github_auth_headers(token)
            response = client.get(
                api_url,
                timeout=timeout,
                follow_redirects=True,
                headers=headers,
            )

            duration = time.time() - start_time

            # Record metrics
            metric_counter("github.api.requests")(1)
            metric_histogram("github.api.duration")(duration)

            # Parse rate limit headers
            rate_info = parse_rate_limit_headers(response.headers)
            if rate_info.get("remaining") is not None:
                add_span_attributes(
                    **{GitHubAttributes.RATE_LIMIT_REMAINING: rate_info["remaining"]}
                )

            if response.status_code == 403:
                metric_counter("github.api.rate_limited")(1)
                error_msg = format_rate_limit_error(response.status_code, response.headers, api_url)
                raise RateLimitError(
                    error_msg,
                    reset_time=rate_info.get("reset_time"),
                    retry_after=rate_info.get("retry_after_seconds"),
                )

            if response.status_code != 200:
                metric_counter("github.api.errors")(1)
                error_msg = format_rate_limit_error(response.status_code, response.headers, api_url)
                raise GitHubError(error_msg, status_code=response.status_code)

            try:
                release_data = response.json()
            except ValueError as e:
                raise GitHubError(f"Failed to parse release JSON: {e}")

            # Add release info to span
            add_span_attributes(
                **{
                    GitHubAttributes.RELEASE_TAG: release_data.get("tag_name", ""),
                    GitHubAttributes.RELEASE_NAME: release_data.get("name", ""),
                }
            )

            add_span_event(
                "github.fetch.completed",
                {
                    "tag": release_data.get("tag_name", ""),
                    "assets_count": len(release_data.get("assets", [])),
                },
            )

            metric_counter("github.api.success")(1)
            return release_data

        finally:
            if should_close_client:
                client.close()


def find_matching_asset(
    release_data: dict[str, Any], ai_assistant: str, script_type: str
) -> dict[str, Any] | None:
    """Find a matching asset in release data.

    Parameters
    ----------
    release_data : dict[str, Any]
        Release data from fetch_latest_release.
    ai_assistant : str
        AI assistant type (e.g., "claude", "copilot").
    script_type : str
        Script type ("sh" or "ps1").

    Returns
    -------
    dict[str, Any] | None
        Matching asset or None if not found.
    """
    assets = release_data.get("assets", [])
    pattern = f"spec-kit-template-{ai_assistant}-{script_type}"

    matching_assets = [
        asset
        for asset in assets
        if pattern in asset.get("name", "") and asset.get("name", "").endswith(".zip")
    ]

    return matching_assets[0] if matching_assets else None


def download_asset(
    asset: dict[str, Any],
    download_dir: Path,
    *,
    token: str | None = None,
    client: httpx.Client | None = None,
    timeout: float = 120.0,
    progress_callback: Any | None = None,
) -> Path:
    """Download a release asset.

    Parameters
    ----------
    asset : dict[str, Any]
        Asset data from release.
    download_dir : Path
        Directory to download to.
    token : str, optional
        GitHub token for authentication.
    client : httpx.Client, optional
        HTTP client to use.
    timeout : float, optional
        Download timeout in seconds.
    progress_callback : callable, optional
        Callback for progress updates: (downloaded_bytes, total_bytes) -> None

    Returns
    -------
    Path
        Path to downloaded file.

    Raises
    ------
    GitHubError
        If download fails.
    """
    download_url = asset["browser_download_url"]
    filename = asset["name"]
    expected_size = asset.get("size", 0)
    start_time = time.time()

    with span(
        GitHubOperations.DOWNLOAD,
        **{
            "github.asset.name": filename,
            "github.asset.size": expected_size,
        },
    ):
        add_span_event("github.download.starting", {"url": download_url, "size": expected_size})

        should_close_client = False
        if client is None:
            client = httpx.Client(verify=_ssl_context)
            should_close_client = True

        zip_path = download_dir / filename

        try:
            headers = github_auth_headers(token)

            with client.stream(
                "GET",
                download_url,
                timeout=timeout,
                follow_redirects=True,
                headers=headers,
            ) as response:
                if response.status_code != 200:
                    error_msg = format_rate_limit_error(
                        response.status_code, response.headers, download_url
                    )
                    raise GitHubError(error_msg, status_code=response.status_code)

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(zip_path, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)

            duration = time.time() - start_time

            # Record metrics
            metric_counter("github.downloads")(1)
            metric_histogram("github.download.duration")(duration)
            metric_histogram("github.download.size")(float(downloaded))

            add_span_event(
                "github.download.completed",
                {
                    "path": str(zip_path),
                    "size": downloaded,
                    "duration": duration,
                },
            )

            return zip_path

        except Exception:
            # Clean up partial download
            if zip_path.exists():
                zip_path.unlink()
            raise

        finally:
            if should_close_client:
                client.close()
