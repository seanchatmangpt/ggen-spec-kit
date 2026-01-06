# Using RevOps MCP with Claude

Learn how to manage subscriptions, invoices, and revenue metrics directly through Claude using the Model Context Protocol (MCP).

**Time to complete:** ~5 minutes
**Difficulty:** Intermediate
**Prerequisites:**
- ggen-spec-kit installed
- Claude Desktop app installed
- Python 3.10+

## What is MCP?

The Model Context Protocol (MCP) allows Claude to directly interact with your RevOps system. Instead of typing CLI commands, you can chat with Claude and ask it to:
- Create subscriptions
- Track usage
- Generate invoices
- Check revenue metrics
- Manage customer subscriptions

## Step 1: Install FastMCP

FastMCP is the framework that powers RevOps MCP integration:

```bash
pip install fastmcp
```

Or with uv:

```bash
uv pip install fastmcp
```

Verify installation:

```bash
python -c "import fastmcp; print('FastMCP ready')"
```

## Step 2: Configure Claude Desktop

Add RevOps MCP to your Claude Desktop configuration.

### macOS

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows

Edit: `%APPDATA%\Claude\claude_desktop_config.json`

### Linux

Edit: `~/.config/Claude/claude_desktop_config.json`

Add this configuration:

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

Replace the paths if your ggen-spec-kit directory is not in the current working directory.

### Restart Claude

Close and reopen Claude Desktop. The RevOps MCP server is now available!

## Step 3: Start Your First RevOps Conversation

Open Claude and ask:

```
Create a subscription for user 100 with the free tier.
```

Claude will respond:

```
I'll create a free subscription for user 100.

Result:
- User ID: 100
- Tier: free
- Status: active
- Monthly Cost: $0/month
- API Quota: 100 calls/month
```

### What Just Happened?

Claude used the RevOps MCP to:
1. Parse your request
2. Call `create_subscription(user_id=100, tier="free")`
3. Return the result

No CLI commands needed!

## Step 4: Check Subscription Status

Ask Claude:

```
What's the subscription status for user 100?
```

Claude responds:

```
Subscription Details for User 100:
- Tier: free
- Status: active
- Monthly Cost: $0
- API Quota: 100 calls/month
- Storage: 2 GB
```

## Step 5: Track Usage from Claude

```
Track 50 API calls for user 100.
```

Claude:

```
I've tracked 50 API calls for user 100.

Event Details:
- User ID: 100
- Metric: api_calls
- Amount: 50
- Timestamp: 2026-01-06T12:34:56
```

Track more usage:

```
User 100 made another 30 API calls.
```

## Step 6: Check Usage and Quota

```
How much of user 100's quota have they used?
```

Claude:

```
Current Usage for User 100:

Tier: free
API Quota: 100 calls/month
API Calls Used: 80 calls
Remaining: 20 calls
Percentage Used: 80.0%
Status: ⚠️ WARNING

The user is approaching their limit!
```

## Step 7: Upgrade the Subscription

```
Upgrade user 100 to the professional tier.
```

Claude:

```
I've upgraded user 100 to professional.

New Details:
- Tier: professional
- Monthly Cost: $49/month
- API Quota: 10,000 calls/month
- Storage: 50 GB
```

## Step 8: Generate Invoice

```
Generate an invoice for user 100.
```

Claude:

```
Invoice created for user 100.

Invoice Details:
- Invoice ID: inv_abc123def456
- Amount: $49.00
- Status: draft
- Due Date: 2026-02-05

Line Items:
- Professional Subscription: $49.00
```

## Step 9: Mark Payment Received

```
I received payment for invoice inv_abc123def456.
```

Claude:

```
I've marked invoice inv_abc123def456 as paid.

Payment Details:
- Status: paid
- Paid Date: 2026-01-06T12:34:56
```

## Step 10: Revenue Dashboard

```
What's our monthly recurring revenue?
```

Claude:

```
Monthly Recurring Revenue (MRR): $49.00
Annual Recurring Revenue (ARR): $588.00

This is based on 1 active subscription.
```

Request a breakdown:

```
Show me revenue by subscription tier.
```

Claude:

```
Revenue Breakdown:

Tier              | Subscribers | MRR
Free              | 0           | $0.00
Professional      | 1           | $49.00
Enterprise        | 0           | $0.00
                  |             |
Total MRR:        |             | $49.00
```

## Advanced: Multi-User Scenario

Let's create a more realistic scenario:

```
Create subscriptions for three new users:
- User 201: free tier
- User 202: professional tier
- User 203: enterprise tier

Then show me the revenue breakdown.
```

Claude:

```
I've created three subscriptions:

✓ User 201: free tier ($0/month)
✓ User 202: professional tier ($49/month)
✓ User 203: enterprise tier ($499/month)

Revenue Breakdown:
Tier              | Subscribers | MRR
Free              | 1           | $0.00
Professional      | 1           | $49.00
Enterprise        | 1           | $499.00
                  |             |
Total MRR:        |             | $548.00

Year-over-year projection: $6,576
```

## Advanced: Feature Access Control

Ask Claude about feature availability:

```
Can professional users access webhooks? What about SSO?
```

Claude:

```
Professional Tier Access:

✓ Webhooks: YES
  - Available in professional tier
  - Required for event subscriptions

✗ SSO (Single Sign-On): NO
  - Only available in enterprise tier
  - Required for large organizations with multiple users

Would you like to upgrade this user to enterprise?
```

## Advanced: Complete Customer Flow

Tell Claude:

```
I have a new customer (user 300) signing up. Walk me through the complete flow:
1. Create them with a free tier
2. They use 85 API calls this month
3. Check their usage and alert them
4. They want to upgrade to professional
5. Generate their first invoice
6. Record payment received
```

Claude will:

```
I'll walk through the complete customer flow for user 300.

Step 1: Creating free subscription...
✓ Created: User 300, free tier, $0/month

Step 2: Tracking usage...
✓ Tracked: 85 API calls

Step 3: Checking usage...
⚠️ ALERT: User 300 is at 85% of quota
  - 85 calls used of 100
  - 15 calls remaining
  - Recommend upgrade

Step 4: Upgrading to professional...
✓ Upgraded to professional
  - Now: 10,000 calls/month
  - Cost: $49/month

Step 5: Generating invoice...
✓ Invoice created: inv_pro123
  - Amount: $49.00
  - Due: 2026-02-05

Step 6: Recording payment...
✓ Payment marked as received
  - Status: paid
  - Date: 2026-01-06

Customer onboarding complete!
```

## Using RevOps with Claude for Business Tasks

### Task 1: Monthly Revenue Report

```
Generate a monthly revenue report including:
- Total MRR
- Revenue by tier
- Number of subscribers
```

Claude generates a formatted report with all metrics.

### Task 2: Customer Alerts

```
Check usage for all customers and alert me about anyone over 75% quota.
```

Claude checks each subscription and reports:

```
Usage Alerts:

⚠️ User 102: 76% of quota (76/100 API calls)
⚠️ User 105: 92% of quota (9200/10000 API calls)

Recommendations:
- Suggest upgrade to User 102 (free tier, approaching limit)
- Contact User 105 (may need enterprise tier)
```

### Task 3: Billing Operations

```
Process end-of-month billing:
1. Generate invoices for all active users
2. Show me the total billing amount
3. List any customers who haven't paid last month
```

Claude executes the workflow:

```
Processing end-of-month billing for 2026-01...

✓ Generated 5 invoices
  - Free tier: 0 invoices ($0)
  - Professional: 3 invoices ($147.00)
  - Enterprise: 2 invoices ($998.00)

Total Billing: $1,145.00

Previous Month Unpaid:
- Invoice inv_123 for User 101: $49.00 (30 days overdue)

Action: Consider sending payment reminder to User 101
```

## Troubleshooting

### "MCP server not found" in Claude

1. Verify FastMCP is installed: `pip list | grep fastmcp`
2. Check configuration file syntax (must be valid JSON)
3. Restart Claude Desktop
4. Check file paths in configuration

### "Database not found" error

Make sure the database path in the configuration exists and has write permissions:

```bash
touch ./revops.db
chmod 600 ./revops.db
```

### Commands not appearing in Claude

1. Restart Claude Desktop (not just the chat)
2. Check that the MCP server process started (look for Python process)
3. Try: "What RevOps operations can you help me with?"

## Key MCP Tools Available

RevOps exposes 18 MCP tools through Claude:

**Subscriptions (4 tools)**
- create_subscription
- get_subscription
- upgrade_subscription
- cancel_subscription

**Usage & Quotas (3 tools)**
- track_usage
- get_usage_status
- get_usage_history

**Invoicing (3 tools)**
- generate_invoice
- get_invoices
- mark_payment_received

**Metrics (3 tools)**
- get_monthly_recurring_revenue
- get_annual_recurring_revenue
- get_revenue_breakdown

**Features (3 tools)**
- check_feature_access
- get_tier_features
- get_tier_limits

**Configuration (2 tools)**
- get_subscription_tiers
- get_revops_status

## Summary

With RevOps MCP, you can:
- ✅ Manage subscriptions through natural language
- ✅ Track usage and check quotas
- ✅ Generate and process invoices
- ✅ Monitor revenue metrics
- ✅ Automate customer workflows
- ✅ Make business decisions with real data

Claude becomes your RevOps assistant, handling complex billing workflows in conversation!

## Next Steps

- **Explore Advanced Scenarios**: Try complex multi-user workflows
- **Automate Processes**: Use Claude in your backend systems
- **Integrate with CRM**: Connect RevOps data with customer records
- **Create Dashboards**: Ask Claude for formatted revenue reports
