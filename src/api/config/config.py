import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
import logging

# Load .env from the config directory
config_dir = Path(__file__).parent
load_dotenv(os.path.join(config_dir, '.env'))

class APIConfig:
    """Configuration for API-specific settings (JWT, CORS, etc.)"""
    
    # Load JWT secret key from environment
    try:
        JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
        if not JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY not found in environment variables")
    except Exception as e:
        logging.error("JWT_SECRET_KEY must be set in .env file")
        logging.error("Please create a .env file in src/api/config with JWT_SECRET_KEY=your_secret_key")
        raise e

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']

    # CORS settings
    CORS_ORIGINS = ["http://localhost:5000", "http://127.0.0.1:5000"]
    CORS_METHODS = ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"]
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
    CORS_SUPPORTS_CREDENTIALS = True

    @staticmethod
    def get_token_expires_delta():
        return timedelta(hours=12)
