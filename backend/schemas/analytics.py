from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime


class AnalyticsInsight(BaseModel):
    """Single insight/alert item"""
    id: str
    type: str  # 'alert' | 'warning' | 'success' | 'info'
    category: str  # 'spending' | 'budget' | 'cashflow' | 'invoice' | 'revenue'
    title: str
    message: str
    severity: int  # 1-5 (1=info, 5=critical)
    icon: str
    color: str
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    created_at: datetime = datetime.utcnow()


class HealthFactor(BaseModel):
    """Individual factor contributing to health score"""
    name: str
    score: int  # 0-20
    max_score: int = 20
    status: str  # 'good' | 'warning' | 'critical'
    description: str


class HealthScore(BaseModel):
    """Overall financial health score"""
    score: int  # 0-100
    grade: str  # 'A+', 'A', 'B', 'C', 'D', 'F'
    trend: str  # 'improving' | 'stable' | 'declining'
    factors: List[HealthFactor]
    summary: str


class SpendingPattern(BaseModel):
    """Spending pattern analysis"""
    category: str
    current_amount: Decimal
    average_amount: Decimal
    change_percent: float
    trend: str  # 'up' | 'down' | 'stable'
    is_spike: bool


class CategoryTrend(BaseModel):
    """Category-wise trend data"""
    category: str
    values: List[Decimal]
    labels: List[str]
    trend_direction: str
    growth_rate: float


class AnalyticsResponse(BaseModel):
    """Main analytics response"""
    insights: List[AnalyticsInsight]
    health_score: HealthScore
    spending_patterns: List[SpendingPattern]
    data_status: str  # 'sufficient' | 'limited' | 'none'
    record_count: int
    ml_ready: bool  # True if enough data for ML


class PredictionResponse(BaseModel):
    """Placeholder for future ML predictions"""
    available: bool = False
    message: str = "Prediksi ML akan tersedia setelah data mencukupi (500+ transaksi)"
    required_records: int = 500
    current_records: int = 0
    predictions: Optional[List[Dict[str, Any]]] = None
