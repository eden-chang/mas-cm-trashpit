/**
 * UI 렌더링 및 이벤트 처리
 */

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
     * 가방 탭 렌더링
     */
    renderBag() {
        const content = document.getElementById('tab-content');
        const char = Inventory.currentCharacter;

        if (!char) {
            content.innerHTML = '<div class="empty-state"><div class="empty-state-text">캐릭터를 선택하세요</div></div>';
            return;
        }

        this.updateCapacityBar(char.bag_used, char.bag_capacity);

        if (char.bag_items.length === 0) {
            content.innerHTML = `
                <div class="inventory-grid" data-drop-zone="bag">
                    <div class="empty-state">
                        <div class="empty-state-icon">🎒</div>
                        <div class="empty-state-text">가방이 비어있습니다</div>
                    </div>
                </div>
            `;
            return;
        }

        content.innerHTML = `
            <div class="inventory-grid" data-drop-zone="bag">
                ${char.bag_items.map(item => `
                    <div class="grid-slot occupied"
                         data-draggable
                         data-source="bag"
                         data-item-name="${item.name}"
                         data-quantity="${item.quantity}"
                         data-volume="${item.volume}"
                         draggable="true">
                        <div class="item">
                            <div class="item-name">${item.name}</div>
                        </div>
                        ${item.volume > 0 ? `<span class="item-volume">${item.volume}</span>` : ''}
                        ${item.quantity > 1 ? `<span class="item-quantity">${item.quantity}</span>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
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
