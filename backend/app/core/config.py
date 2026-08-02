from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "AI Enterprise Chatbot"
    APP_VERSION: str = "0.1.0"
    

    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "chatbot"
    POSTGRES_USER: str = "chatbot_app"
    POSTGRES_PASSWORD: str = "changeme"
    READONLY_POSTGRES_USER: str
    READONLY_POSTGRES_PASSWORD: str
    GROQ_API_KEY: str
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def READONLY_DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://{self.READONLY_POSTGRES_USER}:"
            f"{self.READONLY_POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    UPLOAD_DIR: str = "storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50


settings = Settings()