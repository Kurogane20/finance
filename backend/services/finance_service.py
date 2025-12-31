from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from models.transaction import Transaction, Category
from models.account import Account
from models.budget import Budget
from models.invoice import Invoice
from models.audit_log import AuditLog


class FinanceService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def create_transaction(self, data: dict) -> Transaction:
        """
        Create transaction and update related ledgers (Account Balance, Budget Spent)
        """
        # 1. Create Transaction
        transaction = Transaction(
            **data,
            created_by=self.user_id
        )
        self.db.add(transaction)
        # Flush to get ID and ensure data is valid
        self.db.flush() 

        # 2. Update Account Balance
        if transaction.status == "completed":
            self._update_account_balance(
                transaction.account_id, 
                transaction.amount, 
                transaction.type, 
                reverse=False
            )
            
            # 3. Update Budget (if Expense)
            if transaction.type == "debit" and transaction.category_id:
                self._update_budget_spent(
                    transaction.category_id,
                    transaction.amount,
                    transaction.date,
                    reverse=False
                )

        # 4. Audit Log
        self._log_audit("create", "transaction", transaction.id, f"Created transaction: {transaction.description}", new_values=data)
        
        return transaction

    def update_transaction(self, transaction_id: int, new_data: dict) -> Transaction:
        """
        Update transaction with full ledger reversal and re-application
        """
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise ValueError("Transaction not found")

        # Snapshot old state
        old_values = {
            "amount": float(transaction.amount),
            "type": transaction.type,
            "account_id": transaction.account_id,
            "category_id": transaction.category_id,
            "status": transaction.status,
            "date": transaction.date
        }

        # 1. REVERSE Old Effect (if completed)
        if old_values["status"] == "completed":
            self._update_account_balance(
                old_values["account_id"], 
                Decimal(str(old_values["amount"])), 
                old_values["type"], 
                reverse=True
            )
            if old_values["type"] == "debit" and old_values["category_id"]:
                self._update_budget_spent(
                    old_values["category_id"],
                    Decimal(str(old_values["amount"])),
                    old_values["date"],
                    reverse=True
                )

        # 2. Update Fields
        for key, value in new_data.items():
            setattr(transaction, key, value)

        # 3. APPLY New Effect (if completed)
        if transaction.status == "completed":
            self._update_account_balance(
                transaction.account_id, 
                transaction.amount, 
                transaction.type, 
                reverse=False
            )
            if transaction.type == "debit" and transaction.category_id:
                self._update_budget_spent(
                    transaction.category_id,
                    transaction.amount,
                    transaction.date,
                    reverse=False
                )

        # 4. Audit Log
        self._log_audit("update", "transaction", transaction.id, f"Updated transaction #{transaction.id}", 
                       old_values=old_values, new_values=new_data)
        
        return transaction

    def delete_transaction(self, transaction_id: int):
        """
        Delete transaction and reverse ledger
        """
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise ValueError("Transaction not found")

        # 1. Reverse Effect
        if transaction.status == "completed":
            self._update_account_balance(
                transaction.account_id, 
                transaction.amount, 
                transaction.type, 
                reverse=True
            )
            if transaction.type == "debit" and transaction.category_id:
                self._update_budget_spent(
                    transaction.category_id,
                    transaction.amount,
                    transaction.date,
                    reverse=True
                )
        
        # 2. Audit Log (Before delete)
        self._log_audit("delete", "transaction", transaction.id, f"Deleted transaction: {transaction.description}", 
                       old_values={"amount": float(transaction.amount)})
        
        # 3. Delete
        self.db.delete(transaction)

    def pay_invoice(self, invoice_id: int, account_id: int) -> dict:
        """
        Process invoice payment
        """
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("Invoice not found")
        if invoice.status == 'paid':
            raise ValueError("Invoice already paid")

        account = self.db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise ValueError("Account not found")

        # Create Transaction logic
        trans_type = "credit" if invoice.type == "receivable" else "debit"
        description = f"Payment for Invoice #{invoice.invoice_number} - {invoice.customer_name}"
        
        trans_data = {
            "date": datetime.utcnow(),
            "amount": invoice.total_amount,
            "type": trans_type,
            "category_id": None,
            "account_id": account.id,
            "description": description,
            "reference": invoice.invoice_number,
            "status": "completed"
        }
        
        # This will handle balance update via create_transaction
        transaction = self.create_transaction(trans_data)
        
        # Update Invoice
        invoice.status = "paid"
        invoice.paid_date = date.today()
        
        return {"message": "Invoice paid successfully", "transaction_id": transaction.id}

    # --- Internal Helpers ---

    def _update_account_balance(self, account_id: int, amount: Decimal, type: str, reverse: bool = False):
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if not account:
            return # Should raise error?
        
        # Logic: Credit (Income) Adds, Debit (Expense) Subtracts
        # Reverse does the opposite
        
        delta = amount
        if reverse:
            delta = -delta
            
        if type == "credit":
            account.balance += delta
        else:
            account.balance -= delta

    def _update_budget_spent(self, category_id: int, amount: Decimal, trans_date: datetime, reverse: bool = False):
        """Update budget 'spent' amount based on category and month"""
        # Determine period from date (YYYY-MM)
        if isinstance(trans_date, str):
            # Parse if string (defensive)
            try:
                dt = datetime.fromisoformat(trans_date)
            except:
                return
            period = dt.strftime("%Y-%m")
        else:
            period = trans_date.strftime("%Y-%m")
            
        # Find budget
        budget = self.db.query(Budget).filter(
            Budget.category_id == category_id,
            Budget.period == period
        ).first()
        
        if budget:
            delta = amount
            if reverse:
                delta = -delta
            budget.spent_amount += delta

    def _log_audit(self, action: str, entity: str, entity_id: int, description: str, old_values: dict = None, new_values: dict = None):
        audit = AuditLog(
            user_id=self.user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            timestamp=datetime.utcnow()
        )
        self.db.add(audit)
