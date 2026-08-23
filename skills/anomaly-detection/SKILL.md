---
name: anomaly-detection
description: Flag unusual spend — large txs, new vendors, vendor spikes, card outliers, recurring changes.
version: 1.0.0
metadata:
  hermes:
    tags: [Finance, Anomalies]
    related_skills: [finance-manager, spend-analysis, month-end]
---

# Anomaly detection

## When to Use

“Anything weird?”, “why is AWS up?”, “new vendors this month”, “card outliers.”

## Procedure

1. Fetch **current-window** transactions from AgentOS (default: this month).
2. Fetch a **baseline** window (default: prior 3 complete months). If AgentOS cannot provide it, say so and run with a weaker baseline.
3. Optionally load `knowledge/vendors.yaml` known list via `detect_spend_anomalies` (the tool reads `FINANCE_MANAGER_KNOWLEDGE_DIR` when `use_knowledge_vendors` is true).
4. Call `detect_spend_anomalies` with current + baseline transactions. Amounts are money-out, positive.
5. Report at most five findings, highest severity first. Each finding needs type, amount, who/vendor, and why it flagged. Then stop unless asked to dig in.

## Finding types the tool emits

- `large_transaction` — z-score vs current window
- `new_vendor` — not in baseline and not in known vendors
- `vendor_spike` — this window vs baseline average × `spike_ratio` (default 1.5)
- `card_outlier` — holder vs their own baseline × `card_outlier_ratio` (default 2.0)
- `recurring_change` — same vendor, monthly run-rate moved materially

## Pitfalls

- No findings is a valid answer. Do not invent a scare.
- A new vendor that is $12 is noise; the tool drops below `min_amount` (default 250).
- Never “fix” an anomaly by paying or blocking a card unless the user asked and `financial-controls` is satisfied.
