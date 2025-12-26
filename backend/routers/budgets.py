from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User
from models.budget import Budget
from models.transaction import Transaction, Category
from schemas.account import BudgetCreate, BudgetUpdate, BudgetResponse
from utils.security import get_current_user, require_role
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=List[BudgetResponse])
async def get_budgets(
    period: Optional[str] = Query(None, description="Filter by period e.g. 2024-01"),
    department: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all budgets"""
    query = db.query(Budget)
    if period:
        query = query.filter(Budget.period == period)
    if department:
        query = query.filter(Budget.department == department)
    return query.all()


@router.get("/comparison")
async def get_budget_comparison(
    period: str = Query(None, description="Period e.g. 2024-12"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget vs actual comparison"""
    if period is None:
        period = datetime.now().strftime("%Y-%m")
    
    budgets = db.query(Budget).filter(Budget.period == period).all()
    
    comparison = []
    for budget in budgets:
        allocated = float(budget.allocated_amount)
        spent = float(budget.spent_amount)
        remaining = allocated - spent
        percentage = (spent / allocated * 100) if allocated > 0 else 0
        
        status = "on_track"
        if percentage >= 100:
            status = "over_budget"
        elif percentage >= 80:
            status = "warning"
        
        comparison.append({
            "id": budget.id,
            "department": budget.department,
            "category_id": budget.category_id,
            "allocated": allocated,
            "spent": spent,
            "remaining": remaining,
            "percentage": round(percentage, 1),
            "status": status
        })
    
    total_allocated = sum(b["allocated"] for b in comparison)
    total_spent = sum(b["spent"] for b in comparison)
    
    return {
        "period": period,
        "budgets": comparison,
        "summary": {
            "total_allocated": total_allocated,
            "total_spent": total_spent,
            "total_remaining": total_allocated - total_spent,
            "overall_percentage": round((total_spent / total_allocated * 100) if total_allocated > 0 else 0, 1)
        }
    }


@router.get("/departments")
async def get_departments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of departments with budget allocation"""
    departments = db.query(Budget.department).distinct().all()
    return [d[0] for d in departments]


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget by ID"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget tidak ditemukan")
    return budget


@router.post("", response_model=BudgetResponse)
async def create_budget(
    budget: BudgetCreate,
    current_user: User = Depends(require_role(["admin", "approver"])),
    db: Session = Depends(get_db)
):
    """Create a new budget"""
    # Check if budget already exists for this department and period
    existing = db.query(Budget).filter(
        Budget.department == budget.department,
        Budget.period == budget.period
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Budget untuk departemen dan periode ini sudah ada"
        )
    
    db_budget = Budget(**budget.model_dump(), spent_amount=0)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget: BudgetUpdate,
    current_user: User = Depends(require_role(["admin", "approver"])),
    db: Session = Depends(get_db)
):
    """Update a budget"""
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget tidak ditemukan")
    
    update_data = budget.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_budget, field, value)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Delete a budget (admin only)"""
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget tidak ditemukan")
    
    db.delete(db_budget)
    db.commit()
    return {"message": "Budget berhasil dihapus"}
