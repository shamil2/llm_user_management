from typing import Optional, List
from datetime import date

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


# Billing schemas
class ApiCallInfo(BaseModel):
    id: int
    timestamp: str
    endpoint: str
    method: str
    status_code: int
    tokens_used: float
    model: Optional[str]
    estimated_cost: float
    request_size: int
    response_size: int

    class Config:
        from_attributes = True


class DailyUsage(BaseModel):
    date: Optional[str]
    call_count: int
    tokens_used: float
    estimated_cost: float


class BillingSummary(BaseModel):
    user_id: int
    username: str
    period_days: int
    daily_usage: List[DailyUsage]
    summary: dict


class ApiCallsResponse(BaseModel):
    user_id: int
    total_calls: int
    calls_returned: int
    offset: int
    limit: int
    calls: List[ApiCallInfo]


class MonthlyBillingSummary(BaseModel):
    user_id: int
    billing_period: str
    summary: dict
    daily_breakdown: List[dict]
