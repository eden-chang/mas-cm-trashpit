/**
 * 캐릭터별 개인 링크 토큰 (봇의 [가방 링크] 명령어로 발급)
 *
 * 링크의 #token= 값(서버로 전송되지 않는 프래그먼트)을 세션에 보관하고 주소창에서는 지워
 * 화면 공유·방문 기록으로 새지 않게 한다.
 * 토큰 검증은 서버가 하며, 여기서는 표시용으로 캐릭터 이름만 읽는다.
 */

const STORAGE_KEY = 'inventoryAccessToken';

function readTokenFromUrl(): string | null {
  const hashParams = new URLSearchParams(window.location.hash.slice(1));
  const token = hashParams.get('token');
  if (!token) return null;
  hashParams.delete('token');
  const rest = hashParams.toString();
  window.history.replaceState(null, '', window.location.pathname + window.location.search + (rest ? `#${rest}` : ''));
  return token;
}

function decodePayload(token: string): { n?: unknown; exp?: unknown } | null {
  const [payload] = token.split('.');
  if (!payload) return null;
  try {
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
    const bytes = Uint8Array.from(atob(padded), (c) => c.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  } catch {
    return null;
  }
}

let cachedToken: string | null | undefined;

export function getAccessToken(): string | null {
  if (cachedToken !== undefined) return cachedToken;
  const fromUrl = readTokenFromUrl();
  if (fromUrl) {
    try {
      sessionStorage.setItem(STORAGE_KEY, fromUrl);
    } catch {
      // 저장소가 막힌 환경에서도 현재 탭에서는 동작하도록 메모리 값만 사용
    }
    cachedToken = fromUrl;
    return cachedToken;
  }
  try {
    cachedToken = sessionStorage.getItem(STORAGE_KEY);
  } catch {
    cachedToken = null;
  }
  return cachedToken;
}

/** 토큰에 담긴 캐릭터 이름. 형식이 잘못됐거나 만료됐으면 null */
export function getTokenCharacterName(token: string | null = getAccessToken()): string | null {
  if (!token) return null;
  const data = decodePayload(token);
  if (!data || typeof data.n !== 'string' || typeof data.exp !== 'number') return null;
  if (Date.now() / 1000 >= data.exp) return null;
  return data.n;
}
