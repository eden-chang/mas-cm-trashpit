"""[획득/아이템명] 명령어 핸들러"""

from bot.mastodon_client import reply
from bot.config import SYSTEM_ADMIN_IDS


def handle(status_id: str, user: str, args: list):
    """
    아이템 획득 처리 (관리자 전용)

    1. 관리자 권한 확인
    2. 대상 캐릭터 조회
    3. 아이템 정보 조회
    4. 주변에 아이템 추가
    5. 결과 응답
    """
    item_name = args[0]

    # 관리자 권한 확인
    if user not in SYSTEM_ADMIN_IDS:
        reply(status_id, f"@{user} 이 명령어는 관리자만 사용할 수 있습니다.")
        return

    # TODO: 구현
    reply(status_id, f"@{user} [획득] 명령어는 아직 구현 중입니다. 아이템: {item_name}")
