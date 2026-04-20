from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.repositories.chat_messages import ChatMessagesRepository
from app.repositories.users import UsersRepository
from app.services.openrouter_client import OpenRouterClient
from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session for the lifetime of a request."""
    async with AsyncSessionLocal() as session:
        yield session


def get_users_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UsersRepository:
    """Provide the users repository bound to the current DB session."""
    return UsersRepository(session)


def get_chat_messages_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ChatMessagesRepository:
    """Provide the chat messages repository bound to the current DB session."""
    return ChatMessagesRepository(session)


def get_openrouter_client() -> OpenRouterClient:
    """Provide an OpenRouter client configured from application settings."""
    return OpenRouterClient()


def get_auth_use_case(
    users_repository: UsersRepository = Depends(get_users_repository),
) -> AuthUseCase:
    """Provide the authentication use case."""
    return AuthUseCase(users_repository)


def get_chat_use_case(
    messages_repository: ChatMessagesRepository = Depends(
        get_chat_messages_repository
    ),
    openrouter_client: OpenRouterClient = Depends(get_openrouter_client),
) -> ChatUseCase:
    """Provide the chat use case."""
    return ChatUseCase(messages_repository, openrouter_client)


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
) -> int:
    """Decode the JWT access token and return the current user id."""
    try:
        payload = decode_access_token(token)
        raw_sub = payload.get("sub")
        if raw_sub is None:
            raise UnauthorizedError("Token subject is missing")

        return int(raw_sub)
    except (UnauthorizedError, ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
