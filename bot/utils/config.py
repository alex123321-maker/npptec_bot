from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    ADMIN_IDS: list[int] = Field(default=[], env="ADMIN_IDS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
