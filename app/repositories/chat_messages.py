from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage



class ChatMessagesRepository:
    """Repository for chat message database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: int, role: str, content: str) -> ChatMessage:
        """Create and persist a chat message for a user."""
        message = ChatMessage(
            user_id=user_id,
            role=role,
            content=content,
        )
        self._session.add(message)
        await self._session.commit()
        await self._session.refresh(message)
        return message

    async def get_recent_by_user_id(
        self,
        user_id: int,
        limit: int
    ) -> list[ChatMessage]:
        """Return the latest user messages with configurable sorting."""
        order_by = ChatMessage.created_at.desc()

        result = await self._session.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(order_by, ChatMessage.id.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_by_user_id(self, user_id: int) -> None:
        """Delete the entire chat history for a user."""
        await self._session.execute(
            delete(ChatMessage).where(ChatMessage.user_id == user_id)
        )
        await self._session.commit()
