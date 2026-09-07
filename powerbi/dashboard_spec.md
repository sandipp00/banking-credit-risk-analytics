# Power BI Dashboard Specification

## Page 1 — Executive Overview
KPIs: Total Customers, Total Loans, Total Disbursed, Outstanding Exposure, Default Rate, Average Interest Rate.

Visuals: monthly disbursement line chart; loan-type exposure bar chart; default-rate by product; regional map/bar; customer risk mix.

## Page 2 — Credit Risk
Visuals: default rate by credit-score band; default rate by employment type; default rate by loan type; high-risk exposure; delinquency trend.

Slicers: region, branch, loan type, risk segment, loan status, loan date.

## Page 3 — Loan Performance
Visuals: disbursement trend, outstanding trend, loan product matrix, branch performance table, interest-rate distribution.

## Page 4 — Customer Analytics
Visuals: customer income bands, balance distribution, customer risk segments, top exposure customers, loan count per customer.

## Core DAX measures
```DAX
Total Loans = COUNTROWS(loans)
Total Disbursed = SUM(loans[loan_amount])
Outstanding Exposure = SUM(loans[outstanding_amount])
Default Rate = DIVIDE(SUM(loans[default_flag]), [Total Loans])
Average Interest Rate = AVERAGE(loans[interest_rate])
```
Format Default Rate as percentage.
