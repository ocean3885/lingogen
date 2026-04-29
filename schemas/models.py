from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional, Literal

# 성수 변화 키 제한
DeclensionKey = Literal["ms", "mp", "fs", "fp"]
# 성별 키 제한 (m: 남성, f: 여성, mf: 공통)
GenderKey = Literal["m", "f", "mf"]
# 시제 키 제한
TenseKey = Literal["pres", "pret", "impf", "futr", "cond", "perf"]

class AnalyzedToken(BaseModel):
    text: str = Field(..., description="원문 토큰")
    lemma: str = Field(..., description="기본형(Lemma)")
    pos: str = Field(..., description="품사(POS)")
    morph: Dict[str, Any] = Field(..., description="형태소 분석 정보")
    is_stop: bool = Field(..., description="불용어 여부")

class AnalysisResponse(BaseModel):
    sentence: str
    tokens: List[AnalyzedToken]

class SentenceItem(BaseModel):
    sentence: str
    translation: str

class StoreSentencesRequest(BaseModel):
    items: List[SentenceItem]
