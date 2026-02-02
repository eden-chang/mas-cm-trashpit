-- Migration: 001_add_updated_at
-- Description: characters 테이블에 updated_at 컬럼 추가 (실시간 동기화용)
-- Phase: 5.2 - 실시간 동기화

-- 1. updated_at 컬럼 추가
ALTER TABLE characters
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- 2. 기존 데이터에 현재 시각 설정
UPDATE characters
SET updated_at = NOW()
WHERE updated_at IS NULL;

-- 3. 업데이트 트리거 함수 생성
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- 4. 트리거 생성 (이미 있으면 삭제 후 재생성)
DROP TRIGGER IF EXISTS update_characters_updated_at ON characters;
CREATE TRIGGER update_characters_updated_at
    BEFORE UPDATE ON characters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 확인 쿼리
-- SELECT name, updated_at FROM characters LIMIT 5;
