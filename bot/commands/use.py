"""[사용/아이템명] 명령어 핸들러"""

from bot.mastodon_client import reply


def handle(status_id: str, user: str, args: list):
    """
    아이템 사용 처리

    1. 캐릭터 조회 (마스토돈 ID로)
    2. 주변 또는 가방에서 아이템 찾기
    3. 아이템 효과 적용 (스탯 변경)
    4. 아이템 소모
    5. 결과 응답
    """
    item_name = args[0]

    # TODO: 구현
    reply(status_id, f"@{user} [사용] 명령어는 아직 구현 중입니다. 아이템: {item_name}")
