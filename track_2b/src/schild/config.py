import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_MODEL = "swiss-ai/Apertus-v1.5-8B"


@dataclass(frozen=True)
class Settings:
    llm_base_url: str | None
    llm_api_key: str | None
    llm_name: str
    llm_timeout: float
    upstream_base_url: str | None
    upstream_api_key: str | None
    upstream_model: str | None
    sensitive_pass: bool = True


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if env is None else env

    def get(name: str) -> str | None:
        value = (env.get(name) or "").strip()
        return value or None

    return Settings(
        llm_base_url=get("LLM_BASE_URL"),
        llm_api_key=get("LLM_API_KEY"),
        llm_name=get("LLM_NAME") or DEFAULT_MODEL,
        llm_timeout=float(get("LLM_TIMEOUT") or 120),
        upstream_base_url=get("UPSTREAM_BASE_URL"),
        upstream_api_key=get("UPSTREAM_API_KEY"),
        upstream_model=get("UPSTREAM_MODEL"),
        sensitive_pass=get("SCHILD_SENSITIVE_PASS") != "0",
    )
