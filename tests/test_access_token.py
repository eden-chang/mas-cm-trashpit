# -*- coding: utf-8 -*-
"""캐릭터별 서명 링크 토큰 테스트"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.access_token import issue_token, verify_token

SECRET = "s" * 32
NOW = 1_700_000_000


def test_round_trip_returns_character_name() -> None:
    token = issue_token("엘리사", SECRET, 3600, now=NOW)
    assert verify_token(token, SECRET, now=NOW + 10) == "엘리사"


def test_expired_token_is_rejected() -> None:
    token = issue_token("엘리사", SECRET, 3600, now=NOW)
    assert verify_token(token, SECRET, now=NOW + 3600) is None


def test_token_signed_with_other_secret_is_rejected() -> None:
    token = issue_token("엘리사", "o" * 32, 3600, now=NOW)
    assert verify_token(token, SECRET, now=NOW) is None


def test_tampered_payload_is_rejected() -> None:
    victim = issue_token("엘리사", SECRET, 3600, now=NOW)
    forged_payload = issue_token("아이작", SECRET, 3600, now=NOW).split(".")[0]
    forged = f"{forged_payload}.{victim.split('.')[1]}"
    assert verify_token(forged, SECRET, now=NOW) is None


@pytest.mark.parametrize("token", [None, "", "abc", "abc.", ".abc", "not-base64.sig"])
def test_malformed_tokens_are_rejected(token) -> None:
    assert verify_token(token, SECRET, now=NOW) is None


def test_short_secret_is_refused() -> None:
    with pytest.raises(ValueError):
        issue_token("엘리사", "short", 3600)
    token = issue_token("엘리사", SECRET, 3600, now=NOW)
    assert verify_token(token, "short", now=NOW) is None
