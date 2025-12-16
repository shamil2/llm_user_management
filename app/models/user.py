from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):  # type: ignore
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    api_key = Column(
        String, unique=True, index=True, nullable=True
    )  # API key for OpenAI-compatible endpoints
    token_limit = Column(Integer, default=10000)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to API calls
    api_calls = relationship("ApiCall", back_populates="user")


class ApiCall(Base):  # type: ignore
    __tablename__ = "api_calls"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Request details
    endpoint = Column(String, index=True)  # e.g., "/v1/chat/completions"
    method = Column(String, default="POST")  # HTTP method
    request_size = Column(Integer, default=0)  # Request payload size in bytes

    # Response details
    status_code = Column(Integer, default=200)
    response_size = Column(Integer, default=0)  # Response payload size in bytes

    # Token usage
    tokens_used = Column(Float, default=0.0)  # Tokens used in this call
    model = Column(String, nullable=True)  # Model used (e.g., "gpt-3.5-turbo")

    # Cost tracking (optional, for future billing)
    estimated_cost = Column(Float, default=0.0)  # Estimated cost in USD

    # Relationship back to user
    user = relationship("User", back_populates="api_calls")

    def __repr__(self):
        return f"<ApiCall(user_id={self.user_id}, endpoint='{self.endpoint}', tokens={self.tokens_used}, timestamp={self.timestamp})>"