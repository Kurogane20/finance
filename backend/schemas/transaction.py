from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CategoryBase(BaseModel):
    name: str
    type: str
    icon: str = "📁"
    color: str = "#6366f1"


class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    date: datetime
    type: str  # credit or debit
    amount: Decimal
    category_id: Optional[int] = None
    account_id: int
    description: Optional[str] = None
    reference: Optional[str] = None
    status: str = "completed"


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    date: Optional[datetime] = None
    type: Optional[str] = None
    amount: Optional[Decimal] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    status: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    created_by: int
    created_at: datetime
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True
