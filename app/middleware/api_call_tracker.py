# app/middleware/api_call_tracker.py
"""
Middleware to track API calls for billing purposes
"""

import time
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.dependencies.database import get_db
from app.models.user import ApiCall, User


class ApiCallTrackerMiddleware:
    """
    Middleware that tracks API calls for billing and usage analytics
    """

    def __init__(self, app: Callable):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract request information
        method = scope.get("method", "GET")
        path = scope.get("path", "/")

        # Only track API calls (not static files, docs, etc.)
        if not self._should_track_call(path, method):
            await self.app(scope, receive, send)
            return

        # Start timing
        start_time = time.time()

        # Create a custom receive function to capture request body
        request_body = b""
        original_receive = receive

        async def capture_receive():
            nonlocal request_body
            message = await original_receive()
            if message["type"] == "http.request":
                request_body += message.get("body", b"")
            return message

        # Create a custom send function to capture response
        response_body = b""
        response_status = 200
        original_send = send

        async def capture_send(message):
            nonlocal response_body, response_status
            if message["type"] == "http.response.start":
                response_status = message.get("status", 200)
            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")

            await original_send(message)

        # Process the request
        await self.app(scope, capture_receive, capture_send)

        # Log the API call
        processing_time = time.time() - start_time
        await self._log_api_call(
            method=method,
            path=path,
            request_body=request_body,
            response_body=response_body,
            response_status=response_status,
            processing_time=processing_time,
            scope=scope
        )

    def _should_track_call(self, path: str, method: str) -> bool:
        """
        Determine if this API call should be tracked for billing
        """
        # Track API calls to these endpoints
        trackable_paths = [
            "/v1/chat/completions",
            "/v1/completions",
            "/chat/completions",
        ]

        # Don't track these (health checks, auth, etc.)
        ignore_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/",
            "/users/me",
            "/users/usage",
        ]

        # Check if it's a trackable API call
        for trackable in trackable_paths:
            if trackable in path:
                return True

        # Check if it should be ignored
        for ignore in ignore_paths:
            if path.startswith(ignore):
                return False

        return False

    async def _log_api_call(self, method: str, path: str, request_body: bytes,
                           response_body: bytes, response_status: int,
                           processing_time: float, scope):
        """
        Log the API call to the database
        """
        try:
            # Extract user information from headers or scope
            user_id = None
            api_key = None

            # Check for Authorization header (Bearer token)
            headers = dict(scope.get("headers", []))
            authorization = headers.get(b"authorization", b"").decode("utf-8", errors="ignore")

            if authorization.startswith("Bearer "):
                token = authorization[7:]  # Remove "Bearer " prefix

                # Try to find user by API key
                db: Session = next(get_db())
                try:
                    user = db.query(User).filter(User.api_key == token).first()
                    if user:
                        user_id = user.id
                        api_key = token
                finally:
                    db.close()

            # Parse request body to extract model and estimate tokens
            tokens_used = 0.0
            model = None

            try:
                if request_body:
                    request_data = json.loads(request_body.decode("utf-8", errors="ignore"))
                    model = request_data.get("model")

                    # Estimate tokens (rough calculation)
                    if "messages" in request_data:
                        # Chat completions - count characters roughly
                        content = ""
                        for msg in request_data["messages"]:
                            content += msg.get("content", "")
                        tokens_used = len(content.split()) * 1.3  # Rough estimate
                    elif "prompt" in request_data:
                        # Completions - count words
                        tokens_used = len(request_data["prompt"].split()) * 1.3

                    # Apply max_tokens limit if specified
                    max_tokens = request_data.get("max_tokens", 0)
                    if max_tokens and tokens_used > max_tokens:
                        tokens_used = max_tokens

            except (json.JSONDecodeError, UnicodeDecodeError):
                # If we can't parse the request, skip token estimation
                pass

            # Calculate estimated cost (rough approximation)
            estimated_cost = 0.0
            if tokens_used > 0:
                # Very rough pricing - adjust based on your actual costs
                if "gpt-4" in str(model):
                    estimated_cost = (tokens_used / 1000) * 0.03  # $0.03 per 1K tokens
                elif "gpt-3.5" in str(model):
                    estimated_cost = (tokens_used / 1000) * 0.002  # $0.002 per 1K tokens
                else:
                    estimated_cost = (tokens_used / 1000) * 0.001  # Default rate

            # Create API call record
            if user_id:
                db: Session = next(get_db())
                try:
                    api_call = ApiCall(
                        user_id=user_id,
                        endpoint=path,
                        method=method,
                        request_size=len(request_body),
                        response_size=len(response_body),
                        status_code=response_status,
                        tokens_used=tokens_used,
                        model=model,
                        estimated_cost=estimated_cost
                    )

                    db.add(api_call)

                    # Update user's total token usage
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        user.tokens_used += tokens_used

                    db.commit()

                except Exception as e:
                    print(f"Error logging API call: {e}")
                    db.rollback()
                finally:
                    db.close()

        except Exception as e:
            # Don't let logging errors break the API
            print(f"API call tracking error: {e}")
            pass