# Your First Subscription & Invoice

Welcome to Revenue Operations! In this tutorial, you'll create your first subscription, track usage, and generate an invoice using the `specify billing` command.

**Time to complete:** ~5 minutes
**Difficulty:** Beginner
**Prerequisites:** ggen-spec-kit installed and configured

## Step 1: Create a Subscription

Let's create a free subscription for a new user:

```bash
specify billing create-subscription 1000 --tier free
```

You should see:
```
✓ Subscription created for user 1000
  Tier: free
  Status: active
  Cost: $0/month
  API Quota: 100 calls/month
```

Great! User 1000 now has a free subscription with 100 API calls per month.

### What Happened?

The system created a subscription record with:
- **Tier**: free (no monthly cost)
- **Status**: active (ready to use)
- **API Quota**: 100 calls/month (free tier limit)
- **Storage Quota**: 2 GB (free tier limit)

## Step 2: Check Current Subscription

Verify the subscription was created:

```bash
specify billing get-subscription 1000
```

Output:
```
Subscription for User 1000
Tier                  free
Status                active
Monthly Cost          $0
API Quota             100 calls
Storage Quota         2147483648 bytes
Started               2026-01-06 00:00:00
```

## Step 3: Track API Usage

Now let's simulate the user making API calls. Track 50 API calls:

```bash
specify billing track-usage 1000 --metric api_calls --amount 50
```

Output:
```
✓ Usage tracked for user 1000
  Metric: api_calls
  Amount: 50
  Timestamp: 2026-01-06T12:34:56
```

Track 30 more calls:

```bash
specify billing track-usage 1000 --metric api_calls --amount 30
```

The user has now made 80 total API calls.

### Understanding Usage Tracking

The system tracks every API call the user makes:
- **metric**: What's being tracked (api_calls, storage, webhooks)
- **amount**: How much was consumed
- **Timestamp**: When it was tracked

This data is used for:
1. **Quota enforcement**: Prevent users from exceeding limits
2. **Billing**: Calculate overage charges if usage exceeds quota
3. **Analytics**: Understand product usage patterns

## Step 4: Check Usage Status

See how much of the quota has been used:

```bash
specify billing get-usage 1000
```

Output:
```
Usage Status for User 1000
Tier                  free
API Quota             100 calls
API Used              80 calls
Remaining            20 calls
Percentage Used      80.0%
Status               ⚠️ WARNING
```

**Why WARNING?** When usage reaches 80% of the quota, the system triggers a warning to alert users they're approaching their limit.

### Understanding Status Indicators

- **✅ OK** (0-79%): Normal operation
- **⚠️ WARNING** (80-99%): Approaching limit
- **🔴 EXCEEDED** (100%+): Over quota

## Step 5: Upgrade to Paid Tier

The user is getting close to the API limit. Let's upgrade them to the professional tier:

```bash
specify billing upgrade-subscription 1000 --tier professional
```

Output:
```
✓ Upgraded user 1000 to professional tier
  New Cost: $49/month
  New API Quota: 10000 calls/month
```

Now they have:
- **10,000 API calls/month** (up from 100)
- **50 GB storage** (up from 2 GB)
- **$49/month cost** (billed each month)

## Step 6: Generate an Invoice

Let's generate the invoice for the current billing month:

```bash
specify billing generate-invoice 1000
```

Output:
```
✓ Invoice generated for user 1000
Invoice ID            inv_abc123def456
Amount                $49.00
Status                draft
Issue Date            2026-01-06 00:00:00
Due Date              2026-02-05 00:00:00

Line Items:
Description                              Amount
Professional Subscription                $49.00
```

### Understanding the Invoice

- **Invoice ID**: Unique identifier (inv_abc123def456)
- **Amount**: Total billing charge ($49.00 for the month)
- **Status**: draft (ready for sending, not yet paid)
- **Issue Date**: When the invoice was created
- **Due Date**: When payment is due (30 days)
- **Line Items**: Breakdown of charges
  - Base subscription cost: $49.00
  - (Overage charges would appear here if usage exceeded quota)

## Step 7: Mark Invoice as Paid

When payment is received, mark the invoice as paid:

```bash
specify billing mark-paid inv_abc123def456
```

Output:
```
✓ Invoice inv_abc123def456 marked as paid
  Paid Date: 2026-01-06T12:34:56
```

## Step 8: Check Revenue Metrics

As a business, you want to see how much revenue you're collecting:

```bash
specify billing get-mrr
```

Output:
```
Monthly Recurring Revenue (MRR)
$49.00

Annual Recurring Revenue (ARR): $588.00
```

If you had multiple customers, you'd see the sum of all their subscription costs:

```bash
specify billing get-revenue
```

Output:
```
Revenue Breakdown by Tier
Tier              Subscribers    MRR
Free              1              $0.00
Professional      1              $49.00
Enterprise        0              $0.00

Total MRR: $49.00
```

## Complete Workflow

You've now completed the full subscription lifecycle:

```
1. Create Subscription (free tier)
   ↓
2. Check Subscription Details
   ↓
3. Track Usage (80 API calls)
   ↓
4. Check Usage Status (80% of quota)
   ↓
5. Upgrade Tier (professional)
   ↓
6. Generate Invoice ($49/month)
   ↓
7. Mark Invoice as Paid
   ↓
8. View Revenue Metrics (MRR = $49)
```

## What's Next?

Now that you understand the basics:

- **Learn MCP Integration**: Use RevOps with Claude via [Using RevOps MCP with Claude](./TUTORIAL_MCP_CLAUDE.md)
- **Handle Overages**: Track usage that exceeds quota and see overage charges
- **Multi-User Billing**: Create multiple users and see aggregated revenue metrics
- **Feature Access Control**: Check which features are available by subscription tier

## Key Concepts

### Subscription Tiers

| Tier | Cost/Month | API Calls/Month | Storage | Best For |
|------|-----------|-----------------|---------|----------|
| **Free** | $0 | 100 | 2 GB | Learning, testing |
| **Professional** | $49 | 10,000 | 50 GB | Small teams |
| **Enterprise** | $499 | 100,000 | 1 TB | Large scale |

### Billing Period

Revenue Operations uses monthly billing periods (YYYY-MM format):
- **2026-01** = January 2026
- **2026-02** = February 2026

Invoices are generated once per billing period per user.

### Overage Charges

If a user exceeds their quota:
- **Professional**: $0.05 per extra API call
- **Enterprise**: Contact sales for custom rates

## Troubleshooting

### "No active subscription found"
The user doesn't have a subscription yet. Create one with:
```bash
specify billing create-subscription <user_id> --tier free
```

### "Invoice already exists for this period"
An invoice has already been generated for this user this month. To generate next month's invoice, use:
```bash
specify billing generate-invoice <user_id> --period 2026-02
```

### "Database not found"
RevOps uses SQLite by default. The database is created automatically at `./revops.db`. Make sure you have write permissions in the current directory.

## Summary

Congratulations! You've learned:
- ✅ Creating subscriptions
- ✅ Tracking usage
- ✅ Managing quotas
- ✅ Generating invoices
- ✅ Viewing revenue metrics

In the next tutorial, learn how to use these operations from Claude via the MCP interface.
