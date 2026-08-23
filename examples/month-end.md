# Example: month-end pack

**You:** Prepare our month-end finance report.

**Agent should:**

1. Load `month-end` and state the period.
2. Run the `cash-position` path → `get_cash_runway`.
3. Run `spend-analysis` from AgentOS transactions.
4. Run `anomaly-detection` → `detect_spend_anomalies`.
5. Run `budget-monitoring` → `calculate_budget_variance` (say if the example budget file was used).
6. List outstanding bills/expenses from AgentOS as “needs a human.”
7. Call `generate_cfo_summary` with those structured outputs.

**You should see:** headline bullets + a short “Needs you” list. No payments executed as part of close.
