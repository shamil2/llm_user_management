from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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
