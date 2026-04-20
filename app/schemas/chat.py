from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Request schema for chat interactions with the LLM."""

    prompt: str = Field(min_length=1)
    system: str | None = None
    max_history: int = Field(default=10, ge=0, le=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    """Response schema for chat answers."""

    answer: str


class ChatMessageResponse(BaseModel):
    """Response schema for a stored chat message."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime
