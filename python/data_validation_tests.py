"""
Data validation tests for banking-credit-risk-analytics.
Verifies schema, data quality, and business logic constraints.

Usage:
    pytest python/data_validation_tests.py -v
    
Or run without pytest:
    python python/data_validation_tests.py
"""

import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'banking_db')

class DatabaseValidator:
    """Validate database schema and data quality."""
    
    def __init__(self):
        self.conn = None
        self.passed = 0
        self.failed = 0
    
    def connect(self):
        """Connect to PostgreSQL."""
        try:
            self.conn = psycopg2.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME
            )
            print(f"✅ Connected to {DB_NAME}\n")
        except psycopg2.Error as e:
            print(f"❌ Connection failed: {e}")
            sys.exit(1)
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def query(self, sql):
        """Execute query and return results."""
        cursor = self.conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def test(self, test_name, condition, expected=True):
        """Record test result."""
        if condition == expected:
            print(f"✅ {test_name}")
            self.passed += 1
        else:
            print(f"❌ {test_name} (got {condition}, expected {expected})")
            self.failed += 1
    
    # ==================== Schema Tests ====================
    
    def test_tables_exist(self):
        """Verify all required tables exist."""
        print("📋 Schema Tests\n")
        
        required_tables = ['branches', 'customers', 'accounts', 'loans', 'payments', 'transactions']
        
        for table in required_tables:
            result = self.query(f"""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = '{table}'
                )
            """)
            self.test(f"Table '{table}' exists", result[0][0], True)
    
    def test_indexes_exist(self):
        """Verify performance indexes are created."""
        print("\n📑 Index Tests\n")
        
        indexes = [
            'idx_accounts_customer',
            'idx_loans_customer',
            'idx_loans_date',
            'idx_payments_loan',
            'idx_payments_date',
            'idx_transactions_account',
            'idx_transactions_date',
        ]
        
        for idx in indexes:
            result = self.query(f"""
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes WHERE indexname = '{idx}'
                )
            """)
            self.test(f"Index '{idx}' exists", result[0][0], True)
    
    # ==================== Row Count Tests ====================
    
    def test_row_counts(self):
        """Verify expected row counts after data load."""
        print("\n📊 Row Count Tests\n")
        
        expected_counts = {
            'branches': 40,
            'customers': 10000,
            'accounts': 14000,
            'loans': 18000,
            'payments': 90000,
            'transactions': 100000,
        }
        
        for table, expected in expected_counts.items():
            result = self.query(f"SELECT COUNT(*) FROM {table}")
            actual = result[0][0]
            self.test(f"{table}: {actual} rows (expected {expected})", 
                     actual, expected)
    
    # ==================== Data Quality Tests ====================
    
    def test_no_nulls_in_keys(self):
        """Verify no NULL values in primary keys."""
        print("\n🔑 Primary Key Tests\n")
        
        key_checks = [
            ('branches', 'branch_id'),
            ('customers', 'customer_id'),
            ('accounts', 'account_id'),
            ('loans', 'loan_id'),
            ('payments', 'payment_id'),
            ('transactions', 'transaction_id'),
        ]
        
        for table, key in key_checks:
            result = self.query(f"SELECT COUNT(*) FROM {table} WHERE {key} IS NULL")
            null_count = result[0][0]
            self.test(f"{table}.{key} has no NULLs", null_count, 0)
    
    def test_credit_score_range(self):
        """Verify credit scores are in valid range (300-900)."""
        print("\n💳 Credit Score Tests\n")
        
        result = self.query("""
            SELECT COUNT(*) FROM customers 
            WHERE credit_score < 300 OR credit_score > 900
        """)
        out_of_range = result[0][0]
        self.test("All credit_scores in range [300, 900]", out_of_range, 0)
    
    def test_balance_constraints(self):
        """Verify no negative balances."""
        print("\n💰 Balance Constraint Tests\n")
        
        result = self.query("SELECT COUNT(*) FROM accounts WHERE current_balance < 0")
        negative_balance = result[0][0]
        self.test("No negative account balances", negative_balance, 0)
        
        result = self.query("SELECT COUNT(*) FROM loans WHERE loan_amount < 0")
        negative_loan = result[0][0]
        self.test("No negative loan amounts", negative_loan, 0)
        
        result = self.query("SELECT COUNT(*) FROM loans WHERE outstanding_amount < 0")
        negative_outstanding = result[0][0]
        self.test("No negative outstanding amounts", negative_outstanding, 0)
    
    def test_default_flag_binary(self):
        """Verify default_flag is binary (0 or 1)."""
        print("\n⚠️ Default Flag Tests\n")
        
        result = self.query("""
            SELECT COUNT(*) FROM loans 
            WHERE default_flag NOT IN (0, 1)
        """)
        invalid_default = result[0][0]
        self.test("default_flag is binary (0 or 1)", invalid_default, 0)
    
    def test_referential_integrity(self):
        """Verify foreign key relationships."""
        print("\n🔗 Referential Integrity Tests\n")
        
        # accounts.customer_id -> customers.customer_id
        result = self.query("""
            SELECT COUNT(*) FROM accounts a
            WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.customer_id = a.customer_id)
        """)
        orphaned_accounts = result[0][0]
        self.test("All accounts reference valid customers", orphaned_accounts, 0)
        
        # loans.customer_id -> customers.customer_id
        result = self.query("""
            SELECT COUNT(*) FROM loans l
            WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.customer_id = l.customer_id)
        """)
        orphaned_loans = result[0][0]
        self.test("All loans reference valid customers", orphaned_loans, 0)
        
        # payments.loan_id -> loans.loan_id
        result = self.query("""
            SELECT COUNT(*) FROM payments p
            WHERE NOT EXISTS (SELECT 1 FROM loans l WHERE l.loan_id = p.loan_id)
        """)
        orphaned_payments = result[0][0]
        self.test("All payments reference valid loans", orphaned_payments, 0)
    
    # ==================== Business Logic Tests ====================
    
    def test_portfolio_metrics(self):
        """Verify portfolio-level metrics make sense."""
        print("\n📈 Portfolio Metrics Tests\n")
        
        result = self.query("""
            SELECT 
                COUNT(*) as total_loans,
                SUM(loan_amount) as total_disbursed,
                SUM(outstanding_amount) as total_outstanding,
                ROUND(100.0 * AVG(default_flag), 2) as default_rate_pct
            FROM loans
        """)
        
        total_loans, total_disbursed, total_outstanding, default_rate = result[0]
        
        self.test("Total loans > 0", total_loans > 0, True)
        self.test("Total disbursed > 0", total_disbursed > 0, True)
        self.test("Outstanding < Disbursed", total_outstanding < total_disbursed, True)
        self.test("Default rate in range [0, 100]", 0 <= default_rate <= 100, True)
        
        print(f"   → Total Loans: {total_loans:,}")
        print(f"   → Total Disbursed: ${total_disbursed:,.2f}")
        print(f"   → Total Outstanding: ${total_outstanding:,.2f}")
        print(f"   → Default Rate: {default_rate}%")
    
    def test_interest_rates(self):
        """Verify interest rates are reasonable."""
        print("\n💹 Interest Rate Tests\n")
        
        result = self.query("""
            SELECT 
                MIN(interest_rate) as min_rate,
                MAX(interest_rate) as max_rate,
                AVG(interest_rate) as avg_rate
            FROM loans
        """)
        
        min_rate, max_rate, avg_rate = result[0]
        
        self.test("Minimum interest rate >= 0", min_rate >= 0, True)
        self.test("Maximum interest rate <= 30%", max_rate <= 30, True)
        self.test("Average interest rate in [0, 30]", 0 <= avg_rate <= 30, True)
        
        print(f"   → Min: {min_rate}%, Max: {max_rate}%, Avg: {avg_rate:.2f}%")
    
    def test_no_duplicate_ids(self):
        """Verify IDs are unique within each table."""
        print("\n🆔 Uniqueness Tests\n")
        
        id_columns = [
            ('branches', 'branch_id'),
            ('customers', 'customer_id'),
            ('accounts', 'account_id'),
            ('loans', 'loan_id'),
            ('payments', 'payment_id'),
            ('transactions', 'transaction_id'),
        ]
        
        for table, id_col in id_columns:
            result = self.query(f"""
                SELECT COUNT(*) as total, COUNT(DISTINCT {id_col}) as unique_count
                FROM {table}
            """)
            total, unique_count = result[0]
            self.test(f"{table}.{id_col} is unique ({total} = {unique_count})", 
                     total, unique_count)
    
    # ==================== Summary ====================
    
    def run_all_tests(self):
        """Run all validation tests."""
        print("=" * 70)
        print("Banking Credit Risk Analytics - Data Validation Test Suite")
        print("=" * 70 + "\n")
        
        self.connect()
        
        self.test_tables_exist()
        self.test_indexes_exist()
        self.test_row_counts()
        self.test_no_nulls_in_keys()
        self.test_credit_score_range()
        self.test_balance_constraints()
        self.test_default_flag_binary()
        self.test_referential_integrity()
        self.test_portfolio_metrics()
        self.test_interest_rates()
        self.test_no_duplicate_ids()
        
        self.close()
        
        print("\n" + "=" * 70)
        print(f"Test Results: {self.passed} passed, {self.failed} failed")
        print("=" * 70)
        
        return self.failed == 0

def main():
    """Main entry point."""
    validator = DatabaseValidator()
    success = validator.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
