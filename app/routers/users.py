from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import List, Optional

from app import schemas
from app.dependencies.auth import get_current_user as get_current_user_dep
from app.dependencies.database import get_db
from app.models.user import User, ApiCall

router = APIRouter()


@router.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: User = Depends(get_current_user_dep)):
    return current_user


@router.put("/me/token-limit")
def update_token_limit(
    token_limit: int,
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    if token_limit < current_user.tokens_used:
        raise HTTPException(
            status_code=400, detail="Token limit cannot be less than current usage"
        )

    current_user.token_limit = token_limit
    db.commit()
    return {"message": "Token limit updated"}


@router.get("/usage")
def get_usage(current_user: User = Depends(get_current_user_dep)):
    return {
        "tokens_used": current_user.tokens_used,
        "token_limit": current_user.token_limit,
        "remaining": current_user.token_limit - current_user.tokens_used,
    }


@router.get("/billing/daily")
def get_daily_usage(
    days: int = Query(30, description="Number of days to look back"),
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """
    Get daily usage statistics for billing purposes
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Query daily usage
    daily_usage = db.query(
        func.date(ApiCall.timestamp).label('date'),
        func.count(ApiCall.id).label('call_count'),
        func.sum(ApiCall.tokens_used).label('tokens_used'),
        func.sum(ApiCall.estimated_cost).label('estimated_cost')
    ).filter(
        ApiCall.user_id == current_user.id,
        ApiCall.timestamp >= start_date,
        ApiCall.timestamp <= end_date
    ).group_by(
        func.date(ApiCall.timestamp)
    ).order_by(
        func.date(ApiCall.timestamp)
    ).all()

    # Format the results
    usage_data = []
    for row in daily_usage:
        usage_data.append({
            "date": str(row.date) if row.date else None,
            "call_count": int(row.call_count or 0),
            "tokens_used": float(row.tokens_used or 0),
            "estimated_cost": float(row.estimated_cost or 0)
        })

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "period_days": days,
        "daily_usage": usage_data,
        "summary": {
            "total_calls": sum(row.call_count or 0 for row in daily_usage),
            "total_tokens": float(sum(row.tokens_used or 0 for row in daily_usage)),
            "total_cost": float(sum(row.estimated_cost or 0 for row in daily_usage))
        }
    }


@router.get("/billing/calls")
def get_api_calls(
    limit: int = Query(100, description="Maximum number of calls to return"),
    offset: int = Query(0, description="Number of calls to skip"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """
    Get detailed API call history for billing
    """
    query = db.query(ApiCall).filter(ApiCall.user_id == current_user.id)

    # Apply date filters
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(ApiCall.timestamp >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            # Set to end of day
            end = end.replace(hour=23, minute=59, second=59)
            query = query.filter(ApiCall.timestamp <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

    # Get total count
    total_calls = query.count()

    # Get paginated results
    calls = query.order_by(ApiCall.timestamp.desc()).offset(offset).limit(limit).all()

    # Format the results
    call_data = []
    for call in calls:
        call_data.append({
            "id": call.id,
            "timestamp": call.timestamp.isoformat(),
            "endpoint": call.endpoint,
            "method": call.method,
            "status_code": call.status_code,
            "tokens_used": float(call.tokens_used),
            "model": call.model,
            "estimated_cost": float(call.estimated_cost),
            "request_size": call.request_size,
            "response_size": call.response_size
        })

    return {
        "user_id": current_user.id,
        "total_calls": total_calls,
        "calls_returned": len(call_data),
        "offset": offset,
        "limit": limit,
        "calls": call_data
    }


@router.get("/billing/summary")
def get_billing_summary(
    month: Optional[int] = Query(None, description="Month (1-12)"),
    year: Optional[int] = Query(None, description="Year (e.g., 2025)"),
    current_user: User = Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    """
    Get billing summary for current month or specified month/year
    """
    now = datetime.utcnow()

    if month and year:
        target_month = month
        target_year = year
    else:
        target_month = now.month
        target_year = now.year

    # Calculate start and end of the target month
    start_date = datetime(target_year, target_month, 1)
    if target_month == 12:
        end_date = datetime(target_year + 1, 1, 1)
    else:
        end_date = datetime(target_year, target_month + 1, 1)

    # Get monthly usage
    monthly_stats = db.query(
        func.count(ApiCall.id).label('call_count'),
        func.sum(ApiCall.tokens_used).label('tokens_used'),
        func.sum(ApiCall.estimated_cost).label('estimated_cost'),
        func.avg(ApiCall.tokens_used).label('avg_tokens_per_call'),
        func.min(ApiCall.timestamp).label('first_call'),
        func.max(ApiCall.timestamp).label('last_call')
    ).filter(
        ApiCall.user_id == current_user.id,
        ApiCall.timestamp >= start_date,
        ApiCall.timestamp < end_date
    ).first()

    # Get daily breakdown for the month
    daily_breakdown = db.query(
        func.date(ApiCall.timestamp).label('date'),
        func.count(ApiCall.id).label('calls'),
        func.sum(ApiCall.tokens_used).label('tokens')
    ).filter(
        ApiCall.user_id == current_user.id,
        ApiCall.timestamp >= start_date,
        ApiCall.timestamp < end_date
    ).group_by(
        func.date(ApiCall.timestamp)
    ).order_by(
        func.date(ApiCall.timestamp)
    ).all()

    daily_data = []
    for row in daily_breakdown:
        daily_data.append({
            "date": str(row.date) if row.date else None,
            "calls": int(row.calls or 0),
            "tokens": float(row.tokens or 0)
        })

    return {
        "user_id": current_user.id,
        "billing_period": f"{target_year}-{target_month:02d}",
        "summary": {
            "total_calls": monthly_stats.call_count or 0,
            "total_tokens": float(monthly_stats.tokens_used or 0),
            "estimated_cost": float(monthly_stats.estimated_cost or 0),
            "avg_tokens_per_call": float(monthly_stats.avg_tokens_per_call or 0),
            "first_call": monthly_stats.first_call.isoformat() if monthly_stats.first_call else None,
            "last_call": monthly_stats.last_call.isoformat() if monthly_stats.last_call else None
        },
        "daily_breakdown": daily_data
    }
