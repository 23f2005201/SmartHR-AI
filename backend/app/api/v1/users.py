from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash
from app.api.deps import RoleChecker

router = APIRouter()
allow_management = RoleChecker(["Admin", "HR"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate, 
    db: Session = Depends(get_db),
    current_operator = Depends(allow_management)
):
    # Verify if the email handle is already registered in the system
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A corporate user account with this email address already exists."
        )

    # Hash the raw plain text password before persistence
    hashed_pwd = get_password_hash(payload.password)
    
    new_user = User(
        email=payload.email,
        hashed_password=hashed_pwd,
        role=payload.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user