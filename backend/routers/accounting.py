from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from database_async import get_async_db
from models.accounting import Account, JournalEntry, JournalItem
from schemas.accounting import AccountCreate, AccountRead, JournalEntryCreate, JournalEntryRead

router = APIRouter(
    prefix="/accounting",
    tags=["Accounting"]
)

@router.post("/accounts", response_model=AccountRead)
async def create_account(account: AccountCreate, db: AsyncSession = Depends(get_async_db)):
    # Check if code exists
    result = await db.execute(select(Account).where(Account.code == account.code))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Account code already exists")
    
    new_account = Account(**account.model_dump())
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    return new_account

@router.get("/accounts", response_model=List[AccountRead])
async def get_accounts(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Account).order_by(Account.code))
    accounts = result.scalars().all()
    return accounts

@router.post("/journals", response_model=JournalEntryRead)
async def create_journal_entry(journal: JournalEntryCreate, db: AsyncSession = Depends(get_async_db)):
    try:
        # Validate that all accounts exist
        account_ids = [item.account_id for item in journal.items]
        accounts_result = await db.execute(
            select(Account).where(Account.id.in_(account_ids))
        )
        existing_accounts = {acc.id for acc in accounts_result.scalars().all()}

        missing_accounts = set(account_ids) - existing_accounts
        if missing_accounts:
            raise HTTPException(
                status_code=400,
                detail=f"Account IDs not found: {missing_accounts}"
            )

        # Validate all accounts are active
        inactive_check = await db.execute(
            select(Account).where(
                Account.id.in_(account_ids),
                Account.is_active == False
            )
        )
        inactive_accounts = inactive_check.scalars().all()
        if inactive_accounts:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot post to inactive accounts: {[acc.code for acc in inactive_accounts]}"
            )

        # Create Header
        new_entry = JournalEntry(
            date=journal.date,
            description=journal.description,
            reference=journal.reference,
            posted=journal.posted
        )
        db.add(new_entry)
        await db.flush()  # Get ID

        # Create Items
        for item in journal.items:
            new_item = JournalItem(
                journal_entry_id=new_entry.id,
                account_id=item.account_id,
                debit=item.debit,
                credit=item.credit
            )
            db.add(new_item)

        await db.commit()

        # Refresh to return full object with items
        result = await db.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.items))
            .where(JournalEntry.id == new_entry.id)
        )
        final_entry = result.scalar_one()

        return final_entry

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create journal entry: {str(e)}"
        )

@router.get("/journals", response_model=List[JournalEntryRead])
async def get_journals(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(JournalEntry)
        .options(selectinload(JournalEntry.items))
        .order_by(JournalEntry.date.desc())
    )
    return result.scalars().all()


@router.get("/ledger/{account_id}")
async def get_general_ledger(
    account_id: int,
    start_date: str = None,
    end_date: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get General Ledger for a specific account with running balance.
    Returns all journal items for the account with detailed information.
    """
    from datetime import datetime
    from sqlalchemy import and_

    # Build query for journal items
    query = select(JournalItem).where(JournalItem.account_id == account_id)
    query = query.options(selectinload(JournalItem.entry))

    # Apply date filters if provided
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.join(JournalEntry).where(JournalEntry.date >= start_dt)

    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        if not start_date:
            query = query.join(JournalEntry)
        query = query.where(JournalEntry.date <= end_dt)

    # Order by date
    query = query.join(JournalEntry).order_by(JournalEntry.date, JournalEntry.id)

    result = await db.execute(query)
    items = result.scalars().all()

    # Get account details
    account_result = await db.execute(select(Account).where(Account.id == account_id))
    account = account_result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Calculate running balance
    balance = 0
    ledger_entries = []

    for item in items:
        # For Asset, Expense: Debit increases, Credit decreases
        # For Liability, Equity, Revenue: Credit increases, Debit decreases
        if account.type in ["ASSET", "EXPENSE"]:
            balance += float(item.debit) - float(item.credit)
        else:
            balance += float(item.credit) - float(item.debit)

        ledger_entries.append({
            "date": item.entry.date.isoformat(),
            "reference": item.entry.reference,
            "description": item.entry.description,
            "debit": float(item.debit),
            "credit": float(item.credit),
            "balance": balance,
            "journal_entry_id": item.journal_entry_id
        })

    return {
        "account": {
            "id": account.id,
            "code": account.code,
            "name": account.name,
            "type": account.type
        },
        "entries": ledger_entries,
        "ending_balance": balance
    }


@router.get("/trial-balance")
async def get_trial_balance(
    as_of_date: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Generate Trial Balance report showing all accounts with their debit/credit balances.
    Verifies that Total Debits = Total Credits.
    """
    from datetime import datetime
    from sqlalchemy import and_, func

    # Get all active accounts
    accounts_result = await db.execute(
        select(Account)
        .where(Account.is_active == True)
        .order_by(Account.code)
    )
    accounts = accounts_result.scalars().all()

    # Build query for journal items
    query = select(
        JournalItem.account_id,
        func.sum(JournalItem.debit).label('total_debit'),
        func.sum(JournalItem.credit).label('total_credit')
    )

    # Filter by date if provided
    if as_of_date:
        as_of_dt = datetime.fromisoformat(as_of_date)
        query = query.join(JournalEntry).where(JournalEntry.date <= as_of_dt)

    # Only include posted entries
    query = query.join(JournalEntry).where(JournalEntry.posted == True)

    query = query.group_by(JournalItem.account_id)

    result = await db.execute(query)
    balances = {row.account_id: (float(row.total_debit or 0), float(row.total_credit or 0))
                for row in result}

    # Build trial balance report
    trial_balance = []
    total_debits = 0
    total_credits = 0

    for account in accounts:
        debit_total, credit_total = balances.get(account.id, (0, 0))

        # Calculate account balance based on normal balance side
        if account.type in ["ASSET", "EXPENSE"]:
            # Normal debit balance
            balance = debit_total - credit_total
            debit_balance = balance if balance > 0 else 0
            credit_balance = -balance if balance < 0 else 0
        else:
            # Normal credit balance (LIABILITY, EQUITY, REVENUE)
            balance = credit_total - debit_total
            credit_balance = balance if balance > 0 else 0
            debit_balance = -balance if balance < 0 else 0

        # Only include accounts with balance
        if debit_balance != 0 or credit_balance != 0:
            trial_balance.append({
                "account_code": account.code,
                "account_name": account.name,
                "account_type": account.type,
                "debit": debit_balance,
                "credit": credit_balance
            })

            total_debits += debit_balance
            total_credits += credit_balance

    return {
        "as_of_date": as_of_date or "All Time",
        "accounts": trial_balance,
        "total_debits": total_debits,
        "total_credits": total_credits,
        "is_balanced": abs(total_debits - total_credits) < 0.01
    }
