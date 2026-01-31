/**
 * 인벤토리 상태 관리
 */

const Inventory = {
    // 현재 상태
    currentCharacter: null,
    originalData: null,  // 원본 데이터 (취소용)
    hasChanges: false,

    /**
     * 캐릭터 데이터 로드
     */
    async loadCharacter(name) {
        try {
            const data = await API.getCharacter(name);
            this.currentCharacter = data;
            this.originalData = JSON.parse(JSON.stringify(data));
            this.hasChanges = false;
            return data;
        } catch (error) {
            console.error('캐릭터 로드 실패:', error);
            throw error;
        }
    },

    /**
     * 가방에 아이템 추가
     */
    addToBag(item) {
        if (!this.currentCharacter) return false;

        const existing = this.currentCharacter.bag_items.find(i => i.name === item.name);

        if (existing) {
            existing.quantity += item.quantity;
            existing.total_volume = existing.volume * existing.quantity;
        } else {
            this.currentCharacter.bag_items.push({ ...item });
        }

        this.recalculateBagUsed();
        this.hasChanges = true;
        return true;
    },

    /**
     * 가방에서 아이템 제거
     */
    removeFromBag(itemName, quantity = 1) {
        if (!this.currentCharacter) return false;

        const index = this.currentCharacter.bag_items.findIndex(i => i.name === itemName);
        if (index === -1) return false;

        const item = this.currentCharacter.bag_items[index];

        if (item.quantity <= quantity) {
            this.currentCharacter.bag_items.splice(index, 1);
        } else {
            item.quantity -= quantity;
            item.total_volume = item.volume * item.quantity;
        }

        this.recalculateBagUsed();
        this.hasChanges = true;
        return true;
    },

    /**
     * 주변에서 가방으로 이동
     */
    moveNearbyToBag(itemName, quantity = 1) {
        if (!this.currentCharacter) return { success: false, error: '캐릭터 없음' };

        const nearbyItem = this.currentCharacter.nearby_items.find(i => i.name === itemName);
        if (!nearbyItem) {
            return { success: false, error: '주변에 해당 아이템이 없습니다.' };
        }

        const requiredSpace = nearbyItem.volume * quantity;
        if (requiredSpace > this.currentCharacter.bag_available) {
            return {
                success: false,
                error: `가방 공간 부족 (필요: ${requiredSpace}, 남음: ${this.currentCharacter.bag_available})`,
            };
        }

        // 주변에서 제거
        if (nearbyItem.quantity <= quantity) {
            const index = this.currentCharacter.nearby_items.indexOf(nearbyItem);
            this.currentCharacter.nearby_items.splice(index, 1);
        } else {
            nearbyItem.quantity -= quantity;
            nearbyItem.total_volume = nearbyItem.volume * nearbyItem.quantity;
        }

        // 가방에 추가
        this.addToBag({
            name: itemName,
            quantity: quantity,
            volume: nearbyItem.volume,
            total_volume: nearbyItem.volume * quantity,
        });

        return { success: true };
    },

    /**
     * 가방 사용량 재계산
     */
    recalculateBagUsed() {
        if (!this.currentCharacter) return;

        this.currentCharacter.bag_used = this.currentCharacter.bag_items.reduce(
            (sum, item) => sum + (item.total_volume || item.volume * item.quantity),
            0
        );
        this.currentCharacter.bag_available =
            this.currentCharacter.bag_capacity - this.currentCharacter.bag_used;
    },

    /**
     * 변경 사항 저장
     */
    async save() {
        if (!this.currentCharacter || !this.hasChanges) return;

        const items = this.currentCharacter.bag_items.map(item => ({
            name: item.name,
            quantity: item.quantity,
        }));

        const result = await API.updateBag(this.currentCharacter.name, items);

        if (result.success) {
            this.originalData = JSON.parse(JSON.stringify(this.currentCharacter));
            this.hasChanges = false;
        }

        return result;
    },

    /**
     * 변경 사항 취소
     */
    cancel() {
        if (this.originalData) {
            this.currentCharacter = JSON.parse(JSON.stringify(this.originalData));
            this.hasChanges = false;
        }
    },

    /**
     * 자동 정리 (부피 순 정렬)
     */
    autoArrange() {
        if (!this.currentCharacter) return;

        this.currentCharacter.bag_items.sort((a, b) => b.volume - a.volume);
        this.hasChanges = true;
    },
};
