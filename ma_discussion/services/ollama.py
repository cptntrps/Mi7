"""Wrapper service for Ollama API interactions."""

import json
import logging
from typing import Optional, Generator, Callable
import requests
from requests.exceptions import RequestException

from ma_discussion.constants import OLLAMA_GENERATE_ENDPOINT, OLLAMA_TAGS_ENDPOINT
from ma_discussion.services.settings import ServiceSettings, get_settings

logger = logging.getLogger(__name__)

class OllamaService:
    """Service class for interacting with Ollama API."""
    
    def __init__(self, settings: Optional[ServiceSettings] = None):
        """Initialize the Ollama service with optional settings."""
        self.settings = settings or get_settings()
        self.base_url = str(self.settings.ollama_url)
        self.timeout = self.settings.ollama_timeout
    
    def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text using Ollama's completion endpoint.
        
        Args:
            prompt: The input prompt for text generation
            model: Optional model override, defaults to settings.ollama_model
            
        Returns:
            Generated text response
            
        Raises:
            RequestException: If the API request fails
        """
        model = model or self.settings.ollama_model
        url = f"{self.base_url}{OLLAMA_GENERATE_ENDPOINT}"
        
        try:
            response = requests.post(
                url,
                json={"model": model, "prompt": prompt},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["response"]
        except RequestException as e:
            logger.error(f"Ollama API request failed: {str(e)}")
            raise
    
    def stream_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        on_token: Optional[Callable[[str], None]] = None
    ) -> str:
        """Stream text generation from Ollama with optional token callback.
        
        Args:
            prompt: The input prompt for text generation
            model: Optional model override
            on_token: Optional callback function for token streaming
            
        Returns:
            Complete generated text
            
        Raises:
            RequestException: If the API request fails
        """
        model = model or self.settings.ollama_model
        url = f"{self.base_url}{OLLAMA_GENERATE_ENDPOINT}"
        full_response = ""
        
        try:
            with requests.post(
                url,
                json={"model": model, "prompt": prompt, "stream": True},
                timeout=self.timeout,
                stream=True
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            full_response += token
                            if on_token:
                                on_token(token)
            return full_response
        except RequestException as e:
            logger.error(f"Ollama streaming request failed: {str(e)}")
            raise
    
    def get_available_models(self) -> list[str]:
        """Get list of available models from Ollama.
        
        Returns:
            List of model names
            
        Raises:
            RequestException: If the API request fails
        """
        url = f"{self.base_url}{OLLAMA_TAGS_ENDPOINT}"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except RequestException as e:
            logger.error(f"Failed to fetch Ollama models: {str(e)}")
            return self.settings.ollama_models  # Fall back to default models 