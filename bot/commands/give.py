"""[양도/...] 명령어 핸들러"""

from bot.mastodon_client import reply


def handle_item(status_id: str, user: str, args: list):
    """
    아이템 양도 처리

    1. 보내는 캐릭터 조회
    2. 받는 캐릭터 조회
    3. 아이템 보유 확인
    4. 아이템 이동
    5. 결과 응답
    """
    item_name = args[0]
    target_name = args[1]

    # TODO: 구현
    reply(status_id, f"@{user} [양도] 명령어는 아직 구현 중입니다. 아이템: {item_name}, 대상: {target_name}")


def handle_point(status_id: str, user: str, args: list):
    """
    포인트 양도 처리

    1. 보내는 캐릭터 조회
    2. 받는 캐릭터 조회
    3. 포인트 잔액 확인
    4. 포인트 이동
    5. 결과 응답
    """
    amount = int(args[0])
    target_name = args[1]

    # TODO: 구현
    reply(status_id, f"@{user} [포인트 양도] 명령어는 아직 구현 중입니다. 금액: {amount}, 대상: {target_name}")
