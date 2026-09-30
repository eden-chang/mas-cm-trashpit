"""Pytest setup: load .env if present, then fill required settings with dummies.

shared.config raises at import time when required variables are missing, so
unit tests (which mock all network calls) need placeholder values to import
the bot and API modules. Real values from .env always take precedence.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_TEST_DEFAULTS = {
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_SERVICE_KEY": "test-service-key",
    "MASTODON_API_BASE_URL": "https://mastodon.example",
    "BOT_ACCESS_TOKEN": "test-access-token",
}

for _key, _value in _TEST_DEFAULTS.items():
    os.environ.setdefault(_key, _value)
