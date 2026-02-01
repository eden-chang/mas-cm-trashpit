import { useState } from 'react';

interface NearbyItem {
  id: string;
  name: string;
  volume: number;
  icon?: string;
}

export default function NearbyTab() {
  // 예시 주변 아이템 데이터
  const [nearbyItems, setNearbyItems] = useState<NearbyItem[]>([
    { id: '1', name: '낡은 검', volume: 5, icon: '⚔️' },
    { id: '2', name: '체력 물약', volume: 2, icon: '🧪' },
    { id: '3', name: '철 광석', volume: 8, icon: '⛏️' },
    { id: '4', name: '가죽 갑옷', volume: 6, icon: '🛡️' },
    { id: '5', name: '마법 두루마리', volume: 1, icon: '📜' },
    { id: '6', name: '금화 주머니', volume: 3, icon: '💰' },
  ]);

  // 가방 용량 (예시)
  const bagMaxCapacity = 20;
  const bagUsedCapacity = 15;
  const bagRemainingCapacity = bagMaxCapacity - bagUsedCapacity;

  // 총 부피 계산
  const totalVolume = nearbyItems.reduce((sum, item) => sum + item.volume, 0);

  const handleAddToBag = (itemId: string) => {
    const item = nearbyItems.find((i) => i.id === itemId);
    if (item && item.volume <= bagRemainingCapacity) {
      // 실제로는 가방에 추가하는 로직
      setNearbyItems((prev) => prev.filter((i) => i.id !== itemId));
    }
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg text-[#000000]">주변 아이템</h3>
        <div className="text-sm text-[#333333] flex items-center gap-1">
          <span>⚠️</span>
          <span>자동 삭제 주의!</span>
        </div>
      </div>

      {/* 경고 박스 */}
      <div className="bg-[#F5F5F5] border-l-4 border-[#666666] p-4 rounded">
        <p className="text-sm text-[#333333]">
          주변 아이템은 정기적으로 자동 삭제됩니다. 가방에 넣거나 사용하세요!
        </p>
      </div>

      {/* 아이템 카드 리스트 */}
      <div className="space-y-3">
        {nearbyItems.length > 0 ? (
          nearbyItems.map((item) => {
            const canAddToBag = item.volume <= bagRemainingCapacity;
            
            return (
              <div
                key={item.id}
                className="bg-white border border-[#EEEEEE] rounded-lg p-4 hover:border-[#CCCCCC] transition-colors"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 flex-1">
                    {item.icon && (
                      <span className="text-2xl">{item.icon}</span>
                    )}
                    <div>
                      <div className="text-[#000000] font-medium">
                        {item.name}
                      </div>
                      <div className="text-sm text-[#666666]">
                        부피: {item.volume}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleAddToBag(item.id)}
                    disabled={!canAddToBag}
                    className={`px-4 py-2 rounded text-sm transition-colors ${
                      canAddToBag
                        ? 'bg-[#000000] text-white hover:bg-[#333333]'
                        : 'bg-[#F5F5F5] text-[#999999] border border-[#EEEEEE] cursor-not-allowed'
                    }`}
                  >
                    {canAddToBag ? '가방에 넣기' : '공간 부족'}
                  </button>
                </div>
              </div>
            );
          })
        ) : (
          <div className="bg-[#FAFAFA] border border-[#EEEEEE] rounded-lg p-8 text-center">
            <p className="text-[#999999]">주변에 아이템이 없습니다</p>
          </div>
        )}
      </div>

      {/* 하단 요약 */}
      <div className="pt-4 border-t border-[#EEEEEE] space-y-1">
        <div className="flex justify-between text-sm">
          <span className="text-[#666666]">총 부피:</span>
          <span className="text-[#333333] font-medium">{totalVolume}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-[#666666]">가방 남은 공간:</span>
          <span className={`font-medium ${
            bagRemainingCapacity > 0 ? 'text-[#333333]' : 'text-[#999999]'
          }`}>
            {bagRemainingCapacity}
          </span>
        </div>
      </div>
    </div>
  );
}
