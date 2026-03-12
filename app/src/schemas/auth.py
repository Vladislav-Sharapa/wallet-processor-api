from enum import StrEnum
import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class PasswordValidationMixin:
    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?`~" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class TokenTypeEnum(StrEnum):
    ACCESS_TOKEN_TYPE = "access"
    REFRESH_TOKEN_TYPE = "refresh"
    RESET_TOKEN_TYPE = "reset"


class RoleEnum(StrEnum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class TokenData(BaseModel):
    user_uuid: int


class AccessTokenPayload(BaseModel):
    sub: Optional[str] = None
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenPayload(BaseModel):
    sub: Optional[str] = None
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class RequestUserLoginInfoModel(BaseModel):
    username: str
    password: str


class RequestDataForResetPassword(BaseModel, PasswordValidationMixin):
    email: EmailStr
    password: str
    code: int

    @field_validator("code")
    def validate_code(cls, value):
        if not re.match(r"^\d{6}$", value):
            raise ValueError("Code must be exactly 6 digits (0-9)")
        return value


class RequestEmailForNotification(BaseModel):
    email: EmailStr


class ResetPasswordTokenPayload(BaseModel):
    email: str
