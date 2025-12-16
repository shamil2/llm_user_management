import httpx
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
    prompt = request.get("prompt", "")
    token_count = len(prompt.split())  # rough estimate

    # Check if this request would exceed limit
    if current_user.tokens_used + token_count > current_user.token_limit:
        raise HTTPException(status_code=429, detail="Request would exceed token limit")

    # Proxy to vLLM
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.vllm_endpoint}/v1/completions", json=request, timeout=60.0
            )
            response.raise_for_status()
            result = response.json()

            # Update token usage
            current_user.tokens_used += token_count
            db.commit()

            return result
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"vLLM service error: {str(e)}")
