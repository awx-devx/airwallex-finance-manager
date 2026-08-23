# Airwallex AI Finance Manager

A setup pack for a self-hosted [Hermes Agent](https://hermes-agent.nousresearch.com/) that talks to you on **Telegram** and acts as a company finance manager on top of [Airwallex AgentOS](https://www.airwallex.com/docs/developer-tools/ai/agentos).

Airwallex supplies the financial primitives. This repo supplies the install path, Hermes skills, and a local MCP for computed tools (runway, anomalies, budget variance, CFO summary). It is not a hosted bot and not an AgentOS proxy.

```text
Telegram → Hermes → Airwallex AgentOS MCP
                 → this repo's finance-manager MCP
                 → this repo's skills + SOUL.md
```

## Quickstart

You bring: Hermes, a model API key, an Airwallex account, a Telegram bot token, and numeric Telegram user IDs to allowlist.

**A laptop is enough for the full stack** (Hermes + AgentOS OAuth + this repo’s MCP + Telegram). Run `./scripts/install.sh` and `hermes mcp login airwallex` on that machine — the browser and the OAuth listener are on the same box, so you do not paste callback URLs. Use a VPS only if you want the Telegram bot to stay up when the laptop sleeps. You can also skip Telegram at first and use `hermes chat` on the CLI.

```bash
git clone https://github.com/HeimLabs/airwallex-finance-manager.git
cd airwallex-finance-manager
./scripts/install.sh
```

Then:

1. Put your model key in `~/.hermes/.env`
2. Bind **your** Airwallex account (browser OAuth — no API key in this repo):

   ```bash
   hermes mcp login airwallex
   ```

   Sign in to the Airwallex org you want the agent to see. Hermes stores the
   tokens under `~/.hermes/mcp-tokens/`. On a VPS, run this on the server as
   the gateway user and paste the browser callback URL back into the prompt
   ([remote OAuth](docs/repo-guide.md#remote-server--vps)).
3. `hermes gateway setup` (Telegram) and allowlist users
4. `hermes gateway`
5. Send the bot a **private** DM first

Do not add this bot to a public group. Anyone who can prompt it inherits your Airwallex scopes.

## Docs

| Doc | What it is |
|---|---|
| [docs/repo-guide.md](docs/repo-guide.md) | How this repo is structured and how the agent uses it |
| [docs/airwallex-ai-finance-manager-direction.md](docs/airwallex-ai-finance-manager-direction.md) | Why the project exists |
| [examples/](examples/) | Sample Telegram threads to verify a fresh install |
| [mcp/finance-manager/README.md](mcp/finance-manager/README.md) | Custom MCP tools |

## Layout

- `hermes/` — `SOUL.md`, config fragment, env key names
- `skills/` — Hermes `SKILL.md` workflows and approval policy
- `mcp/finance-manager/` — compute-first FastMCP server
- `knowledge/` — example budgets, vendors, policies
- `scripts/install.sh` — merge the pack into `~/.hermes/`
