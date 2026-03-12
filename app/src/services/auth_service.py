from app.src.core.config import config
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.core.redis import RedisClient
from app.src.exceptions.auth_exceptions import InvalidUserPasswordException

from app.src.schemas.auth import RequestUserLoginInfoModel, TokenInfo
from app.src.utils.auth_security import verify_password
from app.src.models.user import User
from app.src.schemas.user_schemas import RequestUserModel, ResponseUserModel, UserModel
from app.src.services.user import UserService
from app.src.utils.jwt import JWTHandler, get_refresh_token_payload
from app.src.utils.token_handlers import get_current_auth_user


class AuthService:
    def __init__(self, session: AsyncSession, redis: RedisClient):
        self.user_sevice: UserService = UserService(session)
        self.__redis_client = redis

    async def register(self, request_user: RequestUserModel) -> ResponseUserModel:
        user = await self.user_sevice.create_user(request_user)

        token_info = await self.__generate_tokens(user)

        response = ResponseUserModel.model_validate(user)
        response.token_info = token_info

        return response

    async def login(self, request: RequestUserLoginInfoModel) -> TokenInfo:
        key = await self.__check_login_attempts(request.username)
        user = await self.__authenticate(request.username, request.password, key)

        token_info = await self.__generate_tokens(user)

        await self.__reset_attempts(key)

        return token_info

    async def refresh(self, token: str) -> TokenInfo:
        token_payload = get_refresh_token_payload(token)
        user = await get_current_auth_user(token_payload, self.user_sevice)

        access_token = JWTHandler.create_access_token(user)

        return TokenInfo(access_token=access_token)

    async def __generate_tokens(self, user: UserModel) -> TokenInfo:
        """
        Generate access and refresh tokens
        """
        access_token = await JWTHandler.create_access_token(user)
        refresh_token = await JWTHandler.create_refresh_token(user)

        return TokenInfo(
            access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
        )

    async def __authenticate(self, email: str, password: str, key: str) -> UserModel:
        """
        Authenticate a user by verifying their email and password.

        Workflow:
            1. Retrieve the active user record from the database using the provided email.
            2. Compare the given plain-text password with the stored password hash.
            3. If the password does not match, raise InvalidUserPasswordException.
            4. If the password is valid, return a validated UserModel instance.
        Args:
            email (str): The user's email address used for login.
            password (str): The plain-text password provided by the user.
        Returns:
            UserModel: A validated user model containing the authenticated user's data.
        Raises:
            InvalidUserPasswordException: If the provided password does not match the stored hash.
            UserNotExistsException: If no user with the given email exists.
            UserAlreadyBlockedException: If the user account is blocked.
        """
        user: User = await self.user_sevice.get_active_user_by_email(email=email)
        if not verify_password(password, user.password_hash):
            await self.__track_attempts(key)
            raise InvalidUserPasswordException
        return UserModel.model_validate(user)

    async def __check_login_attempts(self, username: str) -> str:
        """Method that checks login attempts for a given user email."""

        key = f"login_attempts:{username}"

        async with self.__redis_client as storage:
            attempts = await storage.get(key)

        if attempts and int(attempts) >= config.auth.MAX_LOGIN_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed login attempts. Try again later.",
            )
        return key

    async def __track_attempts(self, key: str) -> None:
        """
        Track and update the number of attempts.

        This method is called after
        unsuccessful user authentication
        """
        async with self.__redis_client as storage:
            attempts = await storage.get(key)

            if not attempts:
                await storage.set(key, 1)
            else:
                await storage.set(key, attempts + 1)

    async def __reset_attempts(self, key: str):
        """
        Reset the attempt counter for the given key in Redis.

        This method is typically called after a successful user authentication
        to clear any previously recorded failed login attempts.
        """
        async with self.__redis_client as storage:
            await storage.delete(key)
