import asyncio
import json
import os
from dotenv import load_dotenv
from services.generator import generate_words_distractor_deepseek

# .env.local 로드
load_dotenv(dotenv_path=".env.local")

async def test_distractors():
    test_words = ["hablar", "casa", "derecho"]
    print("--- Distractor Generation Test ---")
    
    for word in test_words:
        print(f"\nTarget Word: {word}")
        distractors = await generate_words_distractor_deepseek(word)
        print(json.dumps(distractors, indent=2, ensure_ascii=False))
        
        if len(distractors) == 3:
            print("✅ Success: Generated 3 distractors.")
        else:
            print(f"⚠️ Warning: Generated {len(distractors)} distractors.")

if __name__ == "__main__":
    asyncio.run(test_distractors())
