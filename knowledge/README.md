# Knowledge files

Optional company context for the finance-manager MCP and skills.

Copy an example, drop the `.example` suffix, and edit. The install does not overwrite your copies.

| Example | Your file | Used by |
|---|---|---|
| `budgets.example.yaml` | `budgets.yaml` | `calculate_budget_variance`, `budget-monitoring` |
| `vendors.example.yaml` | `vendors.yaml` | `detect_spend_anomalies` (known vs new vendor) |
| `policies/spending.example.md` | `policies/spending.md` | `financial-controls`, `spend-analysis` |

`budgets.yaml` and `vendors.yaml` are gitignored once created so live plans stay local.
