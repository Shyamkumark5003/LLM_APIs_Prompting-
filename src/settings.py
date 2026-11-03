from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_base_url: str
    llm_api_key: str
    llm_model: str
    llm_fallback_models: str = ""   # "model-b,model-c"
    llm_timeout: float = 30
    llm_max_retries: int = 3

    @property
    def models(self) -> list[str]:
        # main model first, appuram fallback models
        fallbacks = [m.strip() for m in self.llm_fallback_models.split(",") if m.strip()]
        return [self.llm_model] + fallbacks