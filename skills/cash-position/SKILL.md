---
name: cash-position
description: Current cash, by account/currency, change vs prior period, and runway. Use for liquidity questions.
version: 1.0.0
metadata:
  hermes:
    tags: [Finance, Cash, Runway]
    related_skills: [finance-manager, financial-controls, month-end]
---

# Cash position

Answer liquidity questions with current Airwallex data plus computed runway.

## When to Use

“How much cash do we have?”, “runway”, “are we concentrated in one account?”, “cash vs last month.”

## Procedure

1. Fetch **current** balances / accounts from Airwallex AgentOS. Never invent a total.
2. Fetch enough recent outflows to estimate burn (prefer the last 3 complete months). Inflows do not count as negative burn unless the user asked for net cash.
3. Call finance-manager `get_cash_runway` with those balances and monthly outflows (or a stated average monthly burn). Pass `fx_rates` only if you actually have rates; otherwise leave mixed currencies unconverted.
4. Reply: total cash, split by currency and account if more than one, runway months, burn window used, one concentration or caveat.

## Tool contract

`get_cash_runway` is compute-first. Pass AgentOS figures in; do not expect it to log into Airwallex.

- `balances`: `{amount, currency, account_id?, account_name?}`
- `monthly_outflows`: `{period, amount, currency}` (period `YYYY-MM`)
- or `average_monthly_burn` if the user gave a number
- `reporting_currency` + `fx_rates` optional

## Pitfalls

- A single huge month should be called out, not silently averaged away — the tool flags a thin window.
- Do not convert EUR→USD without a rate.
- Prior-period comparison needs two fetches (or a period filter), not memory.
