"""테스트용 가짜 봇 실행기"""

import sys
import os

# 상위 디렉토리 import
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

# Mocking bot.mastodon_client.reply to just print
import bot.mastodon_client
bot.mastodon_client.reply = lambda status_id, msg: print(f"🤖 BOT REPLY: {msg}")

from bot.commands import acquire, use, discard, transfer

# 테스트 데이터
TEST_USER_ID = "song.pyeon" # 실제 시트에 있는 유저 ID여야 함 (데이릭 워드)
# 시트 확인 결과: 데이릭 워드의 ID는 비어있을 수 있음. 
# 테스트를 위해 '데이릭 워드'의 ID를 임시로 가정하거나, ID 없이 이름으로 조회하는 로직 필요할 수도.
# 현재 로직은 get_character_by_mastodon_id를 쓰므로, 시트에 ID가 있어야 함.
# -> 'scripts/test_inventory.py' 에서 확인한 바에 따르면 '데이릭 워드'는 존재함.
# -> 하지만 ID 컬럼(B열)이 비어있으면 조회가 안 됨.
# -> 테스트를 위해 get_character_by_mastodon_id를 잠시 이름 기반으로 우회하거나,
# -> 시트의 B열을 채워야 함. (봇 권한으로 채우기?)

# 여기서는 Mocking을 통해 get_character_by_mastodon_id가 '데이릭 워드'를 리턴하게 하자.
import bot.services.character_service
original_get_char = bot.services.character_service.get_character_by_mastodon_id

def mock_get_char(mid):
    # 무조건 데이릭 워드 리턴 (ID 무시)
    from bot.services.character_service import get_character
    char = get_character("데이릭 워드")
    if char:
        return char
    print("❌ Mock Failed: Character '데이릭 워드' not found in sheet")
    return None

bot.services.character_service.get_character_by_mastodon_id = mock_get_char

def run_tests():
    print("🚀 Running Mock Bot Command Tests...")
    user = "test_user"
    status_id = "12345"

    print("\n--- 1. [획득/테스트사과] ---")
    print(acquire.handle(status_id, user, ["테스트사과"]))

    print("\n--- 2. [사용/테스트사과] ---")
    print(use.handle(status_id, user, ["테스트사과"]))

    # 다시 획득 (양도 테스트용)
    acquire.handle(status_id, user, ["테스트사과"])

    print("\n--- 3. [양도/테스트사과/총괄] ---")
    # '총괄' 캐릭터가 시트에 있는지 확인 필요. (아까 리스트에 있었음)
    print(transfer.handle_item(status_id, user, ["테스트사과", "총괄"]))

    print("\n--- 4. [버리기/테스트사과] (없어서 실패해야 정상) ---")
    print(discard.handle(status_id, user, ["테스트사과"]))

    # 다시 획득 (버리기 성공 테스트용)
    acquire.handle(status_id, user, ["테스트사과"])
    print("\n--- 5. [버리기/테스트사과] ---")
    print(discard.handle(status_id, user, ["테스트사과"]))

if __name__ == "__main__":
    run_tests()
