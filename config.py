import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class APIKeys(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, env_file_encoding="utf-8"
    )
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str


class MainSettings(YamlBaseSettings):
    model_config = SettingsConfigDict(
        yaml_file="settings.yaml",
        yaml_file_encoding="utf-8",
        yaml_config_section="main",
    )
    OUTPUT_DIR: str
    MODEL_NAME: str
    FILE_EXTENSION: str
    OPENAI_ENDPOINT: str
    TIKTOKEN_CACHE_DIR: str
    OPENAI_MAX_TOKENS: int


class Settings(BaseSettings):
    api_keys: APIKeys = Field(default_factory=APIKeys)  # type: ignore
    main: MainSettings = Field(default_factory=MainSettings)  # type: ignore

    @classmethod
    def load(cls, yaml_path: str = "settings.yaml") -> "Settings":
        with open(yaml_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        return cls(api_keys=APIKeys(), main=MainSettings(**config_data["main"]))  # type: ignore


# Глобальный экземпляр настроек
cfg = Settings.load()
