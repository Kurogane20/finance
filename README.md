# Finance Dashboard Application

Aplikasi Dashboard Keuangan Perusahaan dengan FastAPI Backend dan Vue.js Frontend.

![Dashboard Preview](https://img.shields.io/badge/Status-Production_Ready-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Vue.js](https://img.shields.io/badge/Vue.js-3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Fitur Utama

- **Dashboard Overview** - KPI cards, grafik pendapatan vs pengeluaran, kategori breakdown
- **Transaksi** - CRUD transaksi dengan filter dan kategori
- **Akun & AR/AP** - Manajemen akun bank/kas, aging analysis piutang/hutang
- **Anggaran** - Budget vs actual comparison per departemen
- **Laporan** - Laba Rugi, Arus Kas, Neraca, Export CSV
- **User Management** - RBAC (Admin, Approver, Editor, Viewer)
- **Audit Trail** - Log semua aktivitas user
- **Responsive Design** - Mobile-friendly dengan sidebar toggle

## 📋 Prasyarat

- Python 3.9+
- Node.js 18+
- npm atau yarn
- Docker (untuk deployment)

## 🛠️ Instalasi Development

### Backend

```bash
cd backend

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Jalankan server
uvicorn main:app --reload
```

Backend akan berjalan di `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Jalankan dev server
npm run dev
```

Frontend akan berjalan di `http://localhost:5173`

## 🐳 Deploy dengan Docker

```bash
# Clone repository
git clone https://github.com/yourusername/finance.git
cd finance

# Setup environment
cp .env.example .env

# Generate secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output ke .env

nano .env  # Edit SECRET_KEY, DOMAIN, dan database passwords

# Build dan jalankan
docker-compose up -d --build
```

⚠️ **PENTING**: Jangan deploy ke production tanpa mengikuti [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)

Lihat [DEPLOYMENT.md](DEPLOYMENT.md) untuk panduan lengkap deployment ke VPS Ubuntu.

## 👤 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@company.com | admin123 |
| CFO/Approver | cfo@company.com | cfo123 |
| Akuntan/Editor | akuntan@company.com | akuntan123 |
| Staff/Viewer | staff@company.com | staff123 |

## 🏗️ Struktur Project

```
finance/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── database.py          # Database config
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API endpoints
│   ├── utils/               # Utilities
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # Vue components
│   │   ├── views/           # Page views
│   │   ├── stores/          # Pinia stores
│   │   └── router/          # Vue Router
│   └── Dockerfile
├── nginx/                   # Nginx reverse proxy config
├── docker-compose.yml
├── DEPLOYMENT.md
└── README.md
```

## 🔑 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Login |
| GET | /api/dashboard/overview | KPI summary |
| GET | /api/dashboard/charts | Chart data |
| GET/POST | /api/transactions | Transactions CRUD |
| GET | /api/accounts | Accounts list |
| GET | /api/accounts/aging | AR/AP aging |
| GET | /api/budgets/comparison | Budget vs Actuals |
| GET | /api/reports/profit-loss | P&L report |
| GET | /api/reports/cash-flow | Cash flow report |
| GET | /api/users | User management |

## 🛡️ Keamanan

- JWT Authentication
- Role-Based Access Control (RBAC)
- Audit trail untuk semua perubahan data
- Password hashing dengan bcrypt
- Rate limiting pada API
- HTTPS ready

## 📄 License

MIT License
