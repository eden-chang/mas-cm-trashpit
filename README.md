# Trashpit - 마스토돈 TRPG 인벤토리 관리 시스템

마스토돈 기반 TRPG 게임의 인벤토리를 **Supabase**(데이터베이스)와 **웹 인터페이스**(시각화)로 분리 관리하는 시스템입니다.

## 구조 개요

| 구성요소 | 기술 스택 | 역할 |
|---------|----------|------|
| **봇** | Python + Mastodon.py | 마스토돈 명령어 처리 (`[사용/아이템]`, `[획득/아이템]` 등) |
| **API** | Python Flask | Supabase 연동 REST API |
| **웹** | React + TypeScript + Vite | 드래그앤드롭 그리드 UI |
| **데이터** | Supabase (PostgreSQL) | 캐릭터·아이템 마스터 저장소 |

## 데이터베이스

### `characters` 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| name | text | 캐릭터 이름 (PK) |
| id | text | 마스토돈 계정 ID |
| side | text | 진영 (웨가/스카이) |
| con | integer | 체력 |
| str | integer | 근력 |
| luck | integer | 행운 |
| hp | integer | 현재 HP |
| points | integer | 소지금 |
| bag | jsonb | 가방 아이템 |
| misc | jsonb | 여유공간 아이템 |
| around | jsonb | 주변 아이템 |
| arrange | jsonb | 그리드 배치 정보 |

### `items` 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| name | text | 아이템명 (PK) |
| price | text | 가격 또는 "비매품" |
| description | text | 설명 |
| use_script | text | 사용 문구 |
| change_stats | text | 영향 스탯 |
| change_value | text | 변화량 |
| size | integer | 부피 |

## 프로젝트 구조

```
trashpit/
├── bot/                   # 마스토돈 봇
│   ├── main.py            # 진입점 (폴링 루프)
│   ├── mastodon_client.py # 마스토돈 API 래퍼
│   └── services/          # 비즈니스 로직
├── api/                   # 백엔드 API (Flask)
│   ├── app.py             # Flask 앱 진입점
│   ├── routes/            # API 엔드포인트
│   └── services/          # 비즈니스 로직 (Supabase, 인벤토리, 아이템)
├── web/                   # 웹 프론트엔드 (React)
│   ├── src/               # React 컴포넌트
│   └── vite.config.ts     # Vite 설정
├── shared/                # 봇 & API 공용
│   ├── constants.py       # 상수 (용량 규칙 등)
│   ├── models.py          # 데이터 모델
│   ├── supabase_client.py # Supabase 연결
│   └── parser.py          # JSON 인벤토리 파서
├── scripts/               # 유틸리티 스크립트
│   ├── cleanup_nearby.py  # 주변 아이템 자동 삭제 (cron용)
│   └── sync_cache.py      # 캐시 동기화
└── docs/                  # 기획 문서
```

## 설정

1. `.env.example`을 복사하여 `.env` 생성
2. `.env`에 Supabase 및 마스토돈 설정:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# Mastodon
MASTODON_API_BASE_URL=https://trashpit.site
BOT_ACCESS_TOKEN=your_bot_access_token
SYSTEM_ADMIN_ID=admin1,admin2
POLLING_INTERVAL=30
```

## 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 봇 실행
python -m bot.main

# API 서버 실행
python -m api.app

# 웹 개발 서버 실행
cd web && npm install && npm run dev

# 주변 아이템 자동 삭제 (cron 등에서 호출)
python scripts/cleanup_nearby.py

# 캐시 동기화
python scripts/sync_cache.py
```

## 3단계 인벤토리

- **가방**: 근력에 따라 용량 20/40/60, 부피 제한 있음
- **여유 공간**: 부피 0 아이템 전용, 용량 제한 없음
- **주변**: 획득 후 임시 보관, 매일 0시 자동 삭제

## 문서

`docs/` 폴더에 Phase 0~6 기획 문서가 있습니다.

| Phase | 내용 |
|-------|------|
| Phase 0 | 프로젝트 개요 |
| Phase 1 | 데이터베이스 설계 (Supabase) |
| Phase 2 | 마스토돈 봇 |
| Phase 3 | 백엔드 API |
| Phase 4 | 웹 프론트엔드 |
| Phase 5 | 자동화 |
| Phase 6 | 테스트 및 배포 |
