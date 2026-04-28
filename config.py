from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # .env.local의 변수명과 매핑
    supabase_url: str = Field(..., validation_alias='NEXT_PUBLIC_SUPABASE_URL')
    supabase_key: str = Field(..., validation_alias='NEXT_PUBLIC_SUPABASE_ANON_KEY')
    database_url: str = Field(..., validation_alias='DATABASE_URL')
    
    # .env.local에 추가해야 함 (GEMINI_API_KEY=your_key)
    gemini_api_key: str = Field(..., validation_alias='GEMINI_API_KEY')

    model_config = SettingsConfigDict(
        env_file=".env.local", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
