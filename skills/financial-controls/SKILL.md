---
name: financial-controls
description: Read / prepare / execute-after-confirm policy. Always load before any payment, transfer, card, or beneficiary action.
version: 1.0.0
metadata:
  hermes:
    tags: [Finance, Safety, Approvals]
    related_skills: [finance-manager]
---

# Financial controls

Always-on approval policy. AgentOS is the primitive gate (scopes, no money-out by default). This skill is the **behavior** gate.

## When to Use

Every session that might write to Airwallex. Treat as loaded whenever `finance-manager` is loaded.

## Ladder

| Level | You may | You may not |
|---|---|---|
| 1 Read | Balances, accounts, transactions, cards, expenses, bills, reports | Imply a payment was sent |
| 2 Prepare | Draft payment, reimbursement, transfer, beneficiary, card request | Submit, confirm, or “just send it” |
| 3 Execute | Only after an allowlisted operator replies **YES** in this Telegram chat to a specific draft you just described | Infer approval from “ok”, “sure”, a previous chat, or a skill habit |

## Procedure for money-out or irreversible writes

1. Stay at Level 2. Use AgentOS **prepare / create-draft** tools only.
2. Do **not** call finance-manager MCP to move money. It has no payment tools.
3. Reply with what you prepared: amount, currency, counterparty, source account, and what happens if they approve.
4. End with a single clear ask: `Reply YES to submit this. Anything else and I leave it as a draft.`
5. Execute Level 3 only if the next user message is an explicit YES for **that** draft. If they change the amount or vendor, re-prepare and ask again.
6. If they say no, stop. Do not retry quietly. Do not schedule it.

## Never

- Invent “you already approved this.”
- Pay a new beneficiary and fire the first invoice in the same unconfirmed turn.
- Put this agent in a public Telegram group (anyone who can prompt it inherits your Airwallex scopes).
- Paste tokens, OAuth codes, or `.env` values into the chat.

## Verification

Before any Level 3 tool call, quote the draft identifiers back. After a write, tell the operator to confirm the resource in the Airwallex app.
