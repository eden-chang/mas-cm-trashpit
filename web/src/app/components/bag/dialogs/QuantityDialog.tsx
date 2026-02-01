import { X } from 'lucide-react';
import type { Item, NearbyItem, QuantityDialogState } from '../types';

interface QuantityDialogProps {
  state: QuantityDialogState;
  onClose: () => void;
  onQuantityChange: (quantity: number) => void;
  onConfirm: () => void;
}

export function QuantityDialog({
  state,
  onClose,
  onQuantityChange,
  onConfirm,
}: QuantityDialogProps) {
  if (!state.isOpen || !state.item) {
    return null;
  }

  const { item, maxQuantity, selectedQuantity } = state;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(11, 14, 20, 0.9)' }}
    >
      <div className="bg-[#1C2128] border-2 border-[#BF5AF2] rounded-xl p-6 max-w-sm w-full shadow-[0_0_40px_rgba(191,90,242,0.5)] relative">
        {/* Glassmorphism effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#BF5AF2]/10 to-transparent rounded-xl pointer-events-none" />

        <div className="relative space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-[#BF5AF2] uppercase tracking-wider">
              수량 선택
            </h3>
            <button
              onClick={onClose}
              className="text-[#8B92A0] hover:text-[#BF5AF2] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Item info */}
          <div className="bg-[#0B0E14]/50 border border-[#BF5AF2]/30 rounded-lg p-4">
            <div className="text-sm text-[#E8EAED] font-medium mb-2">
              {item.name}
            </div>
            <div className="text-xs text-[#8B92A0] font-mono">
              보유 수량: {maxQuantity}개
            </div>
          </div>

          {/* Quantity selector */}
          <div className="space-y-2">
            <label className="text-sm text-[#E8EAED] font-medium">
              이동할 수량
            </label>
            <div className="flex items-center gap-3">
              <button
                onClick={() => onQuantityChange(Math.max(1, selectedQuantity - 1))}
                className="px-4 py-2 bg-[#2A2F3A] border border-[#BF5AF2]/30 rounded-lg text-[#BF5AF2] font-bold hover:bg-[#BF5AF2]/20 hover:border-[#BF5AF2] transition-all"
              >
                -
              </button>
              <input
                type="number"
                min="1"
                max={maxQuantity}
                value={selectedQuantity}
                onChange={(e) => {
                  const value = Math.min(
                    maxQuantity,
                    Math.max(1, parseInt(e.target.value) || 1)
                  );
                  onQuantityChange(value);
                }}
                className="flex-1 px-4 py-2 bg-[#0B0E14] border border-[#BF5AF2]/30 rounded-lg text-center text-[#E8EAED] font-mono font-bold focus:border-[#BF5AF2] focus:outline-none"
              />
              <button
                onClick={() =>
                  onQuantityChange(Math.min(maxQuantity, selectedQuantity + 1))
                }
                className="px-4 py-2 bg-[#2A2F3A] border border-[#BF5AF2]/30 rounded-lg text-[#BF5AF2] font-bold hover:bg-[#BF5AF2]/20 hover:border-[#BF5AF2] transition-all"
              >
                +
              </button>
            </div>
            <button
              onClick={() => onQuantityChange(maxQuantity)}
              className="w-full py-1.5 text-xs text-[#8B92A0] hover:text-[#BF5AF2] transition-colors font-mono"
            >
              전체 선택
            </button>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-2">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2.5 bg-[#2A2F3A] border border-[#8B92A0]/30 rounded-lg text-[#8B92A0] font-bold hover:bg-[#8B92A0]/20 hover:border-[#8B92A0] transition-all"
            >
              취소
            </button>
            <button
              onClick={onConfirm}
              className="flex-1 px-4 py-2.5 bg-[#BF5AF2]/20 border border-[#BF5AF2] rounded-lg text-[#BF5AF2] font-bold hover:bg-[#BF5AF2]/30 hover:shadow-[0_0_20px_rgba(191,90,242,0.6)] transition-all"
            >
              확인
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
