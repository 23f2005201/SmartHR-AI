from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # Retrieve user from persistence layer by unique email handle
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email credentials or password profile signature."
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account.")

    # Encode critical role signatures directly into the access token payload
    token_claims = {"sub": user.email, "role": user.role, "user_id": user.id}
    jwt_token = create_access_token(data=token_claims)

    return {"access_token": jwt_token, "token_type": "bearer"}