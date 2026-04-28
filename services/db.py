from supabase import create_client, Client
from config import settings
from schemas.models import GeneratedBundle

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

async def save_bundle_pipeline(category_id: int, bundle_data: GeneratedBundle):
    try:
        # 1. Bundle 생성
        bundle_res = supabase.table("bundle").insert({
            "category_id": category_id,
            "title": bundle_data.title,
            "description": bundle_data.description
        }).execute()
        bundle_id = bundle_res.data[0]["id"]

        # 2. 종합 단어 정보 일괄 Upsert
        words_to_upsert = [
            {
                "word": w.word,
                "lang_code": "es",
                "pos": w.pos,
                "meaning": w.meaning,
                "conjugations": w.conjugations,
                "declensions": w.declensions
            }
            for w in bundle_data.words
        ]
        if words_to_upsert:
            supabase.table("words").upsert(words_to_upsert, on_conflict="word,lang_code").execute()

        # 3. 문장 일괄 저장
        sentences_to_insert = [
            {"sentence": s.sentence, "translation": s.translation}
            for s in bundle_data.sentences
        ]
        s_res = supabase.table("sentences").insert(sentences_to_insert).execute()
        
        # 4. Bundle-Sentence 연결 (BundleItems)
        bundle_items = [
            {"bundle_id": bundle_id, "sentence_id": row["id"], "order_index": i}
            for i, row in enumerate(s_res.data)
        ]
        if bundle_items:
            supabase.table("bundle_items").insert(bundle_items).execute()

        return bundle_id
    except Exception as e:
        raise e
