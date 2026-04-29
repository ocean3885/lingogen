from fastapi import FastAPI, HTTPException
from schemas.models import StoreSentencesRequest
from services.pipeline import process_and_store_sentence

app = FastAPI(
    title="LingoGen API",
    description="LLM 기반 스페인어 학습 자료 자동 생성 및 파이프라인 API",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to LingoGen API"}

@app.post("/store-sentences")
async def store_sentences(request: StoreSentencesRequest):
    """
    여러 문장을 전달받아 순차적으로 파이프라인(TTS, 분석, DB 저장)을 실행합니다.
    """
    results = []
    for item in request.items:
        try:
            sentence_id = await process_and_store_sentence(item.sentence, item.translation)
            results.append({
                "sentence": item.sentence,
                "status": "success",
                "sentence_id": sentence_id
            })
        except Exception as e:
            results.append({
                "sentence": item.sentence,
                "status": "error",
                "message": str(e)
            })
    
    return {"results": results}
