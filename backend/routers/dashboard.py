from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from database import get_db
from models.user import User
from models.transaction import Transaction, Category
from models.account import Account
from models.invoice import Invoice
from schemas.dashboard import (
    DashboardOverview, DashboardCharts, KPICard,
    RevenueExpenseChart, CategoryBreakdown, CashFlowData, RecentTransaction
)
from utils.security import get_current_user
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    period: str = Query("month", description="Filter: today, week, month, year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard KPI overview"""
    
    # Calculate date range
    now = datetime.utcnow()
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        prev_start = start_date - timedelta(days=1)
        prev_end = start_date
    elif period == "week":
        start_date = now - timedelta(days=7)
        prev_start = start_date - timedelta(days=7)
        prev_end = start_date
    elif period == "year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        prev_start = start_date.replace(year=start_date.year - 1)
        prev_end = start_date
    else:  # month (default)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 1:
            prev_start = start_date.replace(year=start_date.year - 1, month=12)
        else:
            prev_start = start_date.replace(month=start_date.month - 1)
        prev_end = start_date
    
    # Current period calculations
    current_revenue = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.type == "credit",
        Transaction.date >= start_date,
        Transaction.status == "completed"
    ).scalar() or Decimal("0")
    
    current_expense = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.type == "debit",
        Transaction.date >= start_date,
        Transaction.status == "completed"
    ).scalar() or Decimal("0")
    
    # Previous period calculations
    prev_revenue = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.type == "credit",
        Transaction.date >= prev_start,
        Transaction.date < prev_end,
        Transaction.status == "completed"
    ).scalar() or Decimal("0")
    
    prev_expense = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.type == "debit",
        Transaction.date >= prev_start,
        Transaction.date < prev_end,
        Transaction.status == "completed"
    ).scalar() or Decimal("0")
    
    # Calculate changes
    def calc_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return float((current - previous) / previous * 100)
    
    revenue_change = calc_change(current_revenue, prev_revenue)
    expense_change = calc_change(current_expense, prev_expense)
    
    net_profit = current_revenue - current_expense
    prev_net_profit = prev_revenue - prev_expense
    profit_change = calc_change(net_profit, prev_net_profit)
    
    # Cash on hand (total balance across all accounts)
    cash_on_hand = db.query(func.coalesce(func.sum(Account.balance), 0)).filter(
        Account.is_active == True
    ).scalar() or Decimal("0")
    
    # Invoice counts
    pending_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.status.in_(["sent", "viewed", "draft"])
    ).scalar() or 0
    
    overdue_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.status == "overdue"
    ).scalar() or 0
    
    return DashboardOverview(
        total_revenue=KPICard(
            title="Total Pendapatan",
            value=current_revenue,
            change_percent=round(revenue_change, 1),
            change_type="increase" if revenue_change >= 0 else "decrease",
            icon="💰",
            color="#10b981"
        ),
        total_expense=KPICard(
            title="Total Pengeluaran",
            value=current_expense,
            change_percent=round(abs(expense_change), 1),
            change_type="increase" if expense_change >= 0 else "decrease",
            icon="💸",
            color="#ef4444"
        ),
        net_profit=KPICard(
            title="Laba Bersih",
            value=net_profit,
            change_percent=round(profit_change, 1),
            change_type="increase" if profit_change >= 0 else "decrease",
            icon="📈",
            color="#6366f1"
        ),
        cash_on_hand=KPICard(
            title="Kas Tersedia",
            value=cash_on_hand,
            change_percent=0,
            change_type="increase",
            icon="🏦",
            color="#8b5cf6"
        ),
        pending_invoices=pending_invoices,
        overdue_invoices=overdue_invoices
    )


@router.get("/charts", response_model=DashboardCharts)
async def get_dashboard_charts(
    period: str = Query("month", description="Filter: week, month, quarter, year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard chart data"""
    
    now = datetime.utcnow()
    
    # Determine labels and date ranges based on period
    if period == "week":
        labels = [(now - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
        date_ranges = [(now - timedelta(days=i)).date() for i in range(6, -1, -1)]
    elif period == "quarter":
        labels = [(now - timedelta(days=i*7)).strftime("%d %b") for i in range(12, -1, -1)]
        date_ranges = None  # Will use weekly aggregation
    elif period == "year":
        labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        date_ranges = None  # Will use monthly aggregation
    else:  # month (default)
        days_in_month = 30
        labels = [(now - timedelta(days=i)).strftime("%d") for i in range(days_in_month-1, -1, -1)]
        date_ranges = [(now - timedelta(days=i)).date() for i in range(days_in_month-1, -1, -1)]
    
    # Get revenue and expense data
    revenues = []
    expenses = []
    
    if date_ranges:
        for date in date_ranges:
            rev = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.type == "credit",
                func.date(Transaction.date) == date,
                Transaction.status == "completed"
            ).scalar() or Decimal("0")
            revenues.append(rev)
            
            exp = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.type == "debit",
                func.date(Transaction.date) == date,
                Transaction.status == "completed"
            ).scalar() or Decimal("0")
            expenses.append(exp)
    else:
        # Monthly aggregation for year view
        for month in range(1, 13):
            rev = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.type == "credit",
                extract('month', Transaction.date) == month,
                extract('year', Transaction.date) == now.year,
                Transaction.status == "completed"
            ).scalar() or Decimal("0")
            revenues.append(rev)
            
            exp = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.type == "debit",
                extract('month', Transaction.date) == month,
                extract('year', Transaction.date) == now.year,
                Transaction.status == "completed"
            ).scalar() or Decimal("0")
            expenses.append(exp)
    
    # Category breakdown
    expense_categories = db.query(
        Category.name,
        Category.color,
        func.coalesce(func.sum(Transaction.amount), 0).label('total')
    ).join(Transaction).filter(
        Transaction.type == "debit",
        Transaction.status == "completed"
    ).group_by(Category.id).all()
    
    total_expense = sum([float(c.total) for c in expense_categories]) or 1
    expense_breakdown = [
        CategoryBreakdown(
            category=c.name,
            amount=Decimal(str(c.total)),
            percentage=round(float(c.total) / total_expense * 100, 1),
            color=c.color
        ) for c in expense_categories
    ]
    
    income_categories = db.query(
        Category.name,
        Category.color,
        func.coalesce(func.sum(Transaction.amount), 0).label('total')
    ).join(Transaction).filter(
        Transaction.type == "credit",
        Transaction.status == "completed"
    ).group_by(Category.id).all()
    
    total_income = sum([float(c.total) for c in income_categories]) or 1
    income_breakdown = [
        CategoryBreakdown(
            category=c.name,
            amount=Decimal(str(c.total)),
            percentage=round(float(c.total) / total_income * 100, 1),
            color=c.color
        ) for c in income_categories
    ]
    
    # Cash flow
    inflows = revenues
    outflows = expenses
    net_flow = [Decimal(str(float(r) - float(e))) for r, e in zip(revenues, expenses)]
    
    # Recent transactions
    recent = db.query(Transaction).order_by(Transaction.date.desc()).limit(10).all()
    recent_transactions = [
        RecentTransaction(
            id=t.id,
            date=t.date.strftime("%Y-%m-%d"),
            description=t.description or "Transaksi",
            amount=t.amount,
            type=t.type,
            category=t.category.name if t.category else "Lainnya",
            status=t.status
        ) for t in recent
    ]
    
    return DashboardCharts(
        revenue_expense=RevenueExpenseChart(
            labels=labels,
            revenue=revenues,
            expense=expenses
        ),
        expense_by_category=expense_breakdown,
        income_by_category=income_breakdown,
        cash_flow=CashFlowData(
            labels=labels,
            inflow=inflows,
            outflow=outflows,
            net=net_flow
        ),
        recent_transactions=recent_transactions
    )
