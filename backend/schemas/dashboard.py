from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class KPICard(BaseModel):
    title: str
    value: Decimal
    change_percent: float
    change_type: str  # 'increase' or 'decrease'
    icon: str
    color: str


class DashboardOverview(BaseModel):
    total_revenue: KPICard
    total_expense: KPICard
    net_profit: KPICard
    cash_on_hand: KPICard
    pending_invoices: int
    overdue_invoices: int


class ChartDataPoint(BaseModel):
    label: str
    value: Decimal


class RevenueExpenseChart(BaseModel):
    labels: List[str]
    revenue: List[Decimal]
    expense: List[Decimal]


class CategoryBreakdown(BaseModel):
    category: str
    amount: Decimal
    percentage: float
    color: str


class CashFlowData(BaseModel):
    labels: List[str]
    inflow: List[Decimal]
    outflow: List[Decimal]
    net: List[Decimal]


class RecentTransaction(BaseModel):
    id: int
    date: str
    description: str
    amount: Decimal
    type: str
    category: str
    status: str


class DashboardCharts(BaseModel):
    revenue_expense: RevenueExpenseChart
    expense_by_category: List[CategoryBreakdown]
    income_by_category: List[CategoryBreakdown]
    cash_flow: CashFlowData
    recent_transactions: List[RecentTransaction]
