import asyncio
import random
from typing import List
from unittest.mock import AsyncMock, MagicMock, Mock

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import pytest
import pytest_asyncio

from app.src.core.models import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.core.config import config
from app.src.repositories.user import UserRepository
from app.src.schemas.user_schemas import RequestUserModel, UserStatusEnum


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        url=config.database_test.url,
        echo=False,
    )

    async with engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.drop_all)
        await connection.run_sync(BaseModel.metadata.create_all)

    yield engine


@pytest_asyncio.fixture(scope="function")
async def async_session_maker(engine):
    return async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session(async_session_maker):
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = Mock()
    session.add_all = Mock()
    session.refresh = AsyncMock()

    return session


@pytest.fixture
def mock_execute(mock_session):
    """Helper for setting execute.scalar in tests"""

    def _setup_scalar(return_value):
        mock_scalar = MagicMock(return_value=return_value)
        mock_result = AsyncMock()
        mock_result.scalar = mock_scalar
        mock_session.execute.return_value = mock_result

    return _setup_scalar


@pytest.fixture
def user_models():
    return [
        RequestUserModel(
            email="test@test1.com",
            first_name="test",
            last_name="test",
            password="123Test123!",
        ),
        RequestUserModel(
            email="test@test2.com",
            first_name="test",
            last_name="test",
            password="123Test123!",
        ),
        RequestUserModel(
            email="test@test3.com",
            first_name="test",
            last_name="test",
            password="123Test123!",
        ),
    ]


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession, user_models: List[RequestUserModel]):
    repository = UserRepository(db_session)
    result_list = []

    for user_model in user_models:
        user = await repository.get_by_email(user_model.email)

        if not user:
            user = await repository.create_user(user_model)
        if user.status == UserStatusEnum.BLOCKED:
            user = await repository.update_status(user, UserStatusEnum.ACTIVE)

        result_list.append(user)

    return random.choice(result_list)
