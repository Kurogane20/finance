"""
Analytics Service - Rule-Based Analysis Engine

This service provides rule-based financial analytics that work without historical data.
Designed to be ML-ready for future evolution when sufficient data is available.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
import uuid

from models.transaction import Transaction, Category
from models.budget import Budget
from models.invoice import Invoice
from models.account import Account


class AnalyticsService:
    """
    Rule-based analytics service.
    
    Evolution path:
    - Phase 1 (current): Pure rule-based analysis
    - Phase 2 (100+ records): Simple statistical predictions
    - Phase 3 (500+ records): ML anomaly detection
    - Phase 4 (2000+ records): Full ML forecasting
    """
    
    # Thresholds for rule-based detection
    SPENDING_SPIKE_THRESHOLD = 1.20  # 20% above average
    BUDGET_WARNING_THRESHOLD = 0.80  # 80% budget used
    BUDGET_CRITICAL_THRESHOLD = 1.00  # 100% budget used
    AGING_WARNING_DAYS = 30
    AGING_CRITICAL_DAYS = 60
    ML_READY_THRESHOLD = 500
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_record_count(self) -> int:
        """Get total transaction count"""
        return self.db.query(func.count(Transaction.id)).scalar() or 0
    
    def is_ml_ready(self) -> bool:
        """Check if enough data for ML"""
        return self.get_record_count() >= self.ML_READY_THRESHOLD
    
    def get_data_status(self) -> str:
        """Get data sufficiency status"""
        count = self.get_record_count()
        if count == 0:
            return "none"
        elif count < 100:
            return "limited"
        else:
            return "sufficient"
    
    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate all insights based on current data"""
        insights = []
        
        # Always generate these insights (work with any data level)
        insights.extend(self._analyze_spending_patterns())
        insights.extend(self._analyze_budget_status())
        insights.extend(self._analyze_cashflow_trend())
        insights.extend(self._analyze_invoice_aging())
        insights.extend(self._analyze_revenue_growth())
        
        # Sort by severity (highest first)
        insights.sort(key=lambda x: x['severity'], reverse=True)
        
        return insights[:10]  # Return top 10 insights
    
    def _analyze_spending_patterns(self) -> List[Dict[str, Any]]:
        """Detect unusual spending patterns"""
        insights = []
        now = datetime.utcnow()
        
        # Get spending by category for last 7 days vs last 30 days average
        categories = self.db.query(Category).filter(Category.type == 'expense').all()
        
        for category in categories:
            # Last 7 days spending
            recent_spending = self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            ).filter(
                Transaction.category_id == category.id,
                Transaction.type == 'debit',
                Transaction.date >= now - timedelta(days=7),
                Transaction.status == 'completed'
            ).scalar() or Decimal('0')
            
            # Average weekly spending (from last 30 days)
            monthly_spending = self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            ).filter(
                Transaction.category_id == category.id,
                Transaction.type == 'debit',
                Transaction.date >= now - timedelta(days=30),
                Transaction.status == 'completed'
            ).scalar() or Decimal('0')
            
            avg_weekly = monthly_spending / 4 if monthly_spending > 0 else Decimal('0')
            
            if avg_weekly > 0 and recent_spending > avg_weekly * Decimal(str(self.SPENDING_SPIKE_THRESHOLD)):
                change_pct = float((recent_spending - avg_weekly) / avg_weekly * 100)
                insights.append({
                    'id': f'spending_{category.id}_{uuid.uuid4().hex[:8]}',
                    'type': 'warning',
                    'category': 'spending',
                    'title': f'Peningkatan Pengeluaran {category.name}',
                    'message': f'Pengeluaran {category.name} naik {change_pct:.1f}% dari rata-rata minggu sebelumnya',
                    'severity': 3 if change_pct < 50 else 4,
                    'icon': '📈',
                    'color': '#f59e0b',
                    'data': {
                        'category': category.name,
                        'current': float(recent_spending),
                        'average': float(avg_weekly),
                        'change_percent': change_pct
                    },
                    'action_url': '/transactions'
                })
        
        return insights
    
    def _analyze_budget_status(self) -> List[Dict[str, Any]]:
        """Analyze budget vs actual spending"""
        insights = []
        now = datetime.utcnow()
        current_month = now.month
        current_year = now.year
        
        budgets = self.db.query(Budget).filter(
            Budget.month == current_month,
            Budget.year == current_year,
            Budget.is_active == True
        ).all()
        
        for budget in budgets:
            # Get actual spending for this category
            actual = self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            ).filter(
                Transaction.category_id == budget.category_id,
                Transaction.type == 'debit',
                extract('month', Transaction.date) == current_month,
                extract('year', Transaction.date) == current_year,
                Transaction.status == 'completed'
            ).scalar() or Decimal('0')
            
            if budget.amount > 0:
                usage_pct = float(actual / budget.amount)
                category_name = budget.category.name if budget.category else 'Lainnya'
                
                if usage_pct >= self.BUDGET_CRITICAL_THRESHOLD:
                    insights.append({
                        'id': f'budget_critical_{budget.id}',
                        'type': 'alert',
                        'category': 'budget',
                        'title': f'⚠️ Budget {category_name} Terlampaui!',
                        'message': f'Pengeluaran sudah {usage_pct*100:.1f}% dari budget bulan ini',
                        'severity': 5,
                        'icon': '🚨',
                        'color': '#ef4444',
                        'data': {
                            'category': category_name,
                            'budget': float(budget.amount),
                            'actual': float(actual),
                            'usage_percent': usage_pct * 100
                        },
                        'action_url': '/budgets'
                    })
                elif usage_pct >= self.BUDGET_WARNING_THRESHOLD:
                    insights.append({
                        'id': f'budget_warning_{budget.id}',
                        'type': 'warning',
                        'category': 'budget',
                        'title': f'Budget {category_name} Hampir Habis',
                        'message': f'Sudah terpakai {usage_pct*100:.1f}% dari budget bulan ini',
                        'severity': 3,
                        'icon': '⚡',
                        'color': '#f59e0b',
                        'data': {
                            'category': category_name,
                            'budget': float(budget.amount),
                            'actual': float(actual),
                            'remaining': float(budget.amount - actual),
                            'usage_percent': usage_pct * 100
                        },
                        'action_url': '/budgets'
                    })
        
        return insights
    
    def _analyze_cashflow_trend(self) -> List[Dict[str, Any]]:
        """Analyze cash flow trends"""
        insights = []
        now = datetime.utcnow()
        
        # Calculate net cash flow for last 7 days vs previous 7 days
        def get_net_cashflow(start_date, end_date):
            income = self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            ).filter(
                Transaction.type == 'credit',
                Transaction.date >= start_date,
                Transaction.date < end_date,
                Transaction.status == 'completed'
            ).scalar() or Decimal('0')
            
            expense = self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            ).filter(
                Transaction.type == 'debit',
                Transaction.date >= start_date,
                Transaction.date < end_date,
                Transaction.status == 'completed'
            ).scalar() or Decimal('0')
            
            return income - expense
        
        current_week_cf = get_net_cashflow(now - timedelta(days=7), now)
        previous_week_cf = get_net_cashflow(now - timedelta(days=14), now - timedelta(days=7))
        
        if current_week_cf < 0:
            insights.append({
                'id': f'cashflow_negative_{uuid.uuid4().hex[:8]}',
                'type': 'warning',
                'category': 'cashflow',
                'title': 'Cash Flow Negatif',
                'message': f'Pengeluaran melebihi pendapatan sebesar Rp {abs(float(current_week_cf)):,.0f} minggu ini',
                'severity': 4,
                'icon': '📉',
                'color': '#ef4444',
                'data': {
                    'current_net': float(current_week_cf),
                    'previous_net': float(previous_week_cf)
                },
                'action_url': '/reports'
            })
        elif current_week_cf > previous_week_cf and previous_week_cf > 0:
            growth = float((current_week_cf - previous_week_cf) / previous_week_cf * 100) if previous_week_cf > 0 else 0
            if growth > 10:
                insights.append({
                    'id': f'cashflow_positive_{uuid.uuid4().hex[:8]}',
                    'type': 'success',
                    'category': 'cashflow',
                    'title': 'Cash Flow Membaik! 🎉',
                    'message': f'Net cash flow meningkat {growth:.1f}% dari minggu lalu',
                    'severity': 1,
                    'icon': '📈',
                    'color': '#10b981',
                    'data': {
                        'current_net': float(current_week_cf),
                        'previous_net': float(previous_week_cf),
                        'growth_percent': growth
                    }
                })
        
        return insights
    
    def _analyze_invoice_aging(self) -> List[Dict[str, Any]]:
        """Analyze invoice aging for AR/AP"""
        insights = []
        today = date.today()
        
        # Check overdue invoices
        overdue_invoices = self.db.query(Invoice).filter(
            Invoice.status == 'overdue',
            Invoice.due_date < today
        ).all()
        
        critical_overdue = []
        warning_overdue = []
        
        for invoice in overdue_invoices:
            days_overdue = (today - invoice.due_date).days
            if days_overdue >= self.AGING_CRITICAL_DAYS:
                critical_overdue.append(invoice)
            elif days_overdue >= self.AGING_WARNING_DAYS:
                warning_overdue.append(invoice)
        
        if critical_overdue:
            total_critical = sum(float(inv.total_amount) for inv in critical_overdue)
            insights.append({
                'id': f'aging_critical_{uuid.uuid4().hex[:8]}',
                'type': 'alert',
                'category': 'invoice',
                'title': f'🚨 {len(critical_overdue)} Invoice Kritis!',
                'message': f'Invoice senilai Rp {total_critical:,.0f} sudah overdue >60 hari',
                'severity': 5,
                'icon': '⏰',
                'color': '#ef4444',
                'data': {
                    'count': len(critical_overdue),
                    'total_amount': total_critical
                },
                'action_url': '/accounts'
            })
        
        if warning_overdue:
            total_warning = sum(float(inv.total_amount) for inv in warning_overdue)
            insights.append({
                'id': f'aging_warning_{uuid.uuid4().hex[:8]}',
                'type': 'warning',
                'category': 'invoice',
                'title': f'{len(warning_overdue)} Invoice Perlu Perhatian',
                'message': f'Invoice senilai Rp {total_warning:,.0f} sudah overdue 30-60 hari',
                'severity': 3,
                'icon': '⚠️',
                'color': '#f59e0b',
                'data': {
                    'count': len(warning_overdue),
                    'total_amount': total_warning
                },
                'action_url': '/accounts'
            })
        
        return insights
    
    def _analyze_revenue_growth(self) -> List[Dict[str, Any]]:
        """Analyze revenue trends"""
        insights = []
        now = datetime.utcnow()
        
        # Compare this month vs last month
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 1:
            prev_month_start = current_month_start.replace(year=now.year-1, month=12)
        else:
            prev_month_start = current_month_start.replace(month=now.month-1)
        
        current_revenue = self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.type == 'credit',
            Transaction.date >= current_month_start,
            Transaction.status == 'completed'
        ).scalar() or Decimal('0')
        
        prev_revenue = self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.type == 'credit',
            Transaction.date >= prev_month_start,
            Transaction.date < current_month_start,
            Transaction.status == 'completed'
        ).scalar() or Decimal('0')
        
        if prev_revenue > 0:
            growth = float((current_revenue - prev_revenue) / prev_revenue * 100)
            
            if growth > 20:
                insights.append({
                    'id': f'revenue_growth_{uuid.uuid4().hex[:8]}',
                    'type': 'success',
                    'category': 'revenue',
                    'title': 'Pendapatan Meningkat! 🚀',
                    'message': f'Pendapatan bulan ini naik {growth:.1f}% dari bulan lalu',
                    'severity': 1,
                    'icon': '💰',
                    'color': '#10b981',
                    'data': {
                        'current': float(current_revenue),
                        'previous': float(prev_revenue),
                        'growth_percent': growth
                    }
                })
            elif growth < -20:
                insights.append({
                    'id': f'revenue_decline_{uuid.uuid4().hex[:8]}',
                    'type': 'warning',
                    'category': 'revenue',
                    'title': 'Pendapatan Menurun',
                    'message': f'Pendapatan bulan ini turun {abs(growth):.1f}% dari bulan lalu',
                    'severity': 3,
                    'icon': '📉',
                    'color': '#f59e0b',
                    'data': {
                        'current': float(current_revenue),
                        'previous': float(prev_revenue),
                        'growth_percent': growth
                    }
                })
        
        return insights
    
    def calculate_health_score(self) -> Dict[str, Any]:
        """Calculate overall financial health score (0-100)"""
        factors = []
        now = datetime.utcnow()
        
        # Factor 1: Cash Flow (0-20)
        current_week_income = self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.type == 'credit',
            Transaction.date >= now - timedelta(days=7),
            Transaction.status == 'completed'
        ).scalar() or Decimal('0')
        
        current_week_expense = self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.type == 'debit',
            Transaction.date >= now - timedelta(days=7),
            Transaction.status == 'completed'
        ).scalar() or Decimal('0')
        
        cf_score = 20 if current_week_income >= current_week_expense else max(0, int(20 * float(current_week_income / current_week_expense))) if current_week_expense > 0 else 20
        factors.append({
            'name': 'Cash Flow',
            'score': cf_score,
            'max_score': 20,
            'status': 'good' if cf_score >= 15 else 'warning' if cf_score >= 10 else 'critical',
            'description': 'Arus kas masuk vs keluar minggu ini'
        })
        
        # Factor 2: Budget Compliance (0-20)
        current_month = now.month
        current_year = now.year
        budgets = self.db.query(Budget).filter(
            Budget.month == current_month,
            Budget.year == current_year,
            Budget.is_active == True
        ).all()
        
        if budgets:
            compliant_count = 0
            for budget in budgets:
                actual = self.db.query(
                    func.coalesce(func.sum(Transaction.amount), 0)
                ).filter(
                    Transaction.category_id == budget.category_id,
                    Transaction.type == 'debit',
                    extract('month', Transaction.date) == current_month,
                    extract('year', Transaction.date) == current_year,
                    Transaction.status == 'completed'
                ).scalar() or Decimal('0')
                
                if actual <= budget.amount:
                    compliant_count += 1
            
            budget_score = int(20 * compliant_count / len(budgets))
        else:
            budget_score = 15  # Neutral if no budgets set
        
        factors.append({
            'name': 'Budget Compliance',
            'score': budget_score,
            'max_score': 20,
            'status': 'good' if budget_score >= 15 else 'warning' if budget_score >= 10 else 'critical',
            'description': 'Kepatuhan terhadap budget yang ditetapkan'
        })
        
        # Factor 3: Invoice Health (0-20)
        total_invoices = self.db.query(func.count(Invoice.id)).scalar() or 0
        overdue_invoices = self.db.query(func.count(Invoice.id)).filter(
            Invoice.status == 'overdue'
        ).scalar() or 0
        
        if total_invoices > 0:
            invoice_score = int(20 * (1 - overdue_invoices / total_invoices))
        else:
            invoice_score = 20  # Perfect score if no invoices
        
        factors.append({
            'name': 'Invoice Health',
            'score': invoice_score,
            'max_score': 20,
            'status': 'good' if invoice_score >= 15 else 'warning' if invoice_score >= 10 else 'critical',
            'description': 'Rasio invoice yang terbayar tepat waktu'
        })
        
        # Factor 4: Revenue Trend (0-20)
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0)
        if now.month == 1:
            prev_month_start = current_month_start.replace(year=now.year-1, month=12)
        else:
            prev_month_start = current_month_start.replace(month=now.month-1)
        
        current_revenue = self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.type == 'credit',
            Transaction.date >= current_month_start,
            Transaction.status == 'completed'
        ).scalar() or Decimal('0')
        
        prev_revenue = self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.type == 'credit',
            Transaction.date >= prev_month_start,
            Transaction.date < current_month_start,
            Transaction.status == 'completed'
        ).scalar() or Decimal('0')
        
        if prev_revenue > 0:
            growth = float((current_revenue - prev_revenue) / prev_revenue)
            revenue_score = min(20, max(0, int(10 + growth * 20)))
        else:
            revenue_score = 10  # Neutral
        
        factors.append({
            'name': 'Revenue Trend',
            'score': revenue_score,
            'max_score': 20,
            'status': 'good' if revenue_score >= 15 else 'warning' if revenue_score >= 10 else 'critical',
            'description': 'Tren pertumbuhan pendapatan'
        })
        
        # Factor 5: Expense Control (0-20)
        current_expense = self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.type == 'debit',
            Transaction.date >= current_month_start,
            Transaction.status == 'completed'
        ).scalar() or Decimal('0')
        
        prev_expense = self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.type == 'debit',
            Transaction.date >= prev_month_start,
            Transaction.date < current_month_start,
            Transaction.status == 'completed'
        ).scalar() or Decimal('0')
        
        if prev_expense > 0:
            expense_change = float((current_expense - prev_expense) / prev_expense)
            expense_score = min(20, max(0, int(15 - expense_change * 15)))
        else:
            expense_score = 15  # Neutral
        
        factors.append({
            'name': 'Expense Control',
            'score': expense_score,
            'max_score': 20,
            'status': 'good' if expense_score >= 15 else 'warning' if expense_score >= 10 else 'critical',
            'description': 'Kemampuan mengendalikan pengeluaran'
        })
        
        # Calculate total score
        total_score = sum(f['score'] for f in factors)
        
        # Determine grade
        if total_score >= 90:
            grade = 'A+'
        elif total_score >= 80:
            grade = 'A'
        elif total_score >= 70:
            grade = 'B'
        elif total_score >= 60:
            grade = 'C'
        elif total_score >= 50:
            grade = 'D'
        else:
            grade = 'F'
        
        # Determine trend (simplified - would need historical scores for real trend)
        if total_score >= 70:
            trend = 'stable'
        elif cf_score >= 15 and revenue_score >= 10:
            trend = 'improving'
        else:
            trend = 'declining'
        
        # Generate summary
        if total_score >= 80:
            summary = 'Kesehatan keuangan sangat baik! Pertahankan kondisi ini.'
        elif total_score >= 60:
            summary = 'Kesehatan keuangan cukup baik, ada beberapa area yang perlu perhatian.'
        elif total_score >= 40:
            summary = 'Perlu perbaikan di beberapa area keuangan.'
        else:
            summary = 'Kondisi keuangan memerlukan perhatian serius.'
        
        return {
            'score': total_score,
            'grade': grade,
            'trend': trend,
            'factors': factors,
            'summary': summary
        }
    
    def get_spending_patterns(self) -> List[Dict[str, Any]]:
        """Get spending patterns by category"""
        patterns = []
        now = datetime.utcnow()
        
        categories = self.db.query(Category).filter(Category.type == 'expense').all()
        
        for category in categories:
            # Current week
            current = self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            ).filter(
                Transaction.category_id == category.id,
                Transaction.type == 'debit',
                Transaction.date >= now - timedelta(days=7),
                Transaction.status == 'completed'
            ).scalar() or Decimal('0')
            
            # Last 4 weeks average
            monthly = self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            ).filter(
                Transaction.category_id == category.id,
                Transaction.type == 'debit',
                Transaction.date >= now - timedelta(days=28),
                Transaction.status == 'completed'
            ).scalar() or Decimal('0')
            
            average = monthly / 4 if monthly > 0 else Decimal('0')
            
            if average > 0:
                change_pct = float((current - average) / average * 100)
            else:
                change_pct = 100.0 if current > 0 else 0.0
            
            patterns.append({
                'category': category.name,
                'current_amount': float(current),
                'average_amount': float(average),
                'change_percent': round(change_pct, 1),
                'trend': 'up' if change_pct > 10 else 'down' if change_pct < -10 else 'stable',
                'is_spike': change_pct > 20
            })
        
        # Sort by current amount
        patterns.sort(key=lambda x: x['current_amount'], reverse=True)
        
        return patterns
