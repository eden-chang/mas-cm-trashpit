/**
 * 앱 메인 진입점
 */

const App = {
    /**
     * 앱 초기화
     */
    async init() {
        console.log('Trashpit Inventory App 시작');

        // 모듈 초기화
        UI.init();
        DragDrop.init();

        // 캐릭터 목록 로드
        await this.loadCharacters();
    },

    /**
     * 캐릭터 목록 로드
     */
    async loadCharacters() {
        try {
            const characters = await API.getCharacters();
            UI.renderCharacterList(characters);

            // 첫 번째 캐릭터 자동 선택
            if (characters.length > 0 && !Inventory.currentCharacter) {
                await this.selectCharacter(characters[0].name);
            }
        } catch (error) {
            console.error('캐릭터 목록 로드 실패:', error);
            UI.showToast('캐릭터 목록을 불러오는데 실패했습니다.', 'error');
        }
    },

    /**
     * 캐릭터 선택
     */
    async selectCharacter(name) {
        UI.showLoading();

        try {
            const char = await Inventory.loadCharacter(name);

            // UI 업데이트
            UI.updateCharacterInfo(char);
            UI.updateCapacityBar(char.bag_used, char.bag_capacity);
            UI.renderCurrentTab();

            // 캐릭터 목록에서 활성화
            document.querySelectorAll('#character-list li').forEach(li => {
                li.classList.toggle('active', li.dataset.name === name);
            });
        } catch (error) {
            console.error('캐릭터 로드 실패:', error);
            UI.showToast('캐릭터 정보를 불러오는데 실패했습니다.', 'error');
        }
    },
};

// DOM 로드 후 앱 시작
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
