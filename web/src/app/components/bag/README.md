# Bag Components

Extracted components from `BagTab.tsx` for better code organization and reusability.

## Structure

```
bag/
├── types.ts              # Shared TypeScript interfaces
├── index.ts              # Barrel exports
├── grid/
│   └── constants.ts      # SHAPES, GRID_COLS, helper functions
├── zones/
│   ├── TrashZone.tsx     # Drop zone for deleting items
│   ├── NearbyZone.tsx    # Drop zone for nearby items
│   └── MiscSpaceZone.tsx # Drop zone for misc (volume 0) items
├── items/
│   ├── FreeItemChip.tsx  # Chip component for misc items
│   └── NearbyItemChip.tsx # Chip component for nearby items
├── dialogs/
│   └── QuantityDialog.tsx # Quantity selection modal
└── hooks/                # (Future: state management hooks)
```

## Usage

```tsx
import {
  // Types
  Item,
  NearbyItem,
  QuantityDialogState,

  // Constants
  SHAPES,
  GRID_COLS,
  getShape,
  getItemColors,

  // Components
  TrashZone,
  NearbyZone,
  MiscSpaceZone,
  FreeItemChip,
  NearbyItemChip,
  QuantityDialog,
} from '@/app/components/bag';
```

## Migration Guide

The original `BagTab.tsx` still contains its own component definitions for backward compatibility. To migrate:

1. Import components from `@/app/components/bag`
2. Replace inline component definitions with imported ones
3. Remove duplicate code from `BagTab.tsx`

## Components

### TrashZone
Drop zone that accepts items for deletion.

```tsx
<TrashZone onDrop={(item) => handleDelete(item)} />
```

### NearbyZone
Container for nearby items with drop functionality.

```tsx
<NearbyZone onDrop={(item) => handleMoveToNearby(item)}>
  {nearbyItems.map(item => <NearbyItemChip key={item.id} item={item} />)}
</NearbyZone>
```

### MiscSpaceZone
Container for volume 0 items (misc space).

```tsx
<MiscSpaceZone onDrop={(item) => handleMoveToMisc(item)}>
  {freeItems.map(item => <FreeItemChip key={item.id} item={item} />)}
</MiscSpaceZone>
```

### QuantityDialog
Modal for selecting quantity when moving items.

```tsx
<QuantityDialog
  state={dialogState}
  onClose={() => setDialogState({ isOpen: false, ... })}
  onQuantityChange={(qty) => setDialogState(prev => ({ ...prev, selectedQuantity: qty }))}
  onConfirm={handleQuantityConfirm}
/>
```
