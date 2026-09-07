import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE

loans = pd.read_csv(DATA/'loans_clean.csv', parse_dates=['loan_date','maturity_date'])
customers = pd.read_csv(DATA/'customers_clean.csv', parse_dates=['date_of_birth','customer_since'])
payments = pd.read_csv(DATA/'payments_clean.csv', parse_dates=['payment_date'])
accounts = pd.read_csv(DATA/'accounts_clean.csv', parse_dates=['opening_date'])

# Portfolio KPIs
portfolio = {
    'total_loans': len(loans),
    'total_disbursed': loans['loan_amount'].sum(),
    'outstanding': loans['outstanding_amount'].sum(),
    'default_rate_pct': loans['default_flag'].mean()*100,
    'avg_interest_rate_pct': loans['interest_rate'].mean(),
}
print('Portfolio KPIs')
for k,v in portfolio.items(): print(f'{k}: {v:,.2f}' if isinstance(v,(int,float)) else f'{k}: {v}')

# Risk / product analysis
loans['loan_month'] = loans['loan_date'].dt.to_period('M').astype(str)
product = loans.groupby('loan_type').agg(
    loans=('loan_id','count'), disbursed=('loan_amount','sum'),
    outstanding=('outstanding_amount','sum'), default_rate=('default_flag','mean'),
    avg_rate=('interest_rate','mean')
).sort_values('default_rate', ascending=False)
product['default_rate_pct'] = product['default_rate']*100
print('\nLoan product analysis')
print(product[['loans','disbursed','outstanding','default_rate_pct','avg_rate']].round(2))

# Payment behavior
payment_summary = payments.groupby(payments['payment_date'].dt.to_period('M')).agg(
    payments=('payment_id','count'), avg_days_overdue=('days_overdue','mean'),
    severe_late_rate=('days_overdue', lambda x: (x>30).mean()*100)
)
print('\nRecent payment behavior')
print(payment_summary.tail(12).round(2))

# Customer-level exposure
cust_exposure = loans.groupby('customer_id').agg(
    loans=('loan_id','count'), exposure=('outstanding_amount','sum'), defaults=('default_flag','sum')
).reset_index().merge(customers[['customer_id','credit_score','risk_segment','annual_income']], on='customer_id')
cust_exposure['exposure_to_income'] = cust_exposure['exposure']/cust_exposure['annual_income'].replace(0,pd.NA)
print('\nTop 10 exposure customers')
print(cust_exposure.sort_values('exposure',ascending=False).head(10).round(2).to_string(index=False))

# Save analysis outputs for Power BI/reference
OUT = BASE/'docs'
OUT.mkdir(exist_ok=True)
product.reset_index().to_csv(OUT/'loan_product_analysis.csv',index=False)
payment_summary.reset_index().to_csv(OUT/'payment_monthly_analysis.csv',index=False)
cust_exposure.to_csv(OUT/'customer_exposure_analysis.csv',index=False)
