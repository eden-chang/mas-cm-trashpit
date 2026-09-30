# -*- coding: utf-8 -*-
"""양도·지급 명령어 단위·엣지 테스트 (mock 기반)"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bot.main import parse_command
from bot.commands import transfer, grant


# ============================================================
# 파싱·엣지 (parse_command)
# ============================================================
class TestTransferGrantParsing:
    """양도·지급 파싱 및 args 순서 검증"""

    def test_transfer_item_parsing(self):
        r = parse_command("[양도/사과/엘리사]")
        assert r is not None
        assert r[0] == "give_item"
        assert r[1] == ["사과", "엘리사"]

    def test_transfer_item_multi_args_parsing(self):
        r = parse_command("[양도/사과,사과/엘리사]")
        assert r is not None
        assert r[0] == "give_item"
        assert r[1][0] == "사과,사과"
        assert r[1][1] == "엘리사"

    def test_transfer_point_parsing(self):
        r = parse_command("[양도/10포인트/엘리사]")
        assert r is not None
        assert r[0] == "give_point"
        assert r[1] == ["10", "엘리사"]

    def test_transfer_point_zero_parsing(self):
        r = parse_command("[양도/0포인트/엘리사]")
        assert r is not None
        assert r[0] == "give_point"
        assert r[1] == ["0", "엘리사"]

    def test_grant_parsing(self):
        r = parse_command("[지급/홍길동/사과]")
        assert r is not None
        assert r[0] == "grant_item"
        assert r[1] == ["홍길동", "사과"]

    def test_grant_multi_char_parsing(self):
        r = parse_command("[지급/캐릭터1,캐릭터2/아이템]")
        assert r is not None
        assert r[0] == "grant_item"
        assert r[1][0] == "캐릭터1,캐릭터2"
        assert r[1][1] == "아이템"


# ============================================================
# transfer.handle_item (mock)
# ============================================================
@patch("bot.commands.transfer.get_character")
@patch("bot.commands.transfer.get_character_by_mastodon_id")
class TestTransferHandleItem:
    def test_unregistered_user(self, mock_by_mastodon, mock_get_char):
        mock_by_mastodon.return_value = None
        out = transfer.handle_item("status-1", "user", ["사과", "엘리사"])
        assert "등록된 캐릭터를 찾을 수 없습니다" in out

    def test_recipient_not_found(self, mock_by_mastodon, mock_get_char):
        mock_by_mastodon.return_value = {"name": "송신자"}
        mock_get_char.return_value = None
        out = transfer.handle_item("status-1", "user", ["사과", "없는캐릭터"])
        assert "찾을 수 없습니다" in out

    def test_self_transfer(self, mock_by_mastodon, mock_get_char):
        mock_by_mastodon.return_value = {"name": "동일인"}
        mock_get_char.return_value = {"name": "동일인"}
        out = transfer.handle_item("status-1", "user", ["사과", "동일인"])
        assert "자기 자신에게는 양도할 수 없습니다" in out

    def test_args_too_short(self, mock_by_mastodon, mock_get_char):
        out = transfer.handle_item("status-1", "user", ["사과"])
        assert "사용법" in out
        mock_by_mastodon.assert_not_called()

    def test_item_not_held_partial_success(
        self, mock_by_mastodon, mock_get_char
    ):
        mock_by_mastodon.return_value = {"name": "송신자"}
        mock_get_char.return_value = {"name": "수신자", "mastodon_id": "123"}
        with patch("bot.commands.transfer.get_item_info") as mock_item:
            mock_item.return_value = {"volume": 1}
            with patch(
                "bot.commands.transfer.remove_item_by_priority_detailed"
            ) as mock_remove:
                mock_remove.return_value = (0, [])
                out = transfer.handle_item(
                    "status-1", "user", ["없는아이템", "수신자"]
                )
        assert "양도된 아이템이 없습니다" in out
        assert "소지하지 않음" in out


# ============================================================
# transfer.handle_point (mock)
# ============================================================
@patch("bot.commands.transfer.get_character")
@patch("bot.commands.transfer.get_character_by_mastodon_id")
class TestTransferHandlePoint:
    def test_args_too_short(self, mock_by_mastodon, mock_get_char):
        out = transfer.handle_point("status-1", "user", ["10"])
        assert "사용법" in out
        mock_by_mastodon.assert_not_called()

    def test_amount_not_number(self, mock_by_mastodon, mock_get_char):
        out = transfer.handle_point(
            "status-1", "user", ["십포인트", "엘리사"]
        )
        assert "숫자로 입력" in out

    def test_amount_zero_or_negative(self, mock_by_mastodon, mock_get_char):
        out = transfer.handle_point("status-1", "user", ["0", "엘리사"])
        assert "1 이상" in out

    def test_unregistered_user(self, mock_by_mastodon, mock_get_char):
        mock_by_mastodon.return_value = None
        out = transfer.handle_point("status-1", "user", ["10", "엘리사"])
        assert "등록된 캐릭터를 찾을 수 없습니다" in out

    def test_recipient_not_found(self, mock_by_mastodon, mock_get_char):
        mock_by_mastodon.return_value = {"name": "송신자", "points": 100}
        mock_get_char.return_value = None
        out = transfer.handle_point(
            "status-1", "user", ["10", "없는캐릭터"]
        )
        assert "찾을 수 없습니다" in out

    def test_self_transfer(self, mock_by_mastodon, mock_get_char):
        mock_by_mastodon.return_value = {"name": "동일인", "points": 50}
        mock_get_char.return_value = {"name": "동일인"}
        out = transfer.handle_point("status-1", "user", ["10", "동일인"])
        assert "자기 자신에게는 양도할 수 없습니다" in out

    def test_insufficient_points(self, mock_by_mastodon, mock_get_char):
        mock_by_mastodon.return_value = {"name": "송신자", "points": 5}
        mock_get_char.return_value = {"name": "수신자"}
        out = transfer.handle_point("status-1", "user", ["10", "수신자"])
        assert "소지금이 부족합니다" in out
        assert "5" in out


# ============================================================
# grant.handle (mock)
# ============================================================
@patch("bot.commands.grant.SYSTEM_ADMIN_IDS", ["admin_user"])
class TestGrantHandle:
    def test_unauthorized_user(self):
        out = grant.handle(
            "status-1", "normal_user", ["캐릭터", "아이템"]
        )
        assert out is not None
        assert "운영진만 사용할 수 있습니다" in out

    def test_args_too_short(self):
        out = grant.handle("status-1", "admin_user", ["캐릭터만"])
        assert out is not None
        assert "사용법" in out

    def test_empty_recipients_or_items(self):
        out = grant.handle("status-1", "admin_user", ["", "아이템"])
        assert out is not None
        assert "캐릭터와 아이템" in out
