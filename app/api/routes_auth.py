from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_use_case, get_current_user_id
from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> UserPublic:
    try:
        return await use_case.register(
            email=payload.email,
            password=payload.password,
        )
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        ) from exc


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> TokenResponse:
    try:
        return await use_case.login(
            email=form_data.username,
            password=form_data.password,
        )
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get("/me", response_model=UserPublic)
async def get_me(
    user_id: int = Depends(get_current_user_id),
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> UserPublic:
    try:
        return await use_case.get_profile(user_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.message,
        ) from exc
