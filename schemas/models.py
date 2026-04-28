from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional, Literal

# 성수 변화 키 제한
DeclensionKey = Literal["ms", "mp", "fs", "fp"]
# 시제 키 제한
TenseKey = Literal["pres", "pret", "impf", "futr", "cond", "perf"]

class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=2, description="학습 주제")

class GeneratedWord(BaseModel):
    word: str = Field(..., description="스페인어 원형(Lemma)")
    pos: List[str] = Field(..., description="품사 리스트 (예: ['VERB', 'NOUN'])")
    meaning: Dict[str, List[str]] = Field(..., description="품사별 뜻 (예: {'VERB': ['가다']})")
    # 정형화된 키값을 사용하는 딕셔너리
    conjugations: Optional[Dict[TenseKey, Dict[str, str]]] = Field(
        None, 
        description="시제별(pres, pret, impf, futr, cond, perf) 및 인칭별(s1-p3) 변화"
    )
    declensions: Optional[Dict[DeclensionKey, Optional[str]]] = Field(
        None, 
        description="성/수 변화 (ms, mp, fs, fp)"
    )

class GeneratedSentence(BaseModel):
    sentence: str = Field(..., description="스페인어 예문")
    translation: str = Field(..., description="한국어 번역")
    target_words: List[str] = Field(default_factory=list, description="사용된 원형 리스트")

class GeneratedBundle(BaseModel):
    title: str = Field(..., description="번들 제목")
    description: str = Field(..., description="번들 설명")
    words: List[GeneratedWord] = Field(..., description="종합 단어 정보 목록")
    sentences: List[GeneratedSentence] = Field(..., description="예문 목록")

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)
