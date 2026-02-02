# -*- coding: utf-8 -*-
"""전투/상태 명령어 유닛 테스트"""

import random
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# ============================================================
# [상태 확인] peek_status
# ============================================================
class TestPeekStatus:
    def test_peek_status_no_character(self):
        """미등록 사용자 — 등록된 캐릭터 없음 메시지"""
        with patch("bot.services.character_service.get_character_by_mastodon_id") as m:
            m.return_value = None
            from bot.commands import peek_status

            result = peek_status.handle("s1", "unknown_user", [])
        assert result == "@unknown_user 등록된 캐릭터를 찾을 수 없습니다."

    def test_peek_status_valid_output(self):
        """정상 출력 포맷 — 근력, 체력, 행운, 포인트, HP, 가방"""
        char = {
            "name": "테스트",
            "strength": 5,
            "health": 10,
            "luck": 3,
            "points": 100,
            "hp": 100,
            "bag": {},
        }
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            from bot.commands import peek_status

            result = peek_status.handle("s1", "test", [])

        assert "상태 확인" in result
        assert "근력 5" in result
        assert "체력 10" in result
        assert "행운 3" in result
        assert "100 포인트 소지" in result
        assert "HP 100/100" in result
        assert "가방 0/20" in result

    def test_peek_status_bag_used_calculation(self):
        """가방 사용량 계산 — volume * qty (character.bag 직접 사용)"""
        char = {
            "name": "테스트",
            "strength": 5,
            "health": 10,
            "luck": 0,
            "points": 0,
            "hp": 100,
            "bag": {"사과": 3},
        }
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("bot.commands.peek_status.get_item_info", return_value={"volume": 2}):
                from bot.commands import peek_status

                result = peek_status.handle("s1", "test", [])

        assert "가방 6/20" in result  # 3*2=6

    def test_peek_status_bag_none_or_empty(self):
        """bag가 None이거나 비어있으면 used 0"""
        char = {"name": "테스트", "strength": 5, "health": 10, "luck": 0, "points": 0, "hp": 100, "bag": None}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            from bot.commands import peek_status

            result = peek_status.handle("s1", "test", [])
        assert "가방 0/20" in result

        char_empty = {**char, "bag": {}}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char_empty):
            result = peek_status.handle("s1", "test", [])
        assert "가방 0/20" in result

    def test_peek_status_unknown_item_in_bag_volume_zero(self):
        """알 수 없는 아이템(get_item_info None)은 volume 0으로 취급"""
        char = {"name": "테스트", "strength": 5, "health": 10, "luck": 0, "points": 0, "hp": 100, "bag": {"미등록아이템": 5}}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("bot.commands.peek_status.get_item_info", return_value=None):
                from bot.commands import peek_status

                result = peek_status.handle("s1", "test", [])
        assert "가방 0/20" in result


# ============================================================
# [공격] attack
# ============================================================
class TestAttack:
    def test_attack_no_character(self):
        """미등록 사용자"""
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=None):
            from bot.commands import attack

            result = attack.handle("s1", "unknown", [])
        assert "등록된 캐릭터를 찾을 수 없습니다" in result

    def test_attack_no_faction(self):
        """진영 없음 — 에러 메시지"""
        char = {"name": "테스트", "faction": "", "strength": 5}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            from bot.commands import attack

            result = attack.handle("s1", "test", [])
        assert "진영 정보가 없습니다" in result

    def test_attack_wega_damage_range(self):
        """웨가: 근력×10+40~80 — random 고정 시 예측 가능"""
        char = {"name": "웨가테스트", "faction": "웨가", "strength": 5}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("random.randint", side_effect=[60]):  # 40~80 중 60
                from bot.commands import attack

                result = attack.handle("s1", "test", [])

        assert "웨이스트 가드" in result
        assert "공격" in result
        assert "근력[5] × 10 + 랜덤값[60]" in result
        assert "110" in result  # 5*10+60=110

    def test_attack_sky_damage_range(self):
        """스카이: 60+20~60 — random 고정"""
        char = {"name": "스카이테스트", "faction": "스카이", "strength": 1}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("random.randint", side_effect=[40]):  # 20~60 중 40
                from bot.commands import attack

                result = attack.handle("s1", "test", [])

        assert "스카이 스크래퍼" in result
        assert "기본값[60] + 랜덤값[40]" in result
        assert "100" in result  # 60+40=100


# ============================================================
# [발사] shoot
# ============================================================
class TestShoot:
    def test_shoot_no_character(self):
        """미등록 사용자"""
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=None):
            from bot.commands import shoot

            result = shoot.handle("s1", "unknown", [])
        assert "등록된 캐릭터를 찾을 수 없습니다" in result

    def test_shoot_no_faction(self):
        """진영 없음 — 에러 메시지"""
        char = {"name": "테스트", "faction": "", "strength": 5}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            from bot.commands import shoot

            result = shoot.handle("s1", "test", [])
        assert "진영 정보가 없습니다" in result

    def test_shoot_wega_damage(self):
        """웨가 발사 — 근력 기반"""
        char = {"name": "웨가", "faction": "wega", "strength": 3}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("random.randint", side_effect=[50]):
                from bot.commands import shoot

                result = shoot.handle("s1", "test", [])

        assert "발사" in result
        assert "80" in result  # 3*10+50=80

    def test_shoot_sky_damage(self):
        """스카이 발사"""
        char = {"name": "스카이", "faction": "sky", "strength": 1}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("random.randint", side_effect=[30]):
                from bot.commands import shoot

                result = shoot.handle("s1", "test", [])

        assert "발사" in result
        assert "90" in result  # 60+30=90


# ============================================================
# [방어] defense
# ============================================================
class TestDefense:
    def test_defense_no_character(self):
        """미등록 사용자"""
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=None):
            from bot.commands import defense

            result = defense.handle("s1", "unknown", [])
        assert "등록된 캐릭터를 찾을 수 없습니다" in result

    def test_defense_valid(self):
        """정상 — 체력×10+1~40"""
        char = {"name": "방어테스트", "health": 10}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("random.randint", side_effect=[25]):
                from bot.commands import defense

                result = defense.handle("s1", "test", [])

        assert "방어" in result
        assert "체력[10] × 10 + 랜덤값[25]" in result
        assert "125" in result  # 10*10+25=125

    def test_defense_health_zero(self):
        """체력 0 허용 — 0×10+랜덤 = 1~40"""
        char = {"name": "체력0", "health": 0}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("random.randint", side_effect=[20]):
                from bot.commands import defense

                result = defense.handle("s1", "test", [])

        assert "체력[0] × 10 + 랜덤값[20]" in result
        assert "20" in result

    def test_defense_invalid_health(self):
        """체력 파싱 실패 — 비숫자/빈 문자열/None"""
        char_bad = {"name": "테스트", "health": "abc"}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char_bad):
            from bot.commands import defense

            result = defense.handle("s1", "test", [])
        assert "체력 값이 올바르지 않습니다" in result

        char_none = {"name": "테스트", "health": None}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char_none):
            result = defense.handle("s1", "test", [])
        assert "체력 정보가 없습니다" in result


# ============================================================
# [회피] dodge
# ============================================================
class TestDodge:
    def test_dodge_no_character(self):
        """미등록 사용자"""
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=None):
            from bot.commands import dodge

            result = dodge.handle("s1", "unknown", [])
        assert "등록된 캐릭터를 찾을 수 없습니다" in result

    def test_dodge_success_rate_bounds(self):
        """luck별 성공률 구간 — roll <= success_rate면 성공"""
        from bot.commands.dodge import _success_rate

        assert _success_rate(0) == 30
        assert _success_rate(-1) == 30
        assert _success_rate(4) == 30
        assert _success_rate(5) == 50
        assert _success_rate(8) == 50
        assert _success_rate(9) == 65
        assert _success_rate(12) == 65
        assert _success_rate(13) == 80
        assert _success_rate(99) == 80

    def test_dodge_fallback_message(self):
        """dodge_service 실패 시 기본 문구 반환 — pick_dodge_message mock, 응답 포맷 포함"""
        char = {"name": "회피테스트", "luck": 10}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("bot.commands.dodge.pick_dodge_message", return_value="회피에 성공했습니다!"):
                with patch("random.randint", side_effect=[50]):  # luck 10 -> 65%, 50<=65 성공
                    from bot.commands import dodge

                    result = dodge.handle("s1", "test", [])

        assert "회피테스트의 회피" in result
        assert "주사위 50" in result
        assert "성공률 65%" in result
        assert "회피에 성공했습니다!" in result

    def test_dodge_invalid_luck_fallback(self):
        """luck 파싱 실패 시 0으로 fallback → 성공률 30%"""
        char = {"name": "회피테스트", "luck": "invalid"}
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("bot.commands.dodge.pick_dodge_message", return_value="회피에 실패했습니다!"):
                with patch("random.randint", side_effect=[50]):  # 50 > 30 -> 실패
                    from bot.commands import dodge

                    result = dodge.handle("s1", "test", [])
        assert "성공률 30%" in result
        assert "회피에 실패했습니다!" in result

    def test_dodge_failure_message(self):
        """roll > success_rate 시 실패 문구 반환"""
        char = {"name": "회피테스트", "luck": 10}  # 65% 성공률
        with patch("bot.services.character_service.get_character_by_mastodon_id", return_value=char):
            with patch("bot.commands.dodge.pick_dodge_message", return_value="회피에 실패했습니다!"):
                with patch("random.randint", side_effect=[90]):  # 90 > 65 -> 실패
                    from bot.commands import dodge

                    result = dodge.handle("s1", "test", [])
        assert "회피테스트의 회피" in result
        assert "주사위 90" in result
        assert "성공률 65%" in result
        assert "회피에 실패했습니다!" in result
