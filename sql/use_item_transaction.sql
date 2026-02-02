-- 아이템 사용 트랜잭션 함수
-- 아이템 차감과 스탯 업데이트를 원자적으로 처리합니다.

CREATE OR REPLACE FUNCTION use_item_transaction(
    p_char_name TEXT,
    p_item_name TEXT,
    p_location TEXT,  -- 'bag', 'misc', 'around'
    p_stat_column TEXT,  -- 'con', 'str', 'luck', 'hp'
    p_stat_delta INTEGER
)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_result JSON;
    v_current_inventory JSONB;
    v_current_quantity INTEGER;
    v_new_inventory JSONB;
BEGIN
    -- 트랜잭션 시작 (함수 내에서 자동으로 트랜잭션 처리됨)
    
    -- 1. 캐릭터 조회 및 잠금 (FOR UPDATE)
    SELECT 
        CASE 
            WHEN p_location = 'bag' THEN bag
            WHEN p_location = 'misc' THEN misc
            WHEN p_location = 'around' THEN around
            ELSE NULL
        END
    INTO v_current_inventory
    FROM characters
    WHERE name = p_char_name
    FOR UPDATE;
    
    -- 캐릭터가 없으면 에러
    IF NOT FOUND THEN
        RETURN json_build_object(
            'success', false,
            'error', 'CHARACTER_NOT_FOUND'
        );
    END IF;
    
    -- 2. 아이템 수량 확인
    v_current_quantity := COALESCE((v_current_inventory->>p_item_name)::INTEGER, 0);
    
    IF v_current_quantity < 1 THEN
        RETURN json_build_object(
            'success', false,
            'error', 'ITEM_NOT_FOUND'
        );
    END IF;
    
    -- 3. 아이템 차감
    v_new_inventory := v_current_inventory;
    
    IF v_current_quantity = 1 THEN
        -- 마지막 아이템이면 키 삭제
        v_new_inventory := v_new_inventory - p_item_name;
    ELSE
        -- 수량 감소
        v_new_inventory := jsonb_set(
            v_new_inventory,
            ARRAY[p_item_name],
            to_jsonb(v_current_quantity - 1)
        );
    END IF;
    
    -- 4. 인벤토리 업데이트 및 스탯 업데이트 (원자적 처리)
    IF p_stat_column IS NOT NULL AND p_stat_delta IS NOT NULL AND p_stat_delta != 0 THEN
        -- 스탯 업데이트 포함
        EXECUTE format(
            'UPDATE characters SET %I = %I + $1, %I = $2 WHERE name = $3',
            p_stat_column, p_stat_column,
            CASE 
                WHEN p_location = 'bag' THEN 'bag'
                WHEN p_location = 'misc' THEN 'misc'
                WHEN p_location = 'around' THEN 'around'
            END
        ) USING p_stat_delta, v_new_inventory, p_char_name;
    ELSE
        -- 인벤토리만 업데이트
        EXECUTE format(
            'UPDATE characters SET %I = $1 WHERE name = $2',
            CASE 
                WHEN p_location = 'bag' THEN 'bag'
                WHEN p_location = 'misc' THEN 'misc'
                WHEN p_location = 'around' THEN 'around'
            END
        ) USING v_new_inventory, p_char_name;
    END IF;
    
    -- 5. 성공 응답
    RETURN json_build_object(
        'success', true,
        'removed_quantity', 1,
        'stat_updated', p_stat_delta IS NOT NULL AND p_stat_delta != 0
    );
    
EXCEPTION
    WHEN OTHERS THEN
        -- 에러 발생 시 롤백 (자동)
        RETURN json_build_object(
            'success', false,
            'error', 'TRANSACTION_FAILED',
            'message', SQLERRM
        );
END;
$$;

-- 함수 사용 예시:
-- SELECT use_item_transaction('테스트캐릭터', '회복 물약', 'bag', 'con', 5);
