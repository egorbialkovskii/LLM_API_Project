from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(validation_alias="APP_NAME")
    env: str = Field(validation_alias="ENV")
    cors_enabled: bool = Field(default=False, validation_alias="CORS_ENABLED")
    cors_allow_origins: str = Field(default="", validation_alias="CORS_ALLOW_ORIGINS")

    jwt_secret: SecretStr = Field(validation_alias="JWT_SECRET")
    jwt_alg: str = Field(validation_alias="JWT_ALG")
    access_token_expire_minutes: int = Field(
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    sqlite_path: str = Field(validation_alias="SQLITE_PATH")

    openrouter_api_key: SecretStr = Field(validation_alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(validation_alias="OPENROUTER_BASE_URL")
    openrouter_model: str = Field(validation_alias="OPENROUTER_MODEL")
    openrouter_referer: str = Field(validation_alias="OPENROUTER_SITE_URL")
    openrouter_title: str = Field(validation_alias="OPENROUTER_APP_NAME")


settings = Settings()
