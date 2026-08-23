from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

from finance_manager.compute import budget_variance, cash_runway, cfo_summary, spend_anomalies
from finance_manager.knowledge import default_knowledge_dir
from finance_manager.models import Balance, BudgetLine, CategoryActual, PeriodAmount, Transaction

mcp = FastMCP(
    "finance-manager",
    instructions=(
        "Compute-first finance tools. Pass Airwallex AgentOS figures in. "
        "These tools do not call Airwallex and cannot move money."
    ),
)


def _knowledge_dir() -> Path | None:
    return default_knowledge_dir()


@mcp.tool
def get_cash_runway(
    balances: list[Balance],
    monthly_outflows: list[PeriodAmount] | None = None,
    average_monthly_burn: float | None = None,
    reporting_currency: str | None = None,
    fx_rates: dict[str, float] | None = None,
    burn_lookback_months: int = 3,
) -> dict:
    """Months of runway from current balances and recent monthly burn.

    Pass AgentOS balances and outflows. Does not fetch Airwallex. Mixed
    currencies need fx_rates (currency → reporting) or they are left out of
    the reporting total.
    """
    return cash_runway(
        balances=balances,
        monthly_outflows=monthly_outflows,
        average_monthly_burn=average_monthly_burn,
        reporting_currency=reporting_currency,
        fx_rates=fx_rates,
        burn_lookback_months=burn_lookback_months,
    )


@mcp.tool
def detect_spend_anomalies(
    transactions: list[Transaction],
    baseline_transactions: list[Transaction] | None = None,
    spike_ratio: float = 1.5,
    large_tx_zscore: float = 2.0,
    card_outlier_ratio: float = 2.0,
    min_amount: float = 250.0,
    use_knowledge_vendors: bool = True,
) -> dict:
    """Flag large txs, new vendors, vendor spikes, card outliers, recurring changes.

    Amounts are money-out and positive. Baseline should be prior months.
    When use_knowledge_vendors is true, known vendors are loaded from the
    knowledge directory (vendors.yaml, else the example file).
    """
    return spend_anomalies(
        transactions=transactions,
        baseline_transactions=baseline_transactions,
        spike_ratio=spike_ratio,
        large_tx_zscore=large_tx_zscore,
        card_outlier_ratio=card_outlier_ratio,
        min_amount=min_amount,
        use_knowledge_vendors=use_knowledge_vendors,
        knowledge_dir=_knowledge_dir(),
    )


@mcp.tool
def calculate_budget_variance(
    actuals: list[CategoryActual],
    budgets: list[BudgetLine] | None = None,
    period: str | None = None,
    currency: str | None = None,
    period_elapsed_ratio: float = 0.5,
) -> dict:
    """Compare category actuals to the plan.

    If budgets is omitted, loads knowledge/budgets.yaml then
    budgets.example.yaml. Say so in Telegram if the example file was used.
    """
    return budget_variance(
        actuals=actuals,
        budgets=budgets,
        period=period,
        currency=currency,
        knowledge_dir=_knowledge_dir(),
        period_elapsed_ratio=period_elapsed_ratio,
    )


@mcp.tool
def generate_cfo_summary(
    cash_runway_result: dict | None = None,
    spend_by_category: list[CategoryActual] | None = None,
    anomalies_result: dict | None = None,
    budget_variance_result: dict | None = None,
    outstanding_items: list[str] | None = None,
    period: str | None = None,
) -> dict:
    """Compose a CFO pack from the other tools' outputs. Does not fetch data."""
    return cfo_summary(
        cash_runway_result=cash_runway_result,
        spend_by_category=spend_by_category,
        anomalies_result=anomalies_result,
        budget_variance_result=budget_variance_result,
        outstanding_items=outstanding_items,
        period=period,
    )
