/**
 * UI 렌더링 및 이벤트 처리
 */

const BAG_COLUMNS = 10;
const BAG_CELL_SIZE_PX = 40;

/**
 * 용량에 따른 그리드 행 수 (Phase 0: 20/40/60)
 */
function getBagRows(capacity) {
    if (capacity <= 20) return 2;
    if (capacity <= 40) return 4;
    return 6;
}

/**
 * 아이템 목록을 그리드 셀 단위로 패킹 (row-major).
 * @returns {Array<Array<{name: string, volume: number, quantity: number, isFirst: boolean} | null>>}
 */
function packItemsIntoGrid(bagItems, cols, rows) {
    const grid = Array.from({ length: rows }, () => Array(cols).fill(null));
    let row = 0;
    let col = 0;

    for (const item of bagItems) {
        const cellsNeeded = (item.volume || 0) * (item.quantity || 1);
        if (cellsNeeded <= 0) continue;

        let placed = 0;
        let isFirst = true;

        while (placed < cellsNeeded && row < rows) {
            if (col >= cols) {
                col = 0;
                row++;
                continue;
            }
            grid[row][col] = {
                name: item.name,
                volume: item.volume,
                quantity: item.quantity,
                isFirst,
            };
            placed++;
            isFirst = false;
            col++;
        }
    }

    return grid;
}

const UI = {
    currentTab: 'bag',

    /**
     * UI 초기화
     */
    init() {
        this.bindEvents();
        this.createToastContainer();
    },

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 탭 전환
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchTab(tab.dataset.tab);
            });
        });

        // 새로고침
        document.getElementById('refresh-btn')?.addEventListener('click', () => {
            this.refresh();
        });

        // 자동 정리
        document.getElementById('auto-arrange-btn')?.addEventListener('click', () => {
            Inventory.autoArrange();
            this.renderBag();
            this.showToast('자동 정리 완료', 'success');
        });

        // 저장
        document.getElementById('save-btn')?.addEventListener('click', async () => {
            try {
                await Inventory.save();
                this.showToast('저장되었습니다.', 'success');
            } catch (error) {
                this.showToast(error.message, 'error');
            }
        });

        // 취소
        document.getElementById('cancel-btn')?.addEventListener('click', () => {
            Inventory.cancel();
            this.renderCurrentTab();
            this.showToast('변경 사항이 취소되었습니다.', 'warning');
        });
    },

    /**
     * 캐릭터 목록 렌더링
     */
    renderCharacterList(characters, selectedName = null) {
        const list = document.getElementById('character-list');
        if (!list) return;

        list.innerHTML = characters.map(char => `
            <li class="${char.name === selectedName ? 'active' : ''}" data-name="${char.name}">
                <div class="char-name">${char.name}</div>
                <div class="char-info">
                    가방: ${char.bag_used}/${char.bag_capacity}
                    ${char.nearby_count > 0 ? `| 주변: ${char.nearby_count}개` : ''}
                </div>
            </li>
        `).join('');

        // 클릭 이벤트
        list.querySelectorAll('li').forEach(li => {
            li.addEventListener('click', async () => {
                await App.selectCharacter(li.dataset.name);
            });
        });
    },

    /**
     * 캐릭터 정보 업데이트
     */
    updateCharacterInfo(char) {
        document.getElementById('character-name').textContent = char.name;
        document.getElementById('character-strength').textContent = `(근력: ${char.strength})`;
    },

    /**
     * 용량 바 업데이트
     */
    updateCapacityBar(used, capacity) {
        const bar = document.getElementById('capacity-bar');
        if (!bar) return;

        const fill = bar.querySelector('.capacity-fill');
        const text = bar.querySelector('.capacity-text');

        const percent = (used / capacity) * 100;
        fill.style.width = `${Math.min(percent, 100)}%`;

        // 색상 변경
        fill.classList.remove('warning', 'danger');
        if (percent >= 90) {
            fill.classList.add('danger');
        } else if (percent >= 70) {
            fill.classList.add('warning');
        }

        text.textContent = `${used} / ${capacity}`;
    },

    /**
     * 탭 전환
     */
    switchTab(tabName) {
        this.currentTab = tabName;

        // 탭 버튼 활성화
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        this.renderCurrentTab();
    },

    /**
     * 현재 탭 렌더링
     */
    renderCurrentTab() {
        switch (this.currentTab) {
            case 'bag':
                this.renderBag();
                break;
            case 'misc':
                this.renderMisc();
                break;
            case 'nearby':
                this.renderNearby();
                break;
        }
    },

    /**
     * 가방 탭 렌더링 (테트리스 스타일: 아이템 부피만큼 셀 점유)
     */
    renderBag() {
        const content = document.getElementById('tab-content');
        const char = Inventory.currentCharacter;

        if (!char) {
            content.innerHTML = '<div class="empty-state"><div class="empty-state-text">캐릭터를 선택하세요</div></div>';
            return;
        }

        this.updateCapacityBar(char.bag_used, char.bag_capacity);

        const rows = getBagRows(char.bag_capacity);
        const packed = packItemsIntoGrid(char.bag_items, BAG_COLUMNS, rows);

        content.innerHTML = `
            <div class="bag-tab-content">
                <div class="bag-header">
                    <h3 class="bag-title">가방</h3>
                    <span class="bag-capacity-text">${char.bag_used} / ${char.bag_capacity}</span>
                </div>
                <div class="inventory-grid inventory-grid-cells" data-drop-zone="bag"
                     style="grid-template-columns: repeat(${BAG_COLUMNS}, ${BAG_CELL_SIZE_PX}px); grid-template-rows: repeat(${rows}, ${BAG_CELL_SIZE_PX}px);">
                </div>
                <div class="bag-item-list">
                    <h4 class="bag-item-list-title">보유 아이템</h4>
                    <ul class="bag-items">
                        ${char.bag_items.map(item => `
                            <li class="bag-item-entry">
                                <span>${item.name} x${item.quantity}</span>
                                <span class="item-volume">부피: ${(item.volume || 0) * (item.quantity || 1)}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;

        this._injectGridCells(content, packed, rows);
    },

    /**
     * 패킹 결과로 그리드 셀 DOM 생성 후 주입 (innerHTML로 data- 속성 이스케이프 대응)
     */
    _injectGridCells(container, packed, rows) {
        const grid = container.querySelector('.inventory-grid-cells');
        if (!grid) return;

        grid.innerHTML = '';

        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < BAG_COLUMNS; col++) {
                const cell = packed[row][col];
                const div = document.createElement('div');
                div.className = 'grid-cell';
                div.dataset.row = String(row);
                div.dataset.col = String(col);

                if (cell) {
                    div.classList.add('occupied');
                    div.setAttribute('data-draggable', '');
                    div.dataset.source = 'bag';
                    div.dataset.itemName = cell.name;
                    div.dataset.quantity = String(cell.quantity);
                    div.dataset.volume = String(cell.volume);
                    div.title = `${cell.name} (부피 ${cell.volume}×${cell.quantity})`;
                    div.draggable = true;
                    div.textContent = cell.isFirst ? cell.name.charAt(0) : '';
                } else {
                    div.dataset.dropZone = 'bag';
                }

                grid.appendChild(div);
            }
        }
    },

    /**
     * 여유공간 탭 렌더링
     */
    renderMisc() {
        const content = document.getElementById('tab-content');
        const char = Inventory.currentCharacter;

        // 용량 바 숨기기
        document.getElementById('capacity-bar').style.display = 'none';

        if (!char || char.misc_items.length === 0) {
            content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📦</div>
                    <div class="empty-state-text">여유공간이 비어있습니다</div>
                </div>
            `;
            return;
        }

        content.innerHTML = `
            <div class="misc-list">
                ${char.misc_items.map(item => `
                    <div class="misc-item">
                        <span class="name">${item.name}</span>
                        <span class="quantity">x${item.quantity}</span>
                    </div>
                `).join('')}
            </div>
        `;
    },

    /**
     * 주변 탭 렌더링
     */
    renderNearby() {
        const content = document.getElementById('tab-content');
        const char = Inventory.currentCharacter;

        // 용량 바 표시
        if (char) {
            document.getElementById('capacity-bar').style.display = 'block';
            this.updateCapacityBar(char.bag_used, char.bag_capacity);
        }

        if (!char || char.nearby_items.length === 0) {
            content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">👀</div>
                    <div class="empty-state-text">주변에 아이템이 없습니다</div>
                </div>
            `;
            return;
        }

        content.innerHTML = `
            <div class="nearby-area">
                <h3>주변 아이템 (드래그하여 가방에 넣기)</h3>
                <div class="nearby-items">
                    ${char.nearby_items.map(item => `
                        <div class="nearby-item"
                             data-draggable
                             data-source="nearby"
                             data-item-name="${item.name}"
                             data-quantity="${item.quantity}"
                             data-volume="${item.volume}"
                             draggable="true">
                            <span class="name">${item.name}</span>
                            <span class="info">(부피: ${item.volume}, 수량: ${item.quantity})</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="inventory-grid" data-drop-zone="bag">
                ${char.bag_items.length > 0 ? char.bag_items.map(item => `
                    <div class="grid-slot occupied">
                        <div class="item">
                            <div class="item-name">${item.name}</div>
                        </div>
                        ${item.volume > 0 ? `<span class="item-volume">${item.volume}</span>` : ''}
                        ${item.quantity > 1 ? `<span class="item-quantity">${item.quantity}</span>` : ''}
                    </div>
                `).join('') : `
                    <div class="grid-slot" data-drop-zone="bag"></div>
                    <div class="grid-slot" data-drop-zone="bag"></div>
                    <div class="grid-slot" data-drop-zone="bag"></div>
                    <div class="grid-slot" data-drop-zone="bag"></div>
                `}
            </div>
        `;
    },

    /**
     * 새로고침
     */
    async refresh() {
        if (Inventory.currentCharacter) {
            await App.selectCharacter(Inventory.currentCharacter.name);
        }
        await App.loadCharacters();
        this.showToast('새로고침 완료', 'success');
    },

    /**
     * 토스트 컨테이너 생성
     */
    createToastContainer() {
        if (!document.querySelector('.toast-container')) {
            const container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
    },

    /**
     * 토스트 메시지 표시
     */
    showToast(message, type = 'info') {
        const container = document.querySelector('.toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    },

    /**
     * 로딩 표시
     */
    showLoading() {
        const content = document.getElementById('tab-content');
        content.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    },
};
