# Trashpit - 마스토돈 TRPG 인벤토리 관리 시스템

마스토돈 기반 TRPG 게임의 인벤토리를 구글 시트(데이터)와 웹 인터페이스(시각화)로 분리 관리하는 시스템입니다.

## 구조 개요

| 구성요소 | 기술 스택 | 역할 |
|---------|----------|------|
| **봇** | Python + Mastodon.py | 마스토돈 명령어 처리 (`[사용/아이템]`, `[획득/아이템]` 등) |
| **API** | Python Flask | 구글 시트 연동 REST API |
| **웹** | HTML/CSS/JS | 드래그앤드롭 그리드 UI |
| **데이터** | Google Sheets | 캐릭터·아이템 마스터 저장소 |

## 프로젝트 구조

```
trashpit/
├── bot/                   # 마스토돈 봇
│   ├── main.py            # 진입점 (폴링 루프)
│   ├── mastodon_client.py # 마스토돈 API 래퍼
│   └── commands/          # 명령어 핸들러 (use, give, discard, acquire)
├── api/                   # 백엔드 API (Flask)
│   ├── app.py             # Flask 앱 진입점
│   ├── routes/            # API 엔드포인트
│   ├── services/          # 비즈니스 로직 (시트, 인벤토리, 아이템)
│   └── utils/             # 파서 등 유틸리티
├── web/                   # 웹 프론트엔드
│   ├── index.html
│   ├── css/               # 스타일
│   └── js/                # 앱, API, 인벤토리, 드래그앤드롭, UI
├── shared/                # 봇 & API 공용
│   ├── constants.py       # 상수 (용량 규칙 등)
│   ├── models.py          # 데이터 모델
│   └── google_sheets.py   # 구글 시트 연결
├── scripts/               # 유틸리티 스크립트
│   ├── cleanup_nearby.py  # 주변 아이템 자동 삭제 (cron용)
│   └── sync_cache.py      # 캐시 동기화
└── docs/                  # 기획 문서
```

## 설정

1. `.env.example`을 복사하여 `.env` 생성
2. 구글 서비스 계정 `credentials.json`을 프로젝트 루트에 배치
3. `.env`에 `SHEET_ID`, `MASTODON_API_BASE_URL`, `BOT_ACCESS_TOKEN` 등 설정

## 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 봇 실행
python -m bot.main

# API 서버 실행
python -m api.app

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
