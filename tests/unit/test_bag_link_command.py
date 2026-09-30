# -*- coding: utf-8 -*-
"""[가방 링크] 명령어 단위 테스트"""

import sys
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot import main
from bot.commands import bag_link
from shared import config
from shared.access_token import verify_token

SECRET = "b" * 32
CHARACTER = {"name": "엘리사", "mastodon_id": "elisa"}


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setattr(config, "INVENTORY_LINK_SECRET", SECRET)
    monkeypatch.setattr(config, "INVENTORY_WEB_URL", "https://inventory.example/")
    monkeypatch.setattr(config, "INVENTORY_LINK_TTL_DAYS", 7)


def test_issues_link_for_the_requesting_accounts_character(configured) -> None:
    with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=CHARACTER):
        result = bag_link.handle("status-1", "elisa", [])
    link = result.splitlines()[-1]
    assert link.startswith("https://inventory.example/#token=")
    token = parse_qs(urlparse(link).fragment)["token"][0]
    assert verify_token(token, SECRET) == "엘리사"
    assert "7일" in result


def test_unregistered_account_gets_no_link(configured) -> None:
    with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=None):
        result = bag_link.handle("status-1", "stranger", [])
    assert "token=" not in result


def test_disabled_when_not_configured(monkeypatch) -> None:
    monkeypatch.setattr(config, "INVENTORY_LINK_SECRET", "")
    with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=CHARACTER):
        result = bag_link.handle("status-1", "elisa", [])
    assert "설정되지 않았습니다" in result


def test_link_is_always_sent_as_direct_message(configured) -> None:
    notification = {
        "type": "mention",
        "account": {"acct": "elisa"},
        "status": {"id": "1", "content": "<p>@bot [가방 링크]</p>", "visibility": "public"},
    }
    with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=CHARACTER), \
            patch("bot.main.reply") as reply:
        main.on_notification(notification)
    assert reply.call_args.kwargs["visibility"] == "direct"
