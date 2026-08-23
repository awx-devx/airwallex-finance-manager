from __future__ import annotations

import statistics
from collections import defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from finance_manager.knowledge import load_budgets, load_known_vendors, normalize_name
from finance_manager.models import (
    Balance,
    BudgetLine,
    CategoryActual,
    Finding,
    PeriodAmount,
    Transaction,
)

TWOPLACES = Decimal("0.01")


def money(value: float | Decimal) -> float:
    return float(Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP))


def _convert(amount: float, currency: str, reporting: str, fx_rates: dict[str, float] | None) -> float | None:
    if currency.upper() == reporting.upper():
        return amount
    if not fx_rates:
        return None
    rate = fx_rates.get(currency) or fx_rates.get(currency.upper())
    if rate is None:
        return None
    return amount * rate


def cash_runway(
    balances: list[Balance],
    monthly_outflows: list[PeriodAmount] | None = None,
    average_monthly_burn: float | None = None,
    reporting_currency: str | None = None,
    fx_rates: dict[str, float] | None = None,
    burn_lookback_months: int = 3,
) -> dict:
    if not balances:
        return {"error": "balances is required"}

    currencies = {b.currency.upper() for b in balances}
    reporting = (reporting_currency or next(iter(currencies))).upper()

    by_currency: dict[str, float] = defaultdict(float)
    by_account: list[dict] = []
    unconverted: list[str] = []

    total_reporting = 0.0
    for balance in balances:
        by_currency[balance.currency.upper()] += balance.amount
        converted = _convert(balance.amount, balance.currency, reporting, fx_rates)
        row = {
            "account_id": balance.account_id,
            "account_name": balance.account_name,
            "amount": money(balance.amount),
            "currency": balance.currency.upper(),
        }
        if converted is None and balance.currency.upper() != reporting:
            unconverted.append(balance.currency.upper())
            row["reporting_amount"] = None
        else:
            reporting_amount = converted if converted is not None else balance.amount
            total_reporting += reporting_amount
            row["reporting_amount"] = money(reporting_amount)
        by_account.append(row)

    caveats: list[str] = []
    if unconverted:
        caveats.append(
            f"Could not convert {', '.join(sorted(set(unconverted)))} into {reporting}; "
            "those balances are omitted from the reporting total and runway."
        )

    burn = average_monthly_burn
    burn_periods: list[str] = []
    if burn is None:
        if not monthly_outflows:
            return {
                "error": "Provide monthly_outflows or average_monthly_burn",
                "total_cash": money(total_reporting),
                "reporting_currency": reporting,
                "by_currency": {k: money(v) for k, v in sorted(by_currency.items())},
            }
        grouped: dict[str, float] = defaultdict(float)
        outflow_unconverted: list[str] = []
        for row in monthly_outflows:
            converted = _convert(row.amount, row.currency, reporting, fx_rates)
            if converted is None and row.currency.upper() != reporting:
                outflow_unconverted.append(row.currency.upper())
                continue
            grouped[row.period] += converted if converted is not None else row.amount
        if outflow_unconverted:
            caveats.append(
                f"Skipped outflows in {', '.join(sorted(set(outflow_unconverted)))} (no FX rate)."
            )
        periods = sorted(grouped)[-burn_lookback_months:]
        burn_periods = periods
        if not periods:
            return {"error": "No convertible monthly outflows to estimate burn"}
        burn = sum(grouped[p] for p in periods) / len(periods)
        if len(periods) < 2:
            caveats.append("Burn uses fewer than 2 months — runway is a rough cut.")
        if len(periods) >= 2:
            values = [grouped[p] for p in periods]
            median = statistics.median(values)
            if median > 0 and max(values) > 2 * median:
                caveats.append(
                    "One month in the burn window is more than 2× the median; "
                    "treat runway as sensitive to that spike."
                )

    if burn is None or burn <= 0:
        return {
            "total_cash": money(total_reporting),
            "reporting_currency": reporting,
            "by_currency": {k: money(v) for k, v in sorted(by_currency.items())},
            "by_account": by_account,
            "average_monthly_burn": money(burn or 0),
            "runway_months": None,
            "burn_periods": burn_periods,
            "caveats": caveats + ["Burn is zero or missing; runway is undefined."],
        }

    runway = total_reporting / burn
    concentration = None
    if total_reporting > 0:
        top = max(by_account, key=lambda r: r.get("reporting_amount") or 0)
        share = (top.get("reporting_amount") or 0) / total_reporting
        if share >= 0.7:
            concentration = {
                "account_name": top.get("account_name") or top.get("account_id"),
                "share": money(share * 100),
            }
            caveats.append(
                f"Liquidity is concentrated ({concentration['share']}%) in "
                f"{concentration['account_name']}."
            )

    return {
        "total_cash": money(total_reporting),
        "reporting_currency": reporting,
        "by_currency": {k: money(v) for k, v in sorted(by_currency.items())},
        "by_account": by_account,
        "average_monthly_burn": money(burn),
        "runway_months": money(runway),
        "burn_periods": burn_periods,
        "concentration": concentration,
        "caveats": caveats,
    }


def _period(day: str) -> str:
    parsed = date.fromisoformat(day)
    return parsed.strftime("%Y-%m")


def _zscores(values: list[float]) -> list[float]:
    if len(values) < 2:
        return [0.0] * len(values)
    mean = statistics.mean(values)
    stdev = statistics.pstdev(values)
    if stdev == 0:
        return [0.0] * len(values)
    return [(v - mean) / stdev for v in values]


def spend_anomalies(
    transactions: list[Transaction],
    baseline_transactions: list[Transaction] | None = None,
    spike_ratio: float = 1.5,
    large_tx_zscore: float = 2.0,
    card_outlier_ratio: float = 2.0,
    min_amount: float = 250.0,
    use_knowledge_vendors: bool = True,
    knowledge_dir=None,
) -> dict:
    baseline = baseline_transactions or []
    known, known_source = (
        load_known_vendors(knowledge_dir) if use_knowledge_vendors else (set(), None)
    )

    findings: list[Finding] = []
    current_amounts = [tx.amount for tx in transactions]
    zscores = _zscores(current_amounts)
    if len(transactions) >= 5:
        for tx, z in zip(transactions, zscores, strict=True):
            if z >= large_tx_zscore and tx.amount >= min_amount:
                findings.append(
                    Finding(
                        type="large_transaction",
                        severity="high" if z >= 3 else "medium",
                        title=f"Large transaction vs this window ({tx.vendor or 'unknown'})",
                        detail=f"z={money(z)} versus other transactions in the current window.",
                        amount=money(tx.amount),
                        currency=tx.currency,
                        vendor=tx.vendor,
                        transaction_id=tx.id,
                    )
                )

    baseline_vendors = {
        normalize_name(tx.vendor) for tx in baseline if tx.vendor
    }
    current_vendor_totals: dict[str, float] = defaultdict(float)
    current_vendor_label: dict[str, str] = {}
    for tx in transactions:
        if not tx.vendor:
            continue
        key = normalize_name(tx.vendor)
        current_vendor_totals[key] += tx.amount
        current_vendor_label[key] = tx.vendor

    for key, total in current_vendor_totals.items():
        if total < min_amount:
            continue
        if key not in baseline_vendors and key not in known:
            findings.append(
                Finding(
                    type="new_vendor",
                    severity="high" if total >= 5000 else "medium",
                    title=f"New vendor {current_vendor_label[key]}",
                    detail="Not in the baseline window or known-vendor list.",
                    amount=money(total),
                    vendor=current_vendor_label[key],
                )
            )

    baseline_by_vendor_month: dict[str, dict[str, float]] = defaultdict(
        lambda: defaultdict(float)
    )
    for tx in baseline:
        if not tx.vendor:
            continue
        baseline_by_vendor_month[normalize_name(tx.vendor)][_period(tx.date)] += tx.amount

    for key, total in current_vendor_totals.items():
        months = baseline_by_vendor_month.get(key) or {}
        if not months:
            continue
        avg = sum(months.values()) / len(months)
        if avg <= 0 or total < min_amount:
            continue
        if total >= spike_ratio * avg:
            findings.append(
                Finding(
                    type="vendor_spike",
                    severity="high" if total >= 2.5 * avg else "medium",
                    title=f"Vendor spike {current_vendor_label[key]}",
                    detail=(
                        f"This window {money(total)} vs baseline monthly average "
                        f"{money(avg)} ({len(months)} months)."
                    ),
                    amount=money(total),
                    vendor=current_vendor_label[key],
                )
            )

        if len(months) >= 2:
            mean = sum(months.values()) / len(months)
            if mean >= min_amount:
                delta_pct = (total - mean) / mean
                if abs(delta_pct) >= 0.3 and abs(total - mean) >= min_amount:
                    findings.append(
                        Finding(
                            type="recurring_change",
                            severity="medium",
                            title=f"Recurring change {current_vendor_label[key]}",
                            detail=(
                                f"Run-rate moved {money(delta_pct * 100)}% vs "
                                f"baseline average {money(mean)}."
                            ),
                            amount=money(total),
                            vendor=current_vendor_label[key],
                        )
                    )

    current_cards: dict[str, float] = defaultdict(float)
    for tx in transactions:
        if tx.card_holder:
            current_cards[normalize_name(tx.card_holder)] += tx.amount
    baseline_cards: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    labels: dict[str, str] = {}
    for tx in baseline:
        if tx.card_holder:
            labels[normalize_name(tx.card_holder)] = tx.card_holder
            baseline_cards[normalize_name(tx.card_holder)][_period(tx.date)] += tx.amount
    for tx in transactions:
        if tx.card_holder:
            labels[normalize_name(tx.card_holder)] = tx.card_holder

    for key, total in current_cards.items():
        months = baseline_cards.get(key) or {}
        if not months:
            continue
        avg = sum(months.values()) / len(months)
        if avg <= 0 or total < min_amount:
            continue
        if total >= card_outlier_ratio * avg:
            findings.append(
                Finding(
                    type="card_outlier",
                    severity="high" if total >= 3 * avg else "medium",
                    title=f"Card outlier {labels[key]}",
                    detail=(
                        f"This window {money(total)} vs their baseline monthly "
                        f"average {money(avg)}."
                    ),
                    amount=money(total),
                    card_holder=labels[key],
                )
            )

    severity_rank = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda f: (severity_rank[f.severity], -f.amount))
    return {
        "findings": [f.model_dump() for f in findings],
        "finding_count": len(findings),
        "known_vendors_source": known_source,
        "thresholds": {
            "spike_ratio": spike_ratio,
            "large_tx_zscore": large_tx_zscore,
            "card_outlier_ratio": card_outlier_ratio,
            "min_amount": min_amount,
        },
    }


def budget_variance(
    actuals: list[CategoryActual],
    budgets: list[BudgetLine] | None = None,
    period: str | None = None,
    currency: str | None = None,
    knowledge_dir=None,
    period_elapsed_ratio: float = 0.5,
) -> dict:
    source = "inline"
    budget_period = period
    budget_currency = currency
    lines = list(budgets or [])
    if not lines:
        loaded, file_currency, file_period, filename = load_budgets(knowledge_dir)
        lines = loaded
        source = filename or "none"
        budget_period = budget_period or file_period
        budget_currency = budget_currency or file_currency
    if not lines:
        return {"error": "No budgets provided and no budgets.yaml / example found"}

    actual_map: dict[str, float] = defaultdict(float)
    actual_label: dict[str, str] = {}
    for row in actuals:
        key = normalize_name(row.category)
        actual_map[key] += row.amount
        actual_label[key] = row.category

    used_keys: set[str] = set()
    categories: list[dict] = []
    for line in lines:
        key = normalize_name(line.name)
        used_keys.add(key)
        actual = actual_map.get(key, 0.0)
        variance = line.budget - actual
        pct_used = (actual / line.budget) if line.budget else None
        if line.budget <= 0:
            status = "over" if actual > 0 else "on_track"
        elif actual > line.budget:
            status = "over"
        elif pct_used is not None and pct_used >= 0.8:
            status = "at_risk"
        elif (
            pct_used is not None
            and pct_used < 0.5
            and period_elapsed_ratio >= 0.5
        ):
            status = "under"
        else:
            status = "on_track"
        categories.append(
            {
                "name": line.name,
                "owner": line.owner,
                "budget": money(line.budget),
                "actual": money(actual),
                "variance": money(variance),
                "pct_used": money(pct_used * 100) if pct_used is not None else None,
                "status": status,
            }
        )

    unmatched = [
        {"category": actual_label[k], "actual": money(v)}
        for k, v in actual_map.items()
        if k not in used_keys
    ]

    categories.sort(key=lambda c: (c["status"] != "over", c["status"] != "at_risk", -c["actual"]))
    return {
        "period": budget_period,
        "currency": budget_currency,
        "budget_source": source,
        "example_data": source.endswith("example.yaml") if source else False,
        "categories": categories,
        "unmatched_actuals": unmatched,
        "totals": {
            "budget": money(sum(c["budget"] for c in categories)),
            "actual": money(sum(c["actual"] for c in categories)),
            "variance": money(sum(c["variance"] for c in categories)),
        },
    }


def cfo_summary(
    cash_runway_result: dict | None = None,
    spend_by_category: list[CategoryActual] | None = None,
    anomalies_result: dict | None = None,
    budget_variance_result: dict | None = None,
    outstanding_items: list[str] | None = None,
    period: str | None = None,
) -> dict:
    headlines: list[str] = []
    needs_you: list[str] = list(outstanding_items or [])

    if cash_runway_result and "error" not in cash_runway_result:
        cash = cash_runway_result.get("total_cash")
        ccy = cash_runway_result.get("reporting_currency")
        months = cash_runway_result.get("runway_months")
        burn = cash_runway_result.get("average_monthly_burn")
        if cash is not None:
            line = f"Cash {ccy} {cash}"
            if months is not None:
                line += f"; runway {months} months on {ccy} {burn}/mo burn"
            headlines.append(line)
        for caveat in cash_runway_result.get("caveats") or []:
            needs_you.append(caveat)

    if spend_by_category:
        ranked = sorted(spend_by_category, key=lambda r: r.amount, reverse=True)
        total = money(sum(r.amount for r in ranked))
        top = ranked[0]
        headlines.append(
            f"Spend {total} this period; largest category {top.category} at {money(top.amount)}"
        )

    findings = (anomalies_result or {}).get("findings") or []
    if findings:
        headlines.append(f"{len(findings)} anomal{'y' if len(findings) == 1 else 'ies'} worth a look")
        for finding in findings[:3]:
            needs_you.append(f"{finding.get('title')}: {finding.get('detail')}")
    elif anomalies_result is not None:
        headlines.append("No spend anomalies above threshold")

    variance = budget_variance_result or {}
    if variance.get("example_data"):
        needs_you.append("Budget file is the example plan — replace knowledge/budgets.yaml.")
    overs = [c for c in variance.get("categories") or [] if c.get("status") == "over"]
    at_risk = [c for c in variance.get("categories") or [] if c.get("status") == "at_risk"]
    if overs:
        names = ", ".join(c["name"] for c in overs)
        headlines.append(f"Over budget: {names}")
        needs_you.extend(f"{c['name']} is over budget ({c['actual']} / {c['budget']})" for c in overs)
    if at_risk:
        headlines.append("At risk (≥80% of budget): " + ", ".join(c["name"] for c in at_risk))

    if not headlines:
        headlines.append("Not enough computed inputs to write a CFO summary.")

    return {
        "period": period or variance.get("period"),
        "headlines": headlines,
        "needs_you": needs_you,
        "inputs_used": {
            "cash_runway": cash_runway_result is not None,
            "spend_by_category": bool(spend_by_category),
            "anomalies": anomalies_result is not None,
            "budget_variance": budget_variance_result is not None,
            "outstanding_items": bool(outstanding_items),
        },
    }
