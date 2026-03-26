from typing import List
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.models.user import User
from app.src.repositories.user import UserRepository
from app.src.schemas.auth import RoleEnum
from app.src.schemas.user_schemas import RequestUserModel, UserFilter, UserStatusEnum
from app.src.utils.auth_security import verify_password


class TestUserRepositoryWithMock:
    @pytest.mark.asyncio
    async def test_create_user(
        self, request_user: RequestUserModel, mock_session: AsyncMock, mock_execute
    ):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = request_user.email
        mock_user.first_name = request_user.first_name
        mock_user.last_name = request_user.last_name
        mock_user.status = UserStatusEnum.ACTIVE
        mock_user.role = RoleEnum.USER
        mock_user.user_balance = []
        mock_execute(mock_user)

        repository = UserRepository(mock_session)
        result = await repository.create_user(request_user)

        assert result.id == 1
        assert result.email == request_user.email
        mock_session.add.assert_called_once()
        mock_session.add_all.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.execute.assert_called_once()


class TestUserReporistory:
    @pytest.mark.asyncio
    async def test_repository_create_user(
        self, db_session: AsyncSession, request_user: RequestUserModel
    ):
        repository = UserRepository(db_session)

        user: User = await repository.create_user(request_user)

        assert user.email == request_user.email
        assert user.first_name == request_user.first_name
        assert user.last_name == request_user.last_name

    @pytest.mark.asyncio
    async def test_repository_get_by_email(
        self, db_session: AsyncSession, test_user: User
    ):
        repository = UserRepository(db_session)

        user: User = await repository.get_by_email(test_user.email)

        assert user.email == test_user.email
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_repository_get_by_id(self, db_session, test_user: User):
        repository = UserRepository(db_session)

        user: User = await repository.get(test_user.id)

        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_repository_get_user_with_balance_by_id(
        self, db_session, test_user: User
    ):
        repository = UserRepository(db_session)
        filters = UserFilter(id=test_user.id)

        users = await repository.get_users_with_balancies(filters)
        user = users[0]
        assert len(users) == 1
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_repository_get_user_with_balance_by_status(
        self, db_session, test_user: User
    ):
        repository = UserRepository(db_session)
        filters = UserFilter(status=UserStatusEnum.ACTIVE)

        users = await repository.get_users_with_balancies(filters)

        for user in users:
            assert user.status == UserStatusEnum.ACTIVE

    @pytest.mark.asyncio
    async def test_repository_update_status(self, db_session, test_user: User):
        repository = UserRepository(db_session)
        new_status = UserStatusEnum.BLOCKED

        user: User = await repository.get(test_user.id)
        user = await repository.update_status(user, new_status)

        assert user.id == test_user.id
        assert user.status == UserStatusEnum.BLOCKED

    @pytest.mark.asyncio
    async def test_repository_get_all_users(self, db_session):
        repository = UserRepository(db_session)

        users: List[User] = await repository.get_all()

        assert len(users) > 0
        for user in users:
            assert isinstance(user, User)

    @pytest.mark.asyncio
    async def test_repository_update_password(self, db_session, test_user: User):
        repository = UserRepository(db_session)
        new_password = "new_user_password"

        await repository.update_password(test_user.id, new_password)
        await repository.commit()
        user: User = await repository.get(test_user.id)

        assert user.id == test_user.id
        assert verify_password(new_password, user.password_hash)

    @pytest.mark.asyncio
    async def test_repository_update_role(self, db_session, test_user: User):
        repository = UserRepository(db_session)
        role = RoleEnum.ADMIN

        await repository.update_role(test_user, role)
        await repository.commit()
        user: User = await repository.get(test_user.id)

        assert user.id == test_user.id
        assert user.role == role
