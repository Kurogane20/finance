from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class AccountBase(BaseModel):
    name: str
    type: str
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    currency: str = "IDR"


class AccountCreate(AccountBase):
    balance: Decimal = Decimal("0")


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    balance: Optional[Decimal] = None
    is_active: Optional[bool] = None


class AccountResponse(AccountBase):
    id: int
    balance: Decimal
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    department: str
    category_id: Optional[int] = None
    period: str
    allocated_amount: Decimal


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    department: Optional[str] = None
    category_id: Optional[int] = None
    period: Optional[str] = None
    allocated_amount: Optional[Decimal] = None
    spent_amount: Optional[Decimal] = None


class BudgetResponse(BudgetBase):
    id: int
    spent_amount: Decimal
    
    class Config:
        from_attributes = True
