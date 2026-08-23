---
name: budget-monitoring
description: Plan vs actual by category using knowledge/budgets.yaml and current Airwallex spend.
version: 1.0.0
metadata:
  hermes:
    tags: [Finance, Budget]
    related_skills: [finance-manager, spend-analysis, month-end]
    config:
      - key: finance_manager.knowledge_dir
        description: Directory with budgets.yaml (defaults to this repo's knowledge/)
        default: ""
        prompt: Path to knowledge directory if not FINANCE_MANAGER_KNOWLEDGE_DIR
---

# Budget monitoring

## When to Use

“Are we over budget?”, “which categories are at risk?”, “underspend?”

## Procedure

1. Fetch month-to-date (or the requested period) actuals from AgentOS. Sum by category.
2. Call `calculate_budget_variance` with those actuals. If you omit `budgets`, the tool loads `budgets.yaml` then `budgets.example.yaml` from the knowledge dir.
3. Map AgentOS category names onto budget names conservatively. If you cannot map, put spend in `Other` and say you did.
4. Reply: categories **over** or **>80%** first, then material underspend. Include budget, actual, variance, % used.

## Tool contract

Actuals: `{category, amount, period?}`. Budgets optional if knowledge files exist.

Statuses from the tool: `over`, `at_risk` (≥80% and not over), `on_track`, `under` (<50% with ≥ half the period elapsed — informational only).

## Pitfalls

- Example budgets are fiction. If only `budgets.example.yaml` loaded, say so.
- Do not treat underspend as a problem unless the user asked.
- Variance is not a payment instruction.
