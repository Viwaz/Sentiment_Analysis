"""
src/config.py
Centralised configuration — all settings are read from environment variables
so they work transparently both in local dev and inside Docker containers.
"""

from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# PostgreSQL connection
# ---------------------------------------------------------------------------
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
DB_NAME: str = os.getenv("DB_NAME", "sentiment_db")
DB_USER: str = os.getenv("DB_USER", "sentiment_user")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "changeme")

# ---------------------------------------------------------------------------
# JWT authentication
# ---------------------------------------------------------------------------
# IMPORTANT: override JWT_SECRET_KEY with a strong random value in production.
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# ---------------------------------------------------------------------------
# Groq LLM Insight Engine
# ---------------------------------------------------------------------------
# Set GROQ_API_KEY in your .env file or environment variables.
# Get a free key at: https://console.groq.com/keys
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

