from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models.user import User, Role
from models.transaction import Transaction, Category
from models.account import Account
from models.budget import Budget
from models.invoice import Invoice
from utils.security import get_password_hash
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Create all tables
Base.metadata.create_all(bind=engine)


def seed_database():
    """Seed database with sample data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Role).first():
            print("Database already seeded")
            return
        
        print("Seeding database...")
        
        # === ROLES ===
        roles = [
            Role(name="admin", permissions={"all": True}),
            Role(name="approver", permissions={"view": True, "approve": True, "create": True}),
            Role(name="editor", permissions={"view": True, "create": True, "edit": True}),
            Role(name="viewer", permissions={"view": True})
        ]
        db.add_all(roles)
        db.commit()
        print("✓ Roles created")
        
        # === USERS ===
        users = [
            User(
                email="admin@company.com",
                password_hash=get_password_hash("admin123"),
                full_name="Super Admin",
                role_id=1
            ),
            User(
                email="cfo@company.com",
                password_hash=get_password_hash("cfo123"),
                full_name="Budi Santoso (CFO)",
                role_id=2
            ),
            User(
                email="akuntan@company.com",
                password_hash=get_password_hash("akuntan123"),
                full_name="Siti Rahayu",
                role_id=3
            ),
            User(
                email="staff@company.com",
                password_hash=get_password_hash("staff123"),
                full_name="Ahmad Wijaya",
                role_id=4
            )
        ]
        db.add_all(users)
        db.commit()
        print("✓ Users created")
        
        # === CATEGORIES ===
        categories = [
            # Income categories
            Category(name="Penjualan Produk", type="income", icon="🛍️", color="#10b981"),
            Category(name="Jasa Konsultasi", type="income", icon="💼", color="#06b6d4"),
            Category(name="Pendapatan Lainnya", type="income", icon="💵", color="#8b5cf6"),
            # Expense categories
            Category(name="Gaji & Tunjangan", type="expense", icon="👥", color="#ef4444"),
            Category(name="Sewa Kantor", type="expense", icon="🏢", color="#f97316"),
            Category(name="Utilitas", type="expense", icon="💡", color="#eab308"),
            Category(name="Marketing", type="expense", icon="📢", color="#ec4899"),
            Category(name="Operasional", type="expense", icon="⚙️", color="#6366f1"),
            Category(name="IT & Software", type="expense", icon="💻", color="#14b8a6"),
            Category(name="Transportasi", type="expense", icon="🚗", color="#64748b"),
        ]
        db.add_all(categories)
        db.commit()
        print("✓ Categories created")
        
        # === ACCOUNTS ===
        accounts = [
            Account(
                name="Bank Mandiri - Utama",
                type="bank",
                account_number="1234567890",
                bank_name="Bank Mandiri",
                balance=Decimal("500000000"),
                currency="IDR"
            ),
            Account(
                name="Bank BCA - Operasional",
                type="bank",
                account_number="0987654321",
                bank_name="Bank BCA",
                balance=Decimal("250000000"),
                currency="IDR"
            ),
            Account(
                name="Kas Kecil",
                type="cash",
                balance=Decimal("15000000"),
                currency="IDR"
            ),
            Account(
                name="Kartu Kredit Corporate",
                type="credit_card",
                bank_name="Bank Mandiri",
                balance=Decimal("-25000000"),
                currency="IDR"
            )
        ]
        db.add_all(accounts)
        db.commit()
        print("✓ Accounts created")
        
        # === TRANSACTIONS ===
        transactions = []
        
        # Generate transactions for the last 3 months
        for i in range(90):
            date = datetime.now() - timedelta(days=i)
            
            # Income transactions (1-2 per day)
            for _ in range(random.randint(1, 2)):
                transactions.append(Transaction(
                    date=date,
                    type="credit",
                    amount=Decimal(str(random.randint(5000000, 50000000))),
                    category_id=random.randint(1, 3),
                    account_id=random.randint(1, 2),
                    description=f"Pendapatan {date.strftime('%d/%m/%Y')}",
                    reference=f"INV-{2024000 + i}",
                    status="completed",
                    created_by=3
                ))
            
            # Expense transactions (2-4 per day)
            for _ in range(random.randint(2, 4)):
                transactions.append(Transaction(
                    date=date,
                    type="debit",
                    amount=Decimal(str(random.randint(500000, 15000000))),
                    category_id=random.randint(4, 10),
                    account_id=random.randint(1, 3),
                    description=f"Pengeluaran operasional {date.strftime('%d/%m/%Y')}",
                    reference=f"EXP-{2024000 + i}",
                    status="completed",
                    created_by=3
                ))
        
        db.add_all(transactions)
        db.commit()
        print(f"✓ {len(transactions)} transactions created")
        
        # === BUDGETS ===
        current_month = datetime.now().strftime("%Y-%m")
        departments = ["Finance", "Marketing", "IT", "HR", "Operations"]
        budgets = []
        
        for dept in departments:
            allocated = random.randint(50, 200) * 1000000
            spent = random.randint(20, 80) * allocated // 100
            budgets.append(Budget(
                department=dept,
                period=current_month,
                allocated_amount=Decimal(str(allocated)),
                spent_amount=Decimal(str(spent))
            ))
        
        db.add_all(budgets)
        db.commit()
        print("✓ Budgets created")
        
        # === INVOICES ===
        invoices = []
        customers = [
            "PT Maju Bersama", "CV Sukses Jaya", "PT Mandiri Tech",
            "PT Global Services", "CV Kreatif Digital", "PT Inovasi Prima"
        ]
        
        for i in range(20):
            issue_date = datetime.now() - timedelta(days=random.randint(0, 60))
            due_date = issue_date + timedelta(days=30)
            amount = random.randint(10, 100) * 1000000
            tax = amount * 11 // 100
            
            status = random.choice(["draft", "sent", "viewed", "paid", "overdue"])
            if due_date.date() < datetime.now().date() and status in ["sent", "viewed"]:
                status = "overdue"
            
            invoices.append(Invoice(
                invoice_number=f"INV-{2024}{i+1:04d}",
                type="receivable",
                customer_name=random.choice(customers),
                customer_email=f"finance@{random.choice(customers).lower().replace(' ', '')}.com",
                amount=Decimal(str(amount)),
                tax_amount=Decimal(str(tax)),
                total_amount=Decimal(str(amount + tax)),
                status=status,
                issue_date=issue_date.date(),
                due_date=due_date.date(),
                notes="Pembayaran dalam waktu 30 hari",
                created_by=3
            ))
        
        # Payable invoices
        vendors = ["PT Supplier Utama", "CV Logistik Prima", "PT Media Ads"]
        for i in range(10):
            issue_date = datetime.now() - timedelta(days=random.randint(0, 45))
            due_date = issue_date + timedelta(days=30)
            amount = random.randint(5, 50) * 1000000
            tax = amount * 11 // 100
            
            invoices.append(Invoice(
                invoice_number=f"BILL-{2024}{i+1:04d}",
                type="payable",
                customer_name=random.choice(vendors),
                amount=Decimal(str(amount)),
                tax_amount=Decimal(str(tax)),
                total_amount=Decimal(str(amount + tax)),
                status=random.choice(["sent", "paid"]),
                issue_date=issue_date.date(),
                due_date=due_date.date(),
                created_by=3
            ))
        
        db.add_all(invoices)
        db.commit()
        print(f"✓ {len(invoices)} invoices created")
        
        print("\n✅ Database seeding completed!")
        print("\n📋 Login credentials:")
        print("   Admin: admin@company.com / admin123")
        print("   CFO: cfo@company.com / cfo123")
        print("   Akuntan: akuntan@company.com / akuntan123")
        print("   Staff: staff@company.com / staff123")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
