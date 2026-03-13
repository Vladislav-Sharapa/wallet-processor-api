from typing import Optional, List
from fastapi import APIRouter, Depends, Path, status
from app.src.api.depedencies.auth import check_user_ownership
from app.src.api.depedencies.transaction_dependencies import (
    get_transaction_create_use_case,
    get_transaction_roll_back_use_case,
    get_transaction_service,
)
from app.src.core.permissions import (
    PermissionsDependency,
    UserPermission,
)
from app.src.schemas.transaction_schemas import (
    RequestTransactionModel,
    TransactionModel,
)
from app.src.services.flows.transaction_flows import (
    CreateTransactionUseCase,
    TransactionRollBackUseCase,
)
from app.src.services.transaction import TransactionService

router = APIRouter(dependencies=[Depends(PermissionsDependency([UserPermission]))])


@router.get("/transactions", status_code=status.HTTP_200_OK)
async def get_transactions(
    user_id: Optional[int] = None,
    service: TransactionService = Depends(get_transaction_service),
) -> List[TransactionModel] | None:
    return await service.get_all(user_id=user_id)


@router.post(
    "/{user_id}/transactions",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(check_user_ownership)],
)
async def post_transaction(
    request: RequestTransactionModel,
    user_id: int = Path(ge=0, description="User ID must be positive integer"),
    transaction_use_case: CreateTransactionUseCase = Depends(
        get_transaction_create_use_case
    ),
) -> TransactionModel | None:
    transaction = await transaction_use_case.execute(user_id=user_id, request=request)

    return transaction


@router.patch(
    "/{user_id}/transactions/{transaction_id}",
    dependencies=[Depends(check_user_ownership)],
)
async def patch_rollback_transaction(
    user_id: int = Path(ge=0, description="User ID must be positive integer"),
    transaction_id: int = Path(
        ge=0, description="Transaction ID must be positive integer"
    ),
    transaction_use_case: TransactionRollBackUseCase = Depends(
        get_transaction_roll_back_use_case
    ),
) -> TransactionModel | None:
    transaction = await transaction_use_case.execute(
        user_id=user_id, transaction_id=transaction_id
    )
    return transaction
