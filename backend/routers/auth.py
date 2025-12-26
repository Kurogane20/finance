from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, Role
from models.audit_log import AuditLog
from schemas.user import UserLogin, Token, UserResponse
from utils.security import verify_password, create_access_token, get_current_user
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login dengan email dan password"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun tidak aktif. Hubungi administrator."
        )
    
    # Create audit log
    audit_log = AuditLog(
        user_id=user.id,
        action="login",
        entity="user",
        entity_id=user.id,
        description=f"User {user.email} berhasil login",
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info"""
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user (untuk audit trail)"""
    audit_log = AuditLog(
        user_id=current_user.id,
        action="logout",
        entity="user",
        entity_id=current_user.id,
        description=f"User {current_user.email} logout",
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Berhasil logout"}
