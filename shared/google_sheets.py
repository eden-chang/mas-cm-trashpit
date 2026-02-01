"""구글 시트 연결 모듈 (Enhanced)"""

import time
import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, GSpreadException

from . import config

# 구글 시트 API 범위
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_client = None
_spreadsheet = None

def _retry(func, retries=3, delay=2):
    """간단한 재시도 데코레이터 (Tenacity 대체)"""
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except (APIError, GSpreadException, ConnectionError) as e:
                last_exception = e
                print(f"⚠️ Google Sheets API Error (Attempt {attempt+1}/{retries}): {e}")
                time.sleep(delay * (attempt + 1))  # Exponential Backoff
        raise last_exception
    return wrapper

def get_client() -> gspread.Client:
    """구글 시트 클라이언트 반환 (싱글톤)"""
    global _client

    if _client is None:
        try:
            creds_path = config.GOOGLE_CREDENTIALS_PATH
            credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
            _client = gspread.authorize(credentials)
        except Exception as e:
            print(f"❌ Failed to authorize Google Sheets: {e}")
            raise e

    return _client

@_retry
def get_spreadsheet() -> gspread.Spreadsheet:
    """스프레드시트 객체 반환 (싱글톤 + Retry)"""
    global _spreadsheet

    if _spreadsheet is None:
        client = get_client()
        _spreadsheet = client.open_by_key(config.SHEET_ID)

    return _spreadsheet

@_retry
def get_worksheet(name: str) -> gspread.Worksheet:
    """워크시트 객체 반환 (Retry)"""
    spreadsheet = get_spreadsheet()
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        print(f"❌ Worksheet not found: {name}")
        raise
