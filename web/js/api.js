/**
 * API 통신 모듈
 */

const API = {
    BASE_URL: 'http://localhost:5000/api',

    /**
     * API 요청 헬퍼
     */
    async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;

        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || '요청 실패');
        }

        return data;
    },

    /**
     * 전체 캐릭터 목록 조회
     */
    async getCharacters() {
        return this.request('/characters');
    },

    /**
     * 캐릭터 정보 조회
     */
    async getCharacter(name) {
        return this.request(`/character/${encodeURIComponent(name)}`);
    },

    /**
     * 가방 아이템 조회
     */
    async getBag(name) {
        return this.request(`/bag/${encodeURIComponent(name)}`);
    },

    /**
     * 가방 아이템 업데이트
     */
    async updateBag(name, items) {
        return this.request(`/bag/${encodeURIComponent(name)}`, {
            method: 'POST',
            body: JSON.stringify({ items }),
        });
    },

    /**
     * 주변 아이템 조회
     */
    async getNearby(name) {
        return this.request(`/nearby/${encodeURIComponent(name)}`);
    },

    /**
     * 주변 → 가방 이동
     */
    async moveTooBag(name, itemName, quantity = 1) {
        return this.request(`/nearby/${encodeURIComponent(name)}/move`, {
            method: 'POST',
            body: JSON.stringify({ item_name: itemName, quantity }),
        });
    },

    /**
     * 전체 아이템 목록 조회
     */
    async getItems() {
        return this.request('/items');
    },

    /**
     * 아이템 정보 조회
     */
    async getItem(name) {
        return this.request(`/item/${encodeURIComponent(name)}`);
    },
};
