# UI 디자인 가이드

## 색상 코드

### 기본 색상

```css
:root {
    /* 배경 */
    --bg-primary: #FFFFFF;
    --bg-secondary: #F5F5F5;
    --bg-tertiary: #FAFAFA;

    /* 테두리 */
    --border-light: #EEEEEE;
    --border-default: #DDDDDD;
    --border-dark: #CCCCCC;

    /* 텍스트 */
    --text-primary: #333333;
    --text-secondary: #666666;
    --text-muted: #999999;
}
```

### 상태 색상

```css
:root {
    /* 성공 */
    --success: #4CAF50;
    --success-light: #C8E6C9;
    --success-dark: #388E3C;

    /* 경고 */
    --warning: #FF9800;
    --warning-light: #FFE0B2;
    --warning-dark: #F57C00;

    /* 위험 */
    --danger: #F44336;
    --danger-light: #FFEBEE;
    --danger-dark: #D32F2F;

    /* 정보 */
    --info: #2196F3;
    --info-light: #E3F2FD;
    --info-dark: #1976D2;
}
```

### 아이템 색상

```css
:root {
    /* 아이템 셀 */
    --item-bg: #8B4513;
    --item-text: #FFFFFF;
    --item-border: #6B3510;

    /* 빈 셀 */
    --empty-cell: #FAFAFA;
    --hover-cell: #E3F2FD;

    /* 드롭 대상 */
    --drop-target: #C8E6C9;
}
```

---

## 아이콘

| 용도 | 아이콘 |
|------|--------|
| 가방 | 📦 |
| 주변 아이템 | 🎒 |
| 여유 공간 | 📎 |
| 휴지통 | 🗑️ |
| 새로고침 | 🔄 |
| 저장 | 💾 |
| 자동삭제 타이머 | 🕐 |
| 경고 | ⚠️ |
| 성공 | ✅ |
| 실패 | ❌ |
| 아이템 사용 | ✨ |
| 양도 | 📤 |
| 수신 | 📥 |

---

## 타이포그래피

```css
/* 기본 폰트 */
body {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    color: var(--text-primary);
}

/* 제목 */
h1 { font-size: 1.5rem; font-weight: 700; }
h2 { font-size: 1.25rem; font-weight: 600; }
h3 { font-size: 1.1rem; font-weight: 600; }
h4 { font-size: 1rem; font-weight: 500; }

/* 본문 */
p { font-size: 0.9rem; }
small { font-size: 0.8rem; color: var(--text-muted); }
```

---

## 컴포넌트

### 버튼

```css
.btn {
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary {
    background: var(--info);
    color: white;
    border: none;
}

.btn-primary:hover {
    background: var(--info-dark);
}

.btn-secondary {
    background: white;
    color: var(--text-primary);
    border: 1px solid var(--border-default);
}

.btn-danger {
    background: var(--danger);
    color: white;
    border: none;
}
```

### 카드

```css
.card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 16px;
}

.card-header {
    font-weight: 600;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-light);
}
```

### 알림

```css
.alert {
    padding: 12px 16px;
    border-radius: 4px;
    margin-bottom: 16px;
}

.alert-success {
    background: var(--success-light);
    color: var(--success-dark);
    border-left: 4px solid var(--success);
}

.alert-warning {
    background: var(--warning-light);
    color: var(--warning-dark);
    border-left: 4px solid var(--warning);
}

.alert-danger {
    background: var(--danger-light);
    color: var(--danger-dark);
    border-left: 4px solid var(--danger);
}
```

---

## 반응형 브레이크포인트

```css
/* 데스크톱 */
@media (min-width: 1200px) {
    .inventory-grid {
        grid-template-columns: repeat(10, 60px);
    }
}

/* 태블릿 */
@media (max-width: 1199px) and (min-width: 768px) {
    .inventory-grid {
        grid-template-columns: repeat(10, 50px);
    }
}

/* 모바일 */
@media (max-width: 767px) {
    .inventory-grid {
        grid-template-columns: repeat(5, 60px);
    }

    .sidebar {
        display: none;
    }

    .mobile-menu {
        display: block;
    }
}
```

---

## 그리드 셀

```css
.grid-cell {
    width: 40px;
    height: 40px;
    background: var(--empty-cell);
    border: 1px solid var(--border-default);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.grid-cell:hover {
    background: var(--hover-cell);
    border-color: var(--info);
}

.grid-cell.occupied {
    background: var(--item-bg);
    color: var(--item-text);
    border-color: var(--item-border);
}

.grid-cell.drop-target {
    background: var(--drop-target);
    border-color: var(--success);
    border-style: dashed;
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
    from { transform: translateY(-10px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

/* 펄스 */
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(33, 150, 243, 0); }
    100% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0); }
}

/* 흔들기 */
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}
```
