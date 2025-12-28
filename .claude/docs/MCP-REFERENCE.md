# Model Context Protocol (MCP) Reference

## Overview

MCP is an open standard for AI-tool integrations, enabling Claude Code to connect with external tools, databases, and APIs through a unified protocol.

## Architecture

```
┌─────────────────────────────────────┐
│         Claude Code (Host)          │
│  ┌─────────────────────────────┐   │
│  │  MCP Client (1:1 per server)│   │
│  └──────────────┬──────────────┘   │
└─────────────────┼──────────────────┘
                  │
         Transport Layer
    (STDIO, HTTP, Streamable HTTP)
         │
┌────────▼──────────────────────────┐
│      MCP Server (External)        │
├──────────────────────────────────┤
│  ┌──────────┐  ┌────────┐  ┌────┐│
│  │  Tools   │  │Resources│  │Prompts│
│  └──────────┘  └────────┘  └────┘│
└────────────────────────────────────┘
```

## Configuration

### Installation Commands

```bash
# HTTP server (recommended for remote)
claude mcp add --transport http github https://mcp.example.com/github

# STDIO server (local)
claude mcp add --transport stdio filesystem -- /usr/local/bin/mcp-fs /home

# List servers
claude mcp list

# Get details
claude mcp get github

# Remove server
claude mcp remove github

# Check status
/mcp
```

### Configuration Files

**Project scope (.mcp.json)**:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**User scope (~/.claude/mcp.json)**: Same format, applies to all projects.

## Transport Types

| Transport | Use Case | Performance |
|-----------|----------|-------------|
| **STDIO** | Local tools | Highest |
| **Streamable HTTP** | Remote/cloud | Good |
| **HTTP+SSE** | Legacy (deprecated) | Varies |

## Tool Invocation Pattern

```
mcp__<server-name>__<tool-name> [arguments]

Examples:
mcp__github__search_repositories
mcp__filesystem__read_file
mcp__postgres__execute_query
```

## MCP Slash Commands (Prompts)

```
/mcp__<server-name>__<prompt-name> [arguments]

Examples:
/mcp__github__create_issue title="Bug" body="Description"
/mcp__postgres__query_users
```

## Permission Configuration

```json
{
  "permissions": {
    "allow": [
      "mcp__github",
      "mcp__github__*",
      "mcp__github__read_*",
      "mcp__filesystem__read_file"
    ],
    "deny": [
      "mcp__dangerous__*"
    ]
  }
}
```

## Official Reference Servers

| Server | Purpose | Tools |
|--------|---------|-------|
| **Filesystem** | File operations | 20+ |
| **GitHub** | Repo management | 15+ |
| **Git** | Local git ops | 10+ |
| **Postgres** | Database queries | 8+ |
| **Memory** | Knowledge graph | 5+ |
| **Fetch** | Web scraping | 3 |

## Creating Custom MCP Servers

### Python (FastMCP)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.resource("file:///{path}")
def read_file(path: str) -> str:
    """Read file contents"""
    with open(path) as f:
        return f.read()

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### TypeScript

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "my-server",
  version: "1.0.0",
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "add") {
    return {
      content: [{ type: "text", text: `${a + b}` }],
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

**Critical**: For STDIO servers, NEVER write to stdout except JSON-RPC messages. Use stderr for all logs!

## Configuration Scopes

| Scope | Location | Priority |
|-------|----------|----------|
| Enterprise | Managed settings | Highest |
| User | `~/.claude/mcp.json` | Lower |
| Project Shared | `.mcp.json` | Medium |
| Project Local | `.claude/settings.local.json` | Higher than shared |

## Debugging

```bash
# Check status
/mcp

# Enable debugging
MCP_DEBUG=1 ./myserver

# MCP Inspector
# Access at http://localhost:6274/?token=<token>
```

## Security Best Practices

1. **Trusted Sources Only**: Anthropic doesn't audit third-party servers
2. **Token Security**: Store API keys in environment variables
3. **OAuth 2.1**: Required for HTTP servers
4. **Input Validation**: All server inputs must be validated
5. **Scope Principle**: Use read-only when possible

## Performance Optimization

1. **Idempotency**: Make tools safe for retries
2. **Pagination**: Use for large results
3. **Token Limits**: Warn when output > 10,000 tokens
4. **Caching**: Cache expensive operations
