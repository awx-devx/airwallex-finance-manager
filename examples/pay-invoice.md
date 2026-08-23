# Example: pay this invoice

**You:** Pay this invoice. [attach or paste vendor + amount]

**Agent should:**

1. Load `financial-controls`. Stay at **prepare**.
2. Use AgentOS to draft the beneficiary/payment only.
3. Not call any finance-manager MCP tool to send money (there isn't one).
4. Reply with amount, currency, counterparty, source account.
5. Ask: `Reply YES to submit this. Anything else and I leave it as a draft.`

**You:** No.

**Agent should:** leave the draft and stop. No silent retry.

**You (later, on the same draft):** YES

**Agent should:** only then attempt an execute-level AgentOS call, and tell you to confirm the result in the Airwallex app.
