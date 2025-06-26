from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv


class EnvironmentManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._instance is None:  # We could also check for hasattr(self, 'environment')
            self.environment = None
            self.config = {}

    def initialize(self, environment: str) -> None:
        env_file = Path(__file__).parent / f".env.{environment}"
        if not env_file.exists():
            raise FileNotFoundError(
                f"Environment file .env.{environment} not found in {env_file.parent}"
            )

        load_dotenv(env_file)
        self.environment = environment

    @property
    def base_url(self) -> str:
        if not self.environment:
            raise RuntimeError("Environment not initialized")
        return os.getenv('API_BASE_URL')
