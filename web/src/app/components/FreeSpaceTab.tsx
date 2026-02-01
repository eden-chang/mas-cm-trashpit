import { useState } from 'react';

interface FreeItem {
  id: string;
  name: string;
  count: number;
  icon?: string;
}

export default function FreeSpaceTab() {
  // 예시 부피 0 아이템 데이터
  const [freeItems] = useState<FreeItem[]>([
    { id: '1', name: '클립', count: 5, icon: '📎' },
    { id: '2', name: '메모지', count: 12, icon: '📝' },
    { id: '3', name: '동전', count: 8, icon: '🪙' },
    { id: '4', name: '열쇠고리', count: 3, icon: '🔑' },
    { id: '5', name: '스티커', count: 15, icon: '⭐' },
    { id: '6', name: '명함', count: 7, icon: '💳' },
  ]);

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg text-[#000000]">여유공간</h3>
        <div className="text-sm text-[#999999]">
          부피 0 아이템 전용 (제한 없음)
        </div>
      </div>

      {/* 아이템 칩 영역 */}
      <div className="bg-white border border-[#EEEEEE] p-6 rounded-lg min-h-[200px]">
        {freeItems.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {freeItems.map((item) => (
              <div
                key={item.id}
                className="inline-flex items-center gap-2 px-4 py-2 bg-[#F5F5F5] border border-[#DDDDDD] rounded-full text-sm text-[#333333] hover:bg-[#EEEEEE] transition-colors"
              >
                {item.icon && <span>{item.icon}</span>}
                <span>{item.name}</span>
                <span className="text-[#666666]">x{item.count}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center h-[200px] text-[#999999] text-sm">
            부피 0 아이템이 없습니다
          </div>
        )}
      </div>

      {/* 하단 안내 */}
      <div className="bg-[#FAFAFA] border border-[#EEEEEE] rounded-lg p-4">
        <p className="text-sm text-[#666666] text-center">
          부피가 0인 아이템은 자동으로 여기에 보관됩니다.
        </p>
      </div>
    </div>
  );
}
