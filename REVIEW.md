# 🕵️‍♂️ Code Review Report: Phase 2 Analysis

**Date:** 2026-02-01
**Reviewer:** Ray (Senior Dev Agent)
**Branch:** `refactor/phase2-cleanup`

## 📊 Summary
Phase 2까지의 기능 구현은 구조적으로 잘 잡혀 있으나, **안정성(Stability)**과 **유지보수성(Maintainability)** 측면에서 개선이 필요합니다. 특히 "테스트/디버깅 없음" 상태이므로, 에러 핸들링과 설정 관리를 최우선으로 리팩토링해야 합니다.

---

## 🔍 Key Findings

### 1. 🏗️ Architecture & Structure
- **Good:** `bot`, `api`, `shared`, `web`으로 역할 분리가 명확합니다.
- **Bad:** `bot/main.py`와 `api/app.py`에서 `sys.path.insert`를 사용하여 상위 경로를 강제로 추가하고 있습니다. 이는 배포 환경에 따라 경로 에러를 유발할 수 있는 **Fragile Code**입니다.
- **Fix:** Python 모듈 실행 방식(`python -m bot.main`)을 표준으로 정착시키고, `sys.path` 해킹 코드를 제거해야 합니다.

### 2. ⚙️ Configuration Management
- **Issue:** `.env` 로딩(`load_dotenv()`)이 `bot/main.py`, `api/app.py` 등 여러 곳에 산재해 있습니다. 환경변수 키 이름(`SHEET_ID` vs `GOOGLE_SHEET_ID`)이 혼용될 위험이 있습니다.
- **Fix:** **`shared/config.py`** 모듈을 신설하여 설정을 중앙에서 관리하고, 타입 변환(str -> int/bool) 및 유효성 검사를 수행해야 합니다.

### 3. 🛡️ Google Sheets Integration (`shared/google_sheets.py`)
- **Risk:** `get_client()`와 `get_spreadsheet()`가 싱글톤으로 구현되어 있으나, 네트워크 에러나 API Quota 초과 시 **재시도(Retry) 로직**이 없습니다. TRPG 특성상 동시에 여러 명령어가 몰리면 터질 수 있습니다.
- **Fix:** `gspread` 호출 부에 `retry` 데코레이터를 적용하고, 명시적인 예외 처리를 추가해야 합니다.

### 4. 🤖 Bot Logic
- **Code:** `bot/main.py`의 `run_polling_loop`는 기본적인 백오프(Backoff)를 구현하고 있어 좋습니다.
- **Concern:** 명령어 핸들러(`bot.commands.*`)의 구체적인 구현을 아직 확인하지 못했으나, 시트 조작 실패 시 사용자에게 적절한 피드백(예: "잠시 후 다시 시도해주세요")을 주는지 확인이 필요합니다.

---

## 🚀 Action Plan (Refactoring)

### Step 1: Centralize Config
- `shared/config.py` 생성.
- 모든 `os.getenv` 호출을 제거하고 `config.SHEET_ID` 형태로 변경.

### Step 2: Harden Google Sheets
- `shared/google_sheets.py` 리팩토링.
- `tenacity` 라이브러리(없으면 직접 구현)를 이용한 Retry 로직 추가.

### Step 3: Standardize Entry Points
- `sys.path` hack 제거.
- 실행 스크립트(`run_bot.sh`, `run_api.sh`) 또는 `Makefile` 제공.

---

**Review Verdict:** 🚧 **Needs Refactoring** before Phase 3.
