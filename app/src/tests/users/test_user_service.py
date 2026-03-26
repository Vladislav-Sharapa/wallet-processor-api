import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.core.exceptions import BadRequestDataException
from app.src.exceptions.user_exceptions import (
    UserAlreadyBlockedException,
    UserAlreadyExistsException,
)
from app.src.models.user import User
from app.src.repositories.user import UserRepository
from app.src.schemas.user_schemas import RequestUserModel, UserStatusEnum
from app.src.services.user import UserService


class TestUserService:
    @pytest.mark.asyncio
    async def test_service_create_user(
        self, db_session: AsyncSession, request_user: RequestUserModel
    ):
        request_user.email = "test@test.test"
        service = UserService(db_session)

        user: User = await service.create_user(request_user)

        assert user.email == request_user.email
        assert user.first_name == request_user.first_name
        assert user.last_name == request_user.last_name

    @pytest.mark.asyncio
    async def test_service_create_user_with_exitst_email(
        self, db_session: AsyncSession, request_user: RequestUserModel
    ):
        request_user.email = "test@test1.test"
        service = UserService(db_session)

        await service.create_user(request_user)

        with pytest.raises(UserAlreadyExistsException):
            await service.create_user(request_user)

    @pytest.mark.asyncio
    async def test_service_create_user_with_no_email(
        self, db_session: AsyncSession, request_user: RequestUserModel
    ):
        request_user.email = None
        service = UserService(db_session)

        with pytest.raises(BadRequestDataException):
            await service.create_user(request_user)

    @pytest.mark.asyncio
    async def test_service_get_blocked_user(
        self, db_session: AsyncSession, test_user: User
    ):
        service = UserService(db_session)
        repository = UserRepository(db_session)

        await repository.update_status(test_user, UserStatusEnum.BLOCKED)
        await repository.commit()

        with pytest.raises(UserAlreadyBlockedException):
            await service.get_active_user(test_user.id)
