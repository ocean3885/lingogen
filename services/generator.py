import google.generativeai as genai
import json
from config import settings
from schemas.models import GeneratedBundle

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="당신은 스페인어 교육 전문가입니다. 모든 응답은 약속된 JSON 구조와 콤팩트 키값을 엄격히 준수해야 합니다."
)

async def generate_content_with_gemini(topic: str) -> GeneratedBundle:
    # 1. 프롬프트는 이제 '무엇을' 만들지에 집중하면 됩니다. '형식'은 스키마가 제어합니다.
    prompt = f"""
    주제: '{topic}'와(과) 관련된 스페인어 학습 번들을 생성하세요.
    
    요구사항:
    - 학습자가 주제와 관련된 어휘를 실용적으로 배울 수 있도록 구성하세요.
    - 동사는 주요 6개 시제 변화를 모두 포함해야 합니다.
    - 예문은 일상 대화에서 자주 쓰이는 자연스러운 문장으로 15개 내외 작성하세요.
    """

    try:
        response = await model.generate_content_async(
            prompt, 
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": GeneratedBundle  # 작성하신 모델 주입
            }
        )
        
        # 2. Pydantic V2의 검증 메서드 활용
        # 모델에 선언된 description과 타입을 기반으로 결과물을 즉시 파싱합니다.
        return GeneratedBundle.model_validate_json(response.text)

    except Exception as e:
        # Pydantic ValidationError 발생 시 상세 내용을 로깅하면 디버깅이 쉽습니다.
        raise ValueError(f"학습 자료 생성 및 검증 실패: {str(e)}")
