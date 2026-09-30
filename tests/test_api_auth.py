# -*- coding: utf-8 -*-
"""API 인증 테스트: 캐릭터 링크 토큰과 관리자 토큰"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api import config
from api.app import app
from shared.access_token import issue_token

SECRET = "l" * 32
ADMIN = "a" * 32


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(config, "INVENTORY_LINK_SECRET", SECRET)
    monkeypatch.setattr(config, "ADMIN_API_TOKEN", ADMIN)
    app.config["TESTING"] = True
    return app.test_client()


def _headers(name: str) -> dict:
    return {"X-Character-Token": issue_token(name, SECRET, 3600)}


@pytest.mark.parametrize("method,path", [
    ("get", "/api/character/엘리사"),
    ("get", "/api/bag/엘리사"),
    ("post", "/api/bag/엘리사"),
    ("get", "/api/nearby/엘리사"),
    ("post", "/api/nearby/엘리사/move"),
])
def test_character_endpoints_require_token(client, method, path) -> None:
    with patch("api.routes.bag.get_character_by_name") as lookup:
        response = getattr(client, method)(path, json={})
    assert response.status_code == 401
    lookup.assert_not_called()


def test_token_for_another_character_is_forbidden(client) -> None:
    with patch("api.routes.bag.get_character_by_name") as lookup:
        response = client.post("/api/bag/엘리사", json={"items": []}, headers=_headers("아이작"))
    assert response.status_code == 403
    lookup.assert_not_called()


def test_valid_token_reaches_the_route(client) -> None:
    with patch("api.routes.bag.get_character_by_name", return_value=None) as lookup:
        response = client.get("/api/bag/엘리사", headers=_headers("엘리사"))
    assert response.status_code == 404
    lookup.assert_called_once_with("엘리사")


def test_missing_secret_disables_character_api(client, monkeypatch) -> None:
    monkeypatch.setattr(config, "INVENTORY_LINK_SECRET", "")
    response = client.get("/api/bag/엘리사", headers=_headers("엘리사"))
    assert response.status_code == 503


def test_admin_requires_bearer_token(client) -> None:
    assert client.get("/api/admin/cache/stats").status_code == 401
    assert client.post("/api/admin/cache/clear", headers={"Authorization": "Bearer wrong"}).status_code == 401
    ok = client.get("/api/admin/cache/stats", headers={"Authorization": f"Bearer {ADMIN}"})
    assert ok.status_code == 200


def test_admin_disabled_without_token(client, monkeypatch) -> None:
    monkeypatch.setattr(config, "ADMIN_API_TOKEN", "")
    response = client.get("/api/admin/cache/stats", headers={"Authorization": "Bearer "})
    assert response.status_code == 503
