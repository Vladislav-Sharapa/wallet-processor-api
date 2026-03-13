from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.src.exceptions.transaction_exceptions import TransactionNotExistsException
from app.src.models.transaction import Transaction
from app.src.repositories.transaction import TransactionRepository
from app.src.schemas.transaction_schemas import (
    RequestTransactionModel,
    TransactionModel,
    TransactionStatusEnum,
)


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.__transaction_repository = TransactionRepository(session=self.session)

    async def get_one(self, transaction_id: int) -> Transaction:
        transaction = await self.__transaction_repository.get(transaction_id)

        if not transaction:
            raise TransactionNotExistsException
        return transaction

    async def get_all(self, user_id: int | None) -> List[TransactionModel]:
        if user_id:
            transactions = await self.__transaction_repository.get_all_by_user_id(
                user_id=user_id
            )
        else:
            transactions = await self.__transaction_repository.get_all()
        return [
            TransactionModel.model_validate(transaction) for transaction in transactions
        ]

    async def create_transaction(
        self, user_id: int, obj: RequestTransactionModel
    ) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            currency=obj.currency,
            amount=obj.amount,
            status=TransactionStatusEnum.processed,
        )
        transaction = await self.__transaction_repository.create(transaction)
        return transaction

    async def set_transaction_rollback(self, transaction: Transaction) -> Transaction:
        transaction = await self.__transaction_repository.update(
            transaction, status=TransactionStatusEnum.roll_backed
        )
        return transaction
