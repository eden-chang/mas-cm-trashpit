import BagTab from '@/app/components/BagTab';
import { RefreshCw, Cloud, Menu, X, Search, Loader2, AlertTriangle, Package } from 'lucide-react';
import { useState, useEffect, useCallback, useRef } from 'react';
import {
  getCharacters,
  getCharacter,
  updateBag,
  ApiError,
} from '@/lib/api';
import {
  transformCharacterData,
  gridItemsToApiItems,
  gridItemsToApiLayout,
  nearbyItemsToApiItems,
  freeItemsToApiItems,
} from '@/lib/transform';
import type {
  CharacterSummary,
  ApiCharacter,
  Item,
  NearbyItem,
  FreeItem,
} from '@/lib/types';

// 동기화 폴링 간격 (30초)
const POLL_INTERVAL = 30000;

/**
 * KST 기준 다음 자정(0시)까지 남은 초 계산
 * 주변 아이템은 KST 0시에 리셋됨
 */
function getSecondsUntilMidnightKST(): number {
  const now = new Date();
  
  // KST는 UTC+9
  const KST_OFFSET = 9 * 60; // 분 단위
  
  // 현재 시간을 KST로 변환 (UTC 시간 + 9시간)
  const nowKST = new Date(now.getTime() + (KST_OFFSET + now.getTimezoneOffset()) * 60 * 1000);
  
  // KST 기준 다음 자정 계산
  const midnightKST = new Date(nowKST);
  midnightKST.setHours(24, 0, 0, 0); // 다음 날 0시
  
  // 남은 밀리초를 초로 변환
  const diffMs = midnightKST.getTime() - nowKST.getTime();
  return Math.max(0, Math.floor(diffMs / 1000));
}

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
  const [timeRemaining, setTimeRemaining] = useState(getSecondsUntilMidnightKST);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Current inventory state (managed by BagTab, tracked here for save)
  const [currentItems, setCurrentItems] = useState<Item[]>([]);
  const [currentNearbyItems, setCurrentNearbyItems] = useState<NearbyItem[]>([]);
  const [currentFreeItems, setCurrentFreeItems] = useState<FreeItem[]>([]);
  const isSyncingRef = useRef(false);

  // Sync state
  const [lastKnownUpdate, setLastKnownUpdate] = useState<string | null>(null);
  const [hasExternalChange, setHasExternalChange] = useState(false);

  // Timer effect - KST 기준 다음 0시까지 카운트다운
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          // 자정이 지나면 다시 계산 (24시간 또는 실제 남은 시간)
          return getSecondsUntilMidnightKST();
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Load character list on mount
  useEffect(() => {
    loadCharacters();
  }, []);

  // Polling for external changes
  useEffect(() => {
    if (!selectedCharacterData) return;

    const pollForChanges = async () => {
      try {
        const data = await getCharacter(selectedCharacterData.name);
        if (data.updated_at && lastKnownUpdate && data.updated_at !== lastKnownUpdate) {
          // 외부에서 변경됨
          if (hasUnsavedChanges) {
            setHasExternalChange(true);
          } else {
            // 저장하지 않은 변경사항이 없으면 자동 새로고침
            setSelectedCharacterData(data);
            setLastKnownUpdate(data.updated_at);
          }
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    const interval = setInterval(pollForChanges, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [selectedCharacterData?.name, lastKnownUpdate, hasUnsavedChanges]);

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
        hp: char.hp,
        maxHp: char.max_hp,
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
    // 시트에서 불러온 직후·저장 후 재로드 시 BagTab의 onInventoryChange가 호출되더라도
    // hasUnsavedChanges가 true로 잡히지 않도록 동기화 구간으로 표시
    isSyncingRef.current = true;

    try {
      const charName = chars[index].name;
      const data = await getCharacter(charName);
      setSelectedCharacterData(data);
      setLastKnownUpdate(data.updated_at || null);
      setHasExternalChange(false);

      // Update the character in the list with fresh data
      const updatedChars = [...chars];
      updatedChars[index] = {
        ...updatedChars[index],
        capacity: data.bag_used,
        maxCapacity: data.bag_capacity,
        gridSize: data.bag_capacity,
        strength: data.strength,
        hp: data.hp,
        maxHp: data.max_hp,
      };
      setCharacters(updatedChars);
    } catch (error) {
      console.error('Failed to load character data:', error);
    } finally {
      setIsLoadingCharacterData(false);
      // BagTab useEffect가 초기 state로 onInventoryChange 호출한 뒤에 해제
      setTimeout(() => {
        isSyncingRef.current = false;
      }, 100);
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
    isSyncingRef.current = true;

    try {
      const payload = {
        items: gridItemsToApiItems(currentItems),
        nearby_items: nearbyItemsToApiItems(currentNearbyItems),
        misc_items: freeItemsToApiItems(currentFreeItems),
        layout: gridItemsToApiLayout(currentItems),
        last_known_update: lastKnownUpdate || undefined,
      };
      const result = await updateBag(selectedCharacterData.name, payload);

      // 충돌 처리
      if (result.conflict) {
        setHasExternalChange(true);
        setSaveError('다른 곳에서 변경되었습니다. 새로고침 후 다시 시도하세요.');
        return;
      }

      // 새 타임스탬프 저장
      if (result.updated_at) {
        setLastKnownUpdate(result.updated_at);
      }

      // 시트 반영 후 새 데이터 로드, 완료 후에만 저장 상태 해제
      await selectCharacter(selectedCharacterIndex);
      setHasUnsavedChanges(false);
      setHasExternalChange(false);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : 'Failed to save';
      setSaveError(message);
      console.error('Failed to save:', error);
    } finally {
      setIsSaving(false);
      // 다음 틱까지 대기 후 해제 (BagTab useEffect에서 로드된 데이터로 handleInventoryChange 호출 방지)
      setTimeout(() => {
        isSyncingRef.current = false;
      }, 0);
    }
  };

  const handleInventoryChange = useCallback(
    (state: { items: Item[]; nearbyItems: NearbyItem[]; freeItems: FreeItem[] }) => {
      setCurrentItems(state.items);
      setCurrentNearbyItems(state.nearbyItems);
      setCurrentFreeItems(state.freeItems);
      if (!isSyncingRef.current) {
        setHasUnsavedChanges(true);
      }
    },
    []
  );

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
    <div className="h-full min-h-screen bg-black">
      <div className="h-full max-w-[1196px] mx-auto flex flex-col bg-[var(--bg)] overflow-hidden">
        {/* Header */}
        <header className="h-14 md:h-16 border-b border-[var(--bg-light)] flex items-center justify-between px-4 md:px-6 bg-[var(--bg-mid)] shrink-0">
        <div className="flex items-center">
          <img 
            src="/image/wordmark.png" 
            alt="TRASHPIT" 
            className="h-8 md:h-10 w-auto"
          />
        </div>
        <div className="flex items-center gap-3 md:gap-4">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="md:hidden p-2.5 rounded-lg bg-[var(--bg-light)] text-[var(--blue)] hover:bg-[var(--blue)]/20 transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--blue)]/50"
            aria-label={isSidebarOpen ? '메뉴 닫기' : '메뉴 열기'}
            aria-expanded={isSidebarOpen}
          >
            {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex flex-1 min-h-0 relative">
        {/* Main content area */}
        <main className="flex-1 min-w-0 flex flex-col bg-[var(--bg)] overflow-hidden">
          <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6">
            {(isLoadingCharacterData || isSaving) ? (
              <div className="flex flex-col items-center justify-center h-full min-h-[400px] gap-4">
                <Loader2 className="w-10 h-10 text-[var(--blue)] animate-spin" />
                <p className="text-sm text-[var(--text-muted)]">
                  {isSaving ? '저장 중...' : '데이터 로딩 중...'}
                </p>
              </div>
            ) : currentCharacter && selectedCharacterData ? (
              <BagTab
                gridSize={currentCharacter.gridSize}
                timeRemaining={timeRemaining}
                formatTime={formatTime}
                characterData={selectedCharacterData}
                onInventoryChange={handleInventoryChange}
                onRefresh={handleRefresh}
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-[var(--text-muted)]">
                <Package className="w-16 h-16 mb-4 opacity-30" />
                <p className="text-base font-medium mb-2">캐릭터를 선택하세요</p>
                <p className="text-sm opacity-70">오른쪽 패널에서 캐릭터를 선택하면 인벤토리가 표시됩니다</p>
              </div>
            )}
          </div>
        </main>

        {/* Overlay for mobile sidebar */}
        {isSidebarOpen && (
          <div
            className="md:hidden fixed inset-0 bg-black/60 z-40"
            onClick={() => setIsSidebarOpen(false)}
            aria-hidden="true"
          />
        )}

        {/* Right sidebar */}
        <aside 
          className={`
            w-full sm:w-[340px] md:w-[300px] lg:w-[320px]
            border-l border-[var(--bg-light)] bg-[var(--bg-mid)]
            flex flex-col shrink-0
            fixed md:relative right-0 top-14 md:top-0 bottom-0 z-50 md:z-auto
            transform transition-transform duration-200
            ${isSidebarOpen ? 'translate-x-0' : 'translate-x-full md:translate-x-0'}
          `}
          role="complementary"
          aria-label="캐릭터 선택 패널"
        >
          {/* Mobile Close Button */}
          <div className="md:hidden p-3 border-b border-[var(--bg-light)] flex items-center justify-end shrink-0">
            <button
              onClick={() => setIsSidebarOpen(false)}
              className="p-1.5 rounded-lg text-[var(--text-muted)] hover:text-[var(--blue)] hover:bg-[var(--bg-light)] transition-colors focus:outline-none"
              aria-label="패널 닫기"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Search */}
          <div className="p-3 border-b border-[var(--bg-light)] shrink-0">
            <div className="relative">
              <Search className="absolute top-1/2 -translate-y-1/2 left-3 w-4 h-4 text-[var(--text-muted)] pointer-events-none" />
              <input
                type="text"
                placeholder="캐릭터 검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full py-2 pl-10 pr-4 rounded-lg bg-[var(--bg)] border border-[var(--bg-light)] text-sm text-[var(--text)] placeholder-[var(--text-muted)] focus:border-[var(--blue)] focus:outline-none transition-colors"
                aria-label="캐릭터 검색"
              />
            </div>
          </div>

          {/* Character list */}
          <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-2" role="list" aria-label="캐릭터 목록">
            {isLoadingCharacters ? (
              <div className="flex flex-col items-center justify-center py-12 gap-3">
                <Loader2 className="w-6 h-6 text-[var(--blue)] animate-spin" />
                <p className="text-xs text-[var(--text-muted)]">캐릭터 로딩 중...</p>
              </div>
            ) : characterError ? (
              <div className="flex flex-col items-center justify-center py-12 text-[var(--danger)]">
                <AlertTriangle className="w-6 h-6 mb-3" />
                <p className="text-sm font-medium mb-1">오류 발생</p>
                <p className="text-xs text-[var(--text-muted)] mb-3">{characterError}</p>
                <button
                  onClick={loadCharacters}
                  className="px-4 py-2 text-xs font-medium text-[var(--blue)] bg-[var(--blue)]/10 rounded-lg hover:bg-[var(--blue)]/20 transition-colors focus:outline-none"
                >
                  다시 시도
                </button>
              </div>
            ) : filteredCharacters.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-[var(--text-muted)]">
                <Search className="w-6 h-6 mb-3 opacity-50" />
                <p className="text-sm">캐릭터를 찾을 수 없습니다</p>
              </div>
            ) : (
              filteredCharacters.map((character) => {
                const actualIndex = characters.indexOf(character);
                const isActive = selectedCharacterIndex === actualIndex;
                const hpPercent = (character.hp / character.maxHp) * 100;
                const capacityPercent = (character.capacity / character.gridSize) * 100;

                return (
                  <button
                    key={actualIndex}
                    onClick={() => selectCharacter(actualIndex)}
                    className={`w-full text-left p-3 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--blue)]/50 ${
                      isActive
                        ? 'bg-[var(--blue)]/15 border-2 border-[var(--blue)]'
                        : 'bg-[var(--bg)] border border-[var(--bg-light)] hover:border-[var(--item)]/50'
                    }`}
                    role="listitem"
                    aria-selected={isActive}
                    aria-label={`${character.name}, HP ${character.hp}/${character.maxHp}, 가방 ${character.capacity}/${character.gridSize}`}
                  >
                    <div className="flex items-center gap-3">
                      {/* Avatar */}
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold shrink-0 ${
                        isActive
                          ? 'bg-[var(--blue)] text-white'
                          : 'bg-[var(--bg-light)] text-[var(--text-muted)]'
                      }`}>
                        {character.name[0]}
                      </div>

                      <div className="flex-1 min-w-0 space-y-2">
                        {/* Name and STR */}
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-semibold text-[var(--text)] truncate">{character.name}</span>
                          <div className="flex items-center gap-1 text-[10px] text-[var(--text-muted)] shrink-0 ml-2">
                            <span className="font-bold">STR</span>
                            <span className="text-[var(--item)] font-bold">{character.strength}</span>
                          </div>
                        </div>

                        {/* Stats bars */}
                        <div className="flex gap-3">
                          {/* HP bar */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between text-[10px] text-[var(--text-muted)] mb-1">
                              <span className="font-bold">HP</span>
                              <span className="font-bold text-[var(--danger)]">{character.hp}/{character.maxHp}</span>
                            </div>
                            <div className="h-1.5 bg-[var(--empty-bar)] rounded-full overflow-hidden">
                              <div
                                className="h-full bg-[var(--danger)] rounded-full transition-all duration-300"
                                style={{ width: `${hpPercent}%` }}
                              />
                            </div>
                          </div>

                          {/* Bag capacity bar */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between text-[10px] text-[var(--text-muted)] mb-1">
                              <span className="font-bold flex items-center gap-0.5">
                                <Package className="w-2.5 h-2.5" />
                                BAG
                              </span>
                              <span className={`font-bold ${
                                capacityPercent > 80 ? 'text-[var(--danger)]'
                                  : capacityPercent > 60 ? 'text-[var(--warn)]'
                                  : 'text-[var(--success)]'
                              }`}>{character.capacity}/{character.gridSize}</span>
                            </div>
                            <div className="h-1.5 bg-[var(--empty-bar)] rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all duration-300 ${
                                  capacityPercent > 80 ? 'bg-[var(--danger)]'
                                    : capacityPercent > 60 ? 'bg-[var(--warn)]'
                                    : 'bg-[var(--success)]'
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
          <div className="p-4 border-t border-[var(--bg-light)] space-y-2 shrink-0">
            {/* External change warning */}
            {hasExternalChange && (
              <div className="flex items-center gap-2 px-3 py-2 bg-[var(--warn)]/15 border border-[var(--warn)]/40 rounded-lg" role="alert">
                <RefreshCw className="w-4 h-4 text-[var(--warn)] shrink-0" />
                <span className="text-xs text-[var(--warn)]">다른 곳에서 변경됨. 저장 전 새로고침 권장</span>
              </div>
            )}

            {/* Save error */}
            {saveError && (
              <div className="flex items-center gap-2 px-3 py-2 bg-[var(--danger)]/10 border border-[var(--danger)]/30 rounded-lg" role="alert">
                <AlertTriangle className="w-4 h-4 text-[var(--danger)] shrink-0" />
                <span className="text-xs text-[var(--danger)]">{saveError}</span>
              </div>
            )}

            {/* 안내 문구 */}
            <p className="text-[10px] leading-tight" style={{ color: 'var(--danger)' }}>
              동기화 버튼은 신중하게 수정한 후, 한번만 눌러주세요. 업데이트 한도에 걸리면 수정 사항이 반영되지 않습니다.
            </p>

            {/* Sync to Cloud button — 수정사항 있을 때만 "변경사항 동기화!" + 깜빡임 */}
            <button
              className={`w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm rounded-lg bg-[var(--success)]/15 border border-[var(--success)]/50 text-[var(--success)] hover:bg-[var(--success)]/25 transition-colors font-bold disabled:opacity-30 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-[var(--success)]/50 ${hasUnsavedChanges && !isSaving ? 'animate-pulse' : ''}`}
              onClick={handleSave}
              disabled={isSaving || !hasUnsavedChanges}
              aria-label={hasUnsavedChanges ? '저장되지 않은 변경사항 있음 — 동기화' : '클라우드 동기화'}
            >
              {isSaving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Cloud className="w-4 h-4" />
              )}
              <span>
                {isSaving ? '저장 중...' : hasUnsavedChanges ? '변경사항 동기화!' : '클라우드 동기화'}
              </span>
            </button>

            {/* Refresh Data button */}
            <button
              className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm rounded-lg bg-[var(--blue)]/10 border border-[var(--blue)]/30 text-[var(--blue)] hover:bg-[var(--blue)]/20 transition-colors font-medium disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-[var(--blue)]/50"
              onClick={handleRefresh}
              disabled={isLoadingCharacterData}
              aria-label="데이터 새로고침"
            >
              <RefreshCw className={`w-4 h-4 ${isLoadingCharacterData ? 'animate-spin' : ''}`} />
              데이터 새로고침
            </button>
          </div>
        </aside>
      </div>
      </div>
    </div>
  );
}
