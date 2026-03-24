from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.core.models import BaseModel


class SQLAlchemyRepository:
    model: BaseModel = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[BaseModel] | None:
        query = select(self.model)
        res = await self.session.execute(query)

        return list(res.scalars().all())

    async def get(self, id):
        return await self.session.get(self.model, id)

    async def update(self, model: BaseModel, **kwargs) -> BaseModel:
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        try:
            await self.session.flush()
        except SQLAlchemyError:
            self.session.rollback()
        return model

    async def create(self, obj: BaseModel) -> BaseModel:
        model = obj
        self.session.add(model)
        await self.session.flush()

        return model

    async def commit(self) -> None:
        await self.session.commit()
