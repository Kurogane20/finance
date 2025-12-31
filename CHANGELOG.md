# Changelog - Finance Application

## [v2.1.0] - 2025-12-31

### 🐛 Bug Fixes

#### Critical Fixes
1. **Fixed Duplicate Import in main.py** ([main.py:12](backend/main.py#L12))
   - Removed duplicate `users_router` import that was causing potential issues
   - Impact: Prevents potential routing conflicts

2. **Fixed Hardcoded API URL** ([axios.js:4](frontend/src/api/axios.js#L4))
   - Replaced hardcoded `http://localhost:8000/api` with environment variable
   - Now uses `import.meta.env.VITE_API_URL` with fallback to localhost
   - Impact: Proper production/development environment separation

### ✨ New Features

#### Accounting Module Enhancements

1. **General Ledger Report** (NEW)
   - **Endpoint**: `GET /api/accounting/ledger/{account_id}`
   - Query parameters: `start_date`, `end_date` (optional)
   - Features:
     - Shows all transactions for specific account
     - Displays running balance after each transaction
     - Proper debit/credit handling based on account type
     - Supports date range filtering
   - Returns: Account details, ledger entries with balances

2. **Trial Balance Report** (NEW)
   - **Endpoint**: `GET /api/accounting/trial-balance`
   - Query parameters: `as_of_date` (optional)
   - Features:
     - Lists all accounts with debit/credit balances
     - Automatic balance calculation based on account type
     - Verifies Total Debits = Total Credits
     - Only includes posted journal entries
     - Only shows accounts with non-zero balances
   - Returns: Trial balance with totals and balance verification

### 🔧 Improvements

#### Performance Optimizations

1. **Database Indexing** ([accounting.py](backend/models/accounting.py))
   - Added index on `journal_entries.date` - Improves date range queries
   - Added index on `journal_entries.reference` - Faster reference lookups
   - Added index on `journal_entries.posted` - Efficient filtering of posted entries
   - Added index on `journal_items.journal_entry_id` - Optimizes JOIN operations
   - Added index on `journal_items.account_id` - Faster account queries
   - **Impact**: Significant performance improvement for reports and queries

#### Validation & Error Handling

2. **Enhanced Journal Entry Validation** ([schemas/accounting.py](backend/schemas/accounting.py))
   - Added validation to prevent both debit AND credit in same journal item
   - Added validation to ensure at least one amount (debit or credit) is non-zero
   - Better error messages for validation failures
   - **Impact**: Prevents invalid double-entry transactions

3. **Improved Error Handling in Accounting Routes** ([routers/accounting.py](backend/routers/accounting.py))
   - Validates all account IDs exist before creating journal entry
   - Checks that accounts are active (not disabled)
   - Proper transaction rollback on errors
   - Detailed error messages with specific issues
   - **Impact**: Better data integrity and user experience

#### Configuration Management

4. **Environment Variable Configuration**
   - Created [frontend/.env.development](frontend/.env.development)
     - Configures `VITE_API_URL=http://localhost:8000/api` for dev
   - Updated [frontend/.env.production](frontend/.env.production)
     - Already configured for production API URL
   - Updated [frontend/src/api/axios.js](frontend/src/api/axios.js)
     - Reads from environment variables correctly
   - **Impact**: Clean separation of dev/prod configurations

### 📚 API Documentation

#### New Endpoints

##### General Ledger
```http
GET /api/accounting/ledger/{account_id}?start_date=2024-01-01&end_date=2024-12-31
```

**Response:**
```json
{
  "account": {
    "id": 1,
    "code": "1110",
    "name": "Cash",
    "type": "ASSET"
  },
  "entries": [
    {
      "date": "2024-01-15T00:00:00",
      "reference": "JV-001",
      "description": "Initial deposit",
      "debit": 10000.00,
      "credit": 0.00,
      "balance": 10000.00,
      "journal_entry_id": 1
    }
  ],
  "ending_balance": 10000.00
}
```

##### Trial Balance
```http
GET /api/accounting/trial-balance?as_of_date=2024-12-31
```

**Response:**
```json
{
  "as_of_date": "2024-12-31",
  "accounts": [
    {
      "account_code": "1110",
      "account_name": "Cash",
      "account_type": "ASSET",
      "debit": 50000.00,
      "credit": 0.00
    },
    {
      "account_code": "3000",
      "account_name": "Share Capital",
      "account_type": "EQUITY",
      "debit": 0.00,
      "credit": 50000.00
    }
  ],
  "total_debits": 50000.00,
  "total_credits": 50000.00,
  "is_balanced": true
}
```

### 🔒 Security Notes

**Still Pending** (Recommendations for future updates):
- Add rate limiting to prevent API abuse
- Implement CSRF protection for form submissions
- Add refresh token mechanism for better security
- Move token from localStorage to httpOnly cookies (XSS protection)
- Add request/response encryption for sensitive data

### 📊 Database Changes

**Schema Updates:**
- Added indices to `journal_entries` table (date, reference, posted)
- Added indices to `journal_items` table (journal_entry_id, account_id)

**Note**: Since the app uses `create_all()`, indices will be created automatically on next run. For production databases, consider using Alembic migrations.

### 🚀 Deployment Notes

1. **Frontend Environment Variables:**
   - Development: Uses `.env.development` (auto-loaded by Vite)
   - Production: Uses `.env.production` (used during build)

2. **Database:**
   - Drop and recreate tables to apply new indices, OR
   - Manually add indices to existing tables

3. **Testing:**
   - Test new General Ledger endpoint with various account types
   - Verify Trial Balance calculation accuracy
   - Confirm environment variable loading in both dev/prod

### 📝 Migration Guide

#### For Existing Installations:

1. **Pull Latest Changes:**
   ```bash
   git pull origin main
   ```

2. **Backend:**
   ```bash
   cd backend
   # Activate venv
   pip install -r requirements.txt  # Already up to date

   # For development, the app will auto-create indices
   # For production with existing data, manually add indices or recreate DB
   ```

3. **Frontend:**
   ```bash
   cd frontend
   npm install  # No new dependencies

   # Ensure .env.development exists (created by this update)
   # Update .env.production with your API URL if needed
   ```

4. **Verify:**
   ```bash
   # Start backend
   cd backend
   uvicorn main:app --reload

   # Start frontend (new terminal)
   cd frontend
   npm run dev
   ```

5. **Test New Features:**
   - Navigate to Journal Entry page
   - Create a balanced journal entry
   - Test General Ledger: `GET /api/accounting/ledger/1`
   - Test Trial Balance: `GET /api/accounting/trial-balance`

### 🎯 What's Next

**Recommended Priority:**

1. **High Priority:**
   - [ ] Add Alembic for database migrations
   - [ ] Implement comprehensive unit tests
   - [ ] Add rate limiting middleware
   - [ ] Implement refresh token mechanism

2. **Medium Priority:**
   - [ ] Add Balance Sheet report
   - [ ] Add Income Statement (P&L) report using CoA
   - [ ] PDF export for financial reports
   - [ ] Email notifications for invoices

3. **Low Priority:**
   - [ ] Multi-currency support
   - [ ] Fiscal year closing functionality
   - [ ] Account reconciliation module
   - [ ] Advanced audit trail viewer

### 👥 Contributors

- AI Assistant (Claude Sonnet 4.5) - Code analysis, bug fixes, feature additions

---

**Full Changelog**: Compare [v2.0.0...v2.1.0](#)
