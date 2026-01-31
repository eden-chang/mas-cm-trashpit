"""봇 환경 설정"""

import os
from dotenv import load_dotenv

load_dotenv()

# 마스토돈 설정
MASTODON_API_BASE_URL = os.getenv("MASTODON_API_BASE_URL", "https://trashpit.site")
BOT_ACCESS_TOKEN = os.getenv("BOT_ACCESS_TOKEN", "")

# 관리자 ID (쉼표로 구분)
SYSTEM_ADMIN_IDS = [
    admin.strip()
    for admin in os.getenv("SYSTEM_ADMIN_ID", "").split(",")
    if admin.strip()
]

# 폴링 간격 (초)
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", "30"))
