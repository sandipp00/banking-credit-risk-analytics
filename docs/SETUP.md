# Banking Credit Risk Analytics — Setup & Usage Guide

## Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+** (running locally or remote)
- **Git**

## Quick Start (5 minutes)

### 1. Clone & Install

```bash
git clone https://github.com/sandipp00/banking-credit-risk-analytics.git
cd banking-credit-risk-analytics
pip install -r requirements.txt
```

### 2. Configure Database

Copy `.env.example` to `.env` and fill in your PostgreSQL credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=banking_db
```

### 3. Create Database (if needed)

```bash
psql -U postgres -c "CREATE DATABASE banking_db;"
```

### 4. Run the Full Pipeline

```bash
make all
```

This will:
1. ✅ Install dependencies
2. ✅ Create PostgreSQL schema
3. ✅ Load cleaned CSV data
4. ✅ Run exploratory data analysis
5. ✅ Execute all SQL analysis queries
6. ✅ Run data quality validation tests

---

## Detailed Setup (Manual Steps)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- `pandas` — Data manipulation
- `numpy` — Numerical computing
- `psycopg2-binary` — PostgreSQL driver
- `python-dotenv` — Environment variable management

### Step 2: Set Up PostgreSQL

**Create the database:**
```bash
psql -U postgres -c "CREATE DATABASE banking_db;"
```

**Create tables and indexes:**
```bash
psql -U postgres -d banking_db -f sql/schema.sql
```

Verify schema was created:
```bash
psql -U postgres -d banking_db -c "\dt"
```

You should see 6 tables: branches, customers, accounts, loans, payments, transactions.

### Step 3: Load Data

**Option A: Automated (Recommended)**
```bash
python python/load_data.py
```

**Option B: Manual SQL COPY Commands**
```bash
psql -U postgres -d banking_db << EOF
COPY branches FROM '$(pwd)/branches_clean.csv' CSV HEADER;
COPY customers FROM '$(pwd)/customers_clean.csv' CSV HEADER;
COPY accounts FROM '$(pwd)/accounts_clean.csv' CSV HEADER;
COPY loans FROM '$(pwd)/loans_clean.csv' CSV HEADER;
COPY payments FROM '$(pwd)/payments_clean.csv' CSV HEADER;
COPY transactions FROM '$(pwd)/transactions_clean.csv' CSV HEADER;
EOF
```

Verify data loaded:
```bash
psql -U postgres -d banking_db -c "SELECT COUNT(*) FROM loans;"
```

Should return: `18000`

### Step 4: Run Analysis

**Python EDA (outputs KPIs and CSVs):**
```bash
python python/eda.py
```

Output files saved to `docs/`:
- `loan_product_analysis.csv`
- `customer_exposure_analysis.csv`
- `payment_monthly_analysis.csv`

**SQL Queries (outputs to console):**
```bash
psql -U postgres -d banking_db -f sql/analysis_queries.sql
```

Produces 12 analysis outputs including:
- Portfolio overview (total loans, disbursed, default rate)
- Loan performance by product
- Risk by credit score band
- Branch performance
- Customer exposure analysis

### Step 5: Validate Data Quality

```bash
python python/data_validation_tests.py
```

Runs comprehensive tests:
- ✅ Schema validation (all tables exist)
- ✅ Index verification (performance indexes)
- ✅ Row count validation
- ✅ Data integrity (no NULLs in keys)
- ✅ Business logic constraints (credit scores, balances)
- ✅ Referential integrity (foreign keys)
- ✅ Portfolio metrics sanity checks

---

## Available Commands

### Using Make (Recommended)

```bash
make install          # Install Python dependencies
make setup-db         # Create PostgreSQL schema
make load-data        # Load CSV data into database
make eda              # Run exploratory data analysis
make run-analysis     # Execute SQL analysis queries
make validate         # Run data quality validation tests
make all              # Run everything (full pipeline)
make clean            # Remove cache and generated files
make help             # Show all available commands
```

### Using Python Directly

```bash
# Run EDA only
python python/eda.py

# Run data loading only
python python/load_data.py

# Run validation tests
python python/data_validation_tests.py
```

### Using psql Directly

```bash
# Execute schema setup
psql -U postgres -d banking_db -f sql/schema.sql

# Execute analysis queries
psql -U postgres -d banking_db -f sql/analysis_queries.sql
```

---

## Project Structure

```
banking-credit-risk-analytics/
├── README.md                          Project overview
├── requirements.txt                   Python dependencies
├── .env.example                       Database config template
├── .gitignore                         Git exclusions
├── Makefile                           Automation commands
│
├── data files (*.csv)                 Raw & cleaned data
├── data_dictionary_overview.csv       Table documentation
├── data_quality_validation.csv        Data cleaning audit
│
├── python/
│   ├── eda.py                         Exploratory data analysis
│   ├── load_data.py                   Automated data loader
│   └── data_validation_tests.py       Data quality test suite
│
├── sql/
│   ├── schema.sql                     PostgreSQL table definitions
│   └── analysis_queries.sql           12 production queries
│
├── powerbi/
│   └── dashboard_spec.md              Dashboard specification
│
└── docs/
    ├── SETUP.md                       This file
    ├── eda_output.txt                 Sample EDA console output
    ├── loan_product_analysis.csv      Product-level metrics
    ├── customer_exposure_analysis.csv Customer risk analysis
    └── payment_monthly_analysis.csv   Payment behavior trends
```

---

## Troubleshooting

### "psycopg2 connection refused"

**Problem:** Can't connect to PostgreSQL

**Solution:**
1. Verify PostgreSQL is running: `psql -U postgres -c "SELECT 1"`
2. Check `.env` has correct DB_HOST, DB_PORT, DB_USER
3. If using remote server, verify network access and firewall rules

### "No such file or directory: customers_clean.csv"

**Problem:** Data files not found

**Solution:**
1. Verify you're in the repo root directory: `pwd`
2. Verify CSV files exist: `ls *.csv`
3. Update `DATA_DIR` in `.env` if data files are in a different location

### "permission denied" when running make

**Problem:** Makefile not executable

**Solution:**
```bash
chmod +x Makefile
```

Or just use Python directly:
```bash
python python/eda.py
```

### Out of memory when loading large tables

**Problem:** 100K+ row tables fail to load

**Solution:** The `load_data.py` script loads in batches. If still failing:
1. Use manual SQL COPY (faster): `COPY tablename FROM 'file.csv' CSV HEADER;`
2. Reduce batch size in `load_data.py` (line ~110)

### Validation tests fail

**Problem:** Data validation tests report errors

**Solution:**
1. Verify all data was loaded: `psql -U postgres -d banking_db -c "SELECT COUNT(*) FROM loans;"`
2. Check schema matches expected constraints: `psql -U postgres -d banking_db -c "\d loans"`
3. Run individual tests to identify which constraint failed

---

## Power BI Integration

### Connect to PostgreSQL

1. Open Power BI Desktop
2. Get Data → PostgreSQL Database
3. Server: `localhost` (or your DB_HOST)
4. Database: `banking_db`
5. Username/Password: from `.env`

### Load Tables

Select all 6 tables:
- branches
- customers
- accounts
- loans
- payments
- transactions

### Build Dashboard

Follow the specification in `powerbi/dashboard_spec.md`:
- **Page 1:** Executive Overview (KPIs, trends, regional breakdown)
- **Page 2:** Credit Risk (default rates, delinquency, risk segments)
- **Page 3:** Loan Performance (disbursement trends, product matrix)
- **Page 4:** Customer Analytics (income bands, exposure, segments)

---

## Next Steps

1. ✅ Follow the "Quick Start" above to get data loaded
2. 📊 Check `docs/eda_output.txt` for sample KPIs
3. 🔍 Run `sql/analysis_queries.sql` to explore the portfolio
4. ✅ Run `make validate` to verify data quality
5. 📈 Build Power BI dashboard following `powerbi/dashboard_spec.md`
6. 🐙 Push your Power BI dashboard to GitHub for full reproducibility

---

## Questions?

- Check the README.md for project overview
- Review sql/analysis_queries.sql for all available metrics
- Check powerbi/dashboard_spec.md for BI design details
- Run `python python/data_validation_tests.py` to verify data integrity
