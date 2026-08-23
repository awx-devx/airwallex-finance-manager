from pathlib import Path

from finance_manager.knowledge import load_budgets, load_known_vendors, normalize_name

KNOWLEDGE = Path(__file__).resolve().parents[3] / "knowledge"


def test_normalize_name():
    assert normalize_name("  Amazon  Web ") == "amazon web"


def test_load_example_budgets():
    lines, currency, period, source = load_budgets(KNOWLEDGE)
    assert source == "budgets.example.yaml"
    assert currency == "USD"
    assert period == "2026-08"
    assert any(line.name == "Cloud" and line.budget == 12000 for line in lines)


def test_load_example_vendors():
    known, source = load_known_vendors(KNOWLEDGE)
    assert source == "vendors.example.yaml"
    assert "aws" in known
