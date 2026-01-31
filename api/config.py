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
