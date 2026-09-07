"""
Automated data loading script for banking-credit-risk-analytics.
Loads cleaned CSV files into PostgreSQL database.

Usage:
    python python/load_data.py

Environment variables required (from .env):
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
"""

import os
import sys
from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'banking_db')
DATA_DIR = Path(os.getenv('DATA_DIR', '.'))

# Data files to load (table_name, csv_filename)
DATA_FILES = [
    ('branches', 'branches_clean.csv'),
    ('customers', 'customers_clean.csv'),
    ('accounts', 'accounts_clean.csv'),
    ('loans', 'loans_clean.csv'),
    ('payments', 'payments_clean.csv'),
    ('transactions', 'transactions_clean.csv'),
]

def get_connection():
    """Establish database connection."""
    try:
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        return conn
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def load_table(conn, table_name, csv_file):
    """Load a single table from CSV file."""
    file_path = DATA_DIR / csv_file
    
    if not file_path.exists():
        print(f"⚠️  Skipping {table_name}: file not found ({file_path})")
        return False
    
    try:
        df = pd.read_csv(file_path)
        
        # Convert date columns
        if table_name == 'customers':
            df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
            df['customer_since'] = pd.to_datetime(df['customer_since'], errors='coerce')
        elif table_name == 'accounts':
            df['opening_date'] = pd.to_datetime(df['opening_date'], errors='coerce')
        elif table_name == 'loans':
            df['loan_date'] = pd.to_datetime(df['loan_date'], errors='coerce')
            df['maturity_date'] = pd.to_datetime(df['maturity_date'], errors='coerce')
        elif table_name == 'payments':
            df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')
        elif table_name == 'transactions':
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # Insert via cursor
        cursor = conn.cursor()
        
        # Build INSERT statement
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # Insert rows in batches
        batch_size = 1000
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            for _, row in batch.iterrows():
                cursor.execute(insert_query, tuple(row))
            conn.commit()
            print(f"  ✓ {table_name}: {min(i+batch_size, len(df))}/{len(df)} rows loaded")
        
        cursor.close()
        print(f"✅ {table_name}: {len(df)} rows loaded successfully")
        return True
    
    except Exception as e:
        print(f"❌ Failed to load {table_name}: {e}")
        conn.rollback()
        return False

def main():
    """Main loading pipeline."""
    print("🔄 Starting data load pipeline...\n")
    
    conn = get_connection()
    print(f"✅ Connected to {DB_NAME} on {DB_HOST}\n")
    
    success_count = 0
    for table_name, csv_file in DATA_FILES:
        if load_table(conn, table_name, csv_file):
            success_count += 1
        print()
    
    conn.close()
    
    print(f"📊 Summary: {success_count}/{len(DATA_FILES)} tables loaded successfully")
    if success_count == len(DATA_FILES):
        print("✅ Data pipeline complete!")
        return 0
    else:
        print("⚠️  Some tables failed to load. Check error messages above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
