from datetime import timedelta, datetime, timezone

from typing import Any, Dict, Optional
import uuid
from fastapi import HTTPException, status
import jwt

from app.src.core.config import config
from app.src.schemas.auth import (
    AccessTokenPayload,
    RefreshTokenPayload,
    ResetPasswordTokenPayload,
    TokenTypeEnum,
)
from app.src.schemas.user_schemas import UserModel


def encode_token(
    data: dict, expire_minutes: int, expire_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

    to_encode.update(exp=expire, jti=str(uuid.uuid4()))

    encoded_jwt = jwt.encode(
        to_encode, config.auth.SECRET, algorithm=config.auth.ALGORITH
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode JWT token
    """
    payload: dict = jwt.decode(token, config.auth.SECRET, config.auth.ALGORITH)
    return payload


def get_current_token_payload(token: str):
    """
    Extract and validate the payload from the current JWT token
    """
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            detail="Signature has expired", status_code=status.HTTP_400_BAD_REQUEST
        )
    return payload


class JWTHandler:
    @staticmethod
    async def __create_token(
        token_type: str,
        token_data: dict,
        expire_minutes: int = config.auth.ACCESS_TOKEN_EXPIRE_MINUTES,
        expire_timedelta: timedelta | None = None,
    ) -> str:
        jwt_payload = {"type": token_type}
        jwt_payload.update(token_data)
        return encode_token(
            data=jwt_payload,
            expire_minutes=expire_minutes,
            expire_delta=expire_timedelta,
        )

    @staticmethod
    async def create_access_token(user: UserModel) -> str:
        jwt_payload = AccessTokenPayload(
            sub=user.email, email=user.email, user_id=user.id, role=user.role
        )
        token = await JWTHandler.__create_token(
            token_type=TokenTypeEnum.ACCESS_TOKEN_TYPE,
            token_data=jwt_payload.model_dump(),
            expire_minutes=config.auth.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        return token

    @staticmethod
    async def create_refresh_token(user: UserModel) -> str:
        jwt_payload = RefreshTokenPayload(sub=user.email, user_id=user.id)
        token = await JWTHandler.__create_token(
            token_type=TokenTypeEnum.REFRESH_TOKEN_TYPE,
            token_data=jwt_payload.model_dump(),
            expire_timedelta=timedelta(days=config.auth.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        return token

    @staticmethod
    async def create_reset_token(user: UserModel) -> str:
        jwt_payload = ResetPasswordTokenPayload(email=user.email)
        token = await JWTHandler.__create_token(
            token_type=TokenTypeEnum.RESET_TOKEN_TYPE,
            token_data=jwt_payload.model_dump(),
            expire_minutes=config.auth.RESET_TOKEN_EXPIRE_MINUTES,
        )

        return token


class TokenTypeValidator:
    """
    Allows to get payload from a token depending on valid type.
    """

    def __init__(self, token_type: str):
        self.token_type = token_type

    def __call__(
        self,
        token: str,
    ) -> dict:
        payload = get_current_token_payload(token)
        self.__validate_token_type(payload, self.token_type)

        return payload

    def __validate_token_type(self, payload: dict, token_type: str) -> None:
        current_token_type = payload.get("type")
        if current_token_type == token_type:
            return
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token type {current_token_type!r} expected {token_type!r}",
        )


get_access_token_payload = TokenTypeValidator(TokenTypeEnum.ACCESS_TOKEN_TYPE)
get_refresh_token_payload = TokenTypeValidator(TokenTypeEnum.REFRESH_TOKEN_TYPE)
get_reset_token_payload = TokenTypeValidator(TokenTypeEnum.RESET_TOKEN_TYPE)
