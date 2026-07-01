from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # Retrieve user from persistence layer by unique email handle
    user = db.query(User).filter(User.email == payload.email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email credentials or password profile signature.",
        )

    hashed_password = cast(str, user.hashed_password)

    if not verify_password(payload.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email credentials or password profile signature.",
        )

    is_active = cast(bool, user.is_active)

    if not is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user account.",
        )

    # Encode critical role signatures directly into the access token payload
    token_claims = {
        "sub": cast(str, user.email),
        "role": cast(str, user.role),
        "user_id": cast(Any, user.id),
    }

    jwt_token = create_access_token(data=token_claims)

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
    }