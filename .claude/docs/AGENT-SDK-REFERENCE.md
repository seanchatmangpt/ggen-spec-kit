# Claude Agent SDK Reference

## Overview

The Claude Agent SDK is Anthropic's framework for building autonomous AI agents with capabilities including file operations, code execution, web search, and MCP integration.

## Installation & Availability

```bash
# Python
pip install claude-agent-sdk

# TypeScript
npm install claude-agent-sdk
```

**Web Note**: Agent SDK requires local execution; use Claude Code CLI for web browser sessions.

## Two Primary APIs

### Simple Stateless API: `query()`

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Analyze the repository",
        options=ClaudeAgentOptions(
            allowed_tools=['Read', 'Glob', 'Grep'],
            model='claude-opus-4-1-20250805'
        )
    ):
        print(message)

anyio.run(main)
```

### Stateful API: `ClaudeSDKClient`

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def main():
    async with ClaudeSDKClient() as client:
        await client.query("Find test files")

        async for message in client.receive_response():
            print(message)

        # Follow-up maintains context
        await client.query("Analyze test coverage")
        async for message in client.receive_response():
            print(message)
```

## Configuration Options

```python
options = ClaudeAgentOptions(
    # Model
    model='claude-opus-4-5-20251101',
    fallback_models=['claude-sonnet-4-5-20250929'],

    # Tools
    allowed_tools=['Read', 'Write', 'Edit', 'Bash'],
    disallowed_tools=['WebFetch'],

    # Permissions
    permission_mode='default',  # or 'acceptEdits', 'bypassPermissions'
    can_use_tool=custom_check,  # Callback function

    # Session
    resume=session_id,
    fork_session=False,

    # Context
    system_prompt="You are a code reviewer...",
    setting_sources=['project'],  # Load CLAUDE.md

    # MCP
    mcp_servers={'tools': mcp_server},

    # Hooks
    hooks=[{
        'matcher': 'Write|Edit',
        'callbacks': [validation_callback]
    }],

    # Limits
    max_tokens=100000,

    # Output
    output_format='json'
)
```

## Built-in Tools (8)

| Tool | Purpose |
|------|---------|
| `Read` | Read file contents |
| `Write` | Create/overwrite files |
| `Edit` | Modify file sections |
| `Bash` | Execute shell commands |
| `Glob` | Pattern-based file search |
| `Grep` | Content search |
| `WebSearch` | Search the web |
| `WebFetch` | Fetch URL content |

## Custom Tool Registration

### Using @tool Decorator

```python
from claude_agent_sdk import ClaudeSDKClient, tool, ToolResult

@tool(
    name="get_weather",
    description="Get weather for a location"
)
async def get_weather(location: str) -> ToolResult:
    weather = await fetch_weather_api(location)
    return ToolResult(
        content=f"Weather in {location}: {weather}",
        is_error=False
    )

async with ClaudeSDKClient(tools=[get_weather]) as client:
    await client.query("What's the weather in Seattle?")
```

### In-Process MCP Server

```python
from claude_agent_sdk import createSdkMcpServer, tool, ToolResult

@tool(name="query_db", description="Query database")
async def query_db(sql: str) -> ToolResult:
    result = await db.execute(sql)
    return ToolResult(content=str(result))

mcp_server = createSdkMcpServer(
    name="database_tools",
    version="1.0.0",
    tools=[query_db]
)

options = ClaudeAgentOptions(
    mcp_servers={'db': mcp_server}
)
```

## Message Types

```python
from claude_agent_sdk import (
    UserMessage,
    AssistantMessage,
    SystemMessage,
    ResultMessage,
    StreamEvent
)

async for message in client.receive_response():
    if isinstance(message, SystemMessage):
        if message.subtype == 'init':
            session_id = message.session_id

    elif isinstance(message, AssistantMessage):
        for block in message.content:
            if block.type == 'text':
                print(block.text)
            elif block.type == 'tool_use':
                print(f"Tool: {block.name}")

    elif isinstance(message, ResultMessage):
        print(f"Tokens: {message.usage.input_tokens}")
        print(f"Cost: ${message.cost:.4f}")
```

## Session Management

### Resume Session
```python
options = ClaudeAgentOptions(
    resume=session_id
)
```

### Fork Session
```python
options = ClaudeAgentOptions(
    resume=session_id,
    fork_session=True  # Creates independent branch
)
```

## Hook Integration

```python
async def pre_tool_check(input_data, tool_use_id, context):
    if input_data['tool_name'] == 'Bash':
        command = input_data['tool_input'].get('command', [])
        if 'rm -rf' in ' '.join(command):
            return {'permissionDecision': 'deny', 'reason': 'Dangerous'}
    return {}

options = ClaudeAgentOptions(
    hooks=[{
        'event': 'PreToolUse',
        'callback': pre_tool_check
    }]
)
```

## Error Handling

```python
from claude_agent_sdk import (
    ClaudeSDKError,
    CLINotFoundError,
    ProcessError,
    PermissionDeniedError
)

try:
    async with ClaudeSDKClient() as client:
        await client.query("Analyze code")
        async for msg in client.receive_response():
            pass

except CLINotFoundError:
    print("Install Claude Code CLI")

except PermissionDeniedError as e:
    print(f"Permission denied: {e}")

except ClaudeSDKError as e:
    print(f"SDK error: {e}")
```

## Subagent Configuration

```python
options = ClaudeAgentOptions(
    subagents={
        'code_reviewer': {
            'description': 'Reviews code quality',
            'system_prompt': 'You are a code reviewer...',
            'allowed_tools': ['Read', 'Grep'],
            'model': 'claude-opus-4-5-20251101'
        },
        'test_writer': {
            'description': 'Writes tests',
            'allowed_tools': ['Read', 'Write'],
            'model': 'claude-sonnet-4-5-20250929'
        }
    },
    allowed_tools=['Task']  # Enable delegation
)
```

## Project Context Loading

```python
# Load CLAUDE.md and project settings
client = ClaudeSDKClient(
    options=ClaudeAgentOptions(
        setting_sources=['project']
    )
)
```

**Important**: In SDK v0.6+, project settings are NOT loaded automatically. You must explicitly set `setting_sources`.

## Best Practices

1. **Single Responsibility**: One job per subagent
2. **Explicit Permissions**: Define allowed_tools precisely
3. **Error Handling**: Catch and handle SDK exceptions
4. **Session Management**: Use resume for continuity
5. **Hook Validation**: Validate tool inputs
6. **Context Awareness**: Load project settings explicitly
7. **Web Compatibility**: Use HTTP transports for MCP when on web
