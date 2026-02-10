/**
 * API 클라이언트 (캐릭터·가방·동기화)
 */

import type { CharacterSummary, ApiCharacter } from '@/lib/types';

const BASE = typeof import.meta.env !== 'undefined' && import.meta.env.VITE_API_BASE_URL != null
  ? String(import.meta.env.VITE_API_BASE_URL).replace(/\/$/, '')
  : '';

const REQUEST_TIMEOUT_MS = 15_000;

function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  return fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
    signal: controller.signal,
  }).then(async (res) => {
    let data: unknown;
    try {
      data = await res.json();
    } catch {
      if (res.ok) {
        throw new ApiError('서버 응답 파싱 실패', res.status);
      }
      data = {};
    }
    if (!res.ok) {
      throw new ApiError((data as { error?: string }).error || '요청 실패', res.status);
    }
    return data as T;
  }).catch((err) => {
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError('요청 시간 초과', 0);
    }
    throw new ApiError(err instanceof Error ? err.message : '네트워크 오류', 0);
  }).finally(() => {
    clearTimeout(timeoutId);
  });
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** 전체 캐릭터 목록 */
export async function getCharacters(): Promise<CharacterSummary[]> {
  const data = await request<unknown>('/api/characters');
  if (!Array.isArray(data)) {
    throw new ApiError(
      typeof (data as { error?: string })?.error === 'string'
        ? (data as { error: string }).error
        : '캐릭터 목록을 불러올 수 없습니다. API 주소를 확인해 주세요.',
      0
    );
  }
  return data as CharacterSummary[];
}

/** 캐릭터 상세 (가방·주변·여유공간·배치 포함) */
export function getCharacter(name: string): Promise<ApiCharacter> {
  return request<ApiCharacter>(`/api/character/${encodeURIComponent(name)}`);
}

/** 가방·주변·여유공간·배치 일괄 업데이트 */
export function updateBag(
  name: string,
  payload: {
    items: Array<{ name: string; quantity: number }>;
    nearby_items: Array<{ name: string; quantity: number }>;
    misc_items: Array<{ name: string; quantity: number }>;
    layout?: Array<{ name: string; row: number; col: number; shapeIndex: number }>;
    last_known_update?: string;
  }
): Promise<{ success: boolean; updated_at?: string; conflict?: boolean; error?: string }> {
  return request(`/api/bag/${encodeURIComponent(name)}`, {
    method: 'POST',
    body: JSON.stringify({
      items: payload.items,
      nearby_items: payload.nearby_items,
      misc_items: payload.misc_items,
      layout: payload.layout,
      last_known_update: payload.last_known_update,
    }),
  });
}
