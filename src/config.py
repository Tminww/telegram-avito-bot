# config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

class Settings(BaseSettings):
    # Telegram Bot Token
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")

    # Database settings
    db_host: str = Field(..., env="DB_HOST")
    db_port: int = Field(..., env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")
    db_user: str = Field(..., env="DB_USER")
    db_pass: str = Field(..., env="DB_PASS")

    # Создаем динамически собранный DATABASE_URL
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = "src/.env"

# Экземпляр класса с конфигурацией для использования в других модулях
settings = Settings()
