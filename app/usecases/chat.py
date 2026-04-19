from __future__ import annotations

from app.core.errors import ExternalServiceError
from app.repositories.chat_messages import ChatMessagesRepository
from app.services.openrouter_client import ChatCompletionMessage, OpenRouterClient


class ChatUseCase:
    """Business logic for assembling chat context and talking to the LLM."""

    def __init__(
        self,
        messages_repository: ChatMessagesRepository,
        openrouter_client: OpenRouterClient,
    ) -> None:
        self._messages_repository = messages_repository
        self._openrouter_client = openrouter_client

    async def ask(
        self,
        *,
        user_id: int,
        prompt: str,
        system: str | None = None,
        max_history: int = 10,
    ) -> str:
        """Build model messages, persist the dialogue, and return the answer."""
        messages: list[ChatCompletionMessage] = []

        if system is not None and system.strip():
            messages.append(
                ChatCompletionMessage(
                    role="system",
                    content=system.strip(),
                )
            )

        history = await self._messages_repository.get_recent_by_user_id(
            user_id=user_id,
            limit=max_history,
        )
        for message in reversed(history):
            messages.append(
                ChatCompletionMessage(
                    role=message.role,
                    content=message.content,
                )
            )

        messages.append(
            ChatCompletionMessage(
                role="user",
                content=prompt,
            )
        )

        await self._messages_repository.create(
            user_id=user_id,
            role="user",
            content=prompt,
        )

        response = await self._openrouter_client.create_chat_completion(messages)
        answer = self._extract_answer(response)

        await self._messages_repository.create(
            user_id=user_id,
            role="assistant",
            content=answer,
        )

        return answer

    def _extract_answer(self, response: dict) -> str:
        """Extract assistant text from an OpenRouter chat completion response."""
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ExternalServiceError("OpenRouter returned an invalid response")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise ExternalServiceError("OpenRouter returned an invalid response")

        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise ExternalServiceError("OpenRouter returned an invalid response")

        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content

        raise ExternalServiceError("OpenRouter returned an empty response")
