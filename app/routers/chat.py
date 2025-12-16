import httpx
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User

router = APIRouter()


@router.post("/completions")
async def chat_completions(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check token limit
    if current_user.tokens_used >= current_user.token_limit:
        raise HTTPException(status_code=429, detail="Token limit exceeded")

    # Count tokens in request (simplified - in real implementation use tiktoken)
    if "messages" in request:
        # Chat completions - count characters in messages
        content = ""
        for msg in request["messages"]:
            content += msg.get("content", "")
        token_count = len(content.split()) * 1.3  # Rough estimate for chat
    else:
        # Legacy completions
        prompt = request.get("prompt", "")
        token_count = len(prompt.split())  # rough estimate

    # Check if this request would exceed limit
    if current_user.tokens_used + token_count > current_user.token_limit:
        raise HTTPException(status_code=429, detail="Request would exceed token limit")

    # Proxy to vLLM - use the same endpoint that was called
    endpoint = "/v1/chat/completions"  # Default to chat completions

    # Use requests for now to debug connection issues
    try:
        response = requests.post(
            f"{settings.vllm_endpoint}{endpoint}",
            json=request,
            timeout=30.0
        )
        response.raise_for_status()
        result = response.json()

        # Update token usage
        current_user.tokens_used += token_count
        db.commit()

        return result
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"vLLM service error: {str(e)}")
