/**
 * 드래그 앤 드롭 처리
 */

const DragDrop = {
    draggedItem: null,
    draggedSource: null,  // 'bag', 'nearby', 'misc'

    /**
     * 드래그 앤 드롭 초기화
     */
    init() {
        // 이벤트 위임으로 처리
        document.addEventListener('dragstart', this.handleDragStart.bind(this));
        document.addEventListener('dragend', this.handleDragEnd.bind(this));
        document.addEventListener('dragover', this.handleDragOver.bind(this));
        document.addEventListener('dragleave', this.handleDragLeave.bind(this));
        document.addEventListener('drop', this.handleDrop.bind(this));
    },

    /**
     * 드래그 시작
     */
    handleDragStart(e) {
        const item = e.target.closest('[data-draggable]');
        if (!item) return;

        this.draggedItem = {
            name: item.dataset.itemName,
            quantity: parseInt(item.dataset.quantity) || 1,
            volume: parseInt(item.dataset.volume) || 0,
        };
        this.draggedSource = item.dataset.source;

        item.classList.add('dragging');

        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', JSON.stringify(this.draggedItem));
    },

    /**
     * 드래그 종료
     */
    handleDragEnd(e) {
        const item = e.target.closest('[data-draggable]');
        if (item) {
            item.classList.remove('dragging');
        }

        // 모든 drag-over 클래스 제거
        document.querySelectorAll('.drag-over').forEach(el => {
            el.classList.remove('drag-over');
        });

        this.draggedItem = null;
        this.draggedSource = null;
    },

    /**
     * 드래그 오버
     */
    handleDragOver(e) {
        const dropZone = e.target.closest('[data-drop-zone]');
        if (!dropZone) return;

        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';

        dropZone.classList.add('drag-over');
    },

    /**
     * 드래그 리브
     */
    handleDragLeave(e) {
        const dropZone = e.target.closest('[data-drop-zone]');
        if (!dropZone) return;

        dropZone.classList.remove('drag-over');
    },

    /**
     * 드롭
     */
    handleDrop(e) {
        const dropZone = e.target.closest('[data-drop-zone]');
        if (!dropZone || !this.draggedItem) return;

        e.preventDefault();
        dropZone.classList.remove('drag-over');

        const targetZone = dropZone.dataset.dropZone;

        // 같은 영역으로의 드롭은 무시
        if (this.draggedSource === targetZone) return;

        // 주변 → 가방 이동
        if (this.draggedSource === 'nearby' && targetZone === 'bag') {
            const result = Inventory.moveNearbyToBag(this.draggedItem.name, 1);

            if (result.success) {
                UI.showToast('가방에 넣었습니다.', 'success');
                UI.renderCurrentTab();
            } else {
                UI.showToast(result.error, 'error');
            }
        }

        // TODO: 가방 내 정렬 등 추가 로직
    },
};
