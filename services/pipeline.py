from typing import List
from services.db import supabase
from services.analyzer import analyze_spanish_sentence
from services.tts import generate_and_upload_tts
from services.generator import generate_word_info

async def process_and_store_sentence(sentence_text: str, translation: str, lang_code: str = "es") -> int:
    """
    1. 문장을 TTS 변환 및 저장 (sentences 테이블)
    2. 문장을 형태소 분석
    3. 각 토큰(word)을 words 테이블에 저장 (없을 경우 TTS 변환 및 저장)
    4. 문장과 단어를 word_sentence_map으로 매핑
    """
    print(f"[{sentence_text}] 처리 시작...")

    # 1. 문장 TTS 생성 및 sentences 테이블 저장
    sentence_audio_url = generate_and_upload_tts(sentence_text, folder="sentences", lang=lang_code)
    
    sentence_res = supabase.table("sentences").insert({
        "sentence": sentence_text,
        "translation": translation,
        "audio_url": sentence_audio_url
    }).execute()
    
    sentence_id = sentence_res.data[0]["id"]
    print(f"  - 문장 저장 완료 (ID: {sentence_id}, Audio: {sentence_audio_url})")

    # 2. 문장 분석
    analyzed_tokens = analyze_spanish_sentence(sentence_text)
    
    # 3 & 4. 단어 처리 및 매핑
    for token in analyzed_tokens:
        # 구두점 등 불필요한 토큰 건너뛰기
        if not token.lemma.strip():
            continue
            
        # 불용어(Stop word) 저장 제외
        if token.is_stop:
            print(f"  - 불용어 건너뜀: {token.text}")
            continue
            
        word_lemma = token.lemma.lower()
        
        # 3. DB에 단어가 존재하는지 확인
        word_query = supabase.table("words").select("id").eq("word", word_lemma).eq("lang_code", lang_code).execute()
        
        if word_query.data:
            # 이미 존재하는 단어
            word_id = word_query.data[0]["id"]
            print(f"  - 단어 '{word_lemma}' (이미 존재, ID: {word_id})")
        else:
            # 존재하지 않는 새로운 단어 -> LLM 정보 추출 & TTS 생성 후 삽입
            print(f"  - 단어 '{word_lemma}' LLM 정보 추출 중...")
            llm_info = await generate_word_info(word_lemma)
            
            word_audio_url = generate_and_upload_tts(word_lemma, folder="words", lang=lang_code)
            
            word_res = supabase.table("words").insert({
                "word": word_lemma,
                "lang_code": lang_code,
                "pos": llm_info.get("pos", [token.pos] if token.pos else []),
                "meaning": llm_info.get("meaning", {}), 
                "gender": llm_info.get("gender"),
                "declensions": llm_info.get("declensions", {}),
                "conjugations": llm_info.get("conjugations", {}),
                "audio_url": word_audio_url
                # gender 등은 분석기에서 추출된 정보에 따라 매핑할 수 있으나 여기선 생략
            }).execute()
            
            word_id = word_res.data[0]["id"]
            print(f"  - 단어 '{word_lemma}' (신규 저장, ID: {word_id}, Audio: {word_audio_url})")
            
        # 4. word_sentence_map 연결 정보 저장
        supabase.table("word_sentence_map").insert({
            "word_id": word_id,
            "sentence_id": sentence_id,
            "used_as": token.text,
            "pos_key": token.pos,
            "grammar_info": token.morph
        }).execute()
        
    print(f"[{sentence_text}] 처리 완료!\n")
    return sentence_id
