-- 1. Portfolio overview
SELECT COUNT(*) AS total_loans,
       SUM(loan_amount) AS total_disbursed,
       SUM(outstanding_amount) AS outstanding_amount,
       ROUND(100.0 * AVG(default_flag), 2) AS default_rate_pct
FROM loans;

-- 2. Loan performance by product
SELECT loan_type,
       COUNT(*) AS loans,
       ROUND(SUM(loan_amount),2) AS disbursed,
       ROUND(SUM(outstanding_amount),2) AS outstanding,
       ROUND(100.0*AVG(default_flag),2) AS default_rate_pct,
       ROUND(AVG(interest_rate),2) AS avg_interest_rate
FROM loans
GROUP BY loan_type
ORDER BY default_rate_pct DESC;

-- 3. Risk by credit-score band
SELECT CASE WHEN credit_score >= 750 THEN '750+'
            WHEN credit_score >= 700 THEN '700-749'
            WHEN credit_score >= 650 THEN '650-699'
            WHEN credit_score >= 600 THEN '600-649'
            ELSE '<600' END AS score_band,
       COUNT(*) AS customers,
       ROUND(100.0*AVG(l.default_flag),2) AS default_rate_pct,
       ROUND(SUM(l.outstanding_amount),2) AS exposure
FROM customers c
JOIN loans l USING(customer_id)
GROUP BY 1
ORDER BY 1;

-- 4. Monthly disbursement trend
SELECT DATE_TRUNC('month', loan_date)::date AS month,
       COUNT(*) AS loans,
       ROUND(SUM(loan_amount),2) AS disbursed
FROM loans
GROUP BY 1
ORDER BY 1;

-- 5. Top 10 customers by outstanding exposure
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer_name,
       c.credit_score,
       ROUND(SUM(l.outstanding_amount),2) AS exposure
FROM customers c
JOIN loans l USING(customer_id)
GROUP BY c.customer_id, customer_name, c.credit_score
ORDER BY exposure DESC
LIMIT 10;

-- 6. Branch performance
SELECT b.branch_id, b.branch_name, b.city, b.region,
       COUNT(l.loan_id) AS loans,
       ROUND(SUM(l.loan_amount),2) AS disbursed,
       ROUND(SUM(l.outstanding_amount),2) AS outstanding,
       ROUND(100.0*AVG(l.default_flag),2) AS default_rate_pct
FROM branches b
LEFT JOIN loans l USING(branch_id)
GROUP BY b.branch_id, b.branch_name, b.city, b.region
ORDER BY default_rate_pct DESC NULLS LAST;

-- 7. Customers with repeated severe delinquency
SELECT c.customer_id,
       c.first_name || ' ' || c.last_name AS customer_name,
       COUNT(*) FILTER (WHERE p.days_overdue > 30) AS severe_late_payments,
       MAX(p.days_overdue) AS max_days_overdue
FROM customers c
JOIN loans l USING(customer_id)
JOIN payments p USING(loan_id)
GROUP BY c.customer_id, customer_name
HAVING COUNT(*) FILTER (WHERE p.days_overdue > 30) >= 2
ORDER BY severe_late_payments DESC, max_days_overdue DESC;

-- 8. Running monthly disbursement
WITH monthly AS (
    SELECT DATE_TRUNC('month', loan_date)::date AS month,
           SUM(loan_amount) AS disbursed
    FROM loans
    GROUP BY 1
)
SELECT month,
       ROUND(disbursed,2) AS disbursed,
       ROUND(SUM(disbursed) OVER (ORDER BY month),2) AS cumulative_disbursed
FROM monthly
ORDER BY month;

-- 9. Month-over-month growth
WITH monthly AS (
    SELECT DATE_TRUNC('month', loan_date)::date AS month,
           SUM(loan_amount) AS disbursed
    FROM loans
    GROUP BY 1
)
SELECT month,
       ROUND(disbursed,2) AS disbursed,
       ROUND(100.0*(disbursed-LAG(disbursed) OVER(ORDER BY month)) /
             NULLIF(LAG(disbursed) OVER(ORDER BY month),0),2) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- 10. Rank loan products by outstanding exposure within each region
SELECT b.region, l.loan_type,
       SUM(l.outstanding_amount) AS exposure,
       RANK() OVER(PARTITION BY b.region ORDER BY SUM(l.outstanding_amount) DESC) AS exposure_rank
FROM loans l
JOIN branches b USING(branch_id)
GROUP BY b.region, l.loan_type
ORDER BY b.region, exposure_rank;

-- 11. Delinquency by loan type
SELECT l.loan_type,
       COUNT(p.payment_id) AS payments,
       ROUND(100.0*AVG((p.days_overdue > 0)::int),2) AS late_payment_rate_pct,
       ROUND(AVG(p.days_overdue),2) AS avg_days_overdue
FROM loans l
JOIN payments p USING(loan_id)
GROUP BY l.loan_type
ORDER BY late_payment_rate_pct DESC;

-- 12. High-risk exposure concentration
WITH risk AS (
 SELECT c.customer_id,
        c.risk_segment,
        SUM(l.outstanding_amount) AS exposure
 FROM customers c JOIN loans l USING(customer_id)
 GROUP BY c.customer_id,c.risk_segment
), totals AS (SELECT SUM(exposure) total_exposure FROM risk)
SELECT risk_segment,
       COUNT(*) customers,
       ROUND(SUM(exposure),2) exposure,
       ROUND(100.0*SUM(exposure)/MAX(total_exposure),2) exposure_share_pct
FROM risk CROSS JOIN totals
GROUP BY risk_segment
ORDER BY exposure DESC;
