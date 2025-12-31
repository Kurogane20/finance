from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, Role
from models.audit_log import AuditLog
from schemas.user import UserCreate, UserUpdate, UserResponse, RoleResponse
from utils.security import get_current_user, require_role, get_password_hash
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    is_active: Optional[bool] = Query(None),
    role_id: Optional[int] = Query(None),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if role_id:
        query = query.filter(User.role_id == role_id)
    return query.offset(skip).limit(limit).all()


@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all roles"""
    return db.query(Role).all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return user


@router.post("", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    # Check if email exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    
    # Check if role exists
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="Role tidak ditemukan")
    
    db_user = User(
        email=user.email,
        password_hash=get_password_hash(user.password),
        full_name=user.full_name,
        role_id=user.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="create",
        entity="user",
        entity_id=db_user.id,
        description=f"Membuat user baru: {user.email}",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Update a user (admin only)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    update_data = user.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="update",
        entity="user",
        entity_id=user_id,
        description=f"Mengubah user: {db_user.email}",
        new_values=update_data,
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    
    return db_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Deactivate a user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Tidak dapat menonaktifkan diri sendiri")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    db_user.is_active = False
    db.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="deactivate",
        entity="user",
        entity_id=user_id,
        description=f"Menonaktifkan user: {db_user.email}",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    
    return {"message": "User berhasil dinonaktifkan"}


@router.get("/audit-logs/all")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    current_user: User = Depends(require_role(["admin", "approver"])),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin/approver only)"""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity:
        query = query.filter(AuditLog.entity == entity)
    
    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "user": log.user.email if log.user else "Unknown",
            "user_name": log.user.full_name if log.user else "Unknown",
            "action": log.action,
            "entity": log.entity,
            "entity_id": log.entity_id,
            "description": log.description,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]


@router.get("/profile/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    return current_user


@router.put("/profile/me", response_model=UserResponse)
async def update_my_profile(
    profile: "ProfileUpdate",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    from schemas.user import ProfileUpdate
    
    update_data = profile.model_dump(exclude_unset=True)
    
    # Check if email is being changed and if it's already taken
    if "email" in update_data and update_data["email"] != current_user.email:
        existing = db.query(User).filter(User.email == update_data["email"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email sudah digunakan")
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="update_profile",
        entity="user",
        entity_id=current_user.id,
        description=f"User {current_user.email} update profile",
        new_values=update_data,
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    
    return current_user


@router.post("/profile/change-password")
async def change_password(
    password_data: "PasswordChange",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password"""
    from schemas.user import PasswordChange
    from utils.security import verify_password
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Password lama salah")
    
    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password baru minimal 8 karakter")
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="change_password",
        entity="user",
        entity_id=current_user.id,
        description=f"User {current_user.email} mengganti password",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Password berhasil diubah"}
