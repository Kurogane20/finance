from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from models.accounting import AccountType

# Account Schemas
class AccountBase(BaseModel):
    code: str
    name: str
    type: AccountType
    level: int = 1
    parent_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True

class AccountCreate(AccountBase):
    pass

class AccountRead(AccountBase):
    id: int
    
    class Config:
        from_attributes = True

# Journal Entry Schemas
class JournalItemBase(BaseModel):
    account_id: int
    debit: Decimal = Field(default=0, ge=0)
    credit: Decimal = Field(default=0, ge=0)

    @validator('credit')
    def check_non_negative_credit(cls, v):
        if v < 0:
            raise ValueError('Credit must be non-negative')
        return v

    @validator('debit')
    def check_non_negative_debit(cls, v):
        if v < 0:
            raise ValueError('Debit must be non-negative')
        return v

    @validator('credit')
    def validate_debit_or_credit(cls, v, values):
        """Ensure that each item has either debit OR credit, not both"""
        if 'debit' in values and values['debit'] > 0 and v > 0:
            raise ValueError('A journal item cannot have both debit and credit amounts. Please use either debit or credit.')
        if 'debit' in values and values['debit'] == 0 and v == 0:
            raise ValueError('A journal item must have either a debit or credit amount (not both zero)')
        return v

class JournalItemCreate(JournalItemBase):
    pass

class JournalItemRead(JournalItemBase):
    id: int
    journal_entry_id: int
    account_name: Optional[str] = None # Helper for display

    class Config:
        from_attributes = True

class JournalEntryBase(BaseModel):
    date: datetime
    description: str
    reference: Optional[str] = None
    posted: bool = False

class JournalEntryCreate(JournalEntryBase):
    items: List[JournalItemCreate]

    @validator('items')
    def validate_balance(cls, items):
        total_debit = sum(item.debit for item in items)
        total_credit = sum(item.credit for item in items)
        
        # Allow small floating point differences if needed, but Decimal should be exact
        if total_debit != total_credit:
            raise ValueError(f'Journal Entry is not balanced! Total Debit: {total_debit}, Total Credit: {total_credit}')
        
        if total_debit == 0 and total_credit == 0:
             raise ValueError('Journal Entry must have non-zero value')

        return items

class JournalEntryRead(JournalEntryBase):
    id: int
    created_at: datetime
    items: List[JournalItemRead]

    class Config:
        from_attributes = True
