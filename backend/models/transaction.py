from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # 'income' or 'expense'
    icon = Column(String(50), default="📁")
    color = Column(String(20), default="#6366f1")
    
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    type = Column(String(20), nullable=False)  # 'credit' or 'debit'
    amount = Column(Numeric(15, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    status = Column(String(20), default="completed")  # pending, completed, cancelled
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    category = relationship("Category", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    created_by_user = relationship("User", back_populates="transactions")
