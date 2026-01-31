# 마스토돈 TRPG 인벤토리 관리 시스템 기획서

## 📋 프로젝트 개요

### 목적
마스토돈 기반 TRPG 게임의 인벤토리를 구글 시트(데이터)와 웹 인터페이스(시각화)로 분리 관리하여, 운영진은 텍스트로 간편하게 관리하고 플레이어는 직관적인 그리드 UI로 아이템을 정리할 수 있도록 함

### 핵심 컨셉
- **3단계 인벤토리**: 가방(제한적) + 여유 공간(부피 0 아이템) + 주변(임시 보관)
- **역할 분리**: 운영진(시트 관리) / 봇(명령어 처리) / 플레이어(웹 정리)
- **단순한 부피 시스템**: 부피 단위 1부터, 근력에 따라 20/40/60 용량
- **자동 초기화**: 주변 아이템은 정기적으로 자동 삭제

---

## 🎮 인벤토리 구조

### A. 가방 (Bag)

**정의**: 캐릭터가 실제로 들고 다니는 아이템 공간

**용량 계산**:
```
근력 1~5:   용량 20
근력 6~10:  용량 40
근력 11~15: 용량 60
```

**특징**:
- 부피 제한 있음
- 게임 진행 중 언제든 사용 가능
- 플레이어가 웹에서 직접 정리
- 아이템 배치는 테트리스 스타일

**시각화 예시**:
```
┌─────────────────────────────────────┐
│  발트의 가방           용량: 15/20   │
├─────────────────────────────────────┤
│ ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐           │
│ │사│과│ │ │물│병│ │ │ │ │           │
│ ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤           │
│ │사│과│ │ │물│병│ │ │ │ │           │
│ ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤           │
│ │사│과│ │ │ │ │ │ │ │ │           │
│ ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤           │
│ │ │ │ │ │ │ │ │ │ │ │           │
│ └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘           │
│                                     │
│ 사과 x3 (부피 1개당 1)              │
│ 물병 x2 (부피 1개당 2)              │
└─────────────────────────────────────┘
```

---

### B. 여유 공간 (Misc Space)

**정의**: 부피가 0인 작은 아이템들을 보관하는 특수 공간

**특징**:
- 부피 0 아이템만 자동으로 편입
- 용량 제한 없음
- 텍스트 리스트로 표시
- 사용 가능

**예시**:
```
┌─────────────────────────────────────┐
│  여유 공간 (부피 0 아이템)          │
├─────────────────────────────────────┤
│                                     │
│  클립 x2, 동전 x5, 성냥 x1          │
│  종이쪽지, 펜                       │
│                                     │
└─────────────────────────────────────┘
```

---

### C. 주변 (Nearby / Loot Area)

**정의**: 획득했지만 아직 가방에 넣지 않은 아이템들

**특징**:
- 획득 시 기본적으로 여기에 추가됨
- 가방으로 이동 가능 (웹에서 드래그)
- 즉시 사용 가능 (마스토돈 명령어)
- 즉시 양도 가능 (마스토돈 명령어)
- **자동 초기화**: 매일 0시 또는 정기적으로 삭제
- 들고 다닐 수 없음 (가방에 넣어야 함)

**시각화 예시**:
```
┌─────────────────────────────────────┐
│  주변 아이템 (임시)    🕐 6시간 남음│
├─────────────────────────────────────┤
│                                     │
│  📦 최근 획득한 아이템:             │
│  ├─ [의료 키트]    부피: 5          │
│  │   획득: 2시간 전 (전투 보상)    │
│  │   [가방에 넣기] [사용] [양도]   │
│  │                                  │
│  ├─ [로프]         부피: 3          │
│  │   획득: 2시간 전 (전투 보상)    │
│  │   [가방에 넣기] [사용] [양도]   │
│  │                                  │
│  └─ [배터리 x2]    부피: 2 (각 1)  │
│      획득: 30분 전 (조사 발견)     │
│      [가방에 넣기] [사용] [양도]   │
│                                     │
│  ⚠️ 주변 아이템은 매일 0시에       │
│     자동으로 사라집니다!            │
└─────────────────────────────────────┘
```

---

## 🔄 아이템 흐름도

```
        [운영진이 아이템 지급]
                 ↓
         ┌───────────────┐
         │   주 변       │ ← 획득 시 기본 위치
         │  (임시 보관)   │
         └───────┬───────┘
                 │
        ┌────────┼────────┐
        │        │        │
     [사용]   [양도]  [가방에 넣기]
     (명령어) (명령어)   (웹)
        │        │        │
        ↓        ↓        ↓
     [소모]  [타인에게] ┌──────────┐
                       │  가 방    │
                       │ (영구보관) │
                       └─────┬────┘
                             │
                    ┌────────┼────────┐
                    │        │        │
                 [사용]   [양도]   [버리기]
                 (명령어) (명령어)   (웹)
```

---

## 🗂️ 구글 시트 구조

### Sheet 1: 캐릭터 정보
```
| 캐릭터명 | 근력 | 가방용량 | 마지막수정 |
|---------|------|---------|-----------|
| 발트     | 5    | 20      | 2026-01-30 14:23:45 |
| 엘리사   | 8    | 40      | 2026-01-30 14:20:12 |
| 카인     | 12   | 60      | 2026-01-30 13:15:30 |
```

### Sheet 2: 가방 (텍스트 형식)
```
| 캐릭터명 | 아이템 목록 (텍스트) |
|---------|---------------------|
| 발트     | 사과: 3, 물병: 2, 손전등: 1 |
| 엘리사   | 칼: 1, 로프: 1, 의료키트: 1 |
```

**또는 개별 행 방식**:
```
| 캐릭터명 | 아이템명 | 수량 | 부피(개당) |
|---------|---------|------|-----------|
| 발트     | 사과     | 3    | 1         |
| 발트     | 물병     | 2    | 2         |
| 발트     | 손전등   | 1    | 3         |
| 엘리사   | 칼       | 1    | 4         |
```

### Sheet 3: 여유 공간 (텍스트 형식)
```
| 캐릭터명 | 부피 0 아이템 |
|---------|--------------|
| 발트     | 클립, 클립, 동전, 성냥 |
| 엘리사   | 종이쪽지, 펜 |
```

### Sheet 4: 주변 (텍스트 형식)
```
| 캐릭터명 | 아이템명 | 수량 | 부피(개당) | 획득시각 | 만료시각 |
|---------|---------|------|-----------|---------|---------|
| 발트     | 의료키트 | 1    | 5         | 14:20   | 23:59   |
| 발트     | 로프     | 1    | 3         | 14:20   | 23:59   |
| 발트     | 배터리   | 2    | 1         | 14:50   | 23:59   |
```

### Sheet 5: 상점 (아이템 마스터 정보)
```
| 아이템명     | 부피 | 사용가능 | 효과     | 설명 |
|------------|------|---------|---------|------|
| 사과        | 1    | Y       | 체력+3   | 신선한 사과 |
| 물병        | 2    | Y       | 갈증-5   | 생수 500ml |
| 의료 키트   | 5    | Y       | 체력+10  | 응급처치 도구 |
| 칼          | 4    | N       | 공격+2   | 전투용 나이프 |
| 클립        | 0    | N       | -       | 작은 클립 |
| 동전        | 0    | N       | -       | 10원 동전 |
```

---

## 💻 웹 인터페이스 설계

### 메인 화면
```
┌────────────────────────────────────────────────────────────┐
│  🎮 인벤토리 관리              👤 발트 (근력: 5)           │
├─────────────────┬──────────────────────────────────────────┤
│                 │                                          │
│ [캐릭터 선택]   │          [탭 선택]                       │
│                 │  ┌──────┬──────┬──────┐                 │
│ ◉ 발트 (20)     │  │ 가방 │ 여유 │ 주변 │                 │
│   가방: 15/20   │  └──────┴──────┴──────┘                 │
│   주변: 3개     │                                          │
│                 │  ┌────────────────────────────────────┐ │
│ ○ 엘리사 (40)   │  │                                    │ │
│   가방: 25/40   │  │       [가방 그리드 뷰]             │ │
│   주변: 0개     │  │                                    │ │
│                 │  │    (또는 여유/주변 리스트)         │ │
│ ○ 카인 (60)     │  │                                    │ │
│   가방: 55/60   │  │                                    │ │
│   주변: 1개     │  └────────────────────────────────────┘ │
│                 │                                          │
│ [🔄 새로고침]   │  [자동 정리] [저장] [취소]              │
└─────────────────┴──────────────────────────────────────────┘
```

### 가방 탭
```
┌─────────────────────────────────────────────────┐
│  발트의 가방                       15/20 사용   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐                      │
│  │사│과│ │ │물│병│ │ │ │ │                      │
│  ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤                      │
│  │사│과│ │ │물│병│ │ │ │ │                      │
│  ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤                      │
│  │사│과│ │ │손│전│등│ │ │ │                      │
│  ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤                      │
│  │ │ │ │ │ │ │ │ │ │ │                      │
│  └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘                      │
│                                                 │
│  📦 보유 아이템:                                │
│  • 사과 x3 (부피: 1개당 1 = 총 3)              │
│  • 물병 x2 (부피: 1개당 2 = 총 4)              │
│  • 손전등 x1 (부피: 3)                         │
│                                                 │
│  💡 Tip: 주변 탭에서 드래그해서 가방에 추가    │
│  🗑️ 휴지통으로 드래그해서 아이템 버리기        │
└─────────────────────────────────────────────────┘
```

### 여유 공간 탭
```
┌─────────────────────────────────────────────────┐
│  여유 공간 (부피 0 아이템)         제한 없음    │
├─────────────────────────────────────────────────┤
│                                                 │
│  📎 클립 x2                                     │
│  💰 동전 x5                                     │
│  🔥 성냥 x1                                     │
│  📄 종이쪽지 x1                                 │
│  ✏️ 펜 x1                                       │
│                                                 │
│  ──────────────────────────────────────────    │
│                                                 │
│  💡 부피가 0인 아이템은 자동으로 여기 들어감   │
│  ⚠️ 이 아이템들도 사용/양도 가능 (명령어)      │
└─────────────────────────────────────────────────┘
```

### 주변 탭
```
┌─────────────────────────────────────────────────┐
│  주변 아이템 (임시)         🕐 자동삭제: 6시간  │
├─────────────────────────────────────────────────┤
│                                                 │
│  ⚠️ 주의: 이 아이템들은 매일 0시에 삭제됩니다! │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ 📦 의료 키트          부피: 5             │ │
│  │    획득: 2시간 전 (GM 지급)              │ │
│  │    [▼ 가방으로 드래그]                   │ │
│  ├───────────────────────────────────────────┤ │
│  │ 🪢 로프               부피: 3             │ │
│  │    획득: 2시간 전 (GM 지급)              │ │
│  │    [▼ 가방으로 드래그]                   │ │
│  ├───────────────────────────────────────────┤ │
│  │ 🔋 배터리 x2          부피: 1 (각)       │ │
│  │    획득: 30분 전 (조사 발견)             │ │
│  │    [▼ 가방으로 드래그]                   │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  총 부피: 10                                   │
│  가방 남은 공간: 5칸 ⚠️                        │
│                                                 │
│  💡 명령어 안내:                                │
│  • 사용: @봇 [사용/의료 키트]                  │
│  • 양도: @봇 [양도/로프/엘리사]                │
└─────────────────────────────────────────────────┘
```

---

## 🎯 주요 시나리오

### 시나리오 1: 아이템 획득 (정상)

```
1. 상황
   - 발트가 사과나무를 조사
   - GM이 사과 3개를 보상으로 지급

2. 운영진 작업 (구글 시트)
   마스토돈: @봇 [아이템 추가/발트의 주변/사과 3개]
   
   봇 처리:
   - 상점 시트에서 "사과" 정보 확인 (부피: 1)
   - 발트의 "주변" 시트에 추가:
     | 발트 | 사과 | 3 | 1 | 15:30 | 23:59 |

3. 봇 응답
   @발트 사과 3개를 발견했습니다! (총 부피: 3)
   가방 남은 공간: 5칸
   웹페이지에서 가방에 넣으세요.
   🔗 https://inventory.game.com

4. 플레이어 작업 (웹)
   - 웹사이트 접속
   - "주변" 탭에 사과 3개 표시됨
   - 사과를 드래그해서 가방 그리드에 배치
   - [저장] 버튼 클릭

5. 시스템 처리
   - 주변 시트: 사과 3개 삭제
   - 가방 시트: 사과 3개 추가
   - 마지막수정 시각 업데이트

6. 결과
   - 가방: 15/20 → 18/20
   - 주변: 사과 3개 사라짐
```

### 시나리오 2: 아이템 획득 (가방 꽉 참)

```
1. 상황
   - 발트의 가방: 19/20 (거의 꽉 참)
   - 전투 후 의료 키트(부피 5) 획득

2. 운영진 작업
   마스토돈: @봇 [아이템 추가/발트의 주변/의료 키트]

3. 봇 응답
   @발트 의료 키트를 발견했습니다! (부피: 5)
   ⚠️ 가방 공간이 부족합니다! (남은 공간: 1칸)
   
   선택지:
   1. 웹에서 기존 아이템을 버리고 넣기
   2. 주변에 두고 나중에 정리하기
   3. 다른 플레이어에게 양도하기
   
   ⚠️ 주변 아이템은 오늘 24:00에 자동 삭제됩니다!
   🔗 https://inventory.game.com

4. 플레이어 선택 A: 기존 아이템 버리기
   - 웹 접속
   - 가방에서 사과 3개를 휴지통으로 드래그 (부피 -3)
   - 주변의 의료 키트를 가방으로 드래그 (부피 +5)
   - [저장]
   - 결과: 19/20 → 21/20... 저장 실패!
   - 사과 2개 더 버림
   - 결과: 19/20 → 16/20 → 21/20... 저장 실패!
   
   (다시)
   - 사과 3개 버림 (19→16)
   - 물병 1개 버림 (16→14)
   - 의료 키트 넣기 (14→19)
   - [저장] → 성공!

4. 플레이어 선택 B: 즉시 사용
   마스토돈: @봇 [사용/의료 키트]
   
   봇:
   - 주변에서 의료 키트 확인
   - 체력 +10 적용
   - 주변에서 삭제
   - 응답: "의료 키트를 사용했습니다! 체력 +10"

4. 플레이어 선택 C: 다른 플레이어에게 양도
   마스토돈: @봇 [양도/의료 키트/엘리사]
   
   봇:
   - 발트의 주변에서 의료 키트 삭제
   - 엘리사의 주변에 의료 키트 추가
   - 응답: "의료 키트를 엘리사에게 양도했습니다!"
```

### 시나리오 3: 아이템 사용

```
1. 상황
   - 발트의 가방에 사과 3개
   - 발트가 배고픔

2. 플레이어 명령어
   마스토돈: @봇 [사용/사과]

3. 봇 처리 로직
   a. 주변 확인
      - 발트의 주변 시트 검색
      - 사과 없음 → 다음 단계
   
   b. 가방 확인
      - 발트의 가방 시트 검색
      - 사과 3개 발견! → 사용 가능
   
   c. 효과 적용
      - 상점 시트에서 사과 정보 확인
      - 효과: 체력 +3
      - 발트의 체력 시트에 +3
   
   d. 아이템 차감
      - 가방 시트: 사과 3 → 2
   
   e. 웹 동기화 트리거
      - 마지막수정 시각 업데이트
      - 웹이 2초 후 자동 감지 → 새로고침

4. 봇 응답
   @발트 사과를 먹었습니다!
   효과: 체력 +3 (현재 체력: 45/50)
   남은 사과: 2개

5. 웹 화면
   - 2초 후 가방 그리드에서 사과 1개 사라짐
   - 알림: "사과를 사용했습니다!"
```

### 시나리오 4: 아이템 양도

```
1. 상황
   - 발트의 가방에 로프 1개 (부피 3)
   - 엘리사에게 로프를 주고 싶음

2. 플레이어 명령어
   마스토돈: @봇 [양도/로프/엘리사]

3. 봇 처리
   a. 로프 위치 확인
      - 발트의 주변 확인 → 없음
      - 발트의 가방 확인 → 있음!
   
   b. 이동 처리
      - 발트 가방: 로프 삭제 (부피 -3)
      - 엘리사 주변: 로프 추가 (부피 +3)
   
   c. 웹 동기화
      - 발트와 엘리사의 마지막수정 시각 업데이트

4. 봇 응답
   @발트 로프를 엘리사에게 양도했습니다!
   
   @엘리사 발트가 로프를 양도했습니다!
   주변 탭에서 확인하세요. (자동삭제 23:59)
   🔗 https://inventory.game.com

5. 웹 화면
   발트:
   - 가방에서 로프 사라짐
   - 용량: 18/20 → 15/20
   
   엘리사:
   - 주변 탭에 로프 추가
   - 알림: "발트가 로프를 양도했습니다!"
```

### 시나리오 5: 주변 아이템 자동 삭제

```
1. 상황
   - 발트의 주변에 배터리 2개 (부피 2)
   - 발트가 가방 정리를 안 함
   - 자정이 됨

2. 시스템 처리 (자동)
   - 크론잡 실행 (매일 0시)
   - 모든 캐릭터의 "주변" 시트 확인
   - 만료시각이 지난 아이템 삭제
   - 발트의 주변: 배터리 2개 삭제

3. 마스토돈 알림 (선택)
   @발트 
   ⚠️ 주변에 있던 아이템이 자동으로 사라졌습니다:
   - 배터리 x2 (부피: 2)
   
   다음부터는 빨리 가방에 넣으세요!

4. 웹 화면
   - 주변 탭에서 배터리 사라짐
   - 경고 메시지: "자동 삭제된 아이템이 있습니다"
```

### 시나리오 6: 부피 0 아이템 자동 처리

```
1. 상황
   - 발트가 클립 3개를 발견
   - 상점 시트에서 클립 부피: 0

2. 운영진 작업
   마스토돈: @봇 [아이템 추가/발트의 주변/클립 3개]

3. 봇 처리 (특수 로직)
   a. 상점 시트 확인
      - 클립 부피: 0 발견!
   
   b. 특수 처리
      - 주변이 아닌 여유 공간에 직접 추가
      - 발트 여유공간 시트: "클립, 클립, 클립" 추가
   
   c. 응답
      @발트 클립 3개를 발견했습니다! (부피 0)
      자동으로 여유 공간에 보관되었습니다.

4. 웹 화면
   - 주변 탭: 아무것도 안 나타남
   - 여유 공간 탭: 클립 3개 자동 추가
   - 알림: "클립 3개가 여유 공간에 추가되었습니다"
```

---

## 🔧 기술 구현

### 백엔드 API 엔드포인트

```python
# Flask API

@app.route('/api/character/<name>')
def get_character(name):
    """캐릭터 전체 정보"""
    return {
        'name': name,
        'strength': 5,
        'bag_capacity': 20,
        'bag_used': 15,
        'bag_items': [...],
        'misc_items': [...],
        'nearby_items': [...],
        'last_update': '2026-01-30 14:23:45'
    }

@app.route('/api/bag/<name>', methods=['GET'])
def get_bag(name):
    """가방 아이템 조회"""
    items = sheets.get_bag_items(name)
    capacity = calculate_capacity(name)
    return {
        'capacity': capacity,
        'used': sum(item['volume'] * item['quantity'] for item in items),
        'items': items
    }

@app.route('/api/bag/<name>', methods=['POST'])
def update_bag(name):
    """가방 아이템 업데이트 (웹에서 저장)"""
    new_items = request.json['items']
    
    # 용량 검증
    total_volume = sum(item['volume'] * item['quantity'] for item in new_items)
    capacity = calculate_capacity(name)
    
    if total_volume > capacity:
        return {'error': '용량 초과'}, 400
    
    # 시트 업데이트
    sheets.update_bag(name, new_items)
    sheets.update_timestamp(name)
    
    return {'success': True}

@app.route('/api/nearby/<name>', methods=['POST'])
def move_to_bag(name):
    """주변 → 가방 이동"""
    item_id = request.json['item_id']
    quantity = request.json['quantity']
    
    # 주변에서 아이템 확인
    nearby_items = sheets.get_nearby_items(name)
    item = find_item(nearby_items, item_id)
    
    if not item:
        return {'error': '아이템 없음'}, 404
    
    # 용량 확인
    needed_volume = item['volume'] * quantity
    available = get_available_space(name)
    
    if needed_volume > available:
        return {'error': '공간 부족'}, 400
    
    # 이동 처리
    sheets.move_item_to_bag(name, item_id, quantity)
    sheets.update_timestamp(name)
    
    return {'success': True}

@app.route('/api/nearby/cleanup', methods=['POST'])
def cleanup_nearby():
    """주변 아이템 자동 삭제 (크론잡)"""
    now = datetime.now()
    deleted_items = sheets.delete_expired_nearby_items(now)
    
    # 각 유저에게 마스토돈 알림 (선택)
    for user, items in deleted_items.items():
        send_mastodon_notification(user, items)
    
    return {'deleted': len(deleted_items)}
```

### 웹 프론트엔드 핵심 로직

```javascript
// 주변 → 가방 드래그앤드롭

let draggedItem = null;

// 주변 아이템에 드래그 이벤트
document.querySelectorAll('.nearby-item').forEach(item => {
    item.draggable = true;
    
    item.addEventListener('dragstart', (e) => {
        draggedItem = {
            id: e.target.dataset.itemId,
            name: e.target.dataset.itemName,
            volume: parseInt(e.target.dataset.volume),
            quantity: 1
        };
        e.target.style.opacity = '0.5';
    });
});

// 가방 그리드에 드롭
document.querySelectorAll('.bag-cell').forEach(cell => {
    cell.addEventListener('dragover', (e) => {
        e.preventDefault();
    });
    
    cell.addEventListener('drop', async (e) => {
        e.preventDefault();
        
        // 용량 확인
        const currentUsed = calculateCurrentUsed();
        const capacity = CHARACTER_CAPACITY;
        const needed = draggedItem.volume * draggedItem.quantity;
        
        if (currentUsed + needed > capacity) {
            alert(`공간이 부족합니다! (필요: ${needed}, 남음: ${capacity - currentUsed})`);
            return;
        }
        
        // 임시로 UI에 추가
        addItemToGrid(draggedItem);
        
        // 저장은 [저장] 버튼 클릭 시
        markAsUnsaved();
    });
});

// 저장 버튼
document.getElementById('save-btn').addEventListener('click', async () => {
    const bagItems = collectBagItems();
    
    const response = await fetch(`/api/bag/${characterName}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({items: bagItems})
    });
    
    if (response.ok) {
        alert('저장되었습니다!');
        
        // 주변에서 이동한 아이템 제거 요청
        await moveNearbyToBag();
        
        // 새로고침
        location.reload();
    } else {
        const error = await response.json();
        alert(`저장 실패: ${error.error}`);
    }
});

// 실시간 동기화 (폴링)
setInterval(async () => {
    const response = await fetch(`/api/character/${characterName}`);
    const data = await response.json();
    
    if (data.last_update > lastKnownUpdate) {
        console.log('변경사항 감지!');
        
        if (hasUnsavedChanges()) {
            showNotification('⚠️ 다른 곳에서 변경되었습니다. 저장하지 않은 변경사항이 있습니다.');
        } else {
            location.reload();
        }
        
        lastKnownUpdate = data.last_update;
    }
}, 2000);
```

### 마스토돈 봇 핵심 로직

```python
from mastodon import Mastodon
import gspread

mastodon = Mastodon(access_token='TOKEN')
sheets = gspread.authorize(creds)

@mastodon.stream.user()
def on_notification(notification):
    if notification['type'] != 'mention':
        return
    
    content = notification['status']['content']
    user = notification['account']['username']
    
    # [아이템 추가/캐릭터명/아이템명 수량] - GM 전용
    if '[아이템 추가/' in content:
        parts = extract_command(content, '아이템 추가')
        character = parts[0]
        item_info = parts[1]  # "사과 3개"
        
        item_name, quantity = parse_item_info(item_info)
        
        # 상점에서 아이템 정보 조회
        item_data = sheets.get_item_from_shop(item_name)
        
        if not item_data:
            reply(f"❌ '{item_name}'은(는) 상점에 등록되지 않은 아이템입니다.")
            return
        
        # 부피 0이면 여유 공간에 직접 추가
        if item_data['volume'] == 0:
            sheets.add_to_misc_space(character, item_name, quantity)
            reply(f"@{character} {item_name} {quantity}개를 발견했습니다! (부피 0)\n"
                  f"자동으로 여유 공간에 보관되었습니다.")
            return
        
        # 주변에 추가
        sheets.add_to_nearby(character, item_name, quantity, item_data['volume'])
        
        # 가방 용량 확인
        capacity = calculate_capacity(character)
        used = calculate_bag_used(character)
        available = capacity - used
        total_volume = item_data['volume'] * quantity
        
        # 응답 메시지
        if total_volume <= available:
            reply(f"@{character} {item_name} {quantity}개를 발견했습니다! (총 부피: {total_volume})\n"
                  f"가방 남은 공간: {available}칸\n"
                  f"웹페이지에서 가방에 넣으세요.\n"
                  f"🔗 https://inventory.game.com")
        else:
            reply(f"@{character} {item_name} {quantity}개를 발견했습니다! (총 부피: {total_volume})\n"
                  f"⚠️ 가방 공간이 부족합니다! (남은 공간: {available}칸)\n\n"
                  f"선택지:\n"
                  f"1. 웹에서 기존 아이템을 버리고 넣기\n"
                  f"2. 주변에 두고 나중에 정리하기\n"
                  f"3. [양도] 명령어로 다른 플레이어에게 주기\n\n"
                  f"⚠️ 주변 아이템은 오늘 24:00에 자동 삭제됩니다!\n"
                  f"🔗 https://inventory.game.com")
    
    # [사용/아이템명]
    elif '[사용/' in content:
        item_name = extract_command(content, '사용')[0]
        
        # 1. 주변 확인
        nearby_items = sheets.get_nearby_items(user)
        item = find_item(nearby_items, item_name)
        
        if item:
            # 주변에 있으면 사용
            use_item(user, item)
            sheets.delete_from_nearby(user, item_name, 1)
            reply(f"@{user} {item_name}을(를) 사용했습니다!\n{format_effect(item)}")
            return
        
        # 2. 가방 확인
        bag_items = sheets.get_bag_items(user)
        item = find_item(bag_items, item_name)
        
        if item:
            # 가방에 있으면 사용
            use_item(user, item)
            sheets.decrease_bag_item(user, item_name, 1)
            sheets.update_timestamp(user)
            
            remaining = item['quantity'] - 1
            if remaining > 0:
                reply(f"@{user} {item_name}을(를) 사용했습니다!\n"
                      f"{format_effect(item)}\n"
                      f"남은 {item_name}: {remaining}개")
            else:
                reply(f"@{user} {item_name}을(를) 사용했습니다!\n"
                      f"{format_effect(item)}\n"
                      f"(마지막 {item_name}을 사용했습니다)")
            return
        
        # 3. 여유 공간 확인
        misc_items = sheets.get_misc_items(user)
        if item_name in misc_items:
            use_item(user, {'name': item_name})
            sheets.delete_from_misc(user, item_name, 1)
            sheets.update_timestamp(user)
            reply(f"@{user} {item_name}을(를) 사용했습니다!\n{format_effect(item)}")
            return
        
        # 없음
        reply(f"@{user} ❌ {item_name}을(를) 소지하고 있지 않습니다.")
    
    # [양도/아이템명/받는사람]
    elif '[양도/' in content:
        parts = extract_command(content, '양도')
        item_name = parts[0]
        recipient = parts[1]
        
        # 주변 또는 가방에서 찾기
        location = find_item_location(user, item_name)
        
        if not location:
            reply(f"@{user} ❌ {item_name}을(를) 소지하고 있지 않습니다.")
            return
        
        # 이동 처리
        if location == 'nearby':
            sheets.move_nearby_to_nearby(user, recipient, item_name, 1)
        elif location == 'bag':
            sheets.move_bag_to_nearby(user, recipient, item_name, 1)
        elif location == 'misc':
            sheets.move_misc_to_misc(user, recipient, item_name, 1)
        
        sheets.update_timestamp(user)
        sheets.update_timestamp(recipient)
        
        reply(f"@{user} {item_name}을(를) {recipient}에게 양도했습니다!")
        reply(f"@{recipient} {user}가 {item_name}을(를) 양도했습니다!\n"
              f"{'주변' if location != 'misc' else '여유 공간'} 탭에서 확인하세요.\n"
              f"🔗 https://inventory.game.com")

def calculate_capacity(character_name):
    """근력 기반 가방 용량 계산"""
    strength = sheets.get_strength(character_name)
    
    if 1 <= strength <= 5:
        return 20
    elif 6 <= strength <= 10:
        return 40
    elif 11 <= strength <= 15:
        return 60
    else:
        return 20  # 기본값
```

### 크론잡 (주변 아이템 자동 삭제)

```python
# cron_cleanup.py
import schedule
import time
from datetime import datetime

def cleanup_nearby_items():
    """매일 0시에 실행"""
    print(f"[{datetime.now()}] 주변 아이템 자동 삭제 시작...")
    
    # 모든 캐릭터의 주변 아이템 확인
    all_nearby = sheets.get_all_nearby_items()
    deleted_count = 0
    
    for character, items in all_nearby.items():
        for item in items:
            # 만료 확인
            if is_expired(item['expire_time']):
                sheets.delete_nearby_item(character, item['id'])
                deleted_count += 1
                
                # 마스토돈 알림
                mastodon.status_post(
                    f"@{character}\n"
                    f"⚠️ 주변에 있던 아이템이 자동으로 사라졌습니다:\n"
                    f"- {item['name']} x{item['quantity']} (부피: {item['volume']})\n\n"
                    f"다음부터는 빨리 가방에 넣으세요!"
                )
    
    print(f"[{datetime.now()}] 완료. 삭제된 아이템: {deleted_count}개")

# 매일 0시에 실행
schedule.every().day.at("00:00").do(cleanup_nearby_items)

# 또는 1시간마다 실행
# schedule.every().hour.do(cleanup_nearby_items)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 📊 용량 계산 상세

### 근력별 용량
```
근력 1:  용량 20
근력 2:  용량 20
근력 3:  용량 20
근력 4:  용량 20
근력 5:  용량 20
────────────────
근력 6:  용량 40
근력 7:  용량 40
근력 8:  용량 40
근력 9:  용량 40
근력 10: 용량 40
────────────────
근력 11: 용량 60
근력 12: 용량 60
근력 13: 용량 60
근력 14: 용량 60
근력 15: 용량 60
```

### 예시 계산
```
발트 (근력 5):
- 기본 용량: 20
- 보유 아이템:
  • 사과 x3 (1개당 1) = 3
  • 물병 x2 (1개당 2) = 4
  • 손전등 x1 (3) = 3
- 총 사용: 10/20

엘리사 (근력 8):
- 기본 용량: 40
- 보유 아이템:
  • 칼 x1 (4) = 4
  • 로프 x1 (3) = 3
  • 의료 키트 x2 (1개당 5) = 10
  • 배터리 x5 (1개당 1) = 5
- 총 사용: 22/40
```

---

## 🎨 UI 디자인 가이드

### 색상 코드
```css
/* 기본 */
--bg-primary: #FFFFFF;
--bg-secondary: #F5F5F5;
--border: #DDDDDD;
--text-primary: #333333;
--text-secondary: #666666;

/* 상태 */
--success: #4CAF50;
--warning: #FF9800;
--danger: #F44336;
--info: #2196F3;

/* 아이템 */
--item-bg: #8B4513;
--item-text: #FFFFFF;
--empty-cell: #FAFAFA;
--hover-cell: #E3F2FD;
```

### 아이콘
```
📦 가방
🎒 주변 아이템
📎 여유 공간
🗑️ 휴지통
🔄 새로고침
💾 저장
🕐 자동삭제 타이머
⚠️ 경고
✅ 성공
❌ 실패
```

### 반응형 브레이크포인트
```css
/* 데스크톱 */
@media (min-width: 1200px) {
    .inventory-grid { grid-template-columns: repeat(10, 60px); }
}

/* 태블릿 */
@media (max-width: 1199px) and (min-width: 768px) {
    .inventory-grid { grid-template-columns: repeat(10, 50px); }
}

/* 모바일 */
@media (max-width: 767px) {
    .inventory-grid { grid-template-columns: repeat(5, 60px); }
    .character-list { display: none; } /* 햄버거 메뉴로 */
}
```

---

## 🔐 권한 및 규칙

### 명령어 권한
```
GM (운영진):
- [아이템 추가] ✓
- [강제 삭제] ✓
- [스탯 수정] ✓

플레이어:
- [사용] ✓
- [양도] ✓
- [아이템 추가] ✗
```

### 웹 권한
```
자기 캐릭터:
- 가방 정리 ✓
- 주변 → 가방 이동 ✓
- 아이템 버리기 ✓
- 모든 탭 조회 ✓

다른 캐릭터:
- 조회만 가능 ✓
- 수정 불가 ✗
```

### 규칙
1. **주변 → 가방**: 웹에서만 가능
2. **사용/양도**: 마스토돈 명령어로만 가능
3. **부피 0 아이템**: 자동으로 여유 공간에 편입
4. **주변 아이템**: 정기적으로 자동 삭제
5. **동시 편집**: 마지막 저장이 우선 (충돌 시 경고)

---

## 🐛 예외 상황 처리

### 1. 용량 초과 저장 시도
```
상황: 웹에서 용량 21/20으로 저장 시도

처리:
1. 서버 검증 실패
2. 응답: {"error": "용량 초과 (21/20)"}
3. 웹: 경고 표시 "용량을 초과했습니다! 아이템을 더 빼주세요."
4. 저장 취소
```

### 2. 주변 아이템 만료 중 사용
```
상황: 자동 삭제 스크립트 실행 중 플레이어가 [사용] 명령어 입력

처리:
1. 봇이 주변에서 아이템 확인
2. 아이템 발견 → 즉시 사용 처리
3. 크론잡은 이미 삭제된 아이템이므로 스킵
4. 문제없음 (Race Condition 회피)
```

### 3. 동시 편집 충돌
```
상황: 
- 플레이어가 웹에서 가방 정리 중
- 동시에 [사용] 명령어 입력

처리:
1. 봇이 먼저 처리 → 시트 업데이트 → 타임스탬프 변경
2. 플레이어가 [저장] 버튼 클릭
3. 서버가 타임스탬프 확인 → 불일치 감지
4. 응답: {"error": "다른 곳에서 변경되었습니다. 새로고침 후 다시 시도하세요."}
5. 웹: 경고 + 새로고침 버튼
```

### 4. 존재하지 않는 아이템 추가
```
상황: GM이 상점에 없는 아이템 추가 시도

명령어: @봇 [아이템 추가/발트의 주변/환상의 검]

처리:
1. 봇이 상점 시트 확인
2. "환상의 검" 없음
3. 응답: "❌ '환상의 검'은 상점에 등록되지 않은 아이템입니다."
4. 추가 실패
```

---

## 📈 성능 최적화

### 캐싱
```python
import redis

cache = redis.Redis()

def get_character_data(name):
    # 캐시 확인
    cache_key = f"char:{name}"
    cached = cache.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # 시트에서 로드
    data = sheets.get_character(name)
    
    # 캐시 저장 (30초)
    cache.setex(cache_key, 30, json.dumps(data))
    
    return data

def invalidate_cache(name):
    """저장 시 캐시 무효화"""
    cache.delete(f"char:{name}")
```

### 배치 처리
```python
def update_multiple_characters(updates):
    """여러 캐릭터 동시 업데이트"""
    # 한 번에 처리
    sheets.batch_update(updates)
    
    # 캐시 무효화
    for name in updates.keys():
        invalidate_cache(name)
```

---

## 🧪 테스트 시나리오

### 기본 기능
- [ ] 아이템 획득 (정상)
- [ ] 아이템 획득 (용량 부족)
- [ ] 주변 → 가방 이동
- [ ] 아이템 사용 (주변)
- [ ] 아이템 사용 (가방)
- [ ] 아이템 양도
- [ ] 아이템 버리기 (웹)
- [ ] 부피 0 아이템 자동 편입

### 자동화
- [ ] 주변 아이템 자동 삭제
- [ ] 실시간 동기화 (웹 ↔ 봇)
- [ ] 용량 자동 계산

### 엣지 케이스
- [ ] 동시 편집 충돌
- [ ] 존재하지 않는 아이템
- [ ] 용량 초과 시도
- [ ] 만료된 주변 아이템 사용 시도

---

## 📝 구현 우선순위

### Phase 1: 기본 인프라 (1주)
- [x] 구글 시트 구조 설계
- [ ] 마스토돈 봇 명령어 ([아이템 추가], [사용], [양도])
- [ ] Flask API 기본 틀
- [ ] 웹 페이지 기본 레이아웃

### Phase 2: 핵심 기능 (2주)
- [ ] 가방 그리드 렌더링
- [ ] 주변 리스트 렌더링
- [ ] 여유 공간 리스트 렌더링
- [ ] 드래그앤드롭 (주변 → 가방)
- [ ] 저장 기능
- [ ] 실시간 동기화

### Phase 3: 자동화 (1주)
- [ ] 주변 아이템 자동 삭제 크론잡
- [ ] 부피 0 아이템 자동 처리
- [ ] 마스토돈 알림 시스템

### Phase 4: 최적화 (1주)
- [ ] 캐싱 적용
- [ ] 반응형 디자인
- [ ] 성능 테스트
- [ ] 배포

---

## 🔮 향후 확장 가능성

### 추가 기능
1. **장비 시스템**: 착용 중인 장비 별도 슬롯
2. **무게 시스템**: 부피 외 무게 개념 추가
3. **아이템 조합**: 여러 아이템 합쳐서 새 아이템
4. **내구도**: 사용 횟수 제한
5. **거래소**: 플레이어 간 자동 거래

### 기술 개선
1. **웹소켓**: 실시간 양방향 통신
2. **PostgreSQL**: 구글 시트 대체
3. **모바일 앱**: 네이티브 앱
4. **AI 추천**: 최적 배치 자동 제안
