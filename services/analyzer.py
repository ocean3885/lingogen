import spacy
from typing import List
from schemas.models import AnalyzedToken

# 서버 시작 시 스페인어 모델 로드
# 모델이 없는 경우 터미널에서 `python -m spacy download es_core_news_lg` 실행 필요
try:
    nlp = spacy.load("es_core_news_lg")
except OSError:
    print("WARNING: es_core_news_lg 모델이 설치되지 않았습니다. 분석 기능이 실패할 수 있습니다.")
    nlp = None

def analyze_spanish_sentence(sentence: str) -> List[AnalyzedToken]:
    """
    주어진 스페인어 문장을 spaCy로 분석하여 토큰 단위의 문법 정보를 반환합니다.
    """
    if not nlp:
        raise RuntimeError("spaCy 모델이 로드되지 않았습니다. 서버 환경을 확인해주세요.")
        
    doc = nlp(sentence)
    analyzed_tokens = []
    
    for token in doc:
        # 구두점이나 공백은 무시 (필요에 따라 변경 가능)
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
