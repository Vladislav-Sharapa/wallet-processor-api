from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.core.database import get_async_session
from app.src.services.flows.transaction_flows import (
    CreateTransactionUseCase,
    TransactionRollBackUseCase,
)
from app.src.services.transaction import TransactionService


def get_transaction_service(
    session: AsyncSession = Depends(get_async_session),
) -> TransactionService:
    return TransactionService(session=session)


def get_transaction_create_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> CreateTransactionUseCase:
    return CreateTransactionUseCase(session=session)


def get_transaction_roll_back_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> TransactionRollBackUseCase:
    return TransactionRollBackUseCase(session=session)
