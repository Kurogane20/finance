from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.analytics import (
    AnalyticsResponse, HealthScore, PredictionResponse,
    AnalyticsInsight, SpendingPattern, HealthFactor
)
from utils.security import get_current_user
from utils.analytics_service import AnalyticsService
from typing import List
from datetime import datetime

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/insights", response_model=AnalyticsResponse)
async def get_analytics_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get smart analytics insights based on financial data.
    
    Returns rule-based insights that work without historical data.
    When data reaches 500+ records, ML predictions become available.
    """
    service = AnalyticsService(db)
    
    # Generate insights
    raw_insights = service.generate_insights()
    insights = [
        AnalyticsInsight(
            id=i['id'],
            type=i['type'],
            category=i['category'],
            title=i['title'],
            message=i['message'],
            severity=i['severity'],
            icon=i['icon'],
            color=i['color'],
            data=i.get('data'),
            action_url=i.get('action_url'),
            created_at=datetime.utcnow()
        ) for i in raw_insights
    ]
    
    # Calculate health score
    raw_health = service.calculate_health_score()
    health_score = HealthScore(
        score=raw_health['score'],
        grade=raw_health['grade'],
        trend=raw_health['trend'],
        factors=[
            HealthFactor(
                name=f['name'],
                score=f['score'],
                max_score=f['max_score'],
                status=f['status'],
                description=f['description']
            ) for f in raw_health['factors']
        ],
        summary=raw_health['summary']
    )
    
    # Get spending patterns
    raw_patterns = service.get_spending_patterns()
    spending_patterns = [
        SpendingPattern(
            category=p['category'],
            current_amount=p['current_amount'],
            average_amount=p['average_amount'],
            change_percent=p['change_percent'],
            trend=p['trend'],
            is_spike=p['is_spike']
        ) for p in raw_patterns
    ]
    
    return AnalyticsResponse(
        insights=insights,
        health_score=health_score,
        spending_patterns=spending_patterns,
        data_status=service.get_data_status(),
        record_count=service.get_record_count(),
        ml_ready=service.is_ml_ready()
    )


@router.get("/health-score", response_model=HealthScore)
async def get_health_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get financial health score (0-100).
    
    Calculated based on 5 factors:
    - Cash Flow (20 pts)
    - Budget Compliance (20 pts)
    - Invoice Health (20 pts)
    - Revenue Trend (20 pts)
    - Expense Control (20 pts)
    """
    service = AnalyticsService(db)
    raw_health = service.calculate_health_score()
    
    return HealthScore(
        score=raw_health['score'],
        grade=raw_health['grade'],
        trend=raw_health['trend'],
        factors=[
            HealthFactor(
                name=f['name'],
                score=f['score'],
                max_score=f['max_score'],
                status=f['status'],
                description=f['description']
            ) for f in raw_health['factors']
        ],
        summary=raw_health['summary']
    )


@router.get("/predictions", response_model=PredictionResponse)
async def get_predictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ML-based predictions.
    
    Note: This endpoint is a placeholder that will be activated
    when sufficient data (500+ records) is available.
    """
    service = AnalyticsService(db)
    record_count = service.get_record_count()
    ml_ready = service.is_ml_ready()
    
    if ml_ready:
        # TODO: Implement actual ML predictions when data is sufficient
        return PredictionResponse(
            available=True,
            message="Prediksi ML tersedia berdasarkan data historis",
            required_records=500,
            current_records=record_count,
            predictions=[
                {
                    "type": "cashflow_forecast",
                    "description": "Prediksi arus kas 30 hari ke depan",
                    "status": "coming_soon"
                },
                {
                    "type": "anomaly_detection",
                    "description": "Deteksi transaksi tidak biasa",
                    "status": "coming_soon"
                }
            ]
        )
    else:
        return PredictionResponse(
            available=False,
            message=f"Prediksi ML membutuhkan minimal 500 transaksi. Saat ini: {record_count} transaksi.",
            required_records=500,
            current_records=record_count,
            predictions=None
        )


@router.get("/spending-patterns", response_model=List[SpendingPattern])
async def get_spending_patterns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get spending patterns by category.
    
    Shows current vs average spending with trend analysis.
    """
    service = AnalyticsService(db)
    raw_patterns = service.get_spending_patterns()
    
    return [
        SpendingPattern(
            category=p['category'],
            current_amount=p['current_amount'],
            average_amount=p['average_amount'],
            change_percent=p['change_percent'],
            trend=p['trend'],
            is_spike=p['is_spike']
        ) for p in raw_patterns
    ]
