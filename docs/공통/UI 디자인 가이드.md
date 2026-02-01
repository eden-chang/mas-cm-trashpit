# UI 디자인 가이드

> **Note:** 이 가이드는 실제 Figma 코드(trashpit-figma/)를 기준으로 작성되었습니다.
> 다크 테마 + Glassmorphism + Cyan/Purple 악센트 스타일을 사용합니다.

## 색상 코드

### 기본 색상 (다크 테마)

```css
:root {
    /* 배경 - 다크 테마 */
    --bg-base: #0B0E14;        /* 기본 배경 */
    --bg-raised: #1C2128;      /* 카드/패널 배경 */
    --bg-overlay: #2A2F3A;     /* 오버레이/모달 배경 */
    --bg-surface: #161B22;     /* 표면 배경 */

    /* 테두리 */
    --border-subtle: rgba(255, 255, 255, 0.1);
    --border-default: rgba(255, 255, 255, 0.2);
    --border-strong: rgba(255, 255, 255, 0.3);

    /* 텍스트 */
    --text-primary: #FFFFFF;
    --text-secondary: rgba(255, 255, 255, 0.7);
    --text-muted: rgba(255, 255, 255, 0.5);
    --text-disabled: rgba(255, 255, 255, 0.3);
}
```

### 악센트 색상

```css
:root {
    /* 주요 악센트 */
    --cyan: #00F3FF;
    --cyan-glow: rgba(0, 243, 255, 0.3);
    --cyan-muted: rgba(0, 243, 255, 0.6);

    --purple: #BF5AF2;
    --purple-glow: rgba(191, 90, 242, 0.3);
    --purple-muted: rgba(191, 90, 242, 0.6);

    /* 그라데이션 */
    --gradient-primary: linear-gradient(135deg, var(--cyan), var(--purple));
    --gradient-subtle: linear-gradient(135deg, rgba(0, 243, 255, 0.1), rgba(191, 90, 242, 0.1));
}
```

### 상태 색상

```css
:root {
    /* 성공 */
    --success: #00FF88;
    --success-bg: rgba(0, 255, 136, 0.1);
    --success-border: rgba(0, 255, 136, 0.3);

    /* 경고 */
    --warning: #FFB020;
    --warning-bg: rgba(255, 176, 32, 0.1);
    --warning-border: rgba(255, 176, 32, 0.3);

    /* 위험 */
    --danger: #FF4757;
    --danger-bg: rgba(255, 71, 87, 0.1);
    --danger-border: rgba(255, 71, 87, 0.3);

    /* 정보 */
    --info: #00F3FF;
    --info-bg: rgba(0, 243, 255, 0.1);
    --info-border: rgba(0, 243, 255, 0.3);
}
```

### 아이템/그리드 색상

```css
:root {
    /* 아이템 셀 */
    --item-bg: rgba(0, 243, 255, 0.15);
    --item-border: rgba(0, 243, 255, 0.4);
    --item-text: #00F3FF;

    /* 빈 셀 */
    --empty-cell: rgba(255, 255, 255, 0.03);
    --empty-cell-border: rgba(255, 255, 255, 0.1);

    /* 호버 상태 */
    --hover-cell: rgba(0, 243, 255, 0.1);
    --hover-border: rgba(0, 243, 255, 0.3);

    /* 드롭 대상 */
    --drop-target-bg: rgba(0, 255, 136, 0.15);
    --drop-target-border: rgba(0, 255, 136, 0.5);
}
```

---

## Glassmorphism 스타일

### 기본 Glass 효과

```css
.glass {
    background: rgba(28, 33, 40, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
}

.glass-subtle {
    background: rgba(28, 33, 40, 0.6);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.glass-strong {
    background: rgba(28, 33, 40, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.15);
}
```

### Glow 효과

```css
.glow-cyan {
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.3),
                0 0 40px rgba(0, 243, 255, 0.1);
}

.glow-purple {
    box-shadow: 0 0 20px rgba(191, 90, 242, 0.3),
                0 0 40px rgba(191, 90, 242, 0.1);
}

.glow-success {
    box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
}

.glow-danger {
    box-shadow: 0 0 15px rgba(255, 71, 87, 0.4);
}
```

---

## 아이콘

| 용도 | 아이콘 | 색상 |
|------|--------|------|
| 가방 | 📦 | -- |
| 주변 아이템 | 🎒 | -- |
| 여유 공간 | 📎 | -- |
| 휴지통 | 🗑️ | --danger |
| 새로고침 | 🔄 | --cyan |
| 저장 | 💾 | --success |
| 자동삭제 타이머 | 🕐 | --warning |
| 경고 | ⚠️ | --warning |
| 성공 | ✅ | --success |
| 실패 | ❌ | --danger |
| 아이템 사용 | ✨ | --purple |
| 양도 | 📤 | --cyan |
| 수신 | 📥 | --cyan |

**lucide-react 아이콘 사용 권장:**
- `RefreshCw`: 새로고침
- `Save`: 저장
- `Trash2`: 삭제
- `Package`: 가방
- `Clock`: 타이머
- `AlertTriangle`: 경고
- `Check`: 성공
- `X`: 실패/닫기
- `Menu`: 햄버거 메뉴
- `Search`: 검색
- `ChevronDown/Up`: 펼치기/접기

---

## 타이포그래피

```css
/* 기본 폰트 */
body {
    font-family: 'Inter', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    color: var(--text-primary);
    background: var(--bg-base);
}

/* 제목 */
h1 {
    font-size: 1.5rem;
    font-weight: 700;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
h2 { font-size: 1.25rem; font-weight: 600; color: var(--text-primary); }
h3 { font-size: 1.1rem; font-weight: 600; color: var(--text-primary); }
h4 { font-size: 1rem; font-weight: 500; color: var(--text-secondary); }

/* 본문 */
p { font-size: 0.9rem; color: var(--text-secondary); }
small { font-size: 0.8rem; color: var(--text-muted); }

/* 악센트 텍스트 */
.text-cyan { color: var(--cyan); }
.text-purple { color: var(--purple); }
.text-success { color: var(--success); }
.text-warning { color: var(--warning); }
.text-danger { color: var(--danger); }
```

---

## 컴포넌트

### 버튼

```css
.btn {
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}

/* Primary - Cyan 그라데이션 */
.btn-primary {
    background: var(--gradient-primary);
    color: white;
    border: none;
}

.btn-primary:hover {
    box-shadow: 0 0 20px var(--cyan-glow);
    transform: translateY(-1px);
}

/* Secondary - Glass 스타일 */
.btn-secondary {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
}

.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: var(--cyan);
}

/* Ghost - 투명 */
.btn-ghost {
    background: transparent;
    color: var(--text-secondary);
}

.btn-ghost:hover {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-primary);
}

/* Danger */
.btn-danger {
    background: var(--danger);
    color: white;
}

.btn-danger:hover {
    box-shadow: 0 0 15px var(--danger);
}
```

### 카드

```css
.card {
    background: var(--bg-raised);
    border-radius: 12px;
    border: 1px solid var(--border-subtle);
    padding: 16px;
    backdrop-filter: blur(8px);
}

.card-header {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-subtle);
}

.card:hover {
    border-color: var(--border-default);
}

.card.selected {
    border-color: var(--cyan);
    box-shadow: 0 0 15px var(--cyan-glow);
}
```

### 입력 필드

```css
.input {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    padding: 8px 12px;
    color: var(--text-primary);
    font-size: 0.9rem;
    transition: all 0.2s;
}

.input::placeholder {
    color: var(--text-muted);
}

.input:focus {
    outline: none;
    border-color: var(--cyan);
    box-shadow: 0 0 10px var(--cyan-glow);
}
```

### 알림/토스트

```css
.alert {
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    border-left: 4px solid;
    backdrop-filter: blur(8px);
}

.alert-success {
    background: var(--success-bg);
    border-left-color: var(--success);
    color: var(--success);
}

.alert-warning {
    background: var(--warning-bg);
    border-left-color: var(--warning);
    color: var(--warning);
}

.alert-danger {
    background: var(--danger-bg);
    border-left-color: var(--danger);
    color: var(--danger);
}

.alert-info {
    background: var(--info-bg);
    border-left-color: var(--info);
    color: var(--info);
}
```

### 프로그레스 바 (용량 표시)

```css
.progress-bar {
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease, background 0.3s ease;
}

/* 상태별 색상 */
.progress-fill.safe {
    background: var(--success);
    box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.progress-fill.warning {
    background: var(--warning);
    box-shadow: 0 0 10px rgba(255, 176, 32, 0.5);
}

.progress-fill.danger {
    background: var(--danger);
    box-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
}
```

---

## 그리드 셀

```css
.grid-cell {
    width: 40px;
    height: 40px;
    background: var(--empty-cell);
    border: 1px solid var(--empty-cell-border);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    cursor: pointer;
}

.grid-cell:hover {
    background: var(--hover-cell);
    border-color: var(--hover-border);
}

/* 아이템이 있는 셀 */
.grid-cell.occupied {
    background: var(--item-bg);
    border-color: var(--item-border);
    color: var(--item-text);
}

.grid-cell.occupied:hover {
    box-shadow: 0 0 15px var(--cyan-glow);
}

/* 드롭 대상 */
.grid-cell.drop-target {
    background: var(--drop-target-bg);
    border-color: var(--drop-target-border);
    border-style: dashed;
    animation: pulse 1s infinite;
}

/* 드래그 중인 셀 */
.grid-cell.dragging {
    opacity: 0.5;
    transform: scale(0.95);
}
```

---

## 드래그 앤 드롭 영역

### 휴지통 영역

```css
.trash-zone {
    background: rgba(255, 71, 87, 0.1);
    border: 2px dashed rgba(255, 71, 87, 0.3);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.2s ease;
}

.trash-zone.active {
    background: rgba(255, 71, 87, 0.2);
    border-color: var(--danger);
    box-shadow: 0 0 20px rgba(255, 71, 87, 0.3);
}
```

### 주변 아이템 영역

```css
.nearby-zone {
    background: rgba(191, 90, 242, 0.1);
    border: 1px solid rgba(191, 90, 242, 0.2);
    border-radius: 12px;
    padding: 16px;
}

.nearby-zone.active {
    border-color: var(--purple);
    box-shadow: 0 0 15px var(--purple-glow);
}
```

### 여유공간 영역

```css
.misc-zone {
    background: rgba(0, 243, 255, 0.05);
    border: 1px solid rgba(0, 243, 255, 0.2);
    border-radius: 12px;
    padding: 16px;
}
```

---

## 반응형 브레이크포인트

```css
/* 데스크톱 (1200px 이상) */
@media (min-width: 1200px) {
    .inventory-grid {
        grid-template-columns: repeat(10, 48px);
        gap: 4px;
    }

    .sidebar {
        width: 280px;
    }
}

/* 태블릿 (768px ~ 1199px) */
@media (max-width: 1199px) and (min-width: 768px) {
    .inventory-grid {
        grid-template-columns: repeat(10, 40px);
        gap: 3px;
    }

    .sidebar {
        width: 240px;
    }
}

/* 모바일 (767px 이하) */
@media (max-width: 767px) {
    .inventory-grid {
        grid-template-columns: repeat(5, 48px);
        gap: 4px;
    }

    .sidebar {
        display: none;
        position: fixed;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        z-index: 50;
        background: var(--bg-base);
    }

    .sidebar.open {
        display: block;
    }

    .mobile-menu {
        display: flex;
    }
}
```

---

## 애니메이션

```css
/* 페이드 인 */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* 슬라이드 인 */
@keyframes slideIn {
    from {
        transform: translateY(-10px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

/* 슬라이드 업 */
@keyframes slideUp {
    from {
        transform: translateY(20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

/* 펄스 (드롭 대상) */
@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(0, 255, 136, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(0, 255, 136, 0);
    }
}

/* 글로우 펄스 */
@keyframes glowPulse {
    0%, 100% {
        box-shadow: 0 0 15px var(--cyan-glow);
    }
    50% {
        box-shadow: 0 0 25px var(--cyan-glow), 0 0 35px var(--cyan-glow);
    }
}

/* 흔들기 (에러) */
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

/* 스핀 (로딩) */
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
```

---

## Tailwind CSS 설정 예시

```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        bg: {
          base: '#0B0E14',
          raised: '#1C2128',
          overlay: '#2A2F3A',
          surface: '#161B22',
        },
        cyan: {
          DEFAULT: '#00F3FF',
          glow: 'rgba(0, 243, 255, 0.3)',
        },
        purple: {
          DEFAULT: '#BF5AF2',
          glow: 'rgba(191, 90, 242, 0.3)',
        },
        success: '#00FF88',
        warning: '#FFB020',
        danger: '#FF4757',
      },
      backdropBlur: {
        glass: '12px',
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(0, 243, 255, 0.3)',
        'glow-purple': '0 0 20px rgba(191, 90, 242, 0.3)',
      },
    },
  },
}
```
