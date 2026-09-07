.PHONY: help install setup-db load-data eda run-analysis clean

help:
	@echo "Banking Credit Risk Analytics - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install Python dependencies"
	@echo "  make setup-db         Create PostgreSQL schema"
	@echo "  make load-data        Load cleaned CSV data into database"
	@echo ""
	@echo "Analysis:"
	@echo "  make eda              Run exploratory data analysis"
	@echo "  make run-analysis     Execute all SQL analysis queries"
	@echo "  make validate         Run data quality validation tests"
	@echo ""
	@echo "Full Workflow:"
	@echo "  make all              Run full pipeline: install -> setup-db -> load-data -> eda -> run-analysis"
	@echo "  make clean            Remove generated outputs and cache files"
	@echo ""

install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

setup-db:
	@echo "Setting up PostgreSQL schema..."
	@echo "Make sure PostgreSQL is running and set DB_* environment variables (see .env.example)"
	psql -U $$DB_USER -h $$DB_HOST -d $$DB_NAME -f sql/schema.sql

load-data:
	@echo "Loading cleaned data into PostgreSQL..."
	python python/load_data.py

eda:
	@echo "Running exploratory data analysis..."
	python python/eda.py

run-analysis:
	@echo "Running SQL analysis queries..."
	psql -U $$DB_USER -h $$DB_HOST -d $$DB_NAME -f sql/analysis_queries.sql

validate:
	@echo "Running data quality validation tests..."
	python python/data_validation_tests.py

all: install setup-db load-data eda run-analysis validate
	@echo "✅ Full pipeline complete! Check docs/ for outputs."

clean:
	@echo "Cleaning up generated files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .Python env/ venv/ build/ dist/ *.egg-info/
	@echo "✅ Cleanup complete"
