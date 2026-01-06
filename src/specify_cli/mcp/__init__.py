"""
specify_cli.mcp - Model Context Protocol (MCP) Integration

Exposes ggen-spec-kit operations as MCP tools and resources for Claude and other MCP clients.

Features:
- Subscription management tools
- Usage tracking and quota enforcement
- Invoice generation and payment tracking
- Revenue metrics and reporting
- Feature access control
- Real-time billing status

This module enables Claude and other MCP-compatible clients to interact with
ggen-spec-kit's Revenue Operations infrastructure programmatically.
"""

from .server import create_revops_server

__all__ = ["create_revops_server"]
