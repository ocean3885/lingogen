import google.generativeai as genai
import json
from config import settings

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="당신은 스페인어 교육 전문가입니다. 모든 응답은 약속된 JSON 구조와 콤팩트 키값을 엄격히 준수해야 합니다."
)

async def generate_word_info(word: str) -> dict:
    """
    단어의 품사, 뜻, 성별, 시제/성수 변화 등 상세 문법 정보를 Gemini API를 통해 가져옵니다.
    """
    prompt = f"""
1. 역할 정의 (Persona)
당신은 전문 스페인어 언어학자이자 교육용 콘텐츠 데이터 설계자입니다. 사용자가 스페인어 단어(Topic)를 제시하면, 이를 기반으로 스페인어 학습을 위한 상세 단어 데이터를 생성합니다. 당신의 출력물은 FastAPI 서버를 거쳐 관계형 데이터베이스(Supabase)에 저장되므로, 데이터의 무결성과 형식 준수가 무엇보다 중요합니다.

현재 분석할 단어(Topic): '{word}'

2. 출력 규칙 (Strict Output Rules)
형식: 반드시 순수한 JSON 코드 블록 하나만 출력하세요. 인사말이나 부연 설명은 절대 금지합니다.
언어: 단어 뜻은 한국어로 작성합니다.
무결성: 모든 동사는 지정된 6개 시제 변화를 반드시 포함해야 하며, 명사/형용사는 4가지 성수 변화를 포함해야 합니다.

3. 데이터 구조 가이드라인 (Data Structure)
다음 JSON 구조를 엄격히 따르세요:
word: 스페인어 원형(Lemma)을 적습니다.
pos: 리스트 형식으로 품사를 지정합니다 (예: ["VERB"], ["NOUN", "ADJ"]).
meaning: 품사를 키로 하는 사전형 정의를 제공합니다.
gender: 성별을 나타냅니다. 남성은 "m", 여성은 "f", 공통은 "mf", 해당 없으면 null을 사용합니다.
conjugations: 동사(VERB)인 경우에만 포함합니다. pres, pret, impf, futr, cond, perf 6개 키와 각 시제 내부의 s1, s2, s3, p1, p2, p3 키를 누락 없이 작성합니다.
declensions: 명사나 형용사인 경우에만 포함합니다. ms, mp, fs, fp 키를 사용합니다.

4. 제약 사항 (Constraints)
존재하지 않는 키를 만들지 마세요.
JSON 문법(쉼표, 중괄호 등) 오류가 없어야 합니다.
    """
    
    try:
        import json
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
            
        word_data = json.loads(text.strip())
        return word_data
    except Exception as e:
        print(f"단어 정보 생성 실패 ({word}): {e}")
        # 실패 시 기본 구조 반환
        return {
            "word": word,
            "pos": [],
            "meaning": {},
            "gender": None,
            "conjugations": {},
            "declensions": {}
        }
