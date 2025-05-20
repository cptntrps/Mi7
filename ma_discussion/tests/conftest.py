"""Test configuration and fixtures for ma_discussion tests."""

import pytest
from typing import Dict, List, Optional

from ma_discussion.agents.base import CustomAgent
from ma_discussion.agents.coordinator import CoordinatorAgent
from ma_discussion.ui.state import AppState
from ma_discussion.services.ollama import OllamaService
from ma_discussion.services.settings import ServiceSettings

@pytest.fixture
def settings():
    """Create test settings."""
    return ServiceSettings(
        ollama_url="http://localhost:11434",
        ollama_model="llama2",
        ollama_timeout=30
    )

@pytest.fixture
def ollama_service(settings):
    """Create a real Ollama service instance."""
    return OllamaService(settings=settings)

@pytest.fixture
def agent(ollama_service) -> CustomAgent:
    """Create a real agent for testing."""
    return CustomAgent(
        name="TestAgent",
        role="tester",
        base_prompt="You are a test agent.",
        model="llama2",
        ollama_service=ollama_service
    )

@pytest.fixture
def coordinator(ollama_service) -> CoordinatorAgent:
    """Create a real coordinator agent for testing."""
    return CoordinatorAgent(
        name="Test Coordinator",
        role="Test Coordinator Role",
        archetype="facilitator",
        base_prompt="You are a test coordinator.",
        model="llama2",
        ollama_service=ollama_service
    )

@pytest.fixture
def app_state(ollama_service) -> AppState:
    """Create an application state for testing."""
    state = AppState()
    state.add_agent(CustomAgent(
        name="Test Agent 1",
        role="Test Role 1",
        base_prompt="You are test agent 1.",
        model="llama2",
        ollama_service=ollama_service
    ))
    state.add_agent(CoordinatorAgent(
        name="Test Coordinator",
        role="Test Coordinator Role",
        archetype="facilitator",
        base_prompt="You are a test coordinator.",
        model="llama2",
        ollama_service=ollama_service
    ))
    return state

@pytest.fixture
def conversation_history() -> List[Dict]:
    """Create a conversation history for testing."""
    return [
        {
            "role": "system",
            "content": "Starting discussion on: Test Topic"
        },
        {
            "role": "assistant",
            "content": "This is a test response",
            "avatar": "🤖"
        },
        {
            "role": "user",
            "content": "This is a test user message"
        }
    ] 