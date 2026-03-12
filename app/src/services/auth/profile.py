import secrets
import string
from fastapi.responses import JSONResponse
from fastapi import status, BackgroundTasks
from app.src.core.redis import RedisClient
from app.src.exceptions.profile import (
    DuplicatePasswordException,
    InvalidResetCodeException,
    NoResetPasswordCode,
)
from app.src.schemas.auth import (
    RequestDataForResetPassword,
    RequestEmailForNotification,
)
from app.src.services.notification import NotificationService
from app.src.services.user import UserService
from app.src.utils.auth_security import verify_password


class RequestResetPasswordService:
    def __init__(
        self,
        user_service: UserService,
        notivication_service: NotificationService,
        redis: RedisClient,
    ):
        self.__user_service = user_service
        self.__redis = redis
        self.__notivicetion_service = notivication_service

    async def request_reset_password(
        self, request: RequestEmailForNotification, background_task: BackgroundTasks
    ) -> JSONResponse:
        """
        Request a password reset for a user.

        This method initiates the password reset process by generating a reset code
        and sending it to the user's email address via a background task.
        """
        key = self.__get_reset_key(request.email)

        try:
            _ = await self.__user_service.get_active_user_by_email(request.email)

            code = self.__generate_code()

            async with self.__redis as storage:
                await storage.set(key, code)

            background_task.add_task(
                self.__notivicetion_service.send,
                recepient=request,
                subject="Reset Password",
                template_body={"reset_code": code},
                template_name="email_template.html",
            )
        except Exception as e:
            print(e)
        finally:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "If your email is registered, you will receive password reset instructions"
                },
            )

    async def reset_password(
        self, request: RequestDataForResetPassword
    ) -> JSONResponse:
        """
        Reset a user's password using a verification code.

        This method completes the password reset process by validating and updating
        the user's password in the database.
        """
        key = self.__get_reset_key(request.email)

        async with self.__redis as storage:
            code = await storage.get(key)

        if not code:
            raise NoResetPasswordCode
        elif code != request.code:
            raise InvalidResetCodeException

        user = await self.__user_service.get_active_user_by_email(request.email)

        if verify_password(request.password, user.password_hash):
            raise DuplicatePasswordException

        await self.__user_service.update_password(user.id, request.password)

        async with self.__redis as storage:
            await storage.delete(key)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": f"Password changed successfully for {request.email}"},
        )

    def __get_reset_key(self, email: str) -> str:
        return f"{email}-reset-code"

    def __generate_code(self) -> str:
        return "".join(secrets.choice(string.digits) for _ in range(6))
