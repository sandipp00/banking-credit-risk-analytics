# Banking Customer & Credit Risk Analytics

## Overview
End-to-end Data Analyst portfolio project for a retail banking scenario. The project analyzes customers, accounts, loans, repayments, and transactions to understand portfolio performance, customer behavior, delinquency, and credit-risk exposure.

## Business Questions
- Which loan products and regions perform best?
- What is the bank's default and delinquency rate?
- How does credit score relate to default risk?
- Which customers represent the largest outstanding exposure?
- Where is credit risk concentrated?
- How is loan disbursement changing over time?

## Tech Stack
Python (Pandas, NumPy), PostgreSQL, SQL, Power BI, Git/GitHub.

## Dataset
Synthetic, reproducible banking dataset created for portfolio/learning use. It contains intentional data-quality issues in the raw customer and loan files so the cleaning workflow can be demonstrated.

| Table | Rows (raw) |
|---|---:|
| customers | 10,025 |
| branches | 40 |
| accounts | 14,000 |
| loans | 18,000 |
| payments | 90,000 |
| transactions | 100,000 |

## Workflow
1. Profile raw data with Python.
2. Remove duplicates, handle missing values, standardize types, and validate ranges.
3. Load cleaned tables into PostgreSQL using `sql/schema.sql`.
4. Run business analysis from `sql/analysis_queries.sql`.
5. Perform EDA with `python/eda.py`.
6. Build the four-page Power BI dashboard using `powerbi/dashboard_spec.md`.

## Data Model
`customers` → `accounts` → `transactions`

`customers` → `loans` → `payments`

`branches` → `accounts` and `loans`

## Key Portfolio Metrics
The analysis calculates total disbursement, outstanding exposure, default rate, average interest rate, delinquency rate, product performance, branch performance, and customer-level risk exposure.

## Limitations
The dataset is synthetic and should not be used for real lending decisions. The project demonstrates analytics methods, data modeling, SQL, Python, and BI reporting.

## Project Structure
```text
banking-credit-risk-analytics/
├── customers.csv / customers_clean.csv
├── accounts.csv / accounts_clean.csv
├── loans.csv / loans_clean.csv
├── payments.csv / payments_clean.csv
├── transactions.csv / transactions_clean.csv
├── branches.csv / branches_clean.csv
├── sql/
├── python/
├── powerbi/
└── docs/
```
