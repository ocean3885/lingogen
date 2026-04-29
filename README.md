# 🚀 LingoGen (Language Generation Engine)

LingoGen은 LLM(Gemini), NLP(spaCy), 그리고 TTS 기술을 결합하여 고품질의 스페인어 학습 데이터를 자동으로 처리하고 데이터베이스(Supabase)에 정교하게 적재하는 백엔드 엔진입니다.

## 🌟 핵심 기능

1.  **자동화된 데이터 파이프라인**: 문장과 번역문을 입력받아 [TTS 생성 -> 언어 분석 -> DB 적재] 과정을 한 번에 수행합니다.
2.  **지능형 언어 분석**: spaCy(`es_core_news_lg`)를 사용하여 문장을 형태소 분석하고, 단어의 원형(Lemma) 및 상세 문법 정보(Morphology)를 추출합니다.
3.  **AI 기반 단어 정보 확장**: 새로운 단어가 발견되면 Gemini API를 통해 해당 단어의 성/수 변화, 시제 변화(동사), 의미 등을 자동으로 추출하여 사전 데이터를 구축합니다.
4.  **멀티미디어 통합**: `gTTS`를 활용해 문장 및 단어별 음성 파일을 자동 생성하고 Supabase Storage에 업로드하여 학습 리소스를 완성합니다.
5.  **효율적인 데이터 매핑**: 문장과 단어 간의 관계를 `word_sentence_map` 테이블을 통해 체계적으로 관리합니다.

## 🛠 기술 스택

-   **Backend**: FastAPI (Python)
-   **AI/NLP**: Google Gemini Pro (Generative AI), spaCy (es_core_news_lg)
-   **TTS**: gTTS (Google Text-to-Speech)
-   **Database**: Supabase (PostgreSQL, Storage)
-   **Environment**: Pydantic Settings (v2)

## ⚙️ 설치 및 설정

### 1. 가상환경 설정 및 패키지 설치
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate

# 의존성 패키지 설치
pip install -r requirements.txt

# 스페인어 언어 모델 다운로드
python -m spacy download es_core_news_lg
```

### 2. 환경 변수 설정
`.env.local` 파일을 프로젝트 루트에 생성하고 아래 항목을 입력합니다.
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
DATABASE_URL=your_database_url
GEMINI_API_KEY=your_gemini_api_key
```

### 3. 서버 실행
```bash
uvicorn main:app --reload
```

## 🚀 API 사용법

### 1. 문장 일괄 저장 (Pipeline 실행)
여러 개의 스페인어 문장과 번역을 전달하여 전체 프로세스(TTS, 분석, 저장)를 실행합니다.

**Endpoint**: `POST /store-sentences`

**Request Body**:
```json
{
  "items": [
    {
      "sentence": "La mujer lee un libro interesante.",
      "translation": "그 여자는 흥미로운 책을 읽는다."
    }
  ]
}
```

**Response**:
```json
{
  "results": [
    {
      "sentence": "La mujer lee un libro interesante.",
      "status": "success",
      "sentence_id": 123
    }
  ]
}
```

## 📂 프로젝트 구조

- `main.py`: FastAPI 앱 정의 및 엔드포인트 구성
- `services/`: 핵심 비즈니스 로직
    - `pipeline.py`: 문장 처리 전체 프로세스 오케스트레이션
    - `analyzer.py`: spaCy 기반 형태소 분석
    - `generator.py`: Gemini 기반 단어 문법 정보 추출
    - `tts.py`: 음성 생성 및 Supabase 업로드
    - `db.py`: Supabase 클라이언트 및 DB 인터페이스
- `schemas/`: Pydantic 데이터 모델 (Request/Response, DB 모델)
- `config.py`: 환경 변수 및 설정 관리
