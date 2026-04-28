from fastapi import FastAPI, HTTPException
from schemas.models import GenerateRequest
from services.generator import generate_content_with_gemini
from services.db import save_bundle_pipeline
import traceback

app = FastAPI(
    title="LingoGen API",
    description="LLM 기반 스페인어 학습 자료 자동 생성 및 파이프라인 API",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to LingoGen API"}

@app.post("/generate", status_code=201)
async def generate_and_save(request: GenerateRequest, category_id: int = 1):
    """
    1. Gemini를 호출하여 스페인어 번들/문장 데이터를 생성합니다.
    2. 생성된 문장을 spaCy로 분석합니다.
    3. 분석된 결과 및 원본 데이터를 Supabase에 저장합니다.
    """
    try:
        # 1. 컨텐츠 생성 (Gemini)
        bundle_data = await generate_content_with_gemini(request.topic)
        
        # 2 & 3. 언어 분석 및 DB 적재 (Pipeline 안에서 순차적 처리)
        bundle_id = await save_bundle_pipeline(category_id, bundle_data)
        
        return {
            "message": "데이터 생성 및 DB 적재가 완료되었습니다.",
            "bundle_id": bundle_id,
            "data_summary": {
                "title": bundle_data.title,
                "words_count": len(bundle_data.words),
                "sentences_count": len(bundle_data.sentences)
            }
        }
    except Exception as e:
        # 실제 운영에서는 logger를 사용하여 스택 트레이스 기록
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/push-bundle")
async def push_bundle_to_multiple_tables(bundle: GeneratedBundle):
    try:
        # 1. 번들 기본 정보 저장 (bundles 테이블)
        bundle_res = supabase.table("bundles").insert({
            "title": bundle.title,
            "description": bundle.description
        }).execute()
        bundle_id = bundle_res.data[0]["id"]

        # 2. 단어 저장 및 ID 맵 생성 (words 테이블)
        word_map = {} # { "원형": "db_uuid" }
        for w in bundle.words:
            word_res = supabase.table("words").insert({
                "word": w.word,
                "pos": w.pos,
                "meaning": w.meaning,
                "conjugations": w.conjugations,
                "declensions": w.declensions
            }).execute()
            word_map[w.word] = word_res.data[0]["id"]

        # 3. 문장 저장 및 매핑 (sentences & 관련 map 테이블)
        for s in bundle.sentences:
            # 3-1. 문장 자체 저장
            sent_res = supabase.table("sentences").insert({
                "sentence": s.sentence,
                "translation": s.translation
            }).execute()
            sent_id = sent_res.data[0]["id"]

            # 3-2. word_sentence_map 저장 (문장 내 단어 연결)
            for target_word in s.target_words:
                if target_word in word_map:
                    supabase.table("word_sentence_map").insert({
                        "word_id": word_map[target_word],
                        "sentence_id": sent_id
                    }).execute()

            # 3-3. bundle_items 저장 (번들과 단어/문장 연결)
            # 여기서는 문장 기준으로 번들에 포함시킵니다.
            supabase.table("bundle_items").insert({
                "bundle_id": bundle_id,
                "sentence_id": sent_id
            }).execute()

        return {"status": "success", "bundle_id": bundle_id}

    except Exception as e:
        # 실제 운영 환경에서는 중도 실패 시 이미 들어간 데이터를 롤백하는 로직이 필요할 수 있습니다.
        raise HTTPException(status_code=500, detail=f"Database push failed: {str(e)}")

@app.post("/push-bundle-rpc")
async def push_bundle_rpc(bundle: GeneratedBundle):
    try:
        # rpc() 메서드를 사용하여 작성한 함수 호출
        result = supabase.rpc("push_full_bundle", {
            "p_title": bundle.title,
            "p_description": bundle.description,
            "p_words": [w.model_dump() for w in bundle.words],
            "p_sentences": [s.model_dump() for s in bundle.sentences]
        }).execute()
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))