from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Balance(BaseModel):
    amount: float = Field(description="Asset balance, always >= 0")
    currency: str
    account_id: str | None = None
    account_name: str | None = None


class PeriodAmount(BaseModel):
    period: str = Field(description="YYYY-MM")
    amount: float = Field(description="Money-out for that month, >= 0")
    currency: str = "USD"


class Transaction(BaseModel):
    id: str | None = None
    date: str = Field(description="ISO date YYYY-MM-DD")
    amount: float = Field(description="Money-out, >= 0")
    currency: str = "USD"
    vendor: str | None = None
    category: str | None = None
    card_holder: str | None = None
    description: str | None = None


class CategoryActual(BaseModel):
    category: str
    amount: float
    period: str | None = None
    currency: str | None = None


class BudgetLine(BaseModel):
    name: str
    budget: float
    owner: str | None = None


class Finding(BaseModel):
    type: Literal[
        "large_transaction",
        "new_vendor",
        "vendor_spike",
        "card_outlier",
        "recurring_change",
    ]
    severity: Literal["low", "medium", "high"]
    title: str
    detail: str
    amount: float
    currency: str = "USD"
    vendor: str | None = None
    card_holder: str | None = None
    transaction_id: str | None = None
