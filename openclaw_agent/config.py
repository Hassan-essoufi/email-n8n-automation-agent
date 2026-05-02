from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str 

    google_credentials_path: str
    google_token_path: str

    openclaw_url: str = 'http://localhost:18789'
    openclaw_secret: str
    
    spreadsheet_id: str
    
    model_config= SettingsConfigDict(env_file='.env',
                                    env_file_encoding="utf-8")
    
    
settings = Settings()

