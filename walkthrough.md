# Finance OS v2.0 - System Manual

## 🚀 Overview
Finance OS has been upgraded to a **Premium Financial Platform**. It now features a robust **Service Layer Architecture** for accurate accounting (Double-Entry Ledger) and a new **Glassmorphism UI** for a modern user experience.

---

## 🎨 Design System: "Premium Glass"
The frontend has been completely redesigned.
- **Theme**: Light Mode with Indigo/Pink dynamic gradients.
- **Components**: Floating Glass Panels, blurred backgrounds (`backdrop-filter`), and pill-shaped interactive elements.
- **Responsive**: Fully mobile-optimized with a smart sidebar drawer.

### Key Files
- `frontend/src/style.css`: The core design system definitions.
- `frontend/src/components/layout/Sidebar.vue`: Floating navigation panel.
- `frontend/src/views/DashboardView.vue`: Command center with reactive charts.

---

## 🧠 Backend Architecture: Service Layer
Business logic has been moved from API Routers to a centralized Service Layer.

### 1. Finance Service (`backend/services/finance_service.py`)
This is the "Brain" of the application. It handles:
- **Transaction Processing**: Automatically updates Account Balances and Audit Logs.
- **Budget Tracking**: Detecting expense categories and updating `spent_amount` in the Budget automatically.
- **Ledger Integrity**: Ensures every debit has a credit impact (Logic enforced in code).
- **Invoice Payments**: Handles the complex flow of creating a transaction from an invoice and updating statuses.

### 2. Router Simplification
Routers (`transactions.py`, `accounts.py`) now act as Controllers. They validate input and delegate work to `FinanceService`.

---

## ✅ New Features
1.  **Smart Budgeting**: Transactions automatically update Budget usage. No more manual tracking.
2.  **Integrated Invoicing**: "Pay Invoice" button instantly creates the corresponding transaction and updates the Ledger.
3.  **Audit Logging**: Every financial action (Create/Update/Delete) is logged in `audit_log` table.
4.  **Bulk Import**: CSV Import now runs through the Service Layer, ensuring imported data also updates Balances.

---

## 🛠️ Deployment (VPS / Docker)
The deployment process remains streamlined using Docker Compose.

### Quick Start
```bash
# 1. Start System
docker-compose up -d --build

# 2. Seed Data (Optional)
docker-compose exec backend python utils/seed_data.py
```

### Environment Variables
Ensure `.env` contains:
```ini
DATABASE_URL=mysql+pymysql://user:pass@db/finance_db
SECRET_KEY=your_secret
ALGORITHM=HS256
```

---

## 🔄 Development Workflow
1.  **Frontend**: Edit `frontend/src` files. Vite HMR will update the UI instantly.
2.  **Backend**: Edit `backend/services` or `backend/routers`. FastAPI auto-reloads.
3.  **Testing**:
    - Check "Laporan" to verify Balance Sheet matches Transactions.
    - Check "Anggaran" to verify Marketing expenses reduce the budget.
