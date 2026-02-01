import BagTab from '@/app/components/BagTab';
import { RefreshCw, Cloud, Package, Menu, X, Search, Loader2, AlertTriangle } from 'lucide-react';
import { useState, useEffect, useCallback } from 'react';
import {
  getCharacters,
  getCharacter,
  updateBag,
  ApiError,
} from '@/lib/api';
import {
  transformCharacterData,
  gridItemsToApiItems,
} from '@/lib/transform';
import type {
  CharacterSummary,
  ApiCharacter,
  Item,
  NearbyItem,
  FreeItem,
} from '@/lib/types';

// Character display type for sidebar
interface CharacterDisplay {
  name: string;
  capacity: number;
  maxCapacity: number;
  gridSize: number;
  strength: number;
  hp: number;
  maxHp: number;
}

export default function App() {
  // Character list state
  const [characters, setCharacters] = useState<CharacterDisplay[]>([]);
  const [selectedCharacterIndex, setSelectedCharacterIndex] = useState<number | null>(null);
  const [isLoadingCharacters, setIsLoadingCharacters] = useState(true);
  const [characterError, setCharacterError] = useState<string | null>(null);

  // Selected character data
  const [selectedCharacterData, setSelectedCharacterData] = useState<ApiCharacter | null>(null);
  const [isLoadingCharacterData, setIsLoadingCharacterData] = useState(false);

  // UI state
  const [timeRemaining, setTimeRemaining] = useState(31522);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Current items state (managed by BagTab, tracked here for save)
  const [currentItems, setCurrentItems] = useState<Item[]>([]);

  // Timer effect
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeRemaining((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Load character list on mount
  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    setIsLoadingCharacters(true);
    setCharacterError(null);
    try {
      const data = await getCharacters();
      const displayChars: CharacterDisplay[] = data.map((char: CharacterSummary) => ({
        name: char.name,
        capacity: char.bag_used,
        maxCapacity: char.bag_capacity,
        gridSize: char.bag_capacity,
        strength: Math.ceil(char.bag_capacity / 10), // Estimate from capacity
        hp: char.health ?? 50,
        maxHp: char.max_health ?? 100,
      }));
      setCharacters(displayChars);
      // Auto-select first character
      if (displayChars.length > 0 && selectedCharacterIndex === null) {
        selectCharacter(0, displayChars);
      }
    } catch (error) {
      const message = error instanceof ApiError ? error.message : 'Failed to load characters';
      setCharacterError(message);
      console.error('Failed to load characters:', error);
    } finally {
      setIsLoadingCharacters(false);
    }
  };

  const selectCharacter = async (index: number, charList?: CharacterDisplay[]) => {
    const chars = charList || characters;
    if (index < 0 || index >= chars.length) return;

    setSelectedCharacterIndex(index);
    setIsSidebarOpen(false);
    setIsLoadingCharacterData(true);
    setHasUnsavedChanges(false);

    try {
      const charName = chars[index].name;
      const data = await getCharacter(charName);
      setSelectedCharacterData(data);

      // Update the character in the list with fresh data
      const updatedChars = [...chars];
      updatedChars[index] = {
        ...updatedChars[index],
        capacity: data.bag_used,
        maxCapacity: data.bag_capacity,
        gridSize: data.bag_capacity,
        strength: data.strength,
        hp: data.health,
        maxHp: data.max_health ?? 100,
      };
      setCharacters(updatedChars);
    } catch (error) {
      console.error('Failed to load character data:', error);
    } finally {
      setIsLoadingCharacterData(false);
    }
  };

  const handleRefresh = useCallback(async () => {
    if (selectedCharacterIndex !== null) {
      await selectCharacter(selectedCharacterIndex);
    }
  }, [selectedCharacterIndex]);

  const handleSave = async () => {
    if (!selectedCharacterData || selectedCharacterIndex === null) return;

    setIsSaving(true);
    setSaveError(null);

    try {
      const apiItems = gridItemsToApiItems(currentItems);
      await updateBag(selectedCharacterData.name, apiItems);
      setHasUnsavedChanges(false);
      // Refresh to get updated data
      await selectCharacter(selectedCharacterIndex);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : 'Failed to save';
      setSaveError(message);
      console.error('Failed to save:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleItemsChange = useCallback((items: Item[]) => {
    setCurrentItems(items);
    setHasUnsavedChanges(true);
  }, []);

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const currentCharacter = selectedCharacterIndex !== null ? characters[selectedCharacterIndex] : null;

  // Search filtering
  const filteredCharacters = characters.filter(char =>
    char.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="size-full flex flex-col bg-bg-base">
      {/* Header */}
      <header className="h-14 md:h-16 border-b border-border flex items-center justify-between px-3 md:px-6 bg-bg-raised/50 backdrop-blur-sm shrink-0">
        <h1 className="text-base md:text-xl font-bold bg-gradient-to-r from-cyan to-purple bg-clip-text text-transparent tracking-wide">
          TRPG INVENTORY
        </h1>
        <div className="flex items-center gap-2 md:gap-4">
          <div className="text-xs md:text-sm text-text-secondary font-mono">
            {currentCharacter ? (
              <>{currentCharacter.name} | STR: {currentCharacter.strength}</>
            ) : (
              'No character selected'
            )}
          </div>
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="md:hidden p-2 rounded-lg bg-bg-overlay border border-cyan/30 text-cyan hover:border-cyan hover:shadow-[0_0_15px_rgba(var(--color-primary-rgb),0.3)] transition-all"
          >
            {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Main content area */}
        <main className="flex-1 flex flex-col bg-bg-base overflow-y-auto">
          <div className="p-3 md:p-6">
            {isLoadingCharacterData ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-cyan animate-spin" />
              </div>
            ) : currentCharacter && selectedCharacterData ? (
              <BagTab
                gridSize={currentCharacter.gridSize}
                timeRemaining={timeRemaining}
                formatTime={formatTime}
                characterData={selectedCharacterData}
                onItemsChange={handleItemsChange}
                onRefresh={handleRefresh}
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-text-secondary">
                <Package className="w-12 h-12 mb-4 opacity-50" />
                <p>Select a character to view inventory</p>
              </div>
            )}
          </div>
        </main>

        {/* Overlay for mobile sidebar */}
        {isSidebarOpen && (
          <div
            className="md:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}

        {/* Right sidebar */}
        <aside className={`
          w-full sm:w-96 md:w-80 border-l border-border bg-bg-raised/30 backdrop-blur-md flex flex-col
          fixed md:relative right-0 top-14 md:top-16 bottom-0 z-50
          transform transition-transform duration-300
          ${isSidebarOpen ? 'translate-x-0' : 'translate-x-full md:translate-x-0'}
        `}>
          <div className="p-3 md:p-3 pt-3 md:pt-3 border-b border-border flex items-center justify-between shrink-0">
            <h2 className="text-sm font-semibold text-cyan tracking-wider uppercase">Characters</h2>
            <button
              onClick={() => setIsSidebarOpen(false)}
              className="md:hidden p-1 rounded text-text-secondary hover:text-cyan transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Search */}
          <div className="p-3 border-b border-border shrink-0">
            <div className="relative">
              <Search className="absolute top-2.5 left-3 w-4 h-4 text-text-secondary pointer-events-none" />
              <input
                type="text"
                placeholder="Search characters..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full py-2 pl-10 pr-3 rounded-lg bg-bg-base/50 border border-border text-sm text-text-primary placeholder-text-secondary focus:border-cyan/50 focus:shadow-[0_0_15px_rgba(var(--color-primary-rgb),0.2)] focus:outline-none transition-all"
              />
            </div>
          </div>

          {/* Character list */}
          <div className="flex-1 overflow-y-auto p-2 md:p-3 space-y-2 md:space-y-3">
            {isLoadingCharacters ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 text-cyan animate-spin" />
              </div>
            ) : characterError ? (
              <div className="flex flex-col items-center justify-center py-8 text-danger">
                <AlertTriangle className="w-6 h-6 mb-2" />
                <p className="text-sm">{characterError}</p>
                <button
                  onClick={loadCharacters}
                  className="mt-2 text-xs text-cyan hover:underline"
                >
                  Retry
                </button>
              </div>
            ) : filteredCharacters.length === 0 ? (
              <div className="text-center py-8 text-text-secondary text-sm">
                No characters found
              </div>
            ) : (
              filteredCharacters.map((character, index) => {
                const actualIndex = characters.indexOf(character);
                const isActive = selectedCharacterIndex === actualIndex;
                const hpPercent = (character.hp / character.maxHp) * 100;
                const capacityPercent = (character.capacity / character.gridSize) * 100;

                return (
                  <button
                    key={actualIndex}
                    onClick={() => selectCharacter(actualIndex)}
                    className={`w-full text-left p-2 md:p-3 rounded-lg transition-all relative overflow-hidden group ${
                      isActive
                        ? 'bg-bg-overlay border-2 border-cyan shadow-[0_0_25px_rgba(var(--color-primary-rgb),0.5)]'
                        : 'bg-bg-base/50 border border-border hover:border-purple/50 hover:shadow-[0_0_15px_rgba(var(--color-secondary-rgb),0.2)]'
                    }`}
                  >
                    <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />

                    <div className="relative flex items-center gap-2 md:gap-3">
                      <div className={`w-9 h-9 md:w-10 md:h-10 rounded-full flex items-center justify-center text-sm md:text-base font-bold transition-all shrink-0 ${
                        isActive
                          ? 'bg-gradient-to-br from-cyan to-purple text-black shadow-[0_0_15px_rgba(var(--color-primary-rgb),0.5)]'
                          : 'bg-bg-overlay text-text-secondary group-hover:bg-purple/20'
                      }`}>
                        {character.name[0]}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1.5">
                          <div className="text-xs md:text-sm font-semibold text-text-primary">{character.name}</div>
                          <div className="flex items-center gap-1 text-[9px] md:text-[10px] text-text-secondary">
                            <span className="font-mono font-bold">STR</span>
                            <span className="font-mono text-purple font-bold">{character.strength}</span>
                          </div>
                        </div>

                        <div className="flex gap-2 md:gap-3">
                          {/* HP bar */}
                          <div className="flex-1">
                            <div className="flex items-center justify-between text-[9px] md:text-[10px] text-text-secondary mb-0.5 font-mono">
                              <span className="font-bold">HP</span>
                              <span className="font-bold text-danger">{character.hp}/{character.maxHp}</span>
                            </div>
                            <div className="h-1.5 md:h-2 bg-bg-base/80 rounded-full overflow-hidden border border-border">
                              <div
                                className="h-full bg-danger rounded-full transition-all duration-300 shadow-[0_0_8px_rgba(var(--color-danger-rgb),0.6)]"
                                style={{ width: `${hpPercent}%` }}
                              />
                            </div>
                          </div>

                          {/* Bag capacity bar */}
                          <div className="flex-1">
                            <div className="flex items-center justify-between text-[9px] md:text-[10px] text-text-secondary mb-0.5 font-mono">
                              <span className="font-bold flex items-center gap-0.5">
                                <Package className="w-2 h-2 md:w-2.5 md:h-2.5" />
                                BAG
                              </span>
                              <span className={`font-bold ${
                                capacityPercent > 80
                                  ? 'text-danger'
                                  : capacityPercent > 60
                                  ? 'text-warning'
                                  : 'text-success'
                              }`}>{character.capacity}/{character.gridSize}</span>
                            </div>
                            <div className="h-1.5 md:h-2 bg-bg-base/80 rounded-full overflow-hidden border border-border">
                              <div
                                className={`h-full rounded-full transition-all duration-300 ${
                                  capacityPercent > 80
                                    ? 'bg-danger shadow-[0_0_8px_rgba(var(--color-danger-rgb),0.6)]'
                                    : capacityPercent > 60
                                    ? 'bg-warning shadow-[0_0_8px_rgba(var(--color-warning-rgb),0.6)]'
                                    : 'bg-gradient-to-r from-success to-cyan shadow-[0_0_8px_rgba(var(--color-success-rgb),0.6)]'
                                }`}
                                style={{ width: `${capacityPercent}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </button>
                );
              })
            )}
          </div>

          {/* Action buttons */}
          <div className="p-3 md:p-4 border-t border-border space-y-2 shrink-0">
            {/* Save error */}
            {saveError && (
              <div className="flex items-center gap-2 px-2 md:px-3 py-1.5 md:py-2 bg-danger/10 border border-danger/30 rounded-lg">
                <AlertTriangle className="w-3 h-3 text-danger" />
                <span className="text-[10px] md:text-xs text-danger">{saveError}</span>
              </div>
            )}

            {/* Sync to Cloud button */}
            <button
              className="w-full flex items-center justify-center gap-2 px-3 md:px-4 py-2 md:py-2.5 text-sm md:text-base rounded-lg bg-success/20 border border-success/50 text-success hover:border-success hover:shadow-[0_0_20px_rgba(var(--color-success-rgb),0.4)] transition-all font-bold relative overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={handleSave}
              disabled={isSaving || !hasUnsavedChanges}
            >
              <div className="absolute inset-0 bg-success/10 opacity-0 group-hover:opacity-100 transition-opacity" />
              {isSaving ? (
                <Loader2 className="w-4 h-4 relative z-10 animate-spin" />
              ) : (
                <Cloud className="w-4 h-4 relative z-10" />
              )}
              <span className="relative z-10">{isSaving ? 'SAVING...' : 'SYNC TO CLOUD'}</span>
              {hasUnsavedChanges && !isSaving && (
                <span className="absolute -top-1 -right-1 w-2.5 h-2.5 md:w-3 md:h-3 bg-warning rounded-full animate-pulse shadow-[0_0_10px_rgba(var(--color-warning-rgb),0.8)]" />
              )}
            </button>

            {/* Unsaved Changes indicator */}
            {hasUnsavedChanges && (
              <div className="flex items-center gap-2 px-2 md:px-3 py-1.5 md:py-2 bg-warning/10 border border-warning/30 rounded-lg">
                <div className="w-1.5 h-1.5 md:w-2 md:h-2 bg-warning rounded-full animate-pulse" />
                <span className="text-[10px] md:text-xs text-warning font-mono">Unsaved Changes</span>
              </div>
            )}

            {/* Refresh Data button */}
            <button
              className="w-full flex items-center justify-center gap-2 px-3 md:px-4 py-2 md:py-2.5 text-sm md:text-base rounded-lg bg-gradient-to-r from-cyan/10 to-purple/10 border border-cyan/30 text-cyan hover:border-cyan hover:shadow-[0_0_15px_rgba(var(--color-primary-rgb),0.3)] transition-all font-medium disabled:opacity-50"
              onClick={handleRefresh}
              disabled={isLoadingCharacterData}
            >
              <RefreshCw className={`w-3.5 h-3.5 md:w-4 md:h-4 ${isLoadingCharacterData ? 'animate-spin' : ''}`} />
              Refresh Data
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}
