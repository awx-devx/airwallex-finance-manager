from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from finance_manager.models import BudgetLine


def default_knowledge_dir() -> Path | None:
    raw = os.environ.get("FINANCE_MANAGER_KNOWLEDGE_DIR")
    if raw:
        return Path(raw).expanduser()
    return None


def _read_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def resolve_knowledge_file(knowledge_dir: Path | None, *names: str) -> Path | None:
    if knowledge_dir is None or not knowledge_dir.is_dir():
        return None
    for name in names:
        candidate = knowledge_dir / name
        if candidate.is_file():
            return candidate
    return None


def load_budgets(
    knowledge_dir: Path | None = None,
) -> tuple[list[BudgetLine], str | None, str | None, str | None]:
    """Return (lines, currency, period, source_filename)."""
    path = resolve_knowledge_file(
        knowledge_dir, "budgets.yaml", "budgets.example.yaml"
    )
    if path is None:
        return [], None, None, None
    data = _read_yaml(path)
    lines = [
        BudgetLine(
            name=str(row["name"]),
            budget=float(row["budget"]),
            owner=row.get("owner"),
        )
        for row in data.get("categories") or []
        if row.get("name") is not None and row.get("budget") is not None
    ]
    return lines, data.get("currency"), data.get("period"), path.name


def load_known_vendors(knowledge_dir: Path | None = None) -> tuple[set[str], str | None]:
    path = resolve_knowledge_file(
        knowledge_dir, "vendors.yaml", "vendors.example.yaml"
    )
    if path is None:
        return set(), None
    data = _read_yaml(path)
    known = {normalize_name(v) for v in data.get("known") or [] if v}
    return known, path.name


def normalize_name(value: str) -> str:
    return " ".join(value.strip().split()).casefold()
