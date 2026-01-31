# Phase 1: 기본 인프라 구축 - 상세 기획서

## 📋 Phase 1 목표

**기간**: 1주 (7일)

**목표**: 
- 구글 시트 데이터 구조 완성
- 마스토돈 봇 기본 명령어 구현
- Flask API 서버 구축
- 웹 페이지 기본 틀 완성

**완료 기준**:
- GM이 시트에서 아이템을 추가하면 봇이 마스토돈에 알림을 보낼 수 있음
- 플레이어가 [사용], [양도] 명령어를 사용할 수 있음
- 웹에서 캐릭터의 가방/여유공간/주변 아이템을 조회할 수 있음

---

## 🗂️ Task 1: 구글 시트 설계 및 구축

**소요 시간**: 1일

### 1-1. 시트 구조 설계

#### Sheet 1: 캐릭터 정보 (characters)

**목적**: 캐릭터의 기본 스탯과 인벤토리 메타 정보 관리

**컬럼 구조**:
```
A열: 캐릭터명 (Primary Key)
B열: 근력
C열: 가방용량 (계산값)
D열: 마지막수정시각
E열: 마스토돈ID (선택)
F열: 활성상태 (Y/N)
```

**샘플 데이터**:
```
| 캐릭터명 | 근력 | 가방용량 | 마지막수정시각        | 마스토돈ID  | 활성상태 |
|---------|------|---------|---------------------|------------|---------|
| 발트     | 5    | 20      | 2026-01-30 14:23:45 | @walt      | Y       |
| 엘리사   | 8    | 40      | 2026-01-30 14:20:12 | @elisa     | Y       |
| 카인     | 12   | 60      | 2026-01-30 13:15:30 | @cain      | Y       |
```

**검증 규칙**:
- 근력: 1~15 범위
- 가방용량: 근력에 따라 자동 계산 (공식: `=IF(B2<=5,20,IF(B2<=10,40,60))`)
- 마지막수정시각: ISO 8601 형식

---

#### Sheet 2: 가방 (bag)

**목적**: 캐릭터가 실제로 들고 다니는 아이템 관리

**컬럼 구조**:
```
A열: ID (자동생성, bag_001)
B열: 캐릭터명 (Foreign Key)
C열: 아이템명
D열: 수량
E열: 개당부피
F열: 총부피 (계산값)
```

**샘플 데이터**:
```
| ID      | 캐릭터명 | 아이템명 | 수량 | 개당부피 | 총부피 |
|---------|---------|---------|------|---------|-------|
| bag_001 | 발트     | 사과     | 3    | 1       | 3     |
| bag_002 | 발트     | 물병     | 2    | 2       | 4     |
| bag_003 | 발트     | 손전등   | 1    | 3       | 3     |
| bag_004 | 엘리사   | 칼       | 1    | 4       | 4     |
| bag_005 | 엘리사   | 로프     | 1    | 3       | 3     |
```

**검증 규칙**:
- 총부피 공식: `=D2*E2`
- 같은 캐릭터의 총부피 합계는 가방용량 이하여야 함

**헬퍼 공식** (별도 셀에 배치):
```
// 발트의 가방 사용량 계산
=SUMIF(bag!B:B,"발트",bag!F:F)

// 발트의 가방 잔여 공간
=VLOOKUP("발트",characters!A:C,3,FALSE)-SUMIF(bag!B:B,"발트",bag!F:F)
```

---

#### Sheet 3: 여유 공간 (misc_space)

**목적**: 부피 0 아이템 관리 (텍스트 리스트 형식)

**컬럼 구조**:
```
A열: 캐릭터명 (Primary Key)
B열: 아이템목록 (쉼표 구분)
```

**샘플 데이터**:
```
| 캐릭터명 | 아이템목록 |
|---------|-----------|
| 발트     | 클립, 클립, 동전, 동전, 동전, 성냥 |
| 엘리사   | 종이쪽지, 펜 |
| 카인     | |
```

**데이터 형식**:
- 같은 아이템 여러 개: 반복 나열 (`클립, 클립, 클립`)
- 빈 경우: 빈 셀

**조작 로직**:
```python
# 추가: "클립, 클립" → "클립, 클립, 클립"
# 삭제: "클립, 클립, 클립" → "클립, 클립" (한 개 제거)
# 전체 개수: "클립".count() = 3개
```

---

#### Sheet 4: 주변 (nearby)

**목적**: 획득했지만 아직 가방에 넣지 않은 임시 아이템 관리

**컬럼 구조**:
```
A열: ID (자동생성, nearby_001)
B열: 캐릭터명 (Foreign Key)
C열: 아이템명
D열: 수량
E열: 개당부피
F열: 총부피 (계산값)
G열: 획득시각
H열: 만료시각
I열: 출처 (GM지급/조사발견/전투보상 등)
```

**샘플 데이터**:
```
| ID         | 캐릭터명 | 아이템명   | 수량 | 개당부피 | 총부피 | 획득시각             | 만료시각             | 출처     |
|-----------|---------|-----------|------|---------|-------|---------------------|---------------------|---------|
| nearby_001| 발트     | 의료키트   | 1    | 5       | 5     | 2026-01-30 14:20:00 | 2026-01-31 00:00:00 | GM지급   |
| nearby_002| 발트     | 로프       | 1    | 3       | 3     | 2026-01-30 14:20:00 | 2026-01-31 00:00:00 | GM지급   |
| nearby_003| 발트     | 배터리     | 2    | 1       | 2     | 2026-01-30 14:50:00 | 2026-01-31 00:00:00 | 조사발견 |
```

**만료시각 자동 계산**:
```
// 획득시각의 같은 날 자정
=DATE(YEAR(G2),MONTH(G2),DAY(G2))+1

// 또는 획득 후 12시간
=G2+0.5
```

**검증 규칙**:
- 만료시각은 획득시각보다 미래
- 만료시각 도달 시 자동 삭제 (크론잡)

---

#### Sheet 5: 상점 (shop)

**목적**: 게임 내 모든 아이템의 마스터 데이터

**컬럼 구조**:
```
A열: 아이템명 (Primary Key)
B열: 부피
C열: 사용가능 (Y/N)
D열: 효과 (텍스트)
E열: 설명
F열: 카테고리 (소모품/장비/기타)
G열: 희귀도 (일반/희귀/전설)
```

**샘플 데이터**:
```
| 아이템명     | 부피 | 사용가능 | 효과        | 설명                  | 카테고리 | 희귀도 |
|------------|------|---------|------------|----------------------|---------|-------|
| 사과        | 1    | Y       | 체력+3      | 신선한 빨간 사과       | 소모품   | 일반   |
| 물병        | 2    | Y       | 갈증-5      | 생수 500ml            | 소모품   | 일반   |
| 의료 키트   | 5    | Y       | 체력+10     | 응급처치 도구 세트     | 소모품   | 희귀   |
| 손전등      | 3    | N       | -          | LED 손전등            | 장비     | 일반   |
| 칼          | 4    | N       | 공격+2      | 전투용 나이프          | 장비     | 일반   |
| 로프        | 3    | N       | -          | 10m 등산용 로프        | 기타     | 일반   |
| 배터리      | 1    | N       | -          | AA 건전지             | 소모품   | 일반   |
| 클립        | 0    | N       | -          | 작은 종이 클립         | 기타     | 일반   |
| 동전        | 0    | N       | -          | 10원 동전             | 기타     | 일반   |
| 성냥        | 0    | Y       | -          | 성냥 1개              | 소모품   | 일반   |
| INTP-X 약물 | 1    | Y       | 특수효과    | 실험용 약물            | 소모품   | 전설   |
```

**효과 형식**:
```
단일 효과: "체력+3"
복합 효과: "체력+5, 갈증-3"
특수 효과: "특수효과" (별도 처리)
효과 없음: "-"
```

---

#### Sheet 6: 로그 (logs) - 선택 사항

**목적**: 모든 아이템 이동 및 사용 기록 (디버깅/감사용)

**컬럼 구조**:
```
A열: ID (자동생성)
B열: 타임스탬프
C열: 캐릭터명
D열: 액션 (획득/사용/양도/삭제)
E열: 아이템명
F열: 수량
G열: 상세 (JSON 또는 텍스트)
```

**샘플 데이터**:
```
| ID   | 타임스탬프           | 캐릭터명 | 액션 | 아이템명 | 수량 | 상세 |
|------|---------------------|---------|------|---------|------|------|
| log_001 | 2026-01-30 14:20:00 | 발트  | 획득 | 사과    | 3    | GM 지급 |
| log_002 | 2026-01-30 14:25:30 | 발트  | 사용 | 사과    | 1    | 체력 45→48 |
| log_003 | 2026-01-30 14:30:15 | 발트  | 양도 | 로프    | 1    | 수령자: 엘리사 |
```

---

### 1-2. 구글 시트 API 설정

**작업 순서**:

1. **Google Cloud Console 프로젝트 생성**
   ```
   1. https://console.cloud.google.com 접속
   2. 새 프로젝트 생성: "TRPG-Inventory"
   3. 프로젝트 ID 기록
   ```

2. **Google Sheets API 활성화**
   ```
   1. API 및 서비스 > 라이브러리
   2. "Google Sheets API" 검색
   3. 사용 설정 클릭
   ```

3. **서비스 계정 생성**
   ```
   1. API 및 서비스 > 사용자 인증 정보
   2. 사용자 인증 정보 만들기 > 서비스 계정
   3. 이름: "inventory-bot"
   4. 역할: 편집자
   5. JSON 키 다운로드 → credentials.json
   ```

4. **시트 공유 설정**
   ```
   1. 구글 시트 생성: "TRPG 인벤토리 데이터"
   2. 서비스 계정 이메일 복사 (예: inventory-bot@xxx.iam.gserviceaccount.com)
   3. 시트 공유 > 편집자로 추가
   ```

---

### 1-3. 초기 데이터 입력

**작업 내용**:
1. 각 시트 생성 (6개)
2. 헤더 행 입력
3. 샘플 캐릭터 3명 입력
4. 상점 아이템 10개 입력
5. 테스트용 가방 아이템 몇 개 입력

**완료 체크리스트**:
- [ ] 6개 시트 모두 생성됨
- [ ] 헤더 행이 정확히 입력됨
- [ ] 샘플 데이터가 입력됨
- [ ] 공식이 정상 작동함
- [ ] 서비스 계정이 시트에 접근 가능함

---

## 🤖 Task 2: 마스토돈 봇 구현

**소요 시간**: 2일

### 2-1. 환경 설정

**디렉토리 구조**:
```
trpg-inventory/
├── bot/
│   ├── __init__.py
│   ├── main.py           # 봇 메인 로직
│   ├── commands.py       # 명령어 처리
│   ├── sheets.py         # 구글 시트 연동
│   └── utils.py          # 유틸리티 함수
├── credentials.json      # 구글 시트 인증
├── .env                  # 환경변수
└── requirements.txt      # 의존성
```

**requirements.txt**:
```txt
Mastodon.py==1.8.1
gspread==5.12.0
oauth2client==4.1.3
python-dotenv==1.0.0
```

**.env 파일**:
```env
# 마스토돈 설정
MASTODON_ACCESS_TOKEN=your_access_token_here
MASTODON_INSTANCE_URL=https://your.mastodon.instance

# 구글 시트 설정
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json

# 봇 설정
BOT_COMMAND_PREFIX=@봇
GM_ACCOUNTS=admin1,admin2,admin3
```

---

### 2-2. 구글 시트 연동 모듈 (sheets.py)

```python
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

class InventorySheets:
    def __init__(self):
        """구글 시트 초기화"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        
        self.client = gspread.authorize(creds)
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.workbook = self.client.open_by_key(self.sheet_id)
        
        # 각 시트 로드
        self.characters_sheet = self.workbook.worksheet('characters')
        self.bag_sheet = self.workbook.worksheet('bag')
        self.misc_sheet = self.workbook.worksheet('misc_space')
        self.nearby_sheet = self.workbook.worksheet('nearby')
        self.shop_sheet = self.workbook.worksheet('shop')
        self.logs_sheet = self.workbook.worksheet('logs')
    
    # ========== 캐릭터 정보 ==========
    
    def get_character(self, name):
        """캐릭터 정보 조회"""
        try:
            cell = self.characters_sheet.find(name)
            if not cell:
                return None
            
            row = cell.row
            data = self.characters_sheet.row_values(row)
            
            return {
                'name': data[0],
                'strength': int(data[1]),
                'capacity': int(data[2]),
                'last_update': data[3],
                'mastodon_id': data[4] if len(data) > 4 else '',
                'active': data[5] if len(data) > 5 else 'Y'
            }
        except Exception as e:
            print(f"Error getting character: {e}")
            return None
    
    def update_timestamp(self, name):
        """마지막 수정 시각 업데이트"""
        try:
            cell = self.characters_sheet.find(name)
            if cell:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.characters_sheet.update_cell(cell.row, 4, now)
                return True
        except Exception as e:
            print(f"Error updating timestamp: {e}")
        return False
    
    def get_capacity(self, name):
        """가방 용량 조회"""
        char = self.get_character(name)
        if not char:
            return 20  # 기본값
        
        strength = char['strength']
        if 1 <= strength <= 5:
            return 20
        elif 6 <= strength <= 10:
            return 40
        elif 11 <= strength <= 15:
            return 60
        return 20
    
    # ========== 상점 (아이템 마스터 데이터) ==========
    
    def get_item_info(self, item_name):
        """상점에서 아이템 정보 조회"""
        try:
            cell = self.shop_sheet.find(item_name)
            if not cell:
                return None
            
            row = cell.row
            data = self.shop_sheet.row_values(row)
            
            return {
                'name': data[0],
                'volume': int(data[1]),
                'usable': data[2] == 'Y',
                'effect': data[3],
                'description': data[4],
                'category': data[5] if len(data) > 5 else '',
                'rarity': data[6] if len(data) > 6 else ''
            }
        except Exception as e:
            print(f"Error getting item info: {e}")
            return None
    
    # ========== 가방 ==========
    
    def get_bag_items(self, name):
        """가방 아이템 목록 조회"""
        try:
            all_rows = self.bag_sheet.get_all_records()
            items = [row for row in all_rows if row['캐릭터명'] == name]
            return items
        except Exception as e:
            print(f"Error getting bag items: {e}")
            return []
    
    def get_bag_used(self, name):
        """가방 사용 부피 계산"""
        items = self.get_bag_items(name)
        total = sum(item['총부피'] for item in items)
        return total
    
    def get_bag_available(self, name):
        """가방 잔여 공간 계산"""
        capacity = self.get_capacity(name)
        used = self.get_bag_used(name)
        return capacity - used
    
    def add_to_bag(self, name, item_name, quantity):
        """가방에 아이템 추가"""
        try:
            item_info = self.get_item_info(item_name)
            if not item_info:
                return False
            
            # 기존에 같은 아이템이 있는지 확인
            existing_items = self.get_bag_items(name)
            found = False
            
            for item in existing_items:
                if item['아이템명'] == item_name:
                    # 수량 증가
                    cell = self.bag_sheet.find(item['ID'])
                    row = cell.row
                    new_quantity = item['수량'] + quantity
                    self.bag_sheet.update_cell(row, 4, new_quantity)  # D열 (수량)
                    found = True
                    break
            
            if not found:
                # 새 행 추가
                new_id = f"bag_{int(datetime.now().timestamp())}"
                total_volume = item_info['volume'] * quantity
                
                self.bag_sheet.append_row([
                    new_id,
                    name,
                    item_name,
                    quantity,
                    item_info['volume'],
                    total_volume
                ])
            
            self.update_timestamp(name)
            return True
            
        except Exception as e:
            print(f"Error adding to bag: {e}")
            return False
    
    def remove_from_bag(self, name, item_name, quantity):
        """가방에서 아이템 제거"""
        try:
            items = self.get_bag_items(name)
            
            for item in items:
                if item['아이템명'] == item_name:
                    cell = self.bag_sheet.find(item['ID'])
                    row = cell.row
                    
                    new_quantity = item['수량'] - quantity
                    
                    if new_quantity <= 0:
                        # 행 삭제
                        self.bag_sheet.delete_rows(row)
                    else:
                        # 수량 감소
                        self.bag_sheet.update_cell(row, 4, new_quantity)
                    
                    self.update_timestamp(name)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error removing from bag: {e}")
            return False
    
    def find_item_in_bag(self, name, item_name):
        """가방에서 아이템 찾기"""
        items = self.get_bag_items(name)
        for item in items:
            if item['아이템명'] == item_name:
                return item
        return None
    
    # ========== 여유 공간 ==========
    
    def get_misc_items(self, name):
        """여유 공간 아이템 조회"""
        try:
            cell = self.misc_sheet.find(name)
            if not cell:
                return []
            
            row = cell.row
            items_str = self.misc_sheet.cell(row, 2).value  # B열
            
            if not items_str or items_str.strip() == '':
                return []
            
            # "클립, 클립, 동전" → ['클립', '클립', '동전']
            return [item.strip() for item in items_str.split(',')]
            
        except Exception as e:
            print(f"Error getting misc items: {e}")
            return []
    
    def add_to_misc(self, name, item_name, quantity=1):
        """여유 공간에 아이템 추가"""
        try:
            items = self.get_misc_items(name)
            
            # quantity만큼 추가
            for _ in range(quantity):
                items.append(item_name)
            
            # 다시 문자열로
            items_str = ', '.join(items)
            
            # 업데이트
            cell = self.misc_sheet.find(name)
            if cell:
                self.misc_sheet.update_cell(cell.row, 2, items_str)
            else:
                # 새 행 추가
                self.misc_sheet.append_row([name, items_str])
            
            self.update_timestamp(name)
            return True
            
        except Exception as e:
            print(f"Error adding to misc: {e}")
            return False
    
    def remove_from_misc(self, name, item_name, quantity=1):
        """여유 공간에서 아이템 제거"""
        try:
            items = self.get_misc_items(name)
            
            # quantity만큼 제거
            removed = 0
            while item_name in items and removed < quantity:
                items.remove(item_name)
                removed += 1
            
            if removed == 0:
                return False
            
            # 다시 문자열로
            items_str = ', '.join(items) if items else ''
            
            # 업데이트
            cell = self.misc_sheet.find(name)
            if cell:
                self.misc_sheet.update_cell(cell.row, 2, items_str)
            
            self.update_timestamp(name)
            return True
            
        except Exception as e:
            print(f"Error removing from misc: {e}")
            return False
    
    def find_item_in_misc(self, name, item_name):
        """여유 공간에서 아이템 찾기"""
        items = self.get_misc_items(name)
        count = items.count(item_name)
        if count > 0:
            return {'name': item_name, 'quantity': count}
        return None
    
    # ========== 주변 ==========
    
    def get_nearby_items(self, name):
        """주변 아이템 목록 조회"""
        try:
            all_rows = self.nearby_sheet.get_all_records()
            items = [row for row in all_rows if row['캐릭터명'] == name]
            return items
        except Exception as e:
            print(f"Error getting nearby items: {e}")
            return []
    
    def add_to_nearby(self, name, item_name, quantity, source='GM지급'):
        """주변에 아이템 추가"""
        try:
            item_info = self.get_item_info(item_name)
            if not item_info:
                return False
            
            new_id = f"nearby_{int(datetime.now().timestamp())}"
            now = datetime.now()
            acquired_time = now.strftime('%Y-%m-%d %H:%M:%S')
            
            # 당일 자정 계산
            expire_time = now.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
            
            total_volume = item_info['volume'] * quantity
            
            self.nearby_sheet.append_row([
                new_id,
                name,
                item_name,
                quantity,
                item_info['volume'],
                total_volume,
                acquired_time,
                expire_time,
                source
            ])
            
            self.update_timestamp(name)
            return True
            
        except Exception as e:
            print(f"Error adding to nearby: {e}")
            return False
    
    def remove_from_nearby(self, name, item_name, quantity):
        """주변에서 아이템 제거"""
        try:
            items = self.get_nearby_items(name)
            
            for item in items:
                if item['아이템명'] == item_name:
                    cell = self.nearby_sheet.find(item['ID'])
                    row = cell.row
                    
                    new_quantity = item['수량'] - quantity
                    
                    if new_quantity <= 0:
                        # 행 삭제
                        self.nearby_sheet.delete_rows(row)
                    else:
                        # 수량 감소
                        self.nearby_sheet.update_cell(row, 4, new_quantity)
                    
                    self.update_timestamp(name)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error removing from nearby: {e}")
            return False
    
    def find_item_in_nearby(self, name, item_name):
        """주변에서 아이템 찾기"""
        items = self.get_nearby_items(name)
        for item in items:
            if item['아이템명'] == item_name:
                return item
        return None
    
    # ========== 로그 ==========
    
    def add_log(self, character_name, action, item_name, quantity, details=''):
        """로그 추가"""
        try:
            new_id = f"log_{int(datetime.now().timestamp())}"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.logs_sheet.append_row([
                new_id,
                timestamp,
                character_name,
                action,
                item_name,
                quantity,
                details
            ])
            return True
        except Exception as e:
            print(f"Error adding log: {e}")
            return False
```

---

### 2-3. 명령어 처리 모듈 (commands.py)

```python
from sheets import InventorySheets
import os

class CommandHandler:
    def __init__(self):
        self.sheets = InventorySheets()
        self.gm_accounts = os.getenv('GM_ACCOUNTS', '').split(',')
    
    def is_gm(self, username):
        """GM 권한 확인"""
        return username in self.gm_accounts
    
    # ========== [아이템 추가] - GM 전용 ==========
    
    def handle_add_item(self, username, args):
        """
        명령어: [아이템 추가/캐릭터명/아이템명 수량]
        예시: [아이템 추가/발트/사과 3개]
        """
        if not self.is_gm(username):
            return "❌ 권한이 없습니다. (GM 전용 명령어)"
        
        try:
            # 파싱
            parts = args.split('/')
            if len(parts) < 2:
                return "❌ 형식이 잘못되었습니다.\n사용법: [아이템 추가/캐릭터명/아이템명 수량]"
            
            character_name = parts[0].strip()
            item_info = parts[1].strip()
            
            # "사과 3개" → ("사과", 3)
            item_parts = item_info.split()
            if len(item_parts) < 2:
                return "❌ 수량을 입력해주세요.\n예시: 사과 3개"
            
            item_name = ' '.join(item_parts[:-1])
            quantity_str = item_parts[-1].replace('개', '').strip()
            
            try:
                quantity = int(quantity_str)
            except ValueError:
                return f"❌ 수량이 올바르지 않습니다: {quantity_str}"
            
            # 캐릭터 존재 확인
            character = self.sheets.get_character(character_name)
            if not character:
                return f"❌ '{character_name}' 캐릭터를 찾을 수 없습니다."
            
            # 아이템 정보 확인
            item_data = self.sheets.get_item_info(item_name)
            if not item_data:
                return f"❌ '{item_name}'은(는) 상점에 등록되지 않은 아이템입니다."
            
            # 부피 0이면 여유 공간에 직접 추가
            if item_data['volume'] == 0:
                success = self.sheets.add_to_misc(character_name, item_name, quantity)
                if success:
                    self.sheets.add_log(character_name, '획득', item_name, quantity, '여유공간 자동편입')
                    return (f"@{character_name}\n"
                           f"✅ {item_name} {quantity}개를 발견했습니다! (부피 0)\n"
                           f"자동으로 여유 공간에 보관되었습니다.")
                else:
                    return "❌ 아이템 추가에 실패했습니다."
            
            # 주변에 추가
            success = self.sheets.add_to_nearby(character_name, item_name, quantity, 'GM지급')
            if not success:
                return "❌ 아이템 추가에 실패했습니다."
            
            # 로그 기록
            self.sheets.add_log(character_name, '획득', item_name, quantity, 'GM 지급 → 주변')
            
            # 가방 용량 확인
            capacity = self.sheets.get_capacity(character_name)
            used = self.sheets.get_bag_used(character_name)
            available = capacity - used
            total_volume = item_data['volume'] * quantity
            
            # 응답 메시지
            if total_volume <= available:
                return (f"@{character_name}\n"
                       f"✅ {item_name} {quantity}개를 발견했습니다! (총 부피: {total_volume})\n"
                       f"📦 가방 남은 공간: {available}칸\n"
                       f"웹페이지에서 가방에 넣으세요.\n"
                       f"🔗 https://inventory.game.com")
            else:
                return (f"@{character_name}\n"
                       f"✅ {item_name} {quantity}개를 발견했습니다! (총 부피: {total_volume})\n"
                       f"⚠️ 가방 공간이 부족합니다! (남은 공간: {available}칸)\n\n"
                       f"선택지:\n"
                       f"1. 웹에서 기존 아이템을 버리고 넣기\n"
                       f"2. 주변에 두고 나중에 정리하기\n"
                       f"3. [양도] 명령어로 다른 플레이어에게 주기\n\n"
                       f"⚠️ 주변 아이템은 오늘 24:00에 자동 삭제됩니다!\n"
                       f"🔗 https://inventory.game.com")
            
        except Exception as e:
            print(f"Error in handle_add_item: {e}")
            return f"❌ 오류가 발생했습니다: {str(e)}"
    
    # ========== [사용] ==========
    
    def handle_use_item(self, username, item_name):
        """
        명령어: [사용/아이템명]
        예시: [사용/사과]
        """
        try:
            # 캐릭터명 = 마스토돈 username (매핑 필요)
            character = self.sheets.get_character(username)
            if not character:
                return f"❌ 캐릭터를 찾을 수 없습니다."
            
            character_name = character['name']
            
            # 아이템 정보 확인
            item_data = self.sheets.get_item_info(item_name)
            if not item_data:
                return f"❌ '{item_name}'은(는) 등록되지 않은 아이템입니다."
            
            if not item_data['usable']:
                return f"❌ {item_name}은(는) 사용할 수 없는 아이템입니다."
            
            # 1단계: 주변 확인
            nearby_item = self.sheets.find_item_in_nearby(character_name, item_name)
            if nearby_item:
                # 주변에서 사용
                effect = self._apply_item_effect(character_name, item_data)
                self.sheets.remove_from_nearby(character_name, item_name, 1)
                self.sheets.add_log(character_name, '사용', item_name, 1, f'주변에서 사용, {effect}')
                
                remaining = nearby_item['수량'] - 1
                if remaining > 0:
                    return (f"✅ {item_name}을(를) 사용했습니다! (주변)\n"
                           f"{effect}\n"
                           f"주변에 남은 {item_name}: {remaining}개")
                else:
                    return (f"✅ {item_name}을(를) 사용했습니다! (주변)\n"
                           f"{effect}")
            
            # 2단계: 가방 확인
            bag_item = self.sheets.find_item_in_bag(character_name, item_name)
            if bag_item:
                # 가방에서 사용
                effect = self._apply_item_effect(character_name, item_data)
                self.sheets.remove_from_bag(character_name, item_name, 1)
                self.sheets.add_log(character_name, '사용', item_name, 1, f'가방에서 사용, {effect}')
                
                remaining = bag_item['수량'] - 1
                if remaining > 0:
                    return (f"✅ {item_name}을(를) 사용했습니다!\n"
                           f"{effect}\n"
                           f"남은 {item_name}: {remaining}개")
                else:
                    return (f"✅ {item_name}을(를) 사용했습니다!\n"
                           f"{effect}\n"
                           f"(마지막 {item_name}을 사용했습니다)")
            
            # 3단계: 여유 공간 확인
            misc_item = self.sheets.find_item_in_misc(character_name, item_name)
            if misc_item:
                # 여유 공간에서 사용
                effect = self._apply_item_effect(character_name, item_data)
                self.sheets.remove_from_misc(character_name, item_name, 1)
                self.sheets.add_log(character_name, '사용', item_name, 1, f'여유공간에서 사용, {effect}')
                
                remaining = misc_item['quantity'] - 1
                if remaining > 0:
                    return (f"✅ {item_name}을(를) 사용했습니다! (여유공간)\n"
                           f"{effect}\n"
                           f"남은 {item_name}: {remaining}개")
                else:
                    return (f"✅ {item_name}을(를) 사용했습니다! (여유공간)\n"
                           f"{effect}")
            
            # 없음
            return f"❌ {item_name}을(를) 소지하고 있지 않습니다."
            
        except Exception as e:
            print(f"Error in handle_use_item: {e}")
            return f"❌ 오류가 발생했습니다: {str(e)}"
    
    def _apply_item_effect(self, character_name, item_data):
        """
        아이템 효과 적용 (실제 스탯 변경은 별도 시트에서 처리)
        여기서는 효과 메시지만 반환
        """
        effect = item_data['effect']
        if effect == '-' or effect == '':
            return "효과 없음"
        
        # TODO: 실제 스탯 변경 로직 (체력, 갈증 등)
        # 예: self.sheets.update_character_stat(character_name, 'health', +3)
        
        return f"효과: {effect}"
    
    # ========== [양도] ==========
    
    def handle_transfer_item(self, username, args):
        """
        명령어: [양도/아이템명/받는사람]
        예시: [양도/사과/엘리사]
        """
        try:
            # 파싱
            parts = args.split('/')
            if len(parts) < 2:
                return "❌ 형식이 잘못되었습니다.\n사용법: [양도/아이템명/받는사람]"
            
            item_name = parts[0].strip()
            recipient_name = parts[1].strip()
            
            # 캐릭터 확인
            sender = self.sheets.get_character(username)
            if not sender:
                return "❌ 캐릭터를 찾을 수 없습니다."
            
            sender_name = sender['name']
            
            recipient = self.sheets.get_character(recipient_name)
            if not recipient:
                return f"❌ '{recipient_name}' 캐릭터를 찾을 수 없습니다."
            
            # 아이템 정보 확인
            item_data = self.sheets.get_item_info(item_name)
            if not item_data:
                return f"❌ '{item_name}'은(는) 등록되지 않은 아이템입니다."
            
            # 위치 찾기 (주변 → 가방 → 여유공간 순서)
            location = None
            
            # 1. 주변 확인
            if self.sheets.find_item_in_nearby(sender_name, item_name):
                location = 'nearby'
            # 2. 가방 확인
            elif self.sheets.find_item_in_bag(sender_name, item_name):
                location = 'bag'
            # 3. 여유 공간 확인
            elif self.sheets.find_item_in_misc(sender_name, item_name):
                location = 'misc'
            
            if not location:
                return f"❌ {item_name}을(를) 소지하고 있지 않습니다."
            
            # 이동 처리
            success = False
            
            if location == 'nearby':
                # 주변 → 주변
                success = self._transfer_nearby_to_nearby(sender_name, recipient_name, item_name)
            elif location == 'bag':
                # 가방 → 주변
                success = self._transfer_bag_to_nearby(sender_name, recipient_name, item_name, item_data)
            elif location == 'misc':
                # 여유공간 → 여유공간
                success = self._transfer_misc_to_misc(sender_name, recipient_name, item_name)
            
            if not success:
                return "❌ 양도에 실패했습니다."
            
            # 로그 기록
            self.sheets.add_log(sender_name, '양도', item_name, 1, f'수령자: {recipient_name}')
            self.sheets.add_log(recipient_name, '획득', item_name, 1, f'발신자: {sender_name}')
            
            # 응답 메시지
            location_kr = {'nearby': '주변', 'bag': '가방', 'misc': '여유 공간'}[location]
            target_location = '여유 공간' if location == 'misc' else '주변'
            
            sender_msg = f"✅ {item_name}을(를) {recipient_name}에게 양도했습니다!"
            recipient_msg = (f"@{recipient_name}\n"
                           f"📬 {sender_name}가 {item_name}을(를) 양도했습니다!\n"
                           f"{target_location} 탭에서 확인하세요.\n"
                           f"🔗 https://inventory.game.com")
            
            return f"{sender_msg}\n\n{recipient_msg}"
            
        except Exception as e:
            print(f"Error in handle_transfer_item: {e}")
            return f"❌ 오류가 발생했습니다: {str(e)}"
    
    def _transfer_nearby_to_nearby(self, sender, recipient, item_name):
        """주변 → 주변 이동"""
        try:
            item = self.sheets.find_item_in_nearby(sender, item_name)
            if not item:
                return False
            
            # 발신자에서 제거
            self.sheets.remove_from_nearby(sender, item_name, 1)
            
            # 수신자에게 추가
            self.sheets.add_to_nearby(recipient, item_name, 1, f'{sender}로부터 양도')
            
            return True
        except:
            return False
    
    def _transfer_bag_to_nearby(self, sender, recipient, item_name, item_data):
        """가방 → 주변 이동"""
        try:
            # 발신자 가방에서 제거
            self.sheets.remove_from_bag(sender, item_name, 1)
            
            # 수신자 주변에 추가 (부피 0이면 여유공간에)
            if item_data['volume'] == 0:
                self.sheets.add_to_misc(recipient, item_name, 1)
            else:
                self.sheets.add_to_nearby(recipient, item_name, 1, f'{sender}로부터 양도')
            
            return True
        except:
            return False
    
    def _transfer_misc_to_misc(self, sender, recipient, item_name):
        """여유공간 → 여유공간 이동"""
        try:
            # 발신자에서 제거
            self.sheets.remove_from_misc(sender, item_name, 1)
            
            # 수신자에게 추가
            self.sheets.add_to_misc(recipient, item_name, 1)
            
            return True
        except:
            return False
```

**(계속...)**

다음 부분도 작성할까요? 아니면 여기까지 검토 후 피드백 주시면 이어서 작성하겠습니다.# Phase 1: 기본 인프라 구축 - 상세 기획서 (계속)

---

### 2-4. 봇 메인 로직 (main.py)

```python
from mastodon import Mastodon, StreamListener
from commands import CommandHandler
from dotenv import load_dotenv
import os
import re

# 환경변수 로드
load_dotenv()

class BotListener(StreamListener):
    def __init__(self):
        self.mastodon = Mastodon(
            access_token=os.getenv('MASTODON_ACCESS_TOKEN'),
            api_base_url=os.getenv('MASTODON_INSTANCE_URL')
        )
        self.command_handler = CommandHandler()
        self.bot_prefix = os.getenv('BOT_COMMAND_PREFIX', '@봇')
    
    def on_notification(self, notification):
        """알림 수신 시 호출"""
        try:
            # 멘션만 처리
            if notification['type'] != 'mention':
                return
            
            status = notification['status']
            username = notification['account']['username']
            content = self._clean_html(status['content'])
            
            print(f"[알림] {username}: {content}")
            
            # 봇 멘션 확인
            if self.bot_prefix not in content:
                return
            
            # 명령어 추출
            command = self._extract_command(content)
            if not command:
                return
            
            # 명령어 처리
            response = self._process_command(username, command)
            
            # 응답
            if response:
                self._reply(status, response)
                
        except Exception as e:
            print(f"Error in on_notification: {e}")
    
    def _clean_html(self, html_content):
        """HTML 태그 제거"""
        # 간단한 HTML 제거 (실제로는 html.parser 사용 권장)
        clean = re.sub('<.*?>', '', html_content)
        return clean.strip()
    
    def _extract_command(self, content):
        """명령어 추출"""
        # [명령어/인자1/인자2] 형식
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, content)
        
        if not matches:
            return None
        
        # 첫 번째 매치 사용
        command_str = matches[0]
        return command_str
    
    def _process_command(self, username, command_str):
        """명령어 처리"""
        try:
            # 명령어 파싱
            parts = command_str.split('/')
            if not parts:
                return None
            
            command = parts[0].strip()
            args = '/'.join(parts[1:]) if len(parts) > 1 else ''
            
            print(f"[명령어] {command} | 인자: {args}")
            
            # 명령어별 처리
            if command == '아이템 추가':
                return self.command_handler.handle_add_item(username, args)
            
            elif command == '사용':
                item_name = args.strip()
                if not item_name:
                    return "❌ 사용할 아이템을 입력해주세요.\n사용법: [사용/아이템명]"
                return self.command_handler.handle_use_item(username, item_name)
            
            elif command == '양도':
                return self.command_handler.handle_transfer_item(username, args)
            
            elif command == '도움말' or command == '명령어':
                return self._show_help(username)
            
            elif command == '소지품' or command == '인벤토리':
                return self._show_inventory_link(username)
            
            else:
                return f"❌ 알 수 없는 명령어입니다: {command}\n[도움말]을 입력해 사용 가능한 명령어를 확인하세요."
                
        except Exception as e:
            print(f"Error processing command: {e}")
            return f"❌ 명령어 처리 중 오류가 발생했습니다: {str(e)}"
    
    def _reply(self, original_status, message):
        """답장 보내기"""
        try:
            self.mastodon.status_post(
                status=message,
                in_reply_to_id=original_status['id'],
                visibility=original_status['visibility']
            )
            print(f"[응답 전송] {message[:50]}...")
        except Exception as e:
            print(f"Error sending reply: {e}")
    
    def _show_help(self, username):
        """도움말 메시지"""
        is_gm = self.command_handler.is_gm(username)
        
        help_text = """
📖 **사용 가능한 명령어**

**플레이어 명령어:**
• [사용/아이템명] - 아이템 사용
• [양도/아이템명/받는사람] - 아이템 양도
• [소지품] - 인벤토리 웹페이지 링크
• [도움말] - 이 메시지 표시

**예시:**
@봇 [사용/사과]
@봇 [양도/로프/엘리사]
"""
        
        if is_gm:
            help_text += """
**GM 전용 명령어:**
• [아이템 추가/캐릭터명/아이템명 수량] - 아이템 지급

**예시:**
@봇 [아이템 추가/발트/사과 3개]
"""
        
        help_text += "\n🔗 웹 인터페이스: https://inventory.game.com"
        
        return help_text.strip()
    
    def _show_inventory_link(self, username):
        """인벤토리 링크"""
        character = self.command_handler.sheets.get_character(username)
        
        if not character:
            return "❌ 캐릭터를 찾을 수 없습니다."
        
        name = character['name']
        capacity = character['capacity']
        used = self.command_handler.sheets.get_bag_used(name)
        nearby_count = len(self.command_handler.sheets.get_nearby_items(name))
        
        return f"""
📦 **{name}의 인벤토리**

가방: {used}/{capacity} 사용중
주변 아이템: {nearby_count}개

🔗 웹에서 확인하기:
https://inventory.game.com/character/{name}
""".strip()

def main():
    """봇 시작"""
    print("=" * 50)
    print("TRPG 인벤토리 봇 시작")
    print("=" * 50)
    
    # 봇 리스너 생성
    listener = BotListener()
    
    # 스트림 연결
    print("마스토돈 스트림에 연결 중...")
    listener.mastodon.stream_user(listener)

if __name__ == '__main__':
    main()
```

---

### 2-5. 유틸리티 함수 (utils.py)

```python
from datetime import datetime, timedelta
import re

def parse_item_quantity(text):
    """
    "사과 3개" → ("사과", 3)
    "물병 1" → ("물병", 1)
    "로프" → ("로프", 1)
    """
    text = text.strip()
    
    # 패턴: "아이템명 숫자개" 또는 "아이템명 숫자"
    match = re.match(r'(.+?)\s+(\d+)개?$', text)
    
    if match:
        item_name = match.group(1).strip()
        quantity = int(match.group(2))
        return item_name, quantity
    else:
        # 수량 없으면 1개로 간주
        return text, 1

def calculate_capacity(strength):
    """근력 기반 가방 용량 계산"""
    if 1 <= strength <= 5:
        return 20
    elif 6 <= strength <= 10:
        return 40
    elif 11 <= strength <= 15:
        return 60
    else:
        return 20  # 기본값

def get_midnight_today():
    """오늘 자정 시각 반환"""
    now = datetime.now()
    midnight = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return midnight

def format_datetime(dt):
    """datetime을 문자열로 변환"""
    if isinstance(dt, str):
        return dt
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def parse_datetime(dt_str):
    """문자열을 datetime으로 변환"""
    if isinstance(dt_str, datetime):
        return dt_str
    return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

def is_expired(expire_time_str):
    """만료 여부 확인"""
    try:
        expire_time = parse_datetime(expire_time_str)
        now = datetime.now()
        return now > expire_time
    except:
        return False

def format_item_list(items):
    """
    아이템 리스트를 보기 좋게 포매팅
    [{'name': '사과', 'quantity': 3, 'volume': 1}, ...] 
    → "사과 x3 (부피 3), 물병 x2 (부피 4)"
    """
    if not items:
        return "(없음)"
    
    formatted = []
    for item in items:
        name = item.get('아이템명', item.get('name', '?'))
        quantity = item.get('수량', item.get('quantity', 1))
        volume = item.get('총부피', item.get('volume', 0))
        
        formatted.append(f"{name} x{quantity} (부피 {volume})")
    
    return ", ".join(formatted)

def clean_html_tags(html):
    """HTML 태그 제거"""
    clean = re.sub('<.*?>', '', html)
    clean = re.sub('&nbsp;', ' ', clean)
    clean = re.sub('&lt;', '<', clean)
    clean = re.sub('&gt;', '>', clean)
    clean = re.sub('&amp;', '&', clean)
    return clean.strip()

def validate_character_name(name):
    """캐릭터명 유효성 검사"""
    if not name or len(name) < 2:
        return False, "캐릭터명은 2글자 이상이어야 합니다."
    
    if len(name) > 20:
        return False, "캐릭터명은 20글자 이하여야 합니다."
    
    # 특수문자 제한 (선택)
    if not re.match(r'^[가-힣a-zA-Z0-9_\s]+$', name):
        return False, "캐릭터명에 사용할 수 없는 문자가 포함되어 있습니다."
    
    return True, ""

def validate_item_name(name):
    """아이템명 유효성 검사"""
    if not name or len(name) < 1:
        return False, "아이템명을 입력해주세요."
    
    if len(name) > 50:
        return False, "아이템명은 50글자 이하여야 합니다."
    
    return True, ""
```

---

### 2-6. 봇 실행 및 테스트

**실행 방법**:
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 확인
cat .env

# 봇 실행
python bot/main.py
```

**테스트 시나리오**:

1. **도움말 확인**
   ```
   마스토돈: @봇 [도움말]
   봇 응답: (명령어 목록 표시)
   ```

2. **아이템 추가 (GM)**
   ```
   마스토돈: @봇 [아이템 추가/발트/사과 3개]
   봇 응답: 
   @발트
   ✅ 사과 3개를 발견했습니다! (총 부피: 3)
   📦 가방 남은 공간: 20칸
   웹페이지에서 가방에 넣으세요.
   🔗 https://inventory.game.com
   ```

3. **아이템 사용**
   ```
   마스토돈: @봇 [사용/사과]
   봇 응답:
   ✅ 사과을(를) 사용했습니다! (주변)
   효과: 체력+3
   주변에 남은 사과: 2개
   ```

4. **아이템 양도**
   ```
   마스토돈: @봇 [양도/사과/엘리사]
   봇 응답:
   ✅ 사과을(를) 엘리사에게 양도했습니다!
   
   @엘리사
   📬 발트가 사과을(를) 양도했습니다!
   주변 탭에서 확인하세요.
   🔗 https://inventory.game.com
   ```

**완료 체크리스트**:
- [ ] 봇이 정상적으로 시작됨
- [ ] 마스토돈 멘션을 수신함
- [ ] [도움말] 명령어 작동
- [ ] [아이템 추가] 명령어 작동 (GM)
- [ ] [사용] 명령어 작동
- [ ] [양도] 명령어 작동
- [ ] 구글 시트가 정상적으로 업데이트됨
- [ ] 로그가 기록됨

---

## 🌐 Task 3: Flask API 서버 구축

**소요 시간**: 2일

### 3-1. 프로젝트 구조

```
trpg-inventory/
├── bot/                    # 마스토돈 봇 (이미 완성)
│   └── ...
├── api/                    # Flask API 서버
│   ├── __init__.py
│   ├── app.py             # Flask 앱 메인
│   ├── routes.py          # API 라우트
│   ├── models.py          # 데이터 모델
│   └── sheets.py          # 구글 시트 연동 (bot/sheets.py와 공유)
├── web/                    # 웹 프론트엔드
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       └── index.html
├── credentials.json
├── .env
└── requirements.txt
```

---

### 3-2. Flask 앱 설정 (api/app.py)

```python
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

def create_app():
    """Flask 앱 생성"""
    app = Flask(__name__, 
                static_folder='../web/static',
                template_folder='../web/templates')
    
    # CORS 설정 (프론트엔드와 다른 포트일 경우)
    CORS(app)
    
    # 설정
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    app.config['JSON_AS_ASCII'] = False  # 한글 응답
    
    # 라우트 등록
    from api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 메인 페이지 라우트
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    @app.route('/character/<name>')
    def character_page(name):
        from flask import render_template
        return render_template('index.html', character=name)
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print(f"Flask 서버 시작: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
```

---

### 3-3. API 라우트 (api/routes.py)

```python
from flask import Blueprint, jsonify, request
from api.models import InventoryData
from datetime import datetime

api_bp = Blueprint('api', __name__)
inventory_data = InventoryData()

# ========== 캐릭터 정보 ==========

@api_bp.route('/characters', methods=['GET'])
def get_all_characters():
    """전체 캐릭터 목록 조회"""
    try:
        characters = inventory_data.get_all_characters()
        return jsonify({
            'success': True,
            'data': characters
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/character/<name>', methods=['GET'])
def get_character(name):
    """특정 캐릭터 전체 정보 조회"""
    try:
        character = inventory_data.get_character_full(name)
        
        if not character:
            return jsonify({
                'success': False,
                'error': '캐릭터를 찾을 수 없습니다.'
            }), 404
        
        return jsonify({
            'success': True,
            'data': character
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/character/<name>/stats', methods=['GET'])
def get_character_stats(name):
    """캐릭터 기본 정보만 조회"""
    try:
        stats = inventory_data.get_character_stats(name)
        
        if not stats:
            return jsonify({
                'success': False,
                'error': '캐릭터를 찾을 수 없습니다.'
            }), 404
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== 가방 ==========

@api_bp.route('/character/<name>/bag', methods=['GET'])
def get_bag(name):
    """가방 아이템 조회"""
    try:
        bag_data = inventory_data.get_bag(name)
        
        return jsonify({
            'success': True,
            'data': bag_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/character/<name>/bag', methods=['POST'])
def update_bag(name):
    """가방 아이템 업데이트 (웹에서 저장)"""
    try:
        data = request.json
        items = data.get('items', [])
        
        # 용량 검증
        result = inventory_data.validate_and_update_bag(name, items)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== 여유 공간 ==========

@api_bp.route('/character/<name>/misc', methods=['GET'])
def get_misc_space(name):
    """여유 공간 아이템 조회"""
    try:
        misc_data = inventory_data.get_misc_space(name)
        
        return jsonify({
            'success': True,
            'data': misc_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== 주변 ==========

@api_bp.route('/character/<name>/nearby', methods=['GET'])
def get_nearby(name):
    """주변 아이템 조회"""
    try:
        nearby_data = inventory_data.get_nearby(name)
        
        return jsonify({
            'success': True,
            'data': nearby_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/character/<name>/nearby/move-to-bag', methods=['POST'])
def move_nearby_to_bag(name):
    """주변 → 가방 이동"""
    try:
        data = request.json
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        
        result = inventory_data.move_nearby_to_bag(name, item_id, quantity)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== 상점 ==========

@api_bp.route('/shop/items', methods=['GET'])
def get_shop_items():
    """상점 아이템 목록 조회"""
    try:
        items = inventory_data.get_all_shop_items()
        
        return jsonify({
            'success': True,
            'data': items
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/shop/item/<name>', methods=['GET'])
def get_shop_item(name):
    """특정 아이템 정보 조회"""
    try:
        item = inventory_data.get_shop_item(name)
        
        if not item:
            return jsonify({
                'success': False,
                'error': '아이템을 찾을 수 없습니다.'
            }), 404
        
        return jsonify({
            'success': True,
            'data': item
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== 변경사항 확인 (폴링용) ==========

@api_bp.route('/character/<name>/check-updates', methods=['GET'])
def check_updates(name):
    """마지막 업데이트 시각 확인"""
    try:
        last_update = inventory_data.get_last_update(name)
        
        return jsonify({
            'success': True,
            'data': {
                'last_update': last_update,
                'server_time': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== 헬스체크 ==========

@api_bp.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
```

---

### 3-4. 데이터 모델 (api/models.py)

```python
import sys
sys.path.append('..')

from bot.sheets import InventorySheets
from datetime import datetime

class InventoryData:
    def __init__(self):
        """데이터 레이어 초기화"""
        self.sheets = InventorySheets()
    
    # ========== 캐릭터 ==========
    
    def get_all_characters(self):
        """전체 캐릭터 목록"""
        try:
            all_records = self.sheets.characters_sheet.get_all_records()
            
            characters = []
            for record in all_records:
                if record.get('활성상태') != 'Y':
                    continue
                
                name = record['캐릭터명']
                
                characters.append({
                    'name': name,
                    'strength': record['근력'],
                    'capacity': record['가방용량'],
                    'bag_used': self.sheets.get_bag_used(name),
                    'nearby_count': len(self.sheets.get_nearby_items(name)),
                    'last_update': record['마지막수정시각']
                })
            
            return characters
            
        except Exception as e:
            print(f"Error in get_all_characters: {e}")
            return []
    
    def get_character_full(self, name):
        """캐릭터 전체 정보 (가방+여유공간+주변)"""
        try:
            # 기본 정보
            character = self.sheets.get_character(name)
            if not character:
                return None
            
            # 가방
            bag_items = self.sheets.get_bag_items(name)
            bag_used = self.sheets.get_bag_used(name)
            
            # 여유 공간
            misc_items = self.sheets.get_misc_items(name)
            
            # 주변
            nearby_items = self.sheets.get_nearby_items(name)
            
            return {
                'character': character,
                'bag': {
                    'capacity': character['capacity'],
                    'used': bag_used,
                    'available': character['capacity'] - bag_used,
                    'items': bag_items
                },
                'misc_space': {
                    'items': misc_items
                },
                'nearby': {
                    'items': nearby_items,
                    'count': len(nearby_items)
                }
            }
            
        except Exception as e:
            print(f"Error in get_character_full: {e}")
            return None
    
    def get_character_stats(self, name):
        """캐릭터 기본 정보만"""
        return self.sheets.get_character(name)
    
    # ========== 가방 ==========
    
    def get_bag(self, name):
        """가방 정보"""
        try:
            items = self.sheets.get_bag_items(name)
            capacity = self.sheets.get_capacity(name)
            used = self.sheets.get_bag_used(name)
            
            return {
                'capacity': capacity,
                'used': used,
                'available': capacity - used,
                'items': items
            }
        except Exception as e:
            print(f"Error in get_bag: {e}")
            return {'capacity': 20, 'used': 0, 'available': 20, 'items': []}
    
    def validate_and_update_bag(self, name, items):
        """가방 검증 및 업데이트"""
        try:
            # 용량 계산
            total_volume = 0
            for item in items:
                volume = item.get('총부피', item.get('개당부피', 0) * item.get('수량', 1))
                total_volume += volume
            
            capacity = self.sheets.get_capacity(name)
            
            if total_volume > capacity:
                return {
                    'success': False,
                    'error': f'용량 초과 ({total_volume}/{capacity})'
                }
            
            # TODO: 실제 시트 업데이트 로직
            # 현재는 봇의 sheets.py를 통해 개별 아이템만 추가/제거 가능
            # 전체 가방을 한번에 덮어쓰는 로직 필요
            
            self.sheets.update_timestamp(name)
            
            return {
                'success': True,
                'message': '저장되었습니다.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # ========== 여유 공간 ==========
    
    def get_misc_space(self, name):
        """여유 공간 정보"""
        try:
            items = self.sheets.get_misc_items(name)
            
            # 아이템별 개수 계산
            item_counts = {}
            for item in items:
                item_counts[item] = item_counts.get(item, 0) + 1
            
            items_list = [{'name': name, 'quantity': count} 
                         for name, count in item_counts.items()]
            
            return {
                'items': items_list,
                'total_count': len(items)
            }
        except Exception as e:
            print(f"Error in get_misc_space: {e}")
            return {'items': [], 'total_count': 0}
    
    # ========== 주변 ==========
    
    def get_nearby(self, name):
        """주변 정보"""
        try:
            items = self.sheets.get_nearby_items(name)
            
            # 만료시각 확인
            now = datetime.now()
            for item in items:
                expire_str = item.get('만료시각', '')
                if expire_str:
                    try:
                        expire_time = datetime.strptime(expire_str, '%Y-%m-%d %H:%M:%S')
                        remaining = (expire_time - now).total_seconds()
                        item['remaining_seconds'] = max(0, int(remaining))
                    except:
                        item['remaining_seconds'] = 0
            
            total_volume = sum(item.get('총부피', 0) for item in items)
            
            return {
                'items': items,
                'total_volume': total_volume,
                'count': len(items)
            }
        except Exception as e:
            print(f"Error in get_nearby: {e}")
            return {'items': [], 'total_volume': 0, 'count': 0}
    
    def move_nearby_to_bag(self, name, item_id, quantity):
        """주변 → 가방 이동"""
        try:
            # 주변에서 아이템 찾기
            nearby_items = self.sheets.get_nearby_items(name)
            target_item = None
            
            for item in nearby_items:
                if item['ID'] == item_id:
                    target_item = item
                    break
            
            if not target_item:
                return {'success': False, 'error': '아이템을 찾을 수 없습니다.'}
            
            # 용량 확인
            needed_volume = target_item['개당부피'] * quantity
            available = self.sheets.get_bag_available(name)
            
            if needed_volume > available:
                return {
                    'success': False,
                    'error': f'공간 부족 (필요: {needed_volume}, 남음: {available})'
                }
            
            # 이동 처리
            item_name = target_item['아이템명']
            
            # 주변에서 제거
            self.sheets.remove_from_nearby(name, item_name, quantity)
            
            # 가방에 추가
            self.sheets.add_to_bag(name, item_name, quantity)
            
            return {
                'success': True,
                'message': f'{item_name} {quantity}개를 가방에 넣었습니다.'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ========== 상점 ==========
    
    def get_all_shop_items(self):
        """전체 상점 아이템"""
        try:
            return self.sheets.shop_sheet.get_all_records()
        except Exception as e:
            print(f"Error in get_all_shop_items: {e}")
            return []
    
    def get_shop_item(self, name):
        """특정 아이템 정보"""
        return self.sheets.get_item_info(name)
    
    # ========== 기타 ==========
    
    def get_last_update(self, name):
        """마지막 업데이트 시각"""
        character = self.sheets.get_character(name)
        if character:
            return character.get('last_update', '')
        return ''
```

---

### 3-5. API 테스트

**테스트 스크립트** (test_api.py):
```python
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_health():
    """헬스체크"""
    response = requests.get(f'{BASE_URL}/health')
    print(f"Health Check: {response.json()}")

def test_get_characters():
    """캐릭터 목록 조회"""
    response = requests.get(f'{BASE_URL}/characters')
    data = response.json()
    print(f"\n캐릭터 목록: {json.dumps(data, indent=2, ensure_ascii=False)}")

def test_get_character(name):
    """특정 캐릭터 조회"""
    response = requests.get(f'{BASE_URL}/character/{name}')
    data = response.json()
    print(f"\n{name} 정보: {json.dumps(data, indent=2, ensure_ascii=False)}")

def test_get_bag(name):
    """가방 조회"""
    response = requests.get(f'{BASE_URL}/character/{name}/bag')
    data = response.json()
    print(f"\n{name} 가방: {json.dumps(data, indent=2, ensure_ascii=False)}")

def test_get_nearby(name):
    """주변 아이템 조회"""
    response = requests.get(f'{BASE_URL}/character/{name}/nearby')
    data = response.json()
    print(f"\n{name} 주변: {json.dumps(data, indent=2, ensure_ascii=False)}")

if __name__ == '__main__':
    print("=" * 50)
    print("API 테스트 시작")
    print("=" * 50)
    
    test_health()
    test_get_characters()
    test_get_character('발트')
    test_get_bag('발트')
    test_get_nearby('발트')
    
    print("\n" + "=" * 50)
    print("테스트 완료")
    print("=" * 50)
```

**실행**:
```bash
# Flask 서버 시작 (터미널 1)
python api/app.py

# 테스트 실행 (터미널 2)
python test_api.py
```

**완료 체크리스트**:
- [ ] Flask 서버가 정상적으로 시작됨
- [ ] `/api/health` 엔드포인트 작동
- [ ] `/api/characters` 엔드포인트 작동
- [ ] `/api/character/<name>` 엔드포인트 작동
- [ ] `/api/character/<name>/bag` 엔드포인트 작동
- [ ] `/api/character/<name>/nearby` 엔드포인트 작동
- [ ] 구글 시트에서 데이터를 정상적으로 읽어옴
- [ ] JSON 응답이 한글로 잘 출력됨

---

**(다음: Task 4 웹 프론트엔드 작성 - 계속할까요?)**