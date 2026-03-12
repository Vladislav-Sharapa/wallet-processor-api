from typing import Annotated
from fastapi import Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer
from app.src.api.depedencies.user_dependencies import get_user_service
from app.src.core.redis import RedisClient, get_redis_client
from fastapi import status
from app.src.services.user import UserService
from app.src.utils.jwt import get_access_token_payload
from app.src.services.auth_service import AuthService
from app.src.core.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.utils.token_handlers import get_current_auth_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
    redis_client: RedisClient = Depends(get_redis_client),
) -> AuthService:
    return AuthService(session=session, redis=redis_client)


def get_auth_token(token: Annotated[str, Depends(oauth2_scheme)]):
    return token


async def check_user_ownership(
    user_id: int = Path(ge=0),
    token: str = Depends(get_auth_token),
    user_service: UserService = Depends(get_user_service),
) -> None:
    """Dependency that checks whether the current auth user is the owner of the requested record"""
    token_payload = get_access_token_payload(token)
    current_user = await get_current_auth_user(
        payload=token_payload, user_service=user_service
    )

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own resources",
        )
