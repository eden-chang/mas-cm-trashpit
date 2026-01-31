"""구글 시트 연결 모듈"""

import os
import gspread
from google.oauth2.service_account import Credentials

from .constants import SHEET_ID

# 구글 시트 API 범위
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_client = None
_spreadsheet = None


def get_client() -> gspread.Client:
    """구글 시트 클라이언트 반환 (싱글톤)"""
    global _client

    if _client is None:
        creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        _client = gspread.authorize(credentials)

    return _client


def get_spreadsheet() -> gspread.Spreadsheet:
    """스프레드시트 객체 반환 (싱글톤)"""
    global _spreadsheet

    if _spreadsheet is None:
        client = get_client()
        _spreadsheet = client.open_by_key(SHEET_ID)

    return _spreadsheet


def get_worksheet(name: str) -> gspread.Worksheet:
    """워크시트 객체 반환"""
    spreadsheet = get_spreadsheet()
    return spreadsheet.worksheet(name)
