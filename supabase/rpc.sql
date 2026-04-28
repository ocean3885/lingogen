CREATE OR REPLACE FUNCTION push_full_bundle(
    p_title TEXT,
    p_description TEXT,
    p_words JSONB,
    p_sentences JSONB
) RETURNS VOID AS $$
DECLARE
    v_bundle_id UUID;
    v_word_record JSONB;
    v_sent_record JSONB;
    v_new_word_id UUID;
    v_new_sent_id UUID;
    v_target_word TEXT;
BEGIN
    -- 1. Bundle Insert
    INSERT INTO bundles (title, description) 
    VALUES (p_title, p_description) RETURNING id INTO v_bundle_id;

    -- 2. Words Bulk Insert (여기서는 설명을 위해 루프 처리하거나 별도 로직 사용)
    -- 실제로는 jsonb_to_recordset 등을 활용해 더 빠르게 처리 가능합니다.
    
    -- 3. 매핑 로직을 포함한 복합 Insert 수행...
END;
$$ LANGUAGE plpgsql;