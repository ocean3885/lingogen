import asyncio
import json
import os
from typing import Dict, Any
import httpx
from dotenv import load_dotenv

# Load .env.local
load_dotenv(dotenv_path=".env.local")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

async def generate_word_info_deepseek(word: str) -> dict:
    """
    DEEPSEEK API를 사용하여 단어 정보를 생성합니다. (기존 generator.py의 prompt 활용)
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
word: 반드시 스페인어 사전적 원형(Lemma)을 적습니다. (예: 'fui' 입력 시 'ir', 'casas' 입력 시 'casa')
pos: 리스트 형식으로 품사를 지정합니다 (예: ["VERB"], ["NOUN", "ADJ"]).
meaning: 품사를 키로 하는 사전형 정의를 제공합니다.
gender: 성별을 나타냅니다. 남성은 "m", 여성은 "f", 공통은 "mf", 해당 없으면 null을 사용합니다.
conjugations: 동사(VERB)인 경우에만 포함합니다. pres, pret, impf, futr, cond, perf 6개 키와 각 시제 내부의 s1, s2, s3, p1, p2, p3 키를 누락 없이 작성합니다.
declensions: 명사나 형용사인 경우에만 포함합니다. ms, mp, fs, fp 키를 사용합니다.

4. 제약 사항 (Constraints)
사용자가 어떤 활용형을 입력하더라도 'word' 필드에는 반드시 그 단어의 사전적 기본형을 반환해야 합니다.
만약 제시된 단어가 스페인어가 아니거나, 존재하지 않는 무의미한 단어인 경우 모든 필드를 null로 채우거나 {{"error": "invalid_word"}}와 같은 약속된 에러 구조를 반환하세요.
지어내지 마세요(Do not hallucinate). 모르는 단어라면 솔직하게 데이터가 없음을 나타내야 합니다.
존재하지 않는 키를 만들지 마세요.
JSON 문법(쉼표, 중괄호 등) 오류가 없어야 합니다.
    """

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "당신은 스페인어 교육 전문가입니다. 모든 응답은 약속된 JSON 구조와 콤팩트 키값을 엄격히 준수해야 합니다."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            return json.loads(content)
    except Exception as e:
        print(f"Error for {word}: {e}")
        return {"error": str(e)}

def score_result(word: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    결과물의 품질을 채점합니다.
    """
    scores = {
        "json_validity": 0,
        "required_fields": 0,
        "content_accuracy": 0,
        "format_compliance": 0,
        "total": 0
    }
    details = []

    # 1. JSON Validity (Already parsed if we are here, but double check error)
    if "error" not in data:
        scores["json_validity"] = 25
    else:
        details.append("JSON 파싱 실패 또는 API 에러")
        return {"total_score": 0, "details": details}

    # 2. Required Fields (word, pos, meaning, gender)
    required = ["word", "pos", "meaning", "gender"]
    missing = [f for f in required if f not in data]
    if not missing:
        scores["required_fields"] = 25
    else:
        scores["required_fields"] = max(0, 25 - (len(missing) * 5))
        details.append(f"누락된 필드: {missing}")

    # 3. Content Accuracy (Simple check)
    is_verb = "VERB" in data.get("pos", [])
    is_noun_adj = any(p in ["NOUN", "ADJ"] for p in data.get("pos", []))
    
    acc_score = 25
    if is_verb and "conjugations" not in data:
        acc_score -= 10
        details.append("동사인데 conjugations 필드 누락")
    if is_noun_adj and "declensions" not in data:
        acc_score -= 10
        details.append("명사/형용사인데 declensions 필드 누락")
    
    # Check conjugation keys if verb
    if is_verb and "conjugations" in data:
        c = data["conjugations"]
        missing_tenses = [t for t in ["pres", "pret", "impf", "futr", "cond", "perf"] if t not in c]
        if missing_tenses:
            acc_score -= 10
            details.append(f"누락된 시제: {missing_tenses}")
            
    scores["content_accuracy"] = max(0, acc_score)

    # 4. Format Compliance (gender values, pos format etc)
    fmt_score = 25
    if data.get("gender") not in ["m", "f", "mf", None]:
        fmt_score -= 10
        details.append(f"잘못된 gender 값: {data.get('gender')}")
    if not isinstance(data.get("pos"), list):
        fmt_score -= 10
        details.append("pos 필드가 리스트 형식이 아님")
        
    scores["format_compliance"] = max(0, fmt_score)

    scores["total"] = sum([scores["json_validity"], scores["required_fields"], scores["content_accuracy"], scores["format_compliance"]])
    
    return {
        "word": word,
        "total_score": scores["total"],
        "breakdown": scores,
        "details": details,
        "raw_data": data
    }

async def main():
    # 원형 추출 및 품질 테스트를 위한 더 어려운 단어 5개 추가
    # 1. 재귀 동사 과거형 (me arrepentí -> arrepentirse)
    # 2. 불규칙 과거분사 여성 복수형 (dichas -> decir)
    # 3. 매우 짧고 불규칙한 형태 (sepa -> saber)
    # 4. 미래 완료형 (habré 출력 형태 확인)
    # 5. 복합 형태 또는 극도의 불규칙 (puesto -> poner)
    test_words = ["me arrepentí", "dichas", "sepa", "habré", "puesto"]
    print(f"--- DeepSeek API Extreme Lemma Test (Words: {test_words}) ---")
    
    results = []
    for word in test_words:
        print(f"Testing '{word}'...")
        data = await generate_word_info_deepseek(word)
        scored = score_result(word, data)
        results.append(scored)
        
    print("\n=== TEST RESULTS SUMMARY ===")
    for r in results:
        print(f"Word: {r['word']} | Score: {r['total_score']}/100")
        if r['details']:
            print(f"  - Issues: {r['details']}")
    
    avg_score = sum(r['total_score'] for r in results) / len(results)
    print(f"\nAverage Score: {avg_score:.2f}/100")
    
    # Save results to a file for review
    with open("scratch/deepseek_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nDetailed results saved to scratch/deepseek_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())
