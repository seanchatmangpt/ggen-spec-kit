# Claude Code Settings Reference

## Overview

Claude Code uses a hierarchical configuration system with multiple scopes and precedence levels.

## Settings Hierarchy (Highest to Lowest)

```
1. Enterprise Managed (cannot be overridden)
2. Command-line Arguments
3. Local Settings (.claude/settings.local.json)
4. Project Settings (.claude/settings.json)
5. User Settings (~/.claude/settings.json)
```

## Settings File Locations

| Scope | Location | Version Control |
|-------|----------|-----------------|
| Enterprise | System-managed | N/A |
| User | `~/.claude/settings.json` | No |
| Project | `.claude/settings.json` | Yes |
| Local | `.claude/settings.local.json` | No (gitignored) |

## Complete Settings Schema

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",

  // MODEL CONFIGURATION
  "model": "claude-sonnet-4-5-20250929",
  "outputStyle": "Explanatory|Balanced|Concise",
  "alwaysThinkingEnabled": false,

  // PERMISSIONS
  "permissions": {
    "allow": [
      "Bash(npm run:*)",
      "Bash(git:*)",
      "Read(src/**/*.ts)",
      "Edit(src/**)"
    ],
    "ask": [
      "Bash(git push:*)"
    ],
    "deny": [
      "Read(.env**)",
      "WebFetch",
      "Bash(rm:*)"
    ],
    "additionalDirectories": [
      "../docs/",
      "/shared/"
    ],
    "defaultMode": "acceptEdits|plan|review",
    "disableBypassPermissionsMode": false
  },

  // ENVIRONMENT
  "env": {
    "NODE_ENV": "development",
    "CUSTOM_VAR": "value"
  },

  // SANDBOX
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["git", "docker"]
  },

  // HOOKS
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/start.sh"
      }]
    }],
    "PreToolUse": [{
      "matcher": "Bash|Edit",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/pre-tool.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/format.sh"
      }]
    }],
    "Stop": [...]
  },

  // MCP SERVERS
  "enableAllProjectMcpServers": false,
  "enabledMcpjsonServers": ["npx://approved-server"],
  "disabledMcpjsonServers": ["npx://disabled-server"],

  // PLUGINS
  "enabledPlugins": {
    "plugin@marketplace": true
  },

  // ATTRIBUTION
  "attribution": {
    "commit": "🤖 Generated with Claude Code\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
  },

  // OTHER
  "cleanupPeriodDays": 30,
  "spinnerTipsEnabled": true,
  "vimMode": false
}
```

## Permission Rule Syntax

### Bash Commands (Prefix Matching)
```json
"Bash(npm run test:*)"    // Matches npm run test, npm run test:unit
"Bash(git:*)"             // All git commands
```

### File Paths (Glob Patterns)
```json
"Read(**/*.py)"           // All Python files
"Read(//etc/hosts)"       // Absolute path
"Read(~/Documents/**)"    // Home directory
"Read(src/**/*.ts)"       // Relative to settings.json
"Read(.env**)"            // Current directory relative
```

### Web Access
```json
"WebFetch(domain:github.com)"  // Domain filtering
```

### MCP Tools
```json
"mcp__github__*"              // All GitHub tools
"mcp__postgres__read_*"       // Read-only Postgres
```

## Permission Modes

| Mode | Behavior |
|------|----------|
| `default` | Prompts for sensitive operations |
| `acceptEdits` | Auto-approves file edits |
| `plan` | Analysis only, no modifications |
| `bypassPermissions` | Auto-approves all (unsafe) |

## Environment Variables

### Authentication
| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | API authentication |
| `ANTHROPIC_BASE_URL` | Custom API endpoint |

### Model Configuration
| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_MODEL` | Default model |
| `MAX_THINKING_TOKENS` | Extended thinking budget |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Output limit |

### Cloud Providers
| Variable | Purpose |
|----------|---------|
| `CLAUDE_CODE_USE_BEDROCK` | AWS Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | Google Vertex AI |
| `AWS_REGION` | AWS region |

### Network
| Variable | Purpose |
|----------|---------|
| `HTTP_PROXY` | HTTP proxy |
| `HTTPS_PROXY` | HTTPS proxy |
| `NODE_EXTRA_CA_CERTS` | Custom CA certificate |

### Bash Execution
| Variable | Purpose |
|----------|---------|
| `BASH_DEFAULT_TIMEOUT_MS` | Command timeout |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | Reset to project dir |

## Example Configurations

### Development (Permissive)
```json
{
  "permissions": {
    "allow": [
      "Bash(npm:*)",
      "Bash(git:*)",
      "Edit(src/**)"
    ]
  }
}
```

### Production (Restrictive)
```json
{
  "permissions": {
    "allow": [
      "Read(src/**)"
    ],
    "deny": [
      "Edit(**)",
      "Write(**)",
      "Bash(curl:*)",
      "WebFetch"
    ],
    "defaultMode": "plan"
  }
}
```

### Team Shared
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run:*)",
      "Bash(git commit:*)"
    ],
    "deny": [
      "Read(.env**)"
    ]
  },
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": ".claude/hooks/start.sh"
      }]
    }]
  }
}
```

## Best Practices

1. **Use JSON Schema**: Enable IDE autocomplete
2. **Least Privilege**: Only allow needed tools
3. **Team Configuration**: Commit `.claude/settings.json`
4. **Personal Overrides**: Use `.claude/settings.local.json`
5. **Explicit Denies**: Block sensitive file access
6. **Document Choices**: Comment why rules exist
