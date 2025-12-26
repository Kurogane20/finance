from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    type = Column(String(20), nullable=False)  # 'receivable' or 'payable'
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    status = Column(String(20), default="draft")  # draft, sent, viewed, paid, overdue, cancelled
    issue_date = Column(Date, default=datetime.utcnow().date)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @property
    def days_overdue(self):
        if self.status != 'overdue':
            return 0
        from datetime import date
        return (date.today() - self.due_date).days
