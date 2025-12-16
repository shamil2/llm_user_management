# app/routers/openai_compatible.py
"""
OpenAI-compatible API endpoints for direct integration with opencode and other clients.
These endpoints use API key authentication instead of JWT tokens.
"""

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies.database import get_db
from app.models.user import User
from app.utils.security import verify_api_key

router = APIRouter()


async def get_user_from_api_key(
    authorization: str = Header(..., alias="Authorization"),
    db: Session = Depends(get_db),
):
    """Extract and validate API key from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    # Handle Bearer token format
    if authorization.startswith("Bearer "):
        api_key = authorization[7:]
    else:
        api_key = authorization

    # Verify API key
    user = verify_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user


@router.post("/v1/chat/completions")
async def chat_completions_openai(
    request: Request,
    user: User = Depends(get_user_from_api_key),
    db: Session = Depends(get_db),
):
    """OpenAI-compatible chat completions endpoint"""
    # Parse request body
    body = await request.json()

    # Check token limit
    if user.tokens_used >= user.token_limit:
        raise HTTPException(status_code=429, detail="Token limit exceeded")

    # Extract messages and estimate tokens
    messages = body.get("messages", [])
    prompt_text = ""
    for msg in messages:
        if isinstance(msg, dict) and "content" in msg:
            prompt_text += msg["content"] + " "

    token_count = len(prompt_text.split())  # rough estimate

    # Check if this request would exceed limit
    if user.tokens_used + token_count > user.token_limit:
        raise HTTPException(status_code=429, detail="Request would exceed token limit")

    # Convert OpenAI format to vLLM format
    vllm_request = {
        "prompt": prompt_text.strip(),
        "max_tokens": body.get("max_tokens", 100),
        "temperature": body.get("temperature", 0.7),
        "top_p": body.get("top_p", 1.0),
        "stream": body.get("stream", False),
    }

    # Add any other vLLM-specific parameters
    for key, value in body.items():
        if key not in ["messages", "model"] and key not in vllm_request:
            vllm_request[key] = value

    # Proxy to vLLM
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.vllm_endpoint}/v1/completions",
                json=vllm_request,
                timeout=60.0,
            )
            response.raise_for_status()
            vllm_result = response.json()

            # Convert vLLM response to OpenAI format
            openai_response = {
                "id": vllm_result.get("id", "chatcmpl-" + str(hash(str(vllm_result)))),
                "object": "chat.completion",
                "created": vllm_result.get("created", 0),
                "model": body.get("model", "llm-user-managed"),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": vllm_result.get("choices", [{}])[0].get(
                                "text", ""
                            ),
                        },
                        "finish_reason": vllm_result.get("choices", [{}])[0].get(
                            "finish_reason", "stop"
                        ),
                    }
                ],
                "usage": {
                    "prompt_tokens": token_count,
                    "completion_tokens": len(
                        vllm_result.get("choices", [{}])[0].get("text", "").split()
                    ),
                    "total_tokens": token_count
                    + len(vllm_result.get("choices", [{}])[0].get("text", "").split()),
                },
            }

            # Update token usage
            user.tokens_used += openai_response["usage"]["total_tokens"]
            db.commit()

            return openai_response

        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"vLLM service error: {str(e)}")


@router.post("/v1/completions")
async def completions_openai(
    request: Request,
    user: User = Depends(get_user_from_api_key),
    db: Session = Depends(get_db),
):
    """OpenAI-compatible completions endpoint (legacy)"""
    # Parse request body
    body = await request.json()

    # Check token limit
    if user.tokens_used >= user.token_limit:
        raise HTTPException(status_code=429, detail="Token limit exceeded")

    # Estimate tokens
    prompt = body.get("prompt", "")
    token_count = len(prompt.split())

    if user.tokens_used + token_count > user.token_limit:
        raise HTTPException(status_code=429, detail="Request would exceed token limit")

    # Proxy to vLLM
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.vllm_endpoint}/v1/completions", json=body, timeout=60.0
            )
            response.raise_for_status()
            result = response.json()

            # Update token usage
            completion_tokens = len(
                result.get("choices", [{}])[0].get("text", "").split()
            )
            user.tokens_used += token_count + completion_tokens
            db.commit()

            return result

        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"vLLM service error: {str(e)}")


@router.get("/v1/models")
async def list_models():
    """OpenAI-compatible models endpoint"""
    return {
        "object": "list",
        "data": [
            {
                "id": "llm-user-managed",
                "object": "model",
                "created": 1677610602,
                "owned_by": "llm-user-management",
                "permission": [
                    {
                        "id": "modelperm-mock",
                        "object": "model_permission",
                        "created": 1677610602,
                        "allow_create_engine": False,
                        "allow_sampling": True,
                        "allow_logprobs": True,
                        "allow_search_indices": False,
                        "allow_view": True,
                        "allow_fine_tuning": False,
                        "organization": "*",
                        "group": None,
                        "is_blocking": False,
                    }
                ],
                "root": "llm-user-managed",
                "parent": None,
            }
        ],
    }
