from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database_async import Base

class AccountType(str, enum.Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"

class Account(Base):
    __tablename__ = "accounts_coa"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    level = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey("accounts_coa.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    
    # Self-referential relationship for hierarchy
    parent = relationship("Account", remote_side=[id], back_populates="children")
    children = relationship("Account", back_populates="parent")
    
    journal_items = relationship("JournalItem", back_populates="account")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)  # Index for date queries
    description = Column(Text, nullable=False)
    reference = Column(String(100), nullable=True, index=True)  # Index for reference lookups
    posted = Column(Boolean, default=False, index=True)  # Index for filtering posted/unposted
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("JournalItem", back_populates="entry", cascade="all, delete-orphan")

class JournalItem(Base):
    __tablename__ = "journal_items"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False, index=True)  # Index for joins
    account_id = Column(Integer, ForeignKey("accounts_coa.id"), nullable=False, index=True)  # Index for account queries

    # Standard Double Entry: Debit & Credit columns
    # Alternatively, use signed amount, but separate columns are clearer for many users
    debit = Column(Numeric(20, 2), default=0, nullable=False)
    credit = Column(Numeric(20, 2), default=0, nullable=False)

    entry = relationship("JournalEntry", back_populates="items")
    account = relationship("Account", back_populates="journal_items")
