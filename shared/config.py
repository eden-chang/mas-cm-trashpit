"""
중앙 설정 관리 모듈
모든 환경 변수는 이 파일에서 로드하고 검증합니다.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 로드
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def get_env(key: str, default=None, required=False):
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"❌ 필수 환경변수가 누락되었습니다: {key}")
    return value

def get_int(key: str, default=0) -> int:
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default

def get_bool(key: str, default=False) -> bool:
    val = os.getenv(key, str(default)).lower()
    return val in ("true", "1", "yes", "on")

# ============================================================
# Supabase
# ============================================================
SUPABASE_URL = get_env("SUPABASE_URL", required=True)
SUPABASE_SERVICE_KEY = get_env("SUPABASE_SERVICE_KEY", required=True)

# ============================================================
# Mastodon API
# ============================================================
MASTODON_API_BASE_URL = get_env("MASTODON_API_BASE_URL", required=True)
BOT_ACCESS_TOKEN = get_env("BOT_ACCESS_TOKEN", required=True)
SYSTEM_ADMIN_IDS = [x.strip() for x in get_env("SYSTEM_ADMIN_ID", "").split(",") if x.strip()]

# ============================================================
# Logging & Debug
# ============================================================
LOG_LEVEL = get_env("LOG_LEVEL", "INFO")
DEBUG_MODE = get_bool("DEBUG_MODE", False)

# ============================================================
# App Settings
# ============================================================
POLLING_INTERVAL = get_int("POLLING_INTERVAL", 30)
CACHE_TTL = get_int("CACHE_TTL", 3600)

# API Server
API_HOST = get_env("API_HOST", "0.0.0.0")
API_PORT = get_int("API_PORT", 5000)
CORS_ORIGINS = get_env("CORS_ORIGINS", "*").split(",")

# ============================================================
# Inventory links ([가방 링크] 명령어)
# ============================================================
# API와 동일한 서명 키 (32자 이상). 비어 있으면 명령어가 비활성화됨
INVENTORY_LINK_SECRET = get_env("INVENTORY_LINK_SECRET", "")
# 인벤토리 웹 주소 (예: https://inventory.example.com)
INVENTORY_WEB_URL = get_env("INVENTORY_WEB_URL", "")
INVENTORY_LINK_TTL_DAYS = get_int("INVENTORY_LINK_TTL_DAYS", 30)
