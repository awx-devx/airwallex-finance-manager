# finance-manager MCP

Local stdio MCP server. Hermes launches it; it does **not** call Airwallex.

Tools: `get_cash_runway`, `detect_spend_anomalies`, `calculate_budget_variance`, `generate_cfo_summary`.

## Run

```bash
uv sync
uv run python -m finance_manager
```

Hermes config (also in `hermes/config.example.yaml`):

```yaml
mcp_servers:
  finance-manager:
    command: uv
    args:
      - run
      - --directory
      - ${FINANCE_MANAGER_ROOT}/mcp/finance-manager
      - python
      - -m
      - finance_manager
    env:
      FINANCE_MANAGER_KNOWLEDGE_DIR: ${FINANCE_MANAGER_ROOT}/knowledge
```

## Tests

```bash
uv sync --extra dev
uv run pytest
```

`FINANCE_MANAGER_KNOWLEDGE_DIR` points at `knowledge/` so budget and vendor files can be read when the agent omits inline budgets.
