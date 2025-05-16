#!/usr/bin/env python3
"""
Migration script to migrate from old database models to new models
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from src.config.db_migrate_new_models import run_all_migrations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    # Load environment variables
    env_path = script_dir / 'src' / 'config' / 'environments' / '.env.local'
    if env_path.exists():
        logger.info(f"Loading environment from {env_path}")
        load_dotenv(env_path)
    else:
        logger.warning(f"No .env.local file found at {env_path}. Using existing environment variables.")
    
    try:
        logger.info("Starting migration to new database models")
        run_all_migrations()
        logger.info("Migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 