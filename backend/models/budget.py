from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    department = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    period = Column(String(20), nullable=False)  # e.g., "2024-01" for January 2024
    allocated_amount = Column(Numeric(15, 2), nullable=False, default=0)
    spent_amount = Column(Numeric(15, 2), nullable=False, default=0)
    
    category = relationship("Category", back_populates="budgets")
    
    @property
    def remaining(self):
        return float(self.allocated_amount) - float(self.spent_amount)
    
    @property
    def utilization_percentage(self):
        if self.allocated_amount == 0:
            return 0
        return (float(self.spent_amount) / float(self.allocated_amount)) * 100
