"""API 환경 설정"""

import os
from dotenv import load_dotenv

load_dotenv()

# Flask 설정
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "5000"))

# CORS 설정
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# 캐시 설정 (Phase 3.3)
# - CACHE_TTL: 기본 캐시 유효시간 (초)
# - CACHE_TTL_ITEMS: 아이템 데이터 캐시 (변경 적음)
# - CACHE_TTL_CHARACTERS: 캐릭터 데이터 캐시 (변경 잦음)
# 환경변수로 오버라이드 가능 (shared/cache.py 참조)
