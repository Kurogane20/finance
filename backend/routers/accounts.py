from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User
from models.account import Account
from models.invoice import Invoice
from models.transaction import Transaction
from schemas.account import AccountCreate, AccountUpdate, AccountResponse
from utils.security import get_current_user, require_role
from typing import List, Optional
from datetime import date, timedelta, datetime

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=List[AccountResponse])
async def get_accounts(
    type: Optional[str] = Query(None, description="Filter by type: bank/cash/credit_card"),
    is_active: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all accounts"""
    query = db.query(Account).filter(Account.is_active == is_active)
    if type:
        query = query.filter(Account.type == type)
    return query.all()


@router.get("/summary")
async def get_accounts_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get accounts summary with total balances"""
    accounts = db.query(Account).filter(Account.is_active == True).all()
    
    total_balance = sum(float(a.balance) for a in accounts)
    by_type = {}
    for a in accounts:
        acc_type = a.type
        if acc_type not in by_type:
            by_type[acc_type] = 0
        by_type[acc_type] += float(a.balance)
    
    return {
        "total_balance": total_balance,
        "by_type": by_type,
        "account_count": len(accounts)
    }


@router.get("/aging")
async def get_aging_analysis(
    type: str = Query("receivable", description="receivable or payable"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get aging analysis for AR/AP"""
    today = date.today()
    
    invoices = db.query(Invoice).filter(
        Invoice.type == type,
        Invoice.status.in_(["sent", "viewed", "overdue"])
    ).all()
    
    aging = {
        "current": {"count": 0, "amount": 0},
        "1_30": {"count": 0, "amount": 0},
        "31_60": {"count": 0, "amount": 0},
        "61_90": {"count": 0, "amount": 0},
        "over_90": {"count": 0, "amount": 0}
    }
    
    for inv in invoices:
        days_due = (today - inv.due_date).days
        amount = float(inv.total_amount)
        
        if days_due <= 0:
            aging["current"]["count"] += 1
            aging["current"]["amount"] += amount
        elif days_due <= 30:
            aging["1_30"]["count"] += 1
            aging["1_30"]["amount"] += amount
        elif days_due <= 60:
            aging["31_60"]["count"] += 1
            aging["31_60"]["amount"] += amount
        elif days_due <= 90:
            aging["61_90"]["count"] += 1
            aging["61_90"]["amount"] += amount
        else:
            aging["over_90"]["count"] += 1
            aging["over_90"]["amount"] += amount
    
    return {
        "type": type,
        "aging": aging,
        "total_outstanding": sum(a["amount"] for a in aging.values()),
        "total_invoices": sum(a["count"] for a in aging.values())
    }


# ========================================
# INVOICE ENDPOINTS (BEFORE /{account_id} routes!)
# ========================================

@router.get("/invoices")
async def get_invoices(
    type: Optional[str] = Query(None, description="Filter by type: receivable/payable"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all invoices"""
    query = db.query(Invoice)
    if type:
        query = query.filter(Invoice.type == type)
    if status:
        query = query.filter(Invoice.status == status)
    
    invoices = query.order_by(Invoice.issue_date.desc()).all()
    
    return [
        {
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "type": inv.type,
            "customer_name": inv.customer_name,
            "customer_email": inv.customer_email,
            "amount": float(inv.amount),
            "tax_amount": float(inv.tax_amount) if inv.tax_amount else 0,
            "total_amount": float(inv.total_amount),
            "status": inv.status,
            "issue_date": inv.issue_date.isoformat() if inv.issue_date else None,
            "due_date": inv.due_date.isoformat() if inv.due_date else None,
            "notes": inv.notes
        }
        for inv in invoices
    ]


@router.post("/invoices")
async def create_invoice(
    invoice_data: dict,
    current_user: User = Depends(require_role(["admin", "editor"])),
    db: Session = Depends(get_db)
):
    """Create a new invoice"""
    # Generate invoice number if not provided
    if not invoice_data.get("invoice_number"):
        count = db.query(Invoice).count() + 1
        invoice_data["invoice_number"] = f"INV-{datetime.now().strftime('%Y%m')}-{count:04d}"
    
    # Parse dates
    issue_date = invoice_data.get("issue_date")
    if isinstance(issue_date, str):
        issue_date = date.fromisoformat(issue_date)
    
    due_date = invoice_data.get("due_date")
    if isinstance(due_date, str):
        due_date = date.fromisoformat(due_date)
    
    new_invoice = Invoice(
        invoice_number=invoice_data["invoice_number"],
        type=invoice_data.get("type", "receivable"),
        customer_name=invoice_data["customer_name"],
        customer_email=invoice_data.get("customer_email"),
        amount=invoice_data.get("amount", 0),
        tax_amount=invoice_data.get("tax_amount", 0),
        total_amount=invoice_data.get("total_amount", invoice_data.get("amount", 0)),
        status=invoice_data.get("status", "draft"),
        issue_date=issue_date or date.today(),
        due_date=due_date,
        notes=invoice_data.get("notes"),
        created_by=current_user.id
    )
    
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    
    return {
        "id": new_invoice.id,
        "invoice_number": new_invoice.invoice_number,
        "message": "Invoice berhasil dibuat"
    }


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice by ID"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "type": invoice.type,
        "customer_name": invoice.customer_name,
        "customer_email": invoice.customer_email,
        "amount": float(invoice.amount),
        "tax_amount": float(invoice.tax_amount) if invoice.tax_amount else 0,
        "total_amount": float(invoice.total_amount),
        "status": invoice.status,
        "issue_date": invoice.issue_date.isoformat() if invoice.issue_date else None,
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "paid_date": invoice.paid_date.isoformat() if invoice.paid_date else None,
        "notes": invoice.notes
    }


@router.put("/invoices/{invoice_id}")
async def update_invoice(
    invoice_id: int,
    invoice_data: dict,
    current_user: User = Depends(require_role(["admin", "editor"])),
    db: Session = Depends(get_db)
):
    """Update an invoice"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    # Update fields
    for field in ["type", "customer_name", "customer_email", "amount", "tax_amount", 
                  "total_amount", "status", "notes"]:
        if field in invoice_data:
            setattr(invoice, field, invoice_data[field])
    
    # Handle date fields
    if "issue_date" in invoice_data:
        issue_date = invoice_data["issue_date"]
        if isinstance(issue_date, str):
            issue_date = date.fromisoformat(issue_date)
        invoice.issue_date = issue_date
    
    if "due_date" in invoice_data:
        due_date = invoice_data["due_date"]
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
        invoice.due_date = due_date
    
    db.commit()
    db.refresh(invoice)
    
    return {"message": "Invoice berhasil diupdate", "id": invoice.id}


@router.post("/invoices/{invoice_id}/pay")
async def pay_invoice(
    invoice_id: int,
    payment_data: dict,
    current_user: User = Depends(require_role(["admin", "editor"])),
    db: Session = Depends(get_db)
):
    """Mark invoice as paid and create transaction via Service"""
    from services.finance_service import FinanceService
    
    account_id = payment_data.get("account_id")
    if not account_id:
        raise HTTPException(status_code=400, detail="Account ID required")
        
    try:
        service = FinanceService(db, current_user.id)
        result = service.pay_invoice(invoice_id, account_id)
        db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/invoices/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Delete an invoice"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    db.delete(invoice)
    db.commit()
    
    return {"message": "Invoice berhasil dihapus"}


# ========================================
# ACCOUNT ENDPOINTS (with path parameters - MUST come after /invoices)
# ========================================

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get account by ID"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Akun tidak ditemukan")
    return account


@router.post("", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    current_user: User = Depends(require_role(["admin", "editor"])),
    db: Session = Depends(get_db)
):
    """Create a new account"""
    db_account = Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account: AccountUpdate,
    current_user: User = Depends(require_role(["admin", "editor"])),
    db: Session = Depends(get_db)
):
    """Update an account"""
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Akun tidak ditemukan")
    
    update_data = account.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_account, field, value)
    
    db.commit()
    db.refresh(db_account)
    return db_account


@router.get("/{account_id}/transactions")
async def get_account_transactions(
    account_id: int,
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions for a specific account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Akun tidak ditemukan")
    
    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.date.desc()).limit(limit).all()
    
    return {
        "account": AccountResponse.model_validate(account),
        "transactions": transactions
    }
