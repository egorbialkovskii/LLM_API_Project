from __future__ import annotations

from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.repositories.users import UsersRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserPublic


class AuthUseCase:
    """Business logic for user registration, login, and profile lookup."""

    def __init__(self, users_repository: UsersRepository) -> None:
        self._users_repository = users_repository

    async def register(self, email: str, password: str) -> UserPublic:
        """Register a new user when the email is still available."""
        existing_user = await self._users_repository.get_by_email(email)
        if existing_user is not None:
            raise ConflictError("Email is already registered")

        password_hash = hash_password(password)
        user = await self._users_repository.create(
            email=email,
            password_hash=password_hash,
        )
        return UserPublic.model_validate(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate a user by email and password and issue a JWT."""
        user = await self._users_repository.get_by_email(email)
        if user is None:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        access_token = create_access_token(
            sub=str(user.id),
            role=user.role,
        )
        return TokenResponse(access_token=access_token)

    async def get_profile(self, user_id: int) -> UserPublic:
        """Return the public profile for a user by id."""
        user = await self._users_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")

        return UserPublic.model_validate(user)
