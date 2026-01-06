# RevOps MCP Integration

## Overview

The ggen-spec-kit project is integrated with **FastMCP** to expose Revenue Operations infrastructure as Model Context Protocol (MCP) tools. This enables Claude and other MCP-compatible clients to programmatically interact with billing, subscriptions, usage tracking, and revenue metrics.

## Quick Start

### 1. Install FastMCP

```bash
pip install fastmcp
# or
uv pip install fastmcp
```

### 2. Start the MCP Server

```bash
python -m specify_cli.mcp.server
```

Or with a custom database:

```bash
DATABASE_URL=postgresql://user:pass@localhost/revops python -m specify_cli.mcp.server
```

### 3. Connect from Claude

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "revops": {
      "command": "python",
      "args": ["-m", "specify_cli.mcp.server"],
      "env": {
        "PYTHONPATH": "src",
        "DATABASE_URL": "sqlite:///./revops.db"
      }
    }
  }
}
```

Then restart Claude Desktop to see the RevOps tools available.

## Available Tools

### Subscription Management

#### `create_subscription(user_id, tier="free", stripe_customer_id=None)`
Create a new subscription for a user.

**Parameters:**
- `user_id` (int): Unique user identifier
- `tier` (str): Subscription tier (free, professional, enterprise)
- `stripe_customer_id` (str, optional): Stripe customer ID

**Returns:** Subscription details

**Example:**
```
create_subscription(user_id=123, tier="professional")
```

#### `get_subscription(user_id)`
Retrieve active subscription for a user.

**Parameters:**
- `user_id` (int): Unique user identifier

**Returns:** Subscription details or null

**Example:**
```
get_subscription(user_id=123)
```

#### `upgrade_subscription(user_id, new_tier)`
Upgrade or downgrade subscription tier.

**Parameters:**
- `user_id` (int): Unique user identifier
- `new_tier` (str): Target tier (free, professional, enterprise)

**Returns:** Updated subscription details

**Example:**
```
upgrade_subscription(user_id=123, new_tier="enterprise")
```

#### `cancel_subscription(user_id)`
Cancel an active subscription.

**Parameters:**
- `user_id` (int): Unique user identifier

**Returns:** Cancellation confirmation

**Example:**
```
cancel_subscription(user_id=123)
```

### Usage Tracking & Quotas

#### `track_usage(user_id, metric_type, amount)`
Track usage event for metered billing.

**Parameters:**
- `user_id` (int): Unique user identifier
- `metric_type` (str): Type of usage (api_calls, storage, webhooks)
- `amount` (float): Amount consumed

**Returns:** Event confirmation with timestamp

**Example:**
```
track_usage(user_id=123, metric_type="api_calls", amount=50)
```

#### `get_usage_status(user_id)`
Get current usage status against quota.

**Parameters:**
- `user_id` (int): Unique user identifier

**Returns:** Status with tier, quota, usage, remaining, percentage, warnings

**Example:**
```
get_usage_status(user_id=123)
```

**Response:**
```json
{
  "tier": "professional",
  "api_quota": 10000,
  "api_calls_used": 5000,
  "remaining": 5000,
  "percentage_used": 50.0,
  "warning": false,
  "exceeded": false
}
```

#### `get_usage_history(user_id, billing_period=None)`
Get aggregated usage for a billing period.

**Parameters:**
- `user_id` (int): Unique user identifier
- `billing_period` (str, optional): YYYY-MM format (defaults to current)

**Returns:** Aggregated usage by metric type

**Example:**
```
get_usage_history(user_id=123, billing_period="2026-01")
```

### Invoicing & Payments

#### `generate_invoice(user_id, billing_period=None)`
Generate invoice for a user.

**Parameters:**
- `user_id` (int): Unique user identifier
- `billing_period` (str, optional): YYYY-MM format (defaults to current)

**Returns:** Invoice details with amount, status, line items

**Example:**
```
generate_invoice(user_id=123)
```

**Response:**
```json
{
  "invoice_id": "inv_12345",
  "subscription_id": "sub_789",
  "amount": "54.50",
  "status": "draft",
  "issue_date": "2026-01-06T00:00:00",
  "due_date": "2026-02-05T00:00:00",
  "line_items": [
    {
      "description": "Professional Subscription",
      "quantity": 1,
      "unit_price": "49.00",
      "amount": "49.00"
    },
    {
      "description": "API Calls Overage (110 calls)",
      "quantity": 110,
      "unit_price": "0.05",
      "amount": "5.50"
    }
  ]
}
```

#### `get_invoices(user_id, limit=12)`
Get invoice history for a user.

**Parameters:**
- `user_id` (int): Unique user identifier
- `limit` (int): Maximum number to return (default 12)

**Returns:** List of invoice records (most recent first)

**Example:**
```
get_invoices(user_id=123, limit=6)
```

#### `mark_payment_received(invoice_id, stripe_invoice_id=None)`
Mark invoice as paid.

**Parameters:**
- `invoice_id` (str): Invoice UUID
- `stripe_invoice_id` (str, optional): Stripe invoice ID

**Returns:** Updated invoice with paid_date

**Example:**
```
mark_payment_received(invoice_id="inv_12345", stripe_invoice_id="si_789")
```

### Revenue Metrics

#### `get_monthly_recurring_revenue()`
Get total Monthly Recurring Revenue (MRR).

**Returns:** MRR as decimal string

**Example:**
```
get_monthly_recurring_revenue()
# Returns: "24500.00"
```

#### `get_annual_recurring_revenue()`
Get total Annual Recurring Revenue (ARR).

**Returns:** ARR as decimal string (MRR × 12)

**Example:**
```
get_annual_recurring_revenue()
# Returns: "294000.00"
```

#### `get_revenue_breakdown()`
Get revenue broken down by subscription tier.

**Returns:** Revenue data with count and MRR by tier

**Example:**
```
get_revenue_breakdown()
```

**Response:**
```json
{
  "free": {
    "count": 1000,
    "mrr": "0.00"
  },
  "professional": {
    "count": 500,
    "mrr": "24500.00"
  },
  "enterprise": {
    "count": 10,
    "mrr": "4990.00"
  },
  "total": "29490.00"
}
```

### Feature Access Control

#### `check_feature_access(user_tier, feature)`
Check if a tier has access to a feature.

**Parameters:**
- `user_tier` (str): Subscription tier (free, professional, enterprise)
- `feature` (str): Feature name to check

**Returns:** Access result with allowed, required_tier, reason

**Example:**
```
check_feature_access(user_tier="professional", feature="sso")
```

**Response:**
```json
{
  "allowed": false,
  "feature": "sso",
  "tier": "professional",
  "required_tier": "enterprise",
  "reason": "Feature 'sso' requires enterprise subscription or higher"
}
```

#### `get_tier_features(tier)`
Get all features available in a tier.

**Parameters:**
- `tier` (str): Subscription tier

**Returns:** List of feature names

**Example:**
```
get_tier_features(tier="professional")
```

**Response:**
```json
[
  "web_editor",
  "export_pdf",
  "public_specifications",
  "api_read",
  "custom_domain",
  "private_specifications",
  "api_write",
  "webhooks",
  "priority_email_support",
  "audit_logs"
]
```

#### `get_tier_limits(tier)`
Get rate limits and quotas for a tier.

**Parameters:**
- `tier` (str): Subscription tier

**Returns:** Limits dict with API calls, storage, team members, RPS

**Example:**
```
get_tier_limits(tier="professional")
```

**Response:**
```json
{
  "api_calls_per_month": 10000,
  "api_calls_per_minute": 100,
  "storage_bytes": 53687091200,
  "max_team_members": 25,
  "requests_per_second": 10
}
```

### Configuration

#### `get_subscription_tiers()`
Get configuration for all tiers.

**Returns:** Tier configurations with pricing, quotas, features

**Example:**
```
get_subscription_tiers()
```

**Response:**
```json
{
  "free": {
    "monthly_cost": "0.00",
    "annual_cost": "0.00",
    "api_quota": 100,
    "storage_quota": 2147483648,
    "max_users": 1,
    "features": [...]
  },
  "professional": {
    "monthly_cost": "49.00",
    "annual_cost": "490.00",
    "api_quota": 10000,
    "storage_quota": 53687091200,
    "max_users": 25,
    "features": [...]
  },
  "enterprise": {
    "monthly_cost": "499.00",
    "annual_cost": "4990.00",
    "api_quota": 100000,
    "storage_quota": 1099511627776,
    "max_users": 999,
    "features": [...]
  }
}
```

#### `get_revops_status()`
Get system status.

**Returns:** Version, subscription count, user count, MRR, timestamp

**Example:**
```
get_revops_status()
```

**Response:**
```json
{
  "version": "1.0.0",
  "status": "healthy",
  "active_subscriptions": 1510,
  "total_users": 1510,
  "mrr": "29490.00",
  "timestamp": "2026-01-06T19:00:00.000000"
}
```

## Architecture

### Three-Tier Design

The MCP server maintains the three-tier architecture:

1. **Operations Layer** (`ops/billing.py`)
   - Pure business logic with no I/O
   - Reusable across CLI, API, MCP, webhooks
   - Fully testable in isolation

2. **Runtime Layer** (`runtime/billing.py`)
   - All database I/O operations
   - Session and transaction management
   - Persistence operations

3. **MCP Layer** (`mcp/server.py`)
   - MCP tool definitions
   - Session management for each tool
   - Type-safe parameter validation
   - Error handling

### Tool Organization

Tools are organized by domain:

```
Subscription Management (4 tools)
├── create_subscription
├── get_subscription
├── upgrade_subscription
└── cancel_subscription

Usage & Quotas (3 tools)
├── track_usage
├── get_usage_status
└── get_usage_history

Invoicing (3 tools)
├── generate_invoice
├── get_invoices
└── mark_payment_received

Revenue Metrics (3 tools)
├── get_monthly_recurring_revenue
├── get_annual_recurring_revenue
└── get_revenue_breakdown

Feature Access (3 tools)
├── check_feature_access
├── get_tier_features
└── get_tier_limits

Configuration (2 tools)
├── get_subscription_tiers
└── get_revops_status

Total: 18 MCP Tools
```

## Usage Examples

### Example 1: Create Free Subscription and Track Usage

```python
# Create subscription
sub = create_subscription(user_id=100, tier="free")

# Track usage
track_usage(user_id=100, metric_type="api_calls", amount=50)
track_usage(user_id=100, metric_type="api_calls", amount=30)

# Check status
status = get_usage_status(user_id=100)
# {
#   "tier": "free",
#   "api_quota": 100,
#   "api_calls_used": 80,
#   "remaining": 20,
#   "percentage_used": 80.0,
#   "warning": true,  <- Warning at 80%
#   "exceeded": false
# }
```

### Example 2: Upgrade and Generate Invoice

```python
# Upgrade from free to professional
upgrade_subscription(user_id=100, new_tier="professional")

# Generate invoice with overage
generate_invoice(user_id=100)
# {
#   "amount": "54.50",  # $49 base + $5.50 overage
#   "line_items": [
#     {"description": "Professional Subscription", "amount": "49.00"},
#     {"description": "API Calls Overage (110 calls)", "amount": "5.50"}
#   ]
# }
```

### Example 3: Revenue Analytics

```python
# Get MRR
mrr = get_monthly_recurring_revenue()

# Get breakdown
breakdown = get_revenue_breakdown()
# {
#   "free": {"count": 1000, "mrr": "0.00"},
#   "professional": {"count": 500, "mrr": "24500.00"},
#   "enterprise": {"count": 10, "mrr": "4990.00"},
#   "total": "29490.00"
# }

# Get system status
status = get_revops_status()
# {
#   "active_subscriptions": 1510,
#   "total_users": 1510,
#   "mrr": "29490.00"
# }
```

## Configuration

### Environment Variables

- `DATABASE_URL`: Database connection string (defaults to `sqlite:///./revops.db`)
- `PYTHONPATH`: Must include `src` directory for imports

### FastMCP Configuration

The `revops.fastmcp.json` file configures the MCP server:

```json
{
  "mcpServers": {
    "revops": {
      "command": "python",
      "args": ["-m", "specify_cli.mcp.server"],
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

Copy this to Claude's config directory:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Database Setup

### SQLite (Default)

```bash
python -m specify_cli.mcp.server
# Creates: ./revops.db
```

### PostgreSQL

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/revops python -m specify_cli.mcp.server
```

### MySQL

```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/revops python -m specify_cli.mcp.server
```

## Development

### Adding New Tools

1. Define the operation in `ops/billing.py` (pure logic)
2. Define the runtime in `runtime/billing.py` (I/O)
3. Add MCP tool in `mcp/server.py`:

```python
@mcp.tool
def new_operation(param1: str, param2: int) -> dict[str, Any]:
    """
    Tool description for Claude.
    """
    session = SessionLocal()
    try:
        return runtime_operation(session, param1, param2)
    finally:
        session.close()
```

### Testing Tools

```bash
# Start server
python -m specify_cli.mcp.server

# In another terminal, test with curl or your MCP client
```

## Integration Patterns

### Pattern 1: Automated Billing

Claude can automatically:
- Create subscriptions on signup
- Track usage from API calls
- Generate and send invoices
- Mark payments received from webhooks

### Pattern 2: Customer Support

Claude can help customers:
- Check their subscription tier
- View usage status and warnings
- See available features
- Review invoice history

### Pattern 3: Analytics

Claude can generate reports:
- MRR and ARR trends
- Revenue by tier breakdown
- Subscriber counts
- Overage analysis

### Pattern 4: Admin Operations

Claude can assist with:
- Tier upgrades/downgrades
- Invoice adjustments
- Customer analytics
- System health checks

## Limitations & Future Work

### Current (Phase 1 - 80/20)

- ✅ Subscription management
- ✅ Usage tracking
- ✅ Quota enforcement
- ✅ Invoice generation
- ✅ Revenue metrics
- ✅ Feature access control

### Planned (Phase 2 - Remaining 20%)

- ⏳ Stripe API runtime integration (actual payments)
- ⏳ Webhook endpoints (payment notifications)
- ⏳ Invoice PDF generation
- ⏳ Automated renewal scheduler
- ⏳ Refund processing
- ⏳ Dunning management

### Future Enhancements

- Multi-currency support
- Seat-based billing
- Churn prediction
- Usage optimization recommendations
- Advanced analytics
- Custom pricing rules

## Security Considerations

1. **Database Security**
   - Use environment variables for credentials
   - Never hardcode connection strings
   - Use SSL for remote databases

2. **Tool Authorization**
   - All tools currently open (suitable for internal use)
   - Add authorization layer if exposing to external clients
   - Rate limiting recommended

3. **Data Privacy**
   - Customer data in database
   - PII not stored by RevOps system
   - Comply with GDPR/CCPA as needed

## Troubleshooting

### Server won't start

```bash
# Check Python path
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python -m specify_cli.mcp.server

# Check database permission
chmod 600 ./revops.db
```

### Database errors

```bash
# Reset database
rm ./revops.db

# Recreate empty database
python -m specify_cli.mcp.server
```

### Import errors

```bash
# Ensure dependencies installed
pip install -r requirements.txt

# Check PYTHONPATH
echo $PYTHONPATH
```

## References

- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [RevOps Summary](./REVOPS_SUMMARY.md)
- [RevOps Thesis](./REVOPS_THESIS.tex)

## License

This MCP integration is part of ggen-spec-kit and follows the same license.
