from pathlib import Path

from finance_manager.compute import budget_variance, cash_runway, cfo_summary, spend_anomalies
from finance_manager.models import Balance, BudgetLine, CategoryActual, PeriodAmount, Transaction

REPO_KNOWLEDGE = Path(__file__).resolve().parents[3] / "knowledge"


def test_cash_runway_single_currency():
    result = cash_runway(
        balances=[
            Balance(amount=450_000, currency="USD", account_name="Operating"),
            Balance(amount=50_000, currency="USD", account_name="Reserve"),
        ],
        monthly_outflows=[
            PeriodAmount(period="2026-05", amount=40_000, currency="USD"),
            PeriodAmount(period="2026-06", amount=42_000, currency="USD"),
            PeriodAmount(period="2026-07", amount=38_000, currency="USD"),
        ],
    )
    assert result["total_cash"] == 500000.0
    assert result["average_monthly_burn"] == 40000.0
    assert result["runway_months"] == 12.5
    assert result["concentration"]["share"] == 90.0
    assert any("concentrated" in c for c in result["caveats"])


def test_cash_runway_requires_burn_input():
    result = cash_runway(balances=[Balance(amount=10, currency="USD")])
    assert "error" in result


def test_cash_runway_skips_unconverted_currency():
    result = cash_runway(
        balances=[
            Balance(amount=100_000, currency="USD", account_name="USD"),
            Balance(amount=80_000, currency="EUR", account_name="EUR"),
        ],
        average_monthly_burn=10_000,
        reporting_currency="USD",
    )
    assert result["total_cash"] == 100000.0
    assert result["by_currency"]["EUR"] == 80000.0
    assert any("EUR" in c for c in result["caveats"])


def test_cash_runway_fx_and_spike_caveat():
    result = cash_runway(
        balances=[Balance(amount=100_000, currency="EUR", account_name="EU")],
        monthly_outflows=[
            PeriodAmount(period="2026-05", amount=10_000, currency="EUR"),
            PeriodAmount(period="2026-06", amount=10_000, currency="EUR"),
            PeriodAmount(period="2026-07", amount=30_000, currency="EUR"),
        ],
        reporting_currency="USD",
        fx_rates={"EUR": 1.1},
    )
    assert result["total_cash"] == 110000.0
    assert any("2×" in c for c in result["caveats"])


def test_anomalies_new_vendor_and_spike():
    baseline = [
        Transaction(date="2026-05-02", amount=1000, vendor="AWS", card_holder="Sam"),
        Transaction(date="2026-06-02", amount=1100, vendor="AWS", card_holder="Sam"),
        Transaction(date="2026-07-02", amount=900, vendor="AWS", card_holder="Sam"),
        Transaction(date="2026-05-10", amount=400, vendor="Notion"),
    ]
    current = [
        Transaction(id="t1", date="2026-08-03", amount=4000, vendor="AWS", card_holder="Sam"),
        Transaction(id="t2", date="2026-08-04", amount=14200, vendor="Acme Rare"),
        Transaction(id="t3", date="2026-08-05", amount=300, vendor="Notion"),
        Transaction(id="t4", date="2026-08-06", amount=310, vendor="Notion"),
        Transaction(id="t5", date="2026-08-07", amount=320, vendor="Notion"),
    ]
    result = spend_anomalies(
        current,
        baseline,
        use_knowledge_vendors=False,
        min_amount=250,
    )
    types = {f["type"] for f in result["findings"]}
    assert "new_vendor" in types
    assert "vendor_spike" in types
    assert "card_outlier" in types
    acme = next(f for f in result["findings"] if f["vendor"] == "Acme Rare")
    assert acme["type"] == "new_vendor"
    assert acme["amount"] == 14200.0


def test_anomalies_known_vendor_not_new():
    current = [Transaction(date="2026-08-01", amount=3000, vendor="AWS")]
    result = spend_anomalies(
        current,
        baseline_transactions=[],
        use_knowledge_vendors=True,
        knowledge_dir=REPO_KNOWLEDGE,
        min_amount=250,
    )
    assert result["known_vendors_source"] == "vendors.example.yaml"
    assert not any(f["type"] == "new_vendor" for f in result["findings"])


def test_budget_variance_statuses():
    result = budget_variance(
        actuals=[
            CategoryActual(category="Cloud", amount=11_000),
            CategoryActual(category="Travel", amount=5000),
            CategoryActual(category="Mystery", amount=200),
        ],
        budgets=[
            BudgetLine(name="Cloud", budget=12_000, owner="Eng"),
            BudgetLine(name="Travel", budget=4_000, owner="Ops"),
            BudgetLine(name="Payroll", budget=80_000, owner="People"),
        ],
        period_elapsed_ratio=0.7,
    )
    by_name = {c["name"]: c for c in result["categories"]}
    assert by_name["Travel"]["status"] == "over"
    assert by_name["Cloud"]["status"] == "at_risk"
    assert by_name["Payroll"]["status"] == "under"
    assert result["unmatched_actuals"][0]["category"] == "Mystery"


def test_budget_loads_example_knowledge():
    result = budget_variance(
        actuals=[CategoryActual(category="Cloud", amount=1000)],
        knowledge_dir=REPO_KNOWLEDGE,
    )
    assert result["example_data"] is True
    assert result["budget_source"] == "budgets.example.yaml"
    assert result["totals"]["budget"] == 131500.0


def test_cfo_summary_composes_without_inventing():
    runway = cash_runway(
        balances=[Balance(amount=100_000, currency="USD")],
        average_monthly_burn=20_000,
    )
    anomalies = spend_anomalies(
        [Transaction(date="2026-08-01", amount=9000, vendor="NewCo")],
        [],
        use_knowledge_vendors=False,
        min_amount=250,
    )
    summary = cfo_summary(
        cash_runway_result=runway,
        spend_by_category=[CategoryActual(category="Cloud", amount=8000)],
        anomalies_result=anomalies,
        outstanding_items=["2 bills awaiting approval"],
        period="2026-08",
    )
    assert summary["period"] == "2026-08"
    assert any("100000" in h or "100,000" in h or "Cash USD 100000" in h for h in summary["headlines"])
    assert any("runway 5.0" in h for h in summary["headlines"])
    assert "2 bills awaiting approval" in summary["needs_you"]
    assert summary["inputs_used"]["cash_runway"] is True
