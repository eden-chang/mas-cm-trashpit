"""[버리기/아이템명] 명령어 핸들러"""

from bot.mastodon_client import reply


def handle(status_id: str, user: str, args: list):
    """
    아이템 버리기 처리

    1. 캐릭터 조회
    2. 아이템 보유 확인 (주변 또는 가방)
    3. 아이템 삭제
    4. 결과 응답
    """
    item_name = args[0]

    # TODO: 구현
    reply(status_id, f"@{user} [버리기] 명령어는 아직 구현 중입니다. 아이템: {item_name}")
