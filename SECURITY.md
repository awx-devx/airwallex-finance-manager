# Security

This repository is a **reference demo**. When configured, it talks to a live
Airwallex account through AgentOS OAuth and can prepare financial actions.

## Reporting a vulnerability

Do not open a public GitHub issue for security problems.

Use [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) on this repository.

## What this repo never stores

- API keys, Telegram tokens, or OAuth tokens
- Filled `.env` files
- Live company budgets, vendor lists, or spending policies

Keep secrets in `~/.hermes/.env` and `~/.hermes/mcp-tokens/`. They are outside
this clone. Rotate anything that was pasted into chat or committed by accident.

## Operator rules

- Allowlist numeric Telegram user IDs. Do not enable open pairing.
- Use private DMs first. Do not add the bot to a public group.
- Anyone who can prompt the agent inherits your Airwallex OAuth scopes.
- Start read-only. Money-out requires an explicit confirmation from an allowlisted user.
