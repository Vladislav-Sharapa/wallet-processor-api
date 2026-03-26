import pytest

from app.src.schemas.user_schemas import UserModel


@pytest.fixture
def auth_user_model():
    return UserModel(id=-5, email="test", role="test")
