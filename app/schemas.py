from typing import Optional

from pydantic import BaseModel, field_validator


class UserBase(BaseModel):
    username: str
    token_limit: Optional[int] = 10000


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("password cannot be longer than 72 bytes")
        return v


class User(UserBase):
    id: int
    tokens_used: int

    class Config:
        from_attributes = True


class UserWithApiKey(User):
    api_key: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
