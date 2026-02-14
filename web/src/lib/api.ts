/**
 * API 클라이언트 (캐릭터·가방·동기화)
 */

import type { CharacterSummary, ApiCharacter } from '@/lib/types';

const BASE = typeof import.meta.env !== 'undefined' && import.meta.env.VITE_API_BASE_URL != null
  ? String(import.meta.env.VITE_API_BASE_URL).replace(/\/$/, '')
  : '';

const REQUEST_TIMEOUT_MS = 30_000;
const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 1_000;

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

/** 재시도 가능한 GET 요청 (타임아웃·네트워크 오류 시 자동 재시도) */
async function requestWithRetry<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  let lastError: ApiError | undefined;

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      return await request<T>(endpoint, options);
    } catch (err) {
      lastError = err instanceof ApiError ? err : new ApiError('알 수 없는 오류', 0);

      // 4xx 클라이언트 오류는 재시도하지 않음
      if (lastError.status >= 400 && lastError.status < 500) {
        throw lastError;
      }

      // 마지막 시도였으면 에러 throw
      if (attempt >= MAX_RETRIES) {
        throw lastError;
      }

      // 재시도 전 대기 (지수 백오프)
      await new Promise((r) => setTimeout(r, RETRY_DELAY_MS * (attempt + 1)));
    }
  }

  throw lastError!;
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
  const data = await requestWithRetry<unknown>('/api/characters');
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
  return requestWithRetry<ApiCharacter>(`/api/character/${encodeURIComponent(name)}`);
}

/** 가방·주변·여유공간·배치 일괄 업데이트 (POST는 재시도하지 않음) */
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
