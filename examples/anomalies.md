# Example: anything weird?

**You:** Anything weird happening with spend this month?

**Agent should:**

1. Load `anomaly-detection`.
2. Fetch this month's transactions from AgentOS.
3. Fetch the prior three months as baseline.
4. Call `detect_spend_anomalies` (leave `use_knowledge_vendors` true if you have `knowledge/vendors.yaml` or the example).

**You should see:** up to five findings (new vendor, spike, large tx, card outlier, recurring change) with amounts and why they flagged — or an explicit “nothing above threshold.”
