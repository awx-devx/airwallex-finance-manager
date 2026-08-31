# Airwallex AI Finance Manager

**This is a reference demo, not a product.** Clone it to see how a self-hosted [Hermes Agent](https://hermes-agent.nousresearch.com/) can talk to you on Telegram and act as a company finance manager on top of [Airwallex AgentOS](https://www.airwallex.com/docs/developer-tools/ai/agentos). Use it as a starting point for your own agent — do not treat it as production software, financial advice, or an official Airwallex application.

Airwallex supplies the financial primitives. This repo supplies the install path, Hermes skills, and a local MCP for computed tools (runway, anomalies, budget variance, CFO summary). It is not a hosted bot and not an AgentOS proxy. You run everything on your own machine against **your** Airwallex account.

Dollar amounts in skills, tests, and `knowledge/*.example.yaml` are **fictional**.

```text
Telegram → Hermes → Airwallex AgentOS MCP
                 → this repo's finance-manager MCP
                 → this repo's skills + SOUL.md
```

## What you get

| Piece | Role |
| --- | --- |
| Hermes skills (`skills/`) | When and how to work: cash, spend, anomalies, budgets, month-end, approval policy |
| Custom MCP (`mcp/finance-manager/`) | Deterministic compute: runway, anomalies, variance, CFO summary. Does **not** call Airwallex |
| AgentOS MCP (remote) | Live balances, transactions, cards, bills — OAuth to your org |
| Knowledge examples | Template budgets / vendors / policies you copy and fill locally |

## Prerequisites

| You provide | Why |
| --- | --- |
| [Hermes Agent](https://hermes-agent.nousresearch.com/docs/getting-started/installation) on `PATH` | Runtime, skills, MCP client, Telegram gateway |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | Launches the local Python MCP (`requires-python >= 3.11`) |
| An LLM API key (OpenAI, Anthropic, or another Hermes-supported provider) | Reasoning and tool use |
| An [Airwallex](https://www.airwallex.com/) account with AgentOS access | Live financial primitives |
| A Telegram bot token from [@BotFather](https://t.me/BotFather) | Channel into the agent |
| Numeric Telegram user IDs to allowlist | Only those people can prompt the finance agent |

A laptop is enough. You can skip Telegram at first and use `hermes chat` on the CLI.

## Quickstart

```bash
git clone https://github.com/HeimLabs/airwallex-finance-manager.git
cd airwallex-finance-manager
./scripts/install.sh
```

The installer checks for `hermes` and `uv`, syncs the MCP, and merges this pack into `~/.hermes/` (config, env key names, `SOUL.md`). It does **not** log you into Airwallex or write secrets into this clone.

Then, on that same machine:

1. Put your model key in `~/.hermes/.env` (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`).
2. Bind **your** Airwallex account (browser OAuth — no API key in this repo):

   ```bash
   hermes mcp login airwallex
   ```

   Sign in to the org you want the agent to see. Hermes stores tokens under `~/.hermes/mcp-tokens/`. On a VPS, run this on the server as the gateway user and paste the browser callback URL back into the prompt ([remote OAuth](docs/repo-guide.md#remote-server--vps)).
3. Optional knowledge files (live copies are gitignored):

   ```bash
   cp knowledge/budgets.example.yaml knowledge/budgets.yaml
   cp knowledge/vendors.example.yaml knowledge/vendors.yaml
   cp knowledge/policies/spending.example.md knowledge/policies/spending.md
   ```
4. `hermes gateway setup` (Telegram) and allowlist numeric user IDs, or set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` in `~/.hermes/.env`.
5. `hermes gateway` — or `hermes chat` if you are not using Telegram yet.
6. In Telegram, send `/new` (a restored DM keeps the old session), then ask a finance question. Skills do not load on `"hi"`.

**Do not add this bot to a public group.** Anyone who can prompt it inherits your Airwallex scopes.

## Try it

Once the gateway is up, DM the bot something like:

- “How much cash do we have, and how many months of runway?”
- “Anything unusual in spending this month?”
- “Are we over budget on cloud?”
- “Prepare the month-end pack.”

Sample threads (tool sequence, not live data) live in [`examples/`](examples/).

## Environment variables

Secrets live in `~/.hermes/.env`, **not** in this repository. `hermes/env.example` lists the names; `install.sh` sets `FINANCE_MANAGER_ROOT` for you.

| Variable | Required | Where | Purpose |
| --- | --- | --- | --- |
| `FINANCE_MANAGER_ROOT` | Yes (installer) | `~/.hermes/.env` | Absolute path to this clone |
| `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` | Yes | `~/.hermes/.env` | Model provider Hermes expects |
| `TELEGRAM_BOT_TOKEN` | For Telegram | `~/.hermes/.env` | BotFather token |
| `TELEGRAM_ALLOWED_USERS` | For Telegram | `~/.hermes/.env` | Comma-separated numeric Telegram user IDs |
| `FINANCE_MANAGER_KNOWLEDGE_DIR` | No | MCP env | Defaults to `$FINANCE_MANAGER_ROOT/knowledge` |

There is no `AIRWALLEX_API_KEY` here. AgentOS uses OAuth (`hermes mcp login airwallex`).

## Sandbox vs production

[AgentOS MCP](https://www.airwallex.com/docs/developer-tools/ai/agentos) (`https://mcp.airwallex.com/mcp`) talks to the **live** org you sign in with. There is no sandbox clone of AgentOS.

Sandbox is a different server — [Developer MCP](https://www.airwallex.com/docs/developer-tools/ai/developer-connector) — and tool names will not match 1:1. Details: [docs/repo-guide.md §5.3](docs/repo-guide.md#sandbox-developer-mcp).

Use a **separate** Hermes profile and Telegram bot for experiments vs anything you treat as real finance.

## Security

Read [SECURITY.md](SECURITY.md) and [docs/repo-guide.md §7–8](docs/repo-guide.md#7-telegram-specific-controls).

- Allowlist only. Private DMs first.
- Credentials stay in `~/.hermes/.env` and `~/.hermes/mcp-tokens/`. Never commit them. Never paste them into a prompt.
- The custom MCP has no money-out tools. AgentOS money-out is off by default; `financial-controls` still requires an explicit confirmation from an allowlisted user.
- This is not financial advice. You are responsible for your Airwallex account, scopes, and compliance.

## Layout

```text
airwallex-finance-manager/
├── README.md
├── LICENSE
├── SECURITY.md
├── docs/                  # how the pack is structured; product thesis
├── hermes/                # SOUL.md, config fragment, env key names
├── skills/                # Hermes SKILL.md workflows
├── mcp/finance-manager/   # local FastMCP server (Python)
├── knowledge/             # example budgets, vendors, policies
├── examples/              # sample Telegram threads
└── scripts/install.sh     # merge the pack into ~/.hermes/
```

Hermes reads from `~/.hermes/`, not from the git clone, unless you point it here.

## Development

```bash
cd mcp/finance-manager
uv sync --extra dev
uv run pytest
```

Add a skill as `skills/<name>/SKILL.md`. Add a compute-first tool on the MCP — do not wrap AgentOS `get_accounts()` “for convenience.” See [docs/repo-guide.md §9](docs/repo-guide.md#9-extension-points).

## Docs

| Doc | What it is |
| --- | --- |
| [docs/repo-guide.md](docs/repo-guide.md) | Contract: architecture, setup, security ladder |
| [docs/airwallex-ai-finance-manager-direction.md](docs/airwallex-ai-finance-manager-direction.md) | Why the demo exists (design intent, not a user guide) |
| [examples/](examples/) | Sample Telegram threads to verify a fresh install |
| [mcp/finance-manager/README.md](mcp/finance-manager/README.md) | Custom MCP tools |
| [knowledge/README.md](knowledge/README.md) | How to copy example plans locally |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting and operator rules |

## License

[MIT](LICENSE). Airwallex, Telegram, and Hermes are trademarks of their respective owners. This project is not affiliated with, endorsed by, or an official product of Airwallex.
