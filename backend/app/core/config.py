"""Application configuration settings."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# JWT configuration
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

# Database connection string
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# External API key for user verification
API_KEY: str = os.getenv("API_KEY", "your-api-key")

# Fernet encryption key (must be 32 url-safe base64-encoded bytes)
FORNET_KEY: bytes = os.getenv("FORNET_KEY", "your-fernet-key").encode()

# Application server host and port
RUN_HOST: str = os.getenv("RUN_HOST", "0.0.0.0")
RUN_PORT: int = int(os.getenv("RUN_PORT", 8000))
