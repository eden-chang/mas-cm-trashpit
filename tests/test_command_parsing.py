# -*- coding: utf-8 -*-
"""명령어 파싱 및 화이트리스트 검증 테스트"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bot.main import parse_command


def test_allowed_commands():
    """허용된 명령어는 파싱되어야 함"""
    allowed = [
        "[획득/사과]",
        "[사용/사과]",
        "[버리기/사과]",
        "[설명/아이작]",
        "[상점]",
        "[구매/아이템]",
        "[상태 확인]",
        "[상태확인]",
        "[포인트추가/10/유저]",
        "[포인트차감/5/유저]",
        "[hp/+5]",
        "[체력/-3]",
        "[양도/사과/엘리사]",
        "[양도/10포인트/엘리사]",
        "[지급/홍길동/사과]",
        "[발사]",
        "[공격]",
        "[방어]",
        "[회피]",
    ]
    for cmd in allowed:
        result = parse_command(cmd)
        assert result is not None, f"허용된 명령어가 무시됨: {cmd}"


def test_point_add_deduct_parsing_args():
    """포인트 추가/차감 명령어 파싱 및 args 검증"""
    # [포인트 추가/금액/대상] — 공백 포함
    r = parse_command("[포인트 추가/10/유저]")
    assert r is not None
    assert r[0] == "point_add"
    assert r[1] == ["10", "유저"]

    # [포인트 차감/금액/대상] — 공백 포함
    r = parse_command("[포인트 차감/5/유저]")
    assert r is not None
    assert r[0] == "point_deduct"
    assert r[1] == ["5", "유저"]

    # [포인트추가/금액/대상] — 공백 없음, 금액에 '포인트' 포함
    r = parse_command("[포인트추가/10포인트/캐릭터]")
    assert r is not None
    assert r[0] == "point_add_nospace"
    assert r[1][0] == "10포인트"
    assert r[1][1] == "캐릭터"


def test_transfer_grant_parsing_args_order():
    """양도·지급 명령어 파싱 시 cmd_type 및 args 순서 검증"""
    # [양도/아이템명/캐릭터명] -> give_item
    r = parse_command("[양도/사과/엘리사]")
    assert r is not None
    assert r[0] == "give_item"
    assert r[1] == ["사과", "엘리사"]

    # [양도/n포인트/캐릭터명] -> give_point
    r = parse_command("[양도/10포인트/엘리사]")
    assert r is not None
    assert r[0] == "give_point"
    assert r[1] == ["10", "엘리사"]

    # [지급/캐릭터명/아이템명] -> grant_item (문서·사용자 기대 순서)
    r = parse_command("[지급/홍길동/사과]")
    assert r is not None
    assert r[0] == "grant_item"
    assert r[1] == ["홍길동", "사과"]


def test_shop_description_buy_parsing_args():
    """상점/설명/구매 명령어 파싱 및 args 검증"""
    # [상점] -> shop, []
    r = parse_command("[상점]")
    assert r is not None
    assert r[0] == "shop"
    assert r[1] == []

    # [설명/아이템명]
    r = parse_command("[설명/힐링 포션]")
    assert r is not None
    assert r[0] == "item_description"
    assert r[1] == ["힐링 포션"]

    # [구매/아이템명] — optional quantity group yields None when omitted
    r = parse_command("[구매/사과]")
    assert r is not None
    assert r[0] == "buy"
    assert r[1][0] == "사과"
    assert r[1][1] is None  # 개수 생략 시 두 번째 그룹은 None

    # [설명/아이템명] — 공백 여러 개도 그대로 args로 전달
    r = parse_command("[설명/힐링  포션]")
    assert r is not None
    assert r[0] == "item_description"
    assert r[1] == ["힐링  포션"]

    # [구매/아이템명/n]
    r = parse_command("[구매/사과/3]")
    assert r is not None
    assert r[0] == "buy"
    assert r[1] == ["사과", "3"]

    # 경계: 개수만 다름 (핸들러에서 검증)
    r = parse_command("[구매/아이템/0]")
    assert r is not None
    assert r[0] == "buy"
    assert r[1] == ["아이템", "0"]
    r = parse_command("[구매/아이템/1000]")
    assert r is not None
    assert r[1] == ["아이템", "1000"]


def test_stat_change_parsing():
    """스탯 변경 명령어 파싱 시 cmd_type 및 args 검증"""
    cases = [
        ("[hp/3]", "stat_change", ["hp", "3"]),
        ("[hp/-2]", "stat_change", ["hp", "-2"]),
        ("[hp/+5]", "stat_change", ["hp", "+5"]),
        ("[체력/5]", "stat_change", ["체력", "5"]),
        ("[체력/-5]", "stat_change", ["체력", "-5"]),
        ("[근력/-1]", "stat_change", ["근력", "-1"]),
        ("[근력/0]", "stat_change", ["근력", "0"]),
        ("[행운/+10]", "stat_change", ["행운", "+10"]),
        ("[행운/0]", "stat_change", ["행운", "0"]),
    ]
    for cmd, expected_type, expected_args in cases:
        r = parse_command(cmd)
        assert r is not None, f"명령어가 파싱되어야 함: {cmd}"
        assert r[0] == expected_type, f"cmd_type 불일치: {cmd} -> {r[0]}"
        assert r[1] == expected_args, f"args 불일치: {cmd} -> {r[1]}"

    # HTML 제거 후에도 stat_change 매칭
    r = parse_command("<span>멘션</span> [hp/3]")
    assert r is not None
    assert r[0] == "stat_change"
    assert r[1] == ["hp", "3"]


def test_combat_command_parsing():
    """발사/공격/방어/회피 명령어 파싱 및 cmd_type 검증"""
    cases = [
        ("[발사]", "shoot", []),
        ("[공격]", "attack", []),
        ("[방어]", "defense", []),
        ("[회피]", "dodge", []),
    ]
    for cmd, expected_type, expected_args in cases:
        r = parse_command(cmd)
        assert r is not None, f"명령어가 파싱되어야 함: {cmd}"
        assert r[0] == expected_type, f"cmd_type 불일치: {cmd} -> {r[0]}"
        assert r[1] == expected_args, f"args 불일치: {cmd} -> {r[1]}"


def test_rejected_commands():
    """허용되지 않은 명령어는 무시되어야 함"""
    rejected = [
        "[획득하다/사과]",
        "[나를 위한 설명/아이작]",
    ]
    for cmd in rejected:
        result = parse_command(cmd)
        assert result is None, f"거부되어야 할 명령어가 처리됨: {cmd} -> {result}"
