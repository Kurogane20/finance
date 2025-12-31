"""
Production Seed Script - Users Only
Creates only roles, users, and categories for production deployment.
No demo transactions, accounts, or invoices.
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models.user import User, Role
from models.transaction import Category
from utils.security import get_password_hash
from datetime import datetime

# Create all tables
Base.metadata.create_all(bind=engine)


def seed_users_only():
    """Seed database with only users, roles, and categories for production"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Role).first():
            print("⚠️  Database already has data. Skipping seed.")
            return
        
        print("🌱 Seeding production database (users only)...")
        
        # === ROLES ===
        roles = [
            Role(name="admin", permissions={"all": True}),
            Role(name="approver", permissions={"view": True, "approve": True, "create": True}),
            Role(name="editor", permissions={"view": True, "create": True, "edit": True}),
            Role(name="viewer", permissions={"view": True})
        ]
        db.add_all(roles)
        db.commit()
        print("✓ Roles created: admin, approver, editor, viewer")
        
        # === USERS ===
        # Default admin account - CHANGE PASSWORD IMMEDIATELY AFTER FIRST LOGIN
        users = [
            User(
                email="admin@mitramutiara.co.id",
                password_hash=get_password_hash("AdminFinance2024!"),
                full_name="Administrator",
                role_id=1,
                is_active=True
            )
        ]
        db.add_all(users)
        db.commit()
        print("✓ Admin user created")
        
        # === CATEGORIES ===
        # Required for transaction system to work
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
        print("✓ Categories created (10 categories)")
        
        # === ACCOUNTS ===
        # Required for transaction system to work
        from models.account import Account
        accounts = [
            Account(
                name="Kas Utama",
                type="cash",
                balance=0,
                currency="IDR",
                is_active=True
            ),
            Account(
                name="Bank BCA",
                type="bank",
                account_number="1234567890",
                balance=0,
                currency="IDR",
                is_active=True
            ),
            Account(
                name="Bank Mandiri",
                type="bank",
                account_number="0987654321",
                balance=0,
                currency="IDR",
                is_active=True
            ),
            Account(
                name="Petty Cash",
                type="cash",
                balance=0,
                currency="IDR",
                is_active=True
            ),
        ]
        db.add_all(accounts)
        db.commit()
        print("✓ Accounts created (4 accounts)")
        
        print("\n" + "="*50)
        print("✅ PRODUCTION DATABASE SEEDING COMPLETED!")
        print("="*50)
        print("\n📋 Default Login Credentials:")
        print("   Email    : admin@mitramutiara.co.id")
        print("   Password : AdminFinance2024!")
        print("\n⚠️  IMPORTANT: Change this password immediately after first login!")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_users_only()
