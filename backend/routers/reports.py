from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from database import get_db
from models.user import User
from models.transaction import Transaction, Category
from models.account import Account
from models.invoice import Invoice
from utils.security import get_current_user
from datetime import datetime, date
from io import StringIO, BytesIO
import csv

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/profit-loss")
async def get_profit_loss_report(
    start_date: date = Query(None),
    end_date: date = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate Profit & Loss report"""
    if start_date is None:
        start_date = date(datetime.now().year, 1, 1)
    if end_date is None:
        end_date = date.today()
    
    # Get income by category
    income_data = db.query(
        Category.name,
        func.coalesce(func.sum(Transaction.amount), 0).label('total')
    ).join(Transaction).filter(
        Transaction.type == "credit",
        Transaction.status == "completed",
        func.date(Transaction.date) >= start_date,
        func.date(Transaction.date) <= end_date
    ).group_by(Category.id).all()
    
    # Get expenses by category
    expense_data = db.query(
        Category.name,
        func.coalesce(func.sum(Transaction.amount), 0).label('total')
    ).join(Transaction).filter(
        Transaction.type == "debit",
        Transaction.status == "completed",
        func.date(Transaction.date) >= start_date,
        func.date(Transaction.date) <= end_date
    ).group_by(Category.id).all()
    
    total_income = sum(float(i.total) for i in income_data)
    total_expense = sum(float(e.total) for e in expense_data)
    net_profit = total_income - total_expense
    
    return {
        "report_type": "Profit & Loss",
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "income": {
            "items": [{"category": i.name, "amount": float(i.total)} for i in income_data],
            "total": total_income
        },
        "expenses": {
            "items": [{"category": e.name, "amount": float(e.total)} for e in expense_data],
            "total": total_expense
        },
        "net_profit": net_profit,
        "profit_margin": round((net_profit / total_income * 100) if total_income > 0 else 0, 2),
        "generated_at": datetime.now().isoformat()
    }


@router.get("/cash-flow")
async def get_cash_flow_report(
    year: int = Query(None),
    month: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate Cash Flow report"""
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    # Opening balance (sum of all accounts at start of period)
    accounts = db.query(Account).filter(Account.is_active == True).all()
    
    # Cash inflows for the month
    inflows = db.query(
        Category.name,
        func.coalesce(func.sum(Transaction.amount), 0).label('total')
    ).join(Transaction).filter(
        Transaction.type == "credit",
        Transaction.status == "completed",
        extract('year', Transaction.date) == year,
        extract('month', Transaction.date) == month
    ).group_by(Category.id).all()
    
    # Cash outflows for the month
    outflows = db.query(
        Category.name,
        func.coalesce(func.sum(Transaction.amount), 0).label('total')
    ).join(Transaction).filter(
        Transaction.type == "debit",
        Transaction.status == "completed",
        extract('year', Transaction.date) == year,
        extract('month', Transaction.date) == month
    ).group_by(Category.id).all()
    
    total_inflow = sum(float(i.total) for i in inflows)
    total_outflow = sum(float(o.total) for o in outflows)
    net_cash_flow = total_inflow - total_outflow
    current_balance = sum(float(a.balance) for a in accounts)
    
    return {
        "report_type": "Cash Flow Statement",
        "period": f"{year}-{month:02d}",
        "inflows": {
            "items": [{"source": i.name, "amount": float(i.total)} for i in inflows],
            "total": total_inflow
        },
        "outflows": {
            "items": [{"destination": o.name, "amount": float(o.total)} for o in outflows],
            "total": total_outflow
        },
        "net_cash_flow": net_cash_flow,
        "current_balance": current_balance,
        "generated_at": datetime.now().isoformat()
    }


@router.get("/balance-sheet")
async def get_balance_sheet(
    as_of_date: date = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate Balance Sheet report"""
    if as_of_date is None:
        as_of_date = date.today()
    
    # Assets (all bank accounts and cash)
    accounts = db.query(Account).filter(Account.is_active == True).all()
    assets = [{"name": a.name, "type": a.type, "balance": float(a.balance)} for a in accounts]
    total_assets = sum(a["balance"] for a in assets)
    
    # Liabilities (payable invoices)
    payables = db.query(func.coalesce(func.sum(Invoice.total_amount), 0)).filter(
        Invoice.type == "payable",
        Invoice.status.in_(["sent", "viewed", "overdue"])
    ).scalar() or 0
    
    # Receivables
    receivables = db.query(func.coalesce(func.sum(Invoice.total_amount), 0)).filter(
        Invoice.type == "receivable",
        Invoice.status.in_(["sent", "viewed", "overdue"])
    ).scalar() or 0
    
    return {
        "report_type": "Balance Sheet",
        "as_of_date": as_of_date.isoformat(),
        "assets": {
            "current_assets": {
                "cash_and_bank": assets,
                "accounts_receivable": float(receivables)
            },
            "total": total_assets + float(receivables)
        },
        "liabilities": {
            "accounts_payable": float(payables),
            "total": float(payables)
        },
        "equity": total_assets + float(receivables) - float(payables),
        "generated_at": datetime.now().isoformat()
    }


@router.get("/export/transactions")
async def export_transactions_csv(
    start_date: date = Query(None),
    end_date: date = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export transactions to CSV"""
    query = db.query(Transaction)
    
    if start_date:
        query = query.filter(func.date(Transaction.date) >= start_date)
    if end_date:
        query = query.filter(func.date(Transaction.date) <= end_date)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Tanggal", "Tipe", "Jumlah", "Kategori", "Deskripsi", "Status"])
    
    for t in transactions:
        writer.writerow([
            t.id,
            t.date.strftime("%Y-%m-%d"),
            t.type,
            float(t.amount),
            t.category.name if t.category else "",
            t.description or "",
            t.status
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=transactions_{date.today()}.csv"}
    )
