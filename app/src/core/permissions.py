from typing import List, override
from fastapi import Depends, HTTPException, status

from app.src.api.depedencies.auth import get_auth_token
from app.src.schemas.auth import RoleEnum
from app.src.utils.token_handlers import get_current_role


class BasePermisson:
    role: str = None
    allowed_roles: List[str] = None

    def __init__(self, role: str):
        self.role = role

        if not self.has_required_permission():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted"
            )

    def has_required_permission(self):
        if self.role not in self.allowed_roles:
            return False
        return True


class PermissionsDependency:
    def __init__(self, permissions_classes: List[BasePermisson]):
        self.permissions_classes = permissions_classes

    def __call__(self, token: str = Depends(get_auth_token)):
        role = get_current_role(token)
        for permission_class in self.permissions_classes:
            permission_class(role)


class SuperAdminPermission(BasePermisson):
    @override
    def has_required_permission(self):
        return self.role == RoleEnum.SUPER_ADMIN


class AdminPermission(BasePermisson):
    allowed_roles = [RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN]


class UserPermission(BasePermisson):
    allowed_roles = [RoleEnum.SUPER_ADMIN, RoleEnum.USER]
