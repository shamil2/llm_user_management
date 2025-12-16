from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.dependencies.auth import get_current_user as get_current_user_dep
from app.dependencies.database import get_db
from app.models.user import User

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
