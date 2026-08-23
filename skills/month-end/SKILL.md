---
name: month-end
description: Multi-step finance close — cash, spend, anomalies, outstanding items, CFO summary.
version: 1.0.0
metadata:
  hermes:
    tags: [Finance, Close, Report]
    related_skills:
      - finance-manager
      - cash-position
      - spend-analysis
      - anomaly-detection
      - budget-monitoring
      - financial-controls
---

# Month-end

A workflow, not a single fetch.

## When to Use

“Prepare month-end”, “CFO summary”, “close the month”, “finance pack.”

## Procedure

1. Agree the period (default: last complete calendar month if today is on/after the 1st and they said “close”; otherwise month-to-date). State it.
2. Follow `cash-position` — balances + `get_cash_runway`.
3. Follow `spend-analysis` — period totals by category and top vendors.
4. Follow `anomaly-detection` — current vs prior 3 months.
5. Follow `budget-monitoring` if `budgets.yaml` or the example file exists.
6. Pull outstanding bills / expenses awaiting action from AgentOS if those tools exist. List them as items needing a human; do not pay them.
7. Call `generate_cfo_summary` with the structured outputs from the tools above plus `outstanding_items`.
8. Telegram reply: the summary’s headline bullets, then “Needs you” for anything requiring a human. Offer to drill into one finding.

## Pitfalls

- Do not skip the AgentOS fetches and only call `generate_cfo_summary` with guessed numbers.
- Do not execute payments as part of close. Prepare only under `financial-controls`.
- If a tool is missing, skip that section and say what you could not compute.
