from __future__ import annotations

from typing import TypedDict

import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError


class ChatCompletionMessage(TypedDict):
    """Single message payload accepted by OpenRouter chat completions."""

    role: str
    content: str


class OpenRouterClient:
    """Client for interacting with the OpenRouter chat completions API."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        referer: str | None = None,
        title: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = (base_url or settings.openrouter_base_url).rstrip("/")
        self._api_key = api_key or settings.openrouter_api_key.get_secret_value()
        self._referer = referer or settings.openrouter_referer
        self._title = title or settings.openrouter_title
        self._model = model or settings.openrouter_model
        self._timeout = timeout

    async def create_chat_completion(
        self,
        messages: list[ChatCompletionMessage],
    ) -> dict:
        """Send a chat completion request to OpenRouter."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=self._build_headers(),
                    json={
                        "model": self._model,
                        "messages": messages,
                    },
                )
        except httpx.HTTPError as exc:
            raise ExternalServiceError("OpenRouter request failed") from exc

        if response.is_error:
            raise ExternalServiceError(self._build_error_message(response))

        return response.json()

    def _build_headers(self) -> dict[str, str]:
        """Build required OpenRouter request headers from application settings."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": self._referer,
            "X-Title": self._title,
            "Content-Type": "application/json",
        }

    def _build_error_message(self, response: httpx.Response) -> str:
        """Return a stable domain error message from an OpenRouter error response."""
        try:
            payload = response.json()
        except ValueError:
            payload = None

        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                message = error.get("message")
                if isinstance(message, str) and message.strip():
                    return f"OpenRouter error: {message}"

            message = payload.get("message")
            if isinstance(message, str) and message.strip():
                return f"OpenRouter error: {message}"

        return f"OpenRouter error: HTTP {response.status_code}"
