from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator

from app.src.core.enums import CurrencyEnum


class TransactionStatusEnum(StrEnum):
    processed = "PROCESSED"
    roll_backed = "ROLLBACKED"


class RequestTransactionModel(BaseModel):
    currency: CurrencyEnum
    amount: Decimal

    @field_validator("amount")
    def validate_amount(cls, v):
        if v == 0:
            raise ValueError("Transaction can not have zero amount")
        return v


class ResponseTransactionModel(BaseModel):
    pass


class TransactionModel(BaseModel):
    id: Optional[int]
    user_id: Optional[int] = None
    currency: Optional[CurrencyEnum] = None
    amount: Optional[float] = None
    status: Optional[TransactionStatusEnum] = None
    created: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WeekTransactionAnalyticsModel(BaseModel):
    registered_user_count: Optional[int] = None
    registered_and_deposit_users_count: Optional[int] = None
    not_rollbacked_deposit_sum: Optional[int] = None
    not_rollbacked_withdraw_sum: Optional[int] = None
    transactions_count: Optional[int] = None
    not_rollbacked_transactions: Optional[int] = None
