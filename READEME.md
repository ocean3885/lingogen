# 🚀 LingoGen (Language Generation Engine)

LingoGen은 LLM(Gemini)과 NLP(spaCy) 기술을 결합하여 고품질의 스페인어 학습 데이터를 자동으로 생성하고 데이터베이스(Supabase)에 정교하게 적재하는 자동화 엔진입니다.

## 🌟 핵심 기능

1.  **AI 컨텐츠 생성**: Gemini API를 통해 특정 주제에 최적화된 번들 제목, 설명, 단어 리스트, 예문을 생성합니다.
2.  **지능형 언어 분석**: spaCy(`es_core_news_lg`)를 사용하여 생성된 모든 문장을 형태소 분석하고 원형(Lemma) 및 문법 정보(Morphology)를 추출합니다.
3.  **데이터 스노우볼링**: 예문에 포함된 주요 품사(명사, 동사 등)를 자동으로 추출하여 `words` 테이블에 Upsert 처리함으로써 학습 DB를 자동으로 확장합니다.
4.  **자동화 파이프라인**: API 호출 한 번으로 [생성 -> 분석 -> DB 적재]의 전 과정을 수행합니다.

## 🛠 기술 스택

-   **Backend**: FastAPI (Python)
-   **AI/NLP**: Google Gemini API, spaCy (es_core_news_lg)
-   **Database**: Supabase (PostgreSQL)
-   **Validation**: Pydantic v2 / Settings

## ⚙️ 설치 및 설정

### 1. 가상환경 설정 및 패키지 설치
```bash
# 가상환경 활성화 (이미 되어 있다면 생략)
source .venv/bin/activate

# 의존성 패키지 설치
pip install -r requirements.txt

# 스페인어 언어 모델 다운로드
python -m spacy download es_core_news_lg


uvicorn main:app --reload
