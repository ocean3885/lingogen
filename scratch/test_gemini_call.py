import asyncio
import os
import sys

# 프로젝트 루트 경로를 sys.path에 추가하여 모듈 로딩 가능하게 설정
sys.path.append(os.getcwd())

async def test_llm_call():
    print("=== Gemini API 호출 테스트 시작 ===")
    try:
        from services.generator import generate_word_info
        from config import settings
        
        test_word = "ver"
        print(f"테스트 단어: '{test_word}'")
        print(f"사용 중인 API Key: {settings.gemini_api_key[:10]}...")
        
        print(f"'{test_word}' 정보 추출 중 (결과를 기다리는 중)...")
        result = await generate_word_info(test_word)
        
        print("\n=== 테스트 결과 ===")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get("meaning"):
            print("\n✅ 성공: LLM으로부터 의미를 정상적으로 받아왔습니다.")
        else:
            print("\n❌ 실패: LLM으로부터 의미를 받아오지 못했습니다. (빈 데이터)")
            
    except Exception as e:
        print(f"\n❌ 시스템 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_call())
