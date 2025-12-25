"""Tests for async_core.file module."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest


@pytest.mark.unit
class TestAsyncFileOperations:
    """Test async file operations."""

    @pytest.mark.asyncio
    async def test_async_read_file_mock(self, tmp_path: Path, mocker) -> None:
        """Test async file reading with mocked aiofiles."""
        from specify_cli.async_core.file import async_read_file

        # Create a test file
        test_file = tmp_path / "test.txt"
        test_content = "Hello, Async World!"

        # Mock aiofiles.open
        mock_file = mocker.AsyncMock()
        mock_file.__aenter__ = mocker.AsyncMock(return_value=mock_file)
        mock_file.__aexit__ = mocker.AsyncMock()
        mock_file.read = mocker.AsyncMock(return_value=test_content)

        mocker.patch("aiofiles.open", return_value=mock_file)

        # Test reading
        content = await async_read_file(test_file)
        assert content == test_content

    @pytest.mark.asyncio
    async def test_async_write_file_mock(self, tmp_path: Path, mocker) -> None:
        """Test async file writing with mocked aiofiles."""
        from specify_cli.async_core.file import async_write_file

        test_file = tmp_path / "output.txt"
        test_content = "Hello, Async Write!"

        # Mock aiofiles.open - must be async itself
        mock_file = mocker.AsyncMock()
        mock_file.__aenter__ = mocker.AsyncMock(return_value=mock_file)
        mock_file.__aexit__ = mocker.AsyncMock()
        mock_file.write = mocker.AsyncMock()

        # aiofiles.open is async, so patch with AsyncMock that returns the file mock
        mock_open = mocker.AsyncMock(return_value=mock_file)
        mocker.patch("aiofiles.open", mock_open)

        # Test writing
        await async_write_file(test_file, test_content)

        # Verify open was called correctly
        mock_open.assert_called_once()
        # Note: write.assert_called_once_with won't work due to buffering, so we just verify it was called
        assert mock_file.write.called

    @pytest.mark.asyncio
    async def test_async_file_reader(self, tmp_path: Path, mocker) -> None:
        """Test AsyncFileReader class."""
        from specify_cli.async_core.file import AsyncFileReader

        test_file = tmp_path / "test.txt"
        test_content = "Line 1\nLine 2\nLine 3"

        # Mock aiofiles.open
        mock_file = mocker.AsyncMock()
        mock_file.__aenter__ = mocker.AsyncMock(return_value=mock_file)
        mock_file.__aexit__ = mocker.AsyncMock()
        mock_file.read = mocker.AsyncMock(return_value=test_content)

        mocker.patch("aiofiles.open", return_value=mock_file)

        reader = AsyncFileReader(test_file)
        content = await reader.read()

        assert content == test_content

    @pytest.mark.asyncio
    async def test_async_file_writer(self, tmp_path: Path, mocker) -> None:
        """Test AsyncFileWriter class."""
        from specify_cli.async_core.file import AsyncFileWriter

        test_file = tmp_path / "output.txt"
        test_content = "Test content"

        # Mock aiofiles.open
        mock_file = mocker.AsyncMock()
        mock_file.__aenter__ = mocker.AsyncMock(return_value=mock_file)
        mock_file.__aexit__ = mocker.AsyncMock()
        mock_file.write = mocker.AsyncMock()
        mock_file.close = mocker.AsyncMock()

        mocker.patch("aiofiles.open", return_value=mock_file)

        async with AsyncFileWriter(test_file) as writer:
            await writer.write(test_content)

    @pytest.mark.asyncio
    async def test_walk_async(self, tmp_path: Path) -> None:
        """Test async directory walking."""
        from specify_cli.async_core.file import walk_async

        # Create test directory structure
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir2").mkdir()
        (tmp_path / "file1.txt").touch()
        (tmp_path / "dir1" / "file2.txt").touch()

        # Walk directory
        files = []
        async for file_path in walk_async(tmp_path, pattern="*.txt"):
            files.append(file_path)

        # Should find both txt files
        assert len(files) == 2

    @pytest.mark.asyncio
    async def test_async_file_exists(self, tmp_path: Path, mocker) -> None:
        """Test async file existence check."""
        from specify_cli.async_core.file import async_file_exists

        test_file = tmp_path / "exists.txt"

        # Mock aiofiles.os.path.exists
        mocker.patch("aiofiles.os.path.exists", return_value=True)

        exists = await async_file_exists(test_file)
        assert exists is True

    @pytest.mark.asyncio
    async def test_async_mkdir(self, tmp_path: Path, mocker) -> None:
        """Test async directory creation."""
        from specify_cli.async_core.file import async_mkdir

        new_dir = tmp_path / "new_directory"

        # Mock aiofiles.os.makedirs
        mock_makedirs = mocker.AsyncMock()
        mocker.patch("aiofiles.os.makedirs", mock_makedirs)

        await async_mkdir(new_dir)

        mock_makedirs.assert_called_once()


@pytest.mark.unit
class TestAsyncDirectoryWatcher:
    """Test AsyncDirectoryWatcher functionality."""

    @pytest.mark.asyncio
    async def test_directory_watcher_initialization(self, tmp_path: Path) -> None:
        """Test directory watcher initialization."""
        from specify_cli.async_core.file import AsyncDirectoryWatcher

        watcher = AsyncDirectoryWatcher(tmp_path, patterns=["*.py"])

        assert watcher.directory == tmp_path
        assert watcher.patterns == ["*.py"]
        assert watcher.poll_interval == 1.0

    @pytest.mark.asyncio
    async def test_stop_watcher(self, tmp_path: Path) -> None:
        """Test stopping directory watcher."""
        from specify_cli.async_core.file import AsyncDirectoryWatcher

        watcher = AsyncDirectoryWatcher(tmp_path)
        watcher.stop()

        assert watcher._stopped is True


@pytest.mark.unit
class TestStreamingOperations:
    """Test streaming file operations."""

    @pytest.mark.asyncio
    async def test_stream_lines(self, mocker) -> None:
        """Test line-by-line streaming."""
        from specify_cli.async_core.file import AsyncFileReader

        test_lines = ["Line 1\n", "Line 2\n", "Line 3\n"]

        # Create async iterator for lines
        async def async_lines():
            for line in test_lines:
                yield line

        # Mock aiofiles.open
        mock_file = mocker.AsyncMock()
        mock_file.__aenter__ = mocker.AsyncMock(return_value=mock_file)
        mock_file.__aexit__ = mocker.AsyncMock()
        mock_file.__aiter__ = lambda self: async_lines()

        mocker.patch("aiofiles.open", return_value=mock_file)

        reader = AsyncFileReader(Path("test.txt"))
        lines = []

        async for line in reader.stream_lines():
            lines.append(line)

        assert lines == test_lines

    @pytest.mark.asyncio
    async def test_stream_chunks(self, mocker) -> None:
        """Test chunk-based streaming."""
        from specify_cli.async_core.file import AsyncFileReader

        test_content = "Hello World"
        chunks = ["Hello", " Worl", "d"]

        # Create async iterator for chunks
        chunk_index = 0

        async def read_chunk(size):
            nonlocal chunk_index
            if chunk_index < len(chunks):
                chunk = chunks[chunk_index]
                chunk_index += 1
                return chunk
            return ""

        # Mock aiofiles.open
        mock_file = mocker.AsyncMock()
        mock_file.__aenter__ = mocker.AsyncMock(return_value=mock_file)
        mock_file.__aexit__ = mocker.AsyncMock()
        mock_file.read = read_chunk

        mocker.patch("aiofiles.open", return_value=mock_file)

        reader = AsyncFileReader(Path("test.txt"), chunk_size=5)
        result_chunks = []

        async for chunk in reader.stream():
            result_chunks.append(chunk)

        assert result_chunks == chunks
