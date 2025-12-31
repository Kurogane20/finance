# Corporate Finance Dashboard (Finance OS/ERP)

A robust, scalable, and secure "System Information Finance" application built with FastAPI (Async) and Vue 3. Features Double-Entry Accounting, Chart of Accounts management, and real-time financial reporting.

![Status](https://img.shields.io/badge/Status-Beta-blue)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Vue.js](https://img.shields.io/badge/Vue.js-3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Key Features

### Core ERP & Accounting
- **Chart of Accounts (CoA)**: Hierarchical management of Assets, Liabilities, Equity, Revenue, and Expenses using standard corporate coding (e.g., 101.01).
- **Double-Entry Journal**: Validated journal entries where Debit must equal Credit.
- **General Ledger**: Complete ledger view with running balances per account.
- **Trial Balance**: Automated trial balance generation with debit/credit verification.
- **Financial Reports**: Balance Sheet, Profit & Loss (Income Statement), General Ledger, Trial Balance.

### Operational Finance (Legacy/Hybrid)
- **Dashboard Overview**: KPI cards, revenue vs expense charts.
- **Transactions**: Simple Cash In/Out recording.
- **Budgets**: Departmental budget vs actuals.
- **Invoicing**: Create and track invoices.

### Security & Architecture
- **Async Backend**: High-performance FastAPI with `aiomysql` and SQLAlchemy Async.
- **Role-Based Access Control**: Admin, Manager (Approver), Staff, Viewer levels.
- **Modern Frontend**: Vue 3 Composition API, Pinia State Management, Tailwind CSS styling.
- **Audit Logs**: Full trace of user activities.

## 📋 Technology Stack

*   **Backend**: Python, FastAPI, SQLAlchemy (Async/Sync), Pydantic, Jose (JWT).
*   **Database**: MySQL (Production) / SQLite (Dev) with `aiomysql`.
*   **Frontend**: Vue.js 3, Vite, Pinia, Vue Router, Tailwind CSS, Chart.js.
*   **Infrastructure**: Docker, Docker Compose, Nginx.

## 🛠️ Installation & Setup

### 1. Backend Setup

```bash
cd backend

# Create & Activate Virtual Environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install Dependencies (includes aiomysql, fastpi, etc.)
pip install -r requirements.txt

# Run Database Migrations / Setup Tables
# The app creates tables on startup automatically.
# To seed initial Chart of Accounts data:
# (You may need to run this manually on your DB tool or via script)
# See backend/coa_seed.sql

# Run Server
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.
Docs: `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
cd frontend

# Install Dependencies
npm install

# Run Development Server
npm run dev
```

Frontend runs at `http://localhost:5173`.

## 🐳 Docker Deployment

To deploy the full stack (Backend, Frontend, Nginx, MySQL):

```bash
# Clone & Enter
git clone <repo-url>
cd finance

# Configure Environment
cp .env.example .env.production
# Edit .env.production with real credentials

# Run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🏗️ Project Structure

```
finance/
├── backend/
│   ├── main.py              # App Entry Point & Router Registry
│   ├── database_async.py    # NEW: Async DB Config
│   ├── database.py          # Legacy: Sync DB Config
│   ├── models/              # Modules: accounting.py (ERP), transaction.py (Simple)
│   ├── schemas/             # Pydantic Validators (Balanced Journals)
│   ├── routers/             # API Endpoints (journals, accounts, etc.)
│   └── coa_seed.sql         # SQL Seed for Standard Accounts
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios Setup
│   │   ├── stores/          # Pinia Stores (accounting.js)
│   │   ├── views/           # Pages (JournalEntry.vue, Dashboard.vue)
│   │   └── components/      # Reusable UI
│   ├── tailwind.config.js   # Tailwind Config
│   └── style.css            # Global Styles & Tailwind Directives
└── docker-compose.prod.yml  # Production Orchestration
```

## � Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@company.com | admin123 |
| CFO/Approver | cfo@company.com | cfo123 |
| Staff | staff@company.com | staff123 |

## 🔑 Key API Endpoints (New ERP)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounting/journals` | Create valid Double-Entry Journal |
| GET | `/api/accounting/journals` | List General Journal Entries |
| GET | `/api/accounting/accounts` | Get Chart of Accounts (CoA) |
| POST | `/api/accounting/accounts` | Create new Ledger Account |
| GET | `/api/accounting/ledger/{account_id}` | Get General Ledger for specific account |
| GET | `/api/accounting/trial-balance` | Generate Trial Balance report |

## 📝 Recent Updates (v2.1.0)

**New Features:**
- ✅ General Ledger report with running balances
- ✅ Trial Balance report with automatic verification
- ✅ Enhanced validation for journal entries
- ✅ Performance optimization with database indices
- ✅ Environment-based configuration for dev/prod

**Bug Fixes:**
- ✅ Fixed duplicate router import
- ✅ Fixed hardcoded API URLs
- ✅ Improved error handling with detailed messages

See [CHANGELOG.md](CHANGELOG.md) for complete details.

## �️ License

MIT License
