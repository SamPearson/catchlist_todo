#!/usr/bin/env python3
from src.config.db_migrate import run_migrations

if __name__ == "__main__":
    print("Running database migrations...")
    run_migrations()
    print("Migrations completed successfully.") 