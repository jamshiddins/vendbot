"""Настройки приложения VendBot"""
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Класс настроек приложения"""
    
    # Application Settings
    app_name: str = Field(default="VendBot", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    secret_key: str = Field(default="your-secret-key-here", alias="SECRET_KEY")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # Database Configuration
    database_url: str = Field(default="sqlite+aiosqlite:///./vendbot.db", alias="DATABASE_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")
    database_pool_size: int = Field(default=5, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, alias="DATABASE_MAX_OVERFLOW")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_password: str = Field(default="", alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    
    # Telegram Bot Configuration
    bot_token: str = Field(default="YOUR_BOT_TOKEN_HERE", alias="BOT_TOKEN")
    telegram_bot_token: str = Field(default="YOUR_BOT_TOKEN_HERE", alias="TELEGRAM_BOT_TOKEN")
    webhook_url: str = Field(default="", alias="WEBHOOK_URL")
    webhook_path: str = Field(default="/webhook", alias="WEBHOOK_PATH")
    webhook_secret: str = Field(default="", alias="WEBHOOK_SECRET")
    bot_parse_mode: str = Field(default="HTML", alias="BOT_PARSE_MODE")
    bot_disable_web_page_preview: bool = Field(default=True, alias="BOT_DISABLE_WEB_PAGE_PREVIEW")
    
    # Security Configuration
    jwt_secret_key: str = Field(default="dev-jwt-secret-key", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=1440, alias="JWT_EXPIRE_MINUTES")
    
    # File Storage Configuration
    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")
    upload_max_size: int = Field(default=10485760, alias="UPLOAD_MAX_SIZE")
    photos_dir: str = Field(default="./uploads/photos", alias="PHOTOS_DIR")
    photos_max_size: int = Field(default=5242880, alias="PHOTOS_MAX_SIZE")
    photos_quality: int = Field(default=85, alias="PHOTOS_QUALITY")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="./logs/vendbot.log", alias="LOG_FILE")
    log_json: bool = Field(default=False, alias="LOG_JSON")
    log_correlation_id: bool = Field(default=True, alias="LOG_CORRELATION_ID")
    
    # Business Logic Configuration
    min_stock_threshold: int = Field(default=100, alias="MIN_STOCK_THRESHOLD")
    critical_stock_threshold: int = Field(default=50, alias="CRITICAL_STOCK_THRESHOLD")
    auto_reorder_enabled: bool = Field(default=False, alias="AUTO_REORDER_ENABLED")
    operation_timeout: int = Field(default=30, alias="OPERATION_TIMEOUT")
    work_start_time: str = Field(default="08:00", alias="WORK_START_TIME")
    work_end_time: str = Field(default="20:00", alias="WORK_END_TIME")
    timezone: str = Field(default="Asia/Tashkent", alias="TIMEZONE")
    
    # Development Settings
    hot_reload: bool = Field(default=True, alias="HOT_RELOAD")
    debug_toolbar: bool = Field(default=True, alias="DEBUG_TOOLBAR")
    debug_sql: bool = Field(default=False, alias="DEBUG_SQL")
    seed_test_data: bool = Field(default=True, alias="SEED_TEST_DATA")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Разрешаем дополнительные поля
        extra = "ignore"
    
    @property
    def BOT_TOKEN(self) -> str:
        """Возвращает токен бота (для обратной совместимости)"""
        return self.telegram_bot_token or self.bot_token
    
    @property
    def is_development(self) -> bool:
        """Проверяет режим разработки"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Проверяет продакшн режим"""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки приложения (кешируется)"""
    return Settings()


# Создание глобального экземпляра настроек
settings = get_settings()