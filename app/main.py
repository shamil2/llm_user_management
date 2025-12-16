from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (auth_router, chat_router, openai_compatible_router,
                         users_router)
from app.middleware.api_call_tracker import ApiCallTrackerMiddleware

app = FastAPI(
    title="LLM User Management API",
    description="API proxy for vLLM with user authentication and token usage tracking",
    version="1.0.0",
)

# API Call Tracking Middleware (must be first)
app.add_middleware(ApiCallTrackerMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(openai_compatible_router, tags=["openai-compatible"])


@app.get("/")
async def root():
    return {"message": "LLM User Management API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
