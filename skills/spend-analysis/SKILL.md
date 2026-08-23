---
name: spend-analysis
description: Where money went this period — by category, vendor, card, and largest transactions.
version: 1.0.0
metadata:
  hermes:
    tags: [Finance, Spend, Vendors]
    related_skills: [finance-manager, anomaly-detection, budget-monitoring]
---

# Spend analysis

## When to Use

“What did we spend the most on?”, “top vendors”, “card spend this month”, “largest transactions.”

## Procedure

1. Fetch current-period transactions / expenses / card activity from AgentOS. Default period is calendar month-to-date in the account’s primary timezone; say the window you used.
2. Group in your reply (you may pre-sum before talking):
   - by category
   - by vendor
   - by card holder if the user asked
   - top 5 transactions
3. If they also asked “is that bad?”, load `anomaly-detection` or `budget-monitoring` and compute — do not guess.
4. Optional: pass category totals into `generate_cfo_summary` only as part of a wider close, not for a simple “top vendors” question.

## Reply shape

Lead with the period total and the top driver. Then at most five vendor or category lines. Mention one item that looks like it needs a human only if it is obvious (new vendor, single tx > 20% of the month).

## Pitfalls

- Do not classify a transaction as a category AgentOS did not give you unless you say you inferred it.
- Refunds and transfers can distort “spend” — exclude internal transfers when you can identify them.
- Knowledge policy (`knowledge/policies/spending.md`) is guidance, not a payment permission.
