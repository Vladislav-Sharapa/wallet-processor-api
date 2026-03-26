from fastapi import HTTPException
import pytest

from app.src.schemas.auth import AccessTokenPayload, RefreshTokenPayload
from app.src.schemas.user_schemas import UserModel
from app.src.utils.auth_security import get_password_hash, verify_password
from app.src.utils.jwt import (
    JWTHandler,
    get_current_token_payload,
    get_access_token_payload,
)


class TestAuth:
    @pytest.mark.parametrize(
        "registration_password, plain_password, is_valid",
        [("Test", "Test", True), ("Test", "Test_1", False)],
    )
    def test_verify_password(
        self, registration_password: str, plain_password: str, is_valid: bool
    ):
        hashed_password = get_password_hash(registration_password)

        assert verify_password(plain_password, hashed_password) == is_valid

    @pytest.mark.asyncio
    async def test_create_access_token(self, auth_user_model: UserModel):
        token = await JWTHandler.create_access_token(auth_user_model)
        payload = get_current_token_payload(token)
        payload = AccessTokenPayload.model_validate(payload)

        assert payload.user_id == auth_user_model.id
        assert payload.email == auth_user_model.email
        assert payload.role == auth_user_model.role

    @pytest.mark.asyncio
    async def test_create_refresh_token(self, auth_user_model):
        token = await JWTHandler.create_refresh_token(auth_user_model)
        payload = get_current_token_payload(token)
        payload = RefreshTokenPayload.model_validate(payload)

        assert payload.user_id == auth_user_model.id
        assert payload.sub == auth_user_model.email

    @pytest.mark.asyncio
    async def test_verify_correct_token_type(self, auth_user_model):
        access_token = await JWTHandler.create_access_token(auth_user_model)

        payload = get_access_token_payload(access_token)

        assert isinstance(payload, dict)
        assert payload["user_id"] == auth_user_model.id
        assert payload["email"] == auth_user_model.email

    @pytest.mark.asyncio
    async def test_verify_incorrect_token_type(self, auth_user_model):
        refresh_token = await JWTHandler.create_refresh_token(auth_user_model)

        with pytest.raises(HTTPException):
            get_access_token_payload(refresh_token)
