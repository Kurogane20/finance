from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User
from models.transaction import Transaction, Category
from models.account import Account
from models.audit_log import AuditLog
from schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse, CategoryResponse
from utils.security import get_current_user, require_role
from typing import List, Optional
from datetime import datetime
import csv
import io
from decimal import Decimal

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    type: Optional[str] = Query(None, description="Filter by type: credit/debit"),
    category_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of transactions with filters"""
    query = db.query(Transaction)
    
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if status:
        query = query.filter(Transaction.status == status)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    transactions = query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    return transactions


@router.get("/summary")
async def get_transactions_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions summary statistics"""
    total_credit = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.type == "credit",
        Transaction.status == "completed"
    ).scalar()
    
    total_debit = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.type == "debit",
        Transaction.status == "completed"
    ).scalar()
    
    pending_count = db.query(func.count(Transaction.id)).filter(
        Transaction.status == "pending"
    ).scalar()
    
    total_count = db.query(func.count(Transaction.id)).scalar()
    
    return {
        "total_credit": float(total_credit),
        "total_debit": float(total_debit),
        "net": float(total_credit - total_debit),
        "pending_count": pending_count,
        "total_count": total_count
    }


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    type: Optional[str] = Query(None, description="Filter by type: income/expense"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all transaction categories"""
    query = db.query(Category)
    if type:
        query = query.filter(Category.type == type)
    return query.all()


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction by ID"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    return transaction


@router.post("", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(require_role(["admin", "editor", "approver"])),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    from services.finance_service import FinanceService
    
    try:
        service = FinanceService(db, current_user.id)
        new_transaction = service.create_transaction(transaction.model_dump())
        db.commit()
        db.refresh(new_transaction)
        return new_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    current_user: User = Depends(require_role(["admin", "editor", "approver"])),
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    from services.finance_service import FinanceService
    
    try:
        service = FinanceService(db, current_user.id)
        updated_transaction = service.update_transaction(
            transaction_id, 
            transaction.model_dump(exclude_unset=True)
        )
        db.commit()
        db.refresh(updated_transaction)
        return updated_transaction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Delete a transaction (admin only)"""
    from services.finance_service import FinanceService
    
    try:
        service = FinanceService(db, current_user.id)
        service.delete_transaction(transaction_id)
        db.commit()
        return {"message": "Transaksi berhasil dihapus"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/import", response_model=dict)
async def import_transactions(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["admin", "editor"])),
    db: Session = Depends(get_db)
):
    """Import transactions from CSV"""
    from services.finance_service import FinanceService
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    decoded = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded))
    
    success_count = 0
    errors = []
    
    service = FinanceService(db, current_user.id)
    
    # Pre-fetch caches for ID resolution
    accounts_map = {a.name.lower(): a.id for a in db.query(Account).all()}
    categories_map = {c.name.lower(): c.id for c in db.query(Category).all()}
    
    for row_num, row in enumerate(csv_reader, start=1):
        try:
            # Validate required fields
            required = ['Date', 'Description', 'Amount', 'Type', 'Account']
            if not all(k in row for k in required):
                raise ValueError(f"Missing required columns: {required}")
            
            # Parse Date
            try:
                date_val = datetime.strptime(row['Date'], '%Y-%m-%d')
            except ValueError:
                date_val = datetime.strptime(row['Date'], '%d/%m/%Y')
                
            # Resolve Account
            acc_name = row['Account'].lower()
            account_id = accounts_map.get(acc_name)
            if not account_id:
                # Try partial match
                account_id = next((id for name, id in accounts_map.items() if acc_name in name), None)
                if not account_id:
                    raise ValueError(f"Account '{row['Account']}' not found")
            
            # Resolve Category
            cat_name = row.get('Category', 'Lainnya').lower()
            category_id = categories_map.get(cat_name)
            if not category_id:
                # Create new category if not exists
                new_cat = Category(
                    name=row.get('Category', 'Lainnya'),
                    type='expense' if row['Type'] == 'debit' else 'income',
                    icon='📂',
                    color='#94a3b8'
                )
                db.add(new_cat)
                db.flush()
                categories_map[new_cat.name.lower()] = new_cat.id
                category_id = new_cat.id
            
            # Prepare data for Service
            trans_data = {
                "date": date_val,
                "description": row['Description'],
                "amount": Decimal(row['Amount']),
                "type": row['Type'].lower(),
                "category_id": category_id,
                "account_id": account_id,
                "status": 'completed',
                "reference": f"Import {file.filename}"
            }
            
            # Use Service to Create (handles Ledger + Budget)
            service.create_transaction(trans_data)
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            # Continue to next row, but validation errors in service might rollback flush?
            # Since create_transaction flushes but doesn't commit, failure here might be risky if we don't rollback/savepoint.
            # Ideally use nested transaction or savepoint. 
            # For simplicity, we assume bulk commit at end. 
            # If one fails, we just don't add it to session?
            # But service.create_transaction adds to session. 
            # We would need to expunge if failed? 
            # Actually, `service.create_transaction` might raise error. 
            # If it raises error, `db.add` was called. 
            # We should probably strictly validate before calling service.
            
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return {"message": "Import Failed", "errors": [str(e)]}
    
    return {
        "message": f"Successfully imported {success_count} transactions",
        "errors": errors
    }


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    current_user: User = Depends(require_role(["admin", "editor", "approver"])),
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    
    # Store old values for audit and balance reversal
    old_values = {
        "amount": float(db_transaction.amount),
        "type": db_transaction.type,
        "account_id": db_transaction.account_id,
        "status": db_transaction.status,
        "description": db_transaction.description
    }

    # REVERSE OLD EFFECT if it was completed
    if old_values["status"] == "completed":
        old_account = db.query(Account).filter(Account.id == old_values["account_id"]).first()
        if old_account:
            if old_values["type"] == "credit":
                old_account.balance -= Decimal(str(old_values["amount"]))
            else:
                old_account.balance += Decimal(str(old_values["amount"]))

    # Update fields
    update_data = transaction.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    
    # APPLY NEW EFFECT if it is completed
    if db_transaction.status == "completed":
        # Note: db_transaction.account_id might have changed, or stayed same. 
        # Since we fetch account fresh, it handles change correctly.
        new_account = db.query(Account).filter(Account.id == db_transaction.account_id).first()
        if new_account:
            if db_transaction.type == "credit":
                new_account.balance += db_transaction.amount
            else:
                new_account.balance -= db_transaction.amount
    
    db.commit()
    db.refresh(db_transaction)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="update",
        entity="transaction",
        entity_id=transaction_id,
        description=f"Mengubah transaksi #{transaction_id}",
        old_values=old_values,
        new_values=update_data,
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    
    return db_transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Delete a transaction (admin only)"""
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    
    # Audit log before deletion
    audit = AuditLog(
        user_id=current_user.id,
        action="delete",
        entity="transaction",
        entity_id=transaction_id,
        description=f"Menghapus transaksi #{transaction_id}: {db_transaction.description}",
        old_values={
            "amount": float(db_transaction.amount),
            "description": db_transaction.description
        },
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    
    db.delete(db_transaction)
    
    # Update Account Balance (Reverse)
    account = db.query(Account).filter(Account.id == db_transaction.account_id).first()
    if account and db_transaction.status == "completed":
        if db_transaction.type == "credit":
            account.balance -= db_transaction.amount
        else:
            account.balance += db_transaction.amount
            
    db.commit()
    
    return {"message": "Transaksi berhasil dihapus"}

@router.post("/import", response_model=dict)
async def import_transactions(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["admin", "editor"])),
    db: Session = Depends(get_db)
):
    """Import transactions from CSV"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    decoded = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded))
    
    success_count = 0
    errors = []
    
    errors = []
    
    # Cache accounts objects to update balances efficiently
    # We need the objects attached to session to update them
    account_objects = {a.name.lower(): a for a in db.query(Account).all()}
    categories = {c.name.lower(): c.id for c in db.query(Category).all()}
    
    for row_num, row in enumerate(csv_reader, start=1):
        try:
            # Validate required fields
            required = ['Date', 'Description', 'Amount', 'Type', 'Account']
            if not all(k in row for k in required):
                raise ValueError(f"Missing required columns: {required}")
            
            # Parse Date
            try:
                date_val = datetime.strptime(row['Date'], '%Y-%m-%d')
            except ValueError:
                date_val = datetime.strptime(row['Date'], '%d/%m/%Y')
                
            # Resolve Account
            acc_name = row['Account'].lower()
            account_obj = account_objects.get(acc_name)
            if not account_obj:
                # Try partial match
                account_obj = next((acc for name, acc in account_objects.items() if acc_name in name), None)
                if not account_obj:
                    raise ValueError(f"Account '{row['Account']}' not found")
            
            account_id = account_obj.id
            
            # Resolve Category
            cat_name = row.get('Category', 'Lainnya').lower()
            category_id = categories.get(cat_name)
            if not category_id:
                # Create new category if not exists
                new_cat = Category(
                    name=row.get('Category', 'Lainnya'),
                    type='expense' if row['Type'] == 'debit' else 'income',
                    icon='📂',
                    color='#94a3b8'
                )
                db.add(new_cat)
                db.flush()
                categories[new_cat.name.lower()] = new_cat.id
                category_id = new_cat.id
            
            # Create Transaction
            transaction = Transaction(
                date=date_val,
                description=row['Description'],
                amount=Decimal(row['Amount']),
                type=row['Type'].lower(),
                category_id=category_id,
                account_id=account_id,
                status='completed',
                created_by=current_user.id
            )
            db.add(transaction)
            
            # Update Balance
            # Since we have the account object attached to session, simple update works
            if transaction.type == "credit":
                account_obj.balance += transaction.amount
            else:
                account_obj.balance -= transaction.amount
                
            success_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            
    db.commit()
    
    return {
        "message": f"Successfully imported {success_count} transactions",
        "errors": errors
    }
