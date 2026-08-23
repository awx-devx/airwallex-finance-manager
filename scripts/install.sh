#!/usr/bin/env bash
# Register this pack with a local Hermes profile (~/.hermes).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
MCP_DIR="$ROOT/mcp/finance-manager"

echo "Repo:        $ROOT"
echo "Hermes home: $HERMES_HOME"

if ! command -v hermes >/dev/null 2>&1; then
  echo
  echo "hermes is not on PATH. Install it first:"
  echo "  https://hermes-agent.nousresearch.com/docs/getting-started/installation"
  echo "Then re-run this script."
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo
  echo "uv is not on PATH. The finance-manager MCP is launched with uv."
  echo "  https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
fi

mkdir -p "$HERMES_HOME"
echo "Syncing finance-manager MCP dependencies…"
(cd "$MCP_DIR" && uv sync --extra dev)

echo "Merging Hermes config, env, and SOUL…"
(cd "$MCP_DIR" && uv run python "$ROOT/scripts/install_hermes_config.py" --repo-root "$ROOT" --hermes-home "$HERMES_HOME")

echo
echo "Next (you do these):"
echo "  1. Put your model provider key in $HERMES_HOME/.env"
echo "  2. Log into YOUR Airwallex account (this is how the agent sees your org):"
echo "       hermes mcp login airwallex"
echo "     Tokens go to $HERMES_HOME/mcp-tokens/ — not this repo, not an API key."
echo "     https://www.airwallex.com/docs/developer-tools/ai/agentos"
echo "  3. Create a Telegram bot with @BotFather and allowlist numeric user IDs:"
echo "       hermes gateway setup"
echo "     or set TELEGRAM_BOT_TOKEN and TELEGRAM_ALLOWED_USERS in $HERMES_HOME/.env"
echo "  4. In Telegram send /new (gateway restart restores the old session)."
echo "     Skills do not load on 'hi' — ask a finance question."
echo "     If you had a custom soul, it was backed up to $HERMES_HOME/SOUL.pre-finance-manager.md"
echo "  5. Copy knowledge examples if you want a real plan:"
echo "       cp $ROOT/knowledge/budgets.example.yaml $ROOT/knowledge/budgets.yaml"
echo "  6. Start Telegram:"
echo "       hermes gateway"
echo
echo "Private DM first. Do not add this bot to a public group."
echo "Details: $ROOT/docs/repo-guide.md"
