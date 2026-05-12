from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "BHIV Intelligence Data Universe Registry"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://bhiv:bhiv_secret@localhost:5432/bhiv_registry"
    REGISTRY_ID: str = "BHIV-IDU-REGISTRY-V1"
    TANTRA_ECOSYSTEM_VERSION: str = "V1"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()