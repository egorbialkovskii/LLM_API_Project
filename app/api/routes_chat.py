from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_chat_use_case, get_current_user_id
from app.core.errors import ExternalServiceError
from app.schemas.chat import ChatMessageResponse, ChatRequest, ChatResponse
from app.usecases.chat import ChatUseCase


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask_chat(
    payload: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    use_case: ChatUseCase = Depends(get_chat_use_case),
) -> ChatResponse:
    try:
        answer = await use_case.ask(
            user_id=user_id,
            prompt=payload.prompt,
            system=payload.system,
            max_history=payload.max_history,
            temperature=payload.temperature,
        )
    except ExternalServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc

    return ChatResponse(answer=answer)


@router.get("/history", response_model=list[ChatMessageResponse])
async def get_chat_history(
    user_id: int = Depends(get_current_user_id),
    use_case: ChatUseCase = Depends(get_chat_use_case),
    limit: int = Query(default=50, ge=0, le=100),
) -> list[ChatMessageResponse]:
    return await use_case.get_history(
        user_id=user_id,
        limit=limit,
    )


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_history(
    user_id: int = Depends(get_current_user_id),
    use_case: ChatUseCase = Depends(get_chat_use_case),
) -> Response:
    await use_case.clear_history(user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
