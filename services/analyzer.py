import spacy
from typing import List
from schemas.models import AnalyzedToken, AnalysisResponse

# 이미 설치된 es_core_news_lg 모델 로드
try:
    nlp = spacy.load("es_core_news_lg")
except OSError:
    # 혹시 모를 로드 실패를 대비해 경고만 출력 (사용자 확인 기반)
    print("WARNING: es_core_news_lg 모델을 로드할 수 없습니다. 설치 여부를 다시 확인해주세요.")
    nlp = None

def analyze_spanish_sentence(sentence: str) -> List[AnalyzedToken]:
    """
    단일 문장을 분석합니다.
    """
    if not nlp:
        raise RuntimeError("spaCy 모델이 로드되지 않았습니다.")
        
    doc = nlp(sentence)
    analyzed_tokens = []
    
    for token in doc:
        if token.is_punct or token.is_space:
            continue
            
        analyzed_tokens.append(
            AnalyzedToken(
                text=token.text,
                lemma=token.lemma_,
                pos=token.pos_,
                morph=token.morph.to_dict(),
                is_stop=token.is_stop
            )
        )
    return analyzed_tokens

def analyze_sentences(sentences: List[str]) -> List[AnalysisResponse]:
    """
    문장 리스트를 받아서 각 문장별 분석 결과를 반환합니다.
    """
    results = []
    for s in sentences:
        tokens = analyze_spanish_sentence(s)
        results.append(AnalysisResponse(sentence=s, tokens=tokens))
    return results
