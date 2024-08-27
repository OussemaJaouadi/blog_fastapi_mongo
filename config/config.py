from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str
    DB_NAME: str
    JWT_SECRET: str
    ALGORITHM: str
    DB_USER: str
    DB_PASS: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()

