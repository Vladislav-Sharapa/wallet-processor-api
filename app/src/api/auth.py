from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from fastapi import APIRouter, Depends
from app.src.schemas.auth import RequestUserLoginInfoModel, TokenInfo
from app.src.services.auth_service import AuthService
from app.src.schemas.user_schemas import RequestUserModel, ResponseUserModel
from app.src.api.depedencies.auth import (
    get_auth_service,
    get_auth_token,
)

router = APIRouter(
    tags=[
        "auth",
    ]
)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenInfo:
    user_data = RequestUserLoginInfoModel(
        username=form_data.username, password=form_data.password
    )
    token_info = await auth_service.login(user_data)

    return token_info


@router.post("/refresh", response_model_exclude_none=True)
async def refresh_access_token(
    token: str = Depends(get_auth_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenInfo:
    access_token = await auth_service.refresh(token)

    return access_token


@router.post("/register")
async def register(
    user: RequestUserModel, auth_service: AuthService = Depends(get_auth_service)
) -> ResponseUserModel:
    response = await auth_service.register(user)

    return response
