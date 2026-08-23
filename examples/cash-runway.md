# Example: cash and runway

Use this after AgentOS and the finance-manager MCP are connected. Numbers below are illustrative.

**You:** How much cash do we actually have, and what's runway?

**Agent should:**

1. Load `finance-manager` + `cash-position`.
2. Fetch current balances from Airwallex AgentOS (not memory).
3. Fetch roughly three months of outflows.
4. Call `get_cash_runway` with those figures.

**You should see:** a total, a by-account or by-currency split, months of runway, the burn window, and at most one caveat — not the raw tool payload.
