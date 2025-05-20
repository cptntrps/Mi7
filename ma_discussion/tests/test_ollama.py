"""Tests for the Ollama service."""

import json
import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException

from ma_discussion.services.ollama import OllamaService
from ma_discussion.services.settings import ServiceSettings

@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return ServiceSettings(
        ollama_url="http://test-ollama:11434",
        ollama_model="test-model",
        ollama_timeout=30,
        ollama_models=["model1", "model2"]
    )

@pytest.fixture
def ollama_service(mock_settings):
    """Create an Ollama service instance with mock settings."""
    return OllamaService(settings=mock_settings)

def test_initialization():
    """Test Ollama service initialization."""
    service = OllamaService()
    assert service.base_url is not None
    assert service.timeout > 0

def test_initialization_with_settings(mock_settings):
    """Test Ollama service initialization with custom settings."""
    service = OllamaService(settings=mock_settings)
    assert service.base_url == "http://test-ollama:11434/"
    assert service.timeout == 30

@patch("requests.post")
def test_generate_text(mock_post, ollama_service):
    """Test text generation."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Generated text"}
    mock_post.return_value = mock_response

    result = ollama_service.generate_text("Test prompt")
    assert result == "Generated text"
    mock_post.assert_called_once()

@patch("requests.post")
def test_generate_text_with_model_override(mock_post, ollama_service):
    """Test text generation with model override."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Generated text"}
    mock_post.return_value = mock_response

    result = ollama_service.generate_text("Test prompt", model="custom-model")
    assert result == "Generated text"
    mock_post.assert_called_once()
    assert mock_post.call_args[1]["json"]["model"] == "custom-model"

@patch("requests.post")
def test_generate_text_error(mock_post, ollama_service):
    """Test error handling in text generation."""
    mock_post.side_effect = RequestException("API error")
    
    with pytest.raises(RequestException):
        ollama_service.generate_text("Test prompt")

@patch("requests.post")
def test_stream_text(mock_post, ollama_service):
    """Test text streaming."""
    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_response.iter_lines.return_value = [
        json.dumps({"response": "Hello"}).encode(),
        json.dumps({"response": " world"}).encode()
    ]
    mock_post.return_value = mock_response

    tokens = []
    def on_token(token):
        tokens.append(token)

    result = ollama_service.stream_text("Test prompt", on_token=on_token)
    assert result == "Hello world"
    assert tokens == ["Hello", " world"]
    mock_post.assert_called_once()

@patch("requests.post")
def test_stream_text_error(mock_post, ollama_service):
    """Test error handling in text streaming."""
    mock_post.side_effect = RequestException("API error")
    
    with pytest.raises(RequestException):
        ollama_service.stream_text("Test prompt")

@patch("requests.get")
def test_get_available_models(mock_get, ollama_service):
    """Test fetching available models."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "models": [
            {"name": "model1"},
            {"name": "model2"}
        ]
    }
    mock_get.return_value = mock_response

    result = ollama_service.get_available_models()
    assert result == ["model1", "model2"]
    mock_get.assert_called_once()

@patch("requests.get")
def test_get_available_models_error(mock_get, ollama_service):
    """Test error handling when fetching models."""
    mock_get.side_effect = RequestException("API error")
    
    result = ollama_service.get_available_models()
    assert result == ["model1", "model2"]  # Should fall back to default models

@patch("requests.get")
def test_get_available_models_empty_response(mock_get, ollama_service):
    """Test handling empty response when fetching models."""
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    result = ollama_service.get_available_models()
    assert result == []  # Should return empty list for empty response 