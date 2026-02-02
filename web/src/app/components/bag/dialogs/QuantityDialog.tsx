import { useEffect, useRef } from 'react';
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
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!state.isOpen) return;
    const id = setTimeout(() => {
      dialogRef.current?.querySelector<HTMLElement>('button:not([disabled]), input')?.focus();
    }, 0);
    return () => clearTimeout(id);
  }, [state.isOpen]);

  if (!state.isOpen || !state.item) {
    return null;
  }

  const { item, maxQuantity, selectedQuantity } = state;

  return (
    <div
      ref={dialogRef}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[var(--color-bg-dark)]/90"
      role="dialog"
      aria-modal="true"
      aria-labelledby="quantity-dialog-title"
      onKeyDown={(e) => {
        if (e.key === 'Escape') {
          e.preventDefault();
          onClose();
        }
      }}
    >
      <div className="bg-[var(--color-bg-mid)] border border-[var(--color-item-placed)]/50 rounded-xl p-6 max-w-sm w-full relative">
        <div className="relative space-y-4">
          <div className="flex items-center justify-between">
            <h3 id="quantity-dialog-title" className="text-lg font-bold text-[var(--color-item-placed)] uppercase tracking-wider">
              수량 선택
            </h3>
            <button
              onClick={onClose}
              className="p-1 rounded text-[var(--color-text-secondary)] hover:text-[var(--color-item-placed)] transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-item-placed)]"
              aria-label="닫기"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="bg-[var(--color-bg-dark)]/50 border border-[var(--color-item-placed)]/30 rounded-lg p-4">
            <div className="text-sm text-[var(--color-text-primary)] font-medium mb-2">
              {item.name}
            </div>
            <div className="text-xs text-[var(--color-text-secondary)]">
              보유 수량: {maxQuantity}개
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm text-[var(--color-text-primary)] font-medium">
              이동할 수량
            </label>
            <div className="flex items-center gap-3">
              <button
                onClick={() => onQuantityChange(Math.max(1, selectedQuantity - 1))}
                className="px-4 py-2 bg-[var(--color-bg-light)] border border-[var(--color-item-placed)]/30 rounded-lg text-[var(--color-item-placed)] font-bold hover:bg-[var(--color-item-placed)]/20 hover:border-[var(--color-item-placed)] transition-all"
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
                className="flex-1 px-4 py-2 bg-[var(--color-bg-dark)] border border-[var(--color-item-placed)]/30 rounded-lg text-center text-[var(--color-text-primary)] font-bold focus:border-[var(--color-item-placed)] focus:outline-none"
              />
              <button
                onClick={() =>
                  onQuantityChange(Math.min(maxQuantity, selectedQuantity + 1))
                }
                className="px-4 py-2 bg-[var(--color-bg-light)] border border-[var(--color-item-placed)]/30 rounded-lg text-[var(--color-item-placed)] font-bold hover:bg-[var(--color-item-placed)]/20 hover:border-[var(--color-item-placed)] transition-all"
              >
                +
              </button>
            </div>
            <button
              onClick={() => onQuantityChange(maxQuantity)}
              className="w-full py-1.5 text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-item-placed)] transition-colors"
            >
              전체 선택
            </button>
          </div>
          <div className="flex gap-3 pt-2">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2.5 bg-[var(--color-bg-light)] border border-[var(--color-text-secondary)]/30 rounded-lg text-[var(--color-text-secondary)] font-bold hover:bg-[var(--color-text-secondary)]/20 hover:border-[var(--color-text-secondary)] transition-all"
            >
              취소
            </button>
            <button
              onClick={onConfirm}
              className="flex-1 px-4 py-2.5 bg-[var(--color-item-placed)]/20 border border-[var(--color-item-placed)] rounded-lg text-[var(--color-item-placed)] font-bold hover:bg-[var(--color-item-placed)]/30 transition-all"
            >
              확인
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
