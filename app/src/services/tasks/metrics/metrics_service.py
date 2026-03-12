from datetime import date
from typing import List, Tuple

from sqlalchemy import and_, func, select

from app.src.core.models import BaseModel
from app.src.models.transaction import Transaction
from app.src.models.user import User
from app.src.schemas.transaction_schemas import (
    TransactionStatusEnum,
    WeekTransactionAnalyticsModel,
)
from sqlalchemy.ext.asyncio import AsyncSession


class MetricsService:
    def __init__(self, session: AsyncSession):
        """
        Provider for retrieving metrics from the database.
        """
        self.__session = session
        self.limit = 200
        self.offset = 0

    def __get_query(self, model: BaseModel, offset: int = 0):
        query = (
            select(model)
            .where(
                and_(
                    func.date(model.created) >= self.__date_start,
                    func.date(model.created) <= self.__date_end,
                )
            )
            .order_by(model.id)
            .limit(self.limit)
            .offset(offset)
        )
        return query

    async def __get_data(self) -> Tuple[List[User], List[Transaction]]:
        current_offset = 0
        user_query = self.__get_query(User)
        query_result = await self.__session.execute(user_query)
        users_list = query_result.scalars().all()

        transactions_list = []
        while True:
            transaction_query = self.__get_query(Transaction, offset=current_offset)
            query_result = await self.__session.execute(transaction_query)
            transactions = query_result.scalars().all()

            if not transactions:
                break
            transactions_list.extend(transactions)
            current_offset += self.limit

        return users_list, transactions_list

    async def calculate_metrics(
        self, date_start: date, date_end: date
    ) -> WeekTransactionAnalyticsModel:
        self.__date_end = date_end
        self.__date_start = date_start

        users, transactions = await self.__get_data()

        registered_user_count = len(users)
        registered_and_deposit_users_count = set()
        not_rollbacked_deposit_sum = 0
        not_rollbacked_withdraw_sum = 0
        not_rollback_transaction = 0
        transactions_count = len(transactions)

        for transaction in transactions:
            if transaction.status != TransactionStatusEnum.roll_backed:
                not_rollback_transaction += 1
                if transaction.amount > 0:
                    not_rollbacked_deposit_sum += transaction.amount
                elif transaction.amount < 0:
                    not_rollbacked_withdraw_sum += abs(transaction.amount)

            if transaction.amount > 0:
                registered_and_deposit_users_count.add(transaction.user_id)

        return WeekTransactionAnalyticsModel(
            registered_user_count=registered_user_count,
            registered_and_deposit_users_count=len(registered_and_deposit_users_count),
            not_rollbacked_deposit_sum=not_rollbacked_deposit_sum,
            not_rollbacked_withdraw_sum=not_rollbacked_withdraw_sum,
            transactions_count=transactions_count,
            not_rollbacked_transactions=not_rollback_transaction,
        )
