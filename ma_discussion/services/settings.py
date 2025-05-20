"""Service settings configuration using Pydantic."""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, HttpUrl

from ma_discussion.constants import (
    OLLAMA_BASE_URL,
    DEFAULT_MODEL,
    REQUEST_TIMEOUT,
    WIKIPEDIA_USER_AGENT,
)

class ServiceSettings(BaseSettings):
    """Settings for external services used by the application."""
    
    # Ollama settings
    ollama_url: HttpUrl = Field(default=OLLAMA_BASE_URL)
    ollama_timeout: int = Field(default=REQUEST_TIMEOUT)
    ollama_model: str = Field(default=DEFAULT_MODEL)
    ollama_models: List[str] = Field(default=[DEFAULT_MODEL])
    
    # Wikipedia settings
    wikipedia_user_agent: str = Field(default=WIKIPEDIA_USER_AGENT)
    wikipedia_language: str = Field(default="en")
    wikipedia_timeout: int = Field(default=REQUEST_TIMEOUT)
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "MADISC_"  # Environment variables will be prefixed with MADISC_
        case_sensitive = False
        
def get_settings() -> ServiceSettings:
    """Get service settings, optionally from environment variables."""
    return ServiceSettings() 