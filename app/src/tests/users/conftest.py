import pytest
from app.src.repositories.user import UserRepository
from app.src.schemas.user_schemas import RequestUserModel


@pytest.fixture
def mock_user_repository(mock_session):
    return UserRepository(session=mock_session)


@pytest.fixture
def request_user():
    return RequestUserModel(
        email="test@test0.com",
        first_name="test",
        last_name="test",
        password="123Test123!",
    )
