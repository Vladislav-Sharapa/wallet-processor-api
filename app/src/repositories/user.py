from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, selectinload

from app.src.core.enums import CurrencyEnum
from app.src.core.repository import SQLAlchemyRepository
from app.src.models.user import User, UserBalance
from app.src.schemas.user_schemas import RequestUserModel, UserFilter, UserStatusEnum
from app.src.utils.auth_security import get_password_hash


class UserRepository(SQLAlchemyRepository):
    model: User = User

    async def get_users_with_balancies(
        self, filters: Optional[UserFilter]
    ) -> List[User]:
        query = select(User).options(selectinload(User.user_balance))

        for field, value in filters.model_dump(exclude_none=True).items():
            query = query.filter(getattr(self.model, field) == value)
        result = await self.session.execute(query)

        return result.scalars().all()

    async def update_password(self, model_id: int, password: str) -> None:
        password_hash = get_password_hash(password)
        query = (
            update(User).where(User.id == model_id).values(password_hash=password_hash)
        )

        await self.session.execute(query)

    async def create_user(self, model: RequestUserModel) -> User:
        user = User(
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            status=UserStatusEnum.ACTIVE,
        )

        user.password_hash = get_password_hash(model.password)

        self.session.add(user)
        balances = [
            UserBalance(
                owner=user,
                currency=str(currency),
                amount=0,
                created=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            for currency in CurrencyEnum
        ]

        self.session.add_all(balances)

        await self.session.commit()
        query = (
            select(User)
            .options(joinedload(User.user_balance))
            .where(User.id == user.id)
        )
        query_result = await self.session.execute(query)
        return query_result.scalar()

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_status(self, user: User, status: str) -> User:
        db_user = user
        if db_user not in self.session:
            db_user: User = await self.get(user.id)
        db_user.status = status
        return db_user

    async def update_role(self, user: User, role: str) -> User:
        db_user = user
        if db_user not in self.session:
            db_user: User = await self.get(user.id)
        db_user.role = role
        return db_user


class UserBalanceRepository(SQLAlchemyRepository):
    model: UserBalance = UserBalance

    async def get_user_balance_by_currency(
        self, user_id: int, currency: str
    ) -> UserBalance | None:
        query = select(UserBalance).filter(
            UserBalance.user_id == user_id, UserBalance.currency == currency
        )
        query_result = await self.session.execute(query)
        return query_result.scalar_one_or_none()

    async def update_balance(
        self, user_balance: UserBalance, amount: Decimal
    ) -> UserBalance:
        balance = user_balance
        query = (
            update(UserBalance)
            .where(UserBalance.id == balance.id)
            .values(amount=amount)
        )

        await self.session.execute(query)
        await self.session.flush(balance)

        return balance
