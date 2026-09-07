CREATE TABLE branches (
    branch_id INT PRIMARY KEY,
    branch_name VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    region VARCHAR(30) NOT NULL,
    branch_type VARCHAR(30) NOT NULL
);

CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    gender VARCHAR(20),
    date_of_birth DATE,
    city VARCHAR(100),
    state VARCHAR(100),
    occupation VARCHAR(100),
    employment_type VARCHAR(50),
    annual_income NUMERIC(15,2),
    credit_score INT CHECK (credit_score BETWEEN 300 AND 900),
    customer_since DATE,
    risk_segment VARCHAR(20)
);

CREATE TABLE accounts (
    account_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    branch_id INT NOT NULL REFERENCES branches(branch_id),
    account_type VARCHAR(30) NOT NULL,
    opening_date DATE,
    current_balance NUMERIC(18,2) CHECK (current_balance >= 0),
    account_status VARCHAR(20)
);

CREATE TABLE loans (
    loan_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
    branch_id INT NOT NULL REFERENCES branches(branch_id),
    loan_type VARCHAR(30) NOT NULL,
    loan_amount NUMERIC(18,2) CHECK (loan_amount >= 0),
    interest_rate NUMERIC(6,2) CHECK (interest_rate >= 0),
    tenure_months INT,
    loan_date DATE,
    maturity_date DATE,
    loan_status VARCHAR(20),
    outstanding_amount NUMERIC(18,2) CHECK (outstanding_amount >= 0),
    default_flag INT CHECK (default_flag IN (0,1))
);

CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    loan_id BIGINT NOT NULL REFERENCES loans(loan_id),
    payment_date DATE,
    due_amount NUMERIC(18,2) CHECK (due_amount >= 0),
    payment_amount NUMERIC(18,2) CHECK (payment_amount >= 0),
    days_overdue INT CHECK (days_overdue >= 0),
    payment_status VARCHAR(30)
);

CREATE TABLE transactions (
    transaction_id BIGINT PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES accounts(account_id),
    transaction_date TIMESTAMP,
    transaction_type VARCHAR(30),
    amount NUMERIC(18,2) CHECK (amount >= 0),
    merchant_category VARCHAR(50),
    channel VARCHAR(30),
    transaction_status VARCHAR(20)
);

CREATE INDEX idx_accounts_customer ON accounts(customer_id);
CREATE INDEX idx_loans_customer ON loans(customer_id);
CREATE INDEX idx_loans_date ON loans(loan_date);
CREATE INDEX idx_payments_loan ON payments(loan_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
