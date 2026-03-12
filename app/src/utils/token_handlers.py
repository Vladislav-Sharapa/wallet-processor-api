from app.src.exceptions.auth_exceptions import CredentialException
from app.src.schemas.user_schemas import UserModel
from app.src.services.user import UserService
from app.src.utils.jwt import get_reset_token_payload, get_access_token_payload


def get_current_role(token: str) -> str:
    payload = get_access_token_payload(token)

    return payload.get("role", None)


def get_user_email_for_reset(token: str) -> str | None:
    payload = get_reset_token_payload(token)

    return payload.get("email", None)


async def get_current_auth_user(payload: dict, user_service: UserService) -> UserModel:
    user_id = payload.get("user_id", None)
    email = payload.get("email", None)
    if user_id:
        user = await user_service.get_active_user(user_id)
    elif email:
        user = await user_service.get_active_user_by_email(email)

    if not user:
        raise CredentialException
    return UserModel.model_validate(user)
