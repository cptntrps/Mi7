"""Tests for the state management functionality."""

import pytest
from unittest.mock import MagicMock
from ma_discussion.ui.state import AppState
from ma_discussion.agents.base import CustomAgent
from ma_discussion.agents.coordinator import CoordinatorAgent
from ma_discussion.services.wikipedia import WikipediaService
from ma_discussion.services.ollama import OllamaService

@pytest.fixture
def mock_wikipedia_service():
    """Create a mock Wikipedia service."""
    service = MagicMock(spec=WikipediaService)
    return service

@pytest.fixture
def mock_ollama_service():
    """Create a mock Ollama service."""
    service = MagicMock(spec=OllamaService)
    service.generate_text.return_value = "Test response"
    return service

@pytest.fixture
def mock_agent(mock_wikipedia_service, mock_ollama_service):
    """Create a mock agent for testing."""
    return CustomAgent(
        name="Test Agent",
        role="Test Role",
        base_prompt="You are a test agent.",
        model="llama3:latest",
        wikipedia_service=mock_wikipedia_service,
        ollama_service=mock_ollama_service
    )

@pytest.fixture
def mock_coordinator(mock_wikipedia_service, mock_ollama_service):
    """Create a mock coordinator agent for testing."""
    return CoordinatorAgent(
        name="Test Coordinator",
        archetype="facilitator",
        model="llama3:latest",
        wikipedia_service=mock_wikipedia_service,
        ollama_service=mock_ollama_service
    )

def test_app_state_initialization():
    """Test that AppState initializes with default values."""
    state = AppState()
    assert state.agents == []
    assert state.coordinator is None
    assert state.coordinator_archetype == "facilitator"
    assert state.conversation_history == []
    assert state.current_streaming_message == ""
    assert state.last_system_prompt == ""
    assert state.ollama_models == []

def test_add_agent(mock_agent):
    """Test adding an agent to the state."""
    state = AppState()
    state.add_agent(mock_agent)
    assert len(state.agents) == 1
    assert state.agents[0] == mock_agent

def test_add_coordinator(mock_coordinator):
    """Test adding a coordinator to the state."""
    state = AppState()
    state.add_coordinator(mock_coordinator)
    assert state.coordinator == mock_coordinator
    assert state.coordinator_archetype == mock_coordinator.archetype

def test_remove_agent(mock_agent):
    """Test removing an agent from the state."""
    state = AppState()
    state.add_agent(mock_agent)
    state.remove_agent(mock_agent.name)
    assert len(state.agents) == 0

def test_remove_coordinator(mock_coordinator):
    """Test removing a coordinator from the state."""
    state = AppState()
    state.add_coordinator(mock_coordinator)
    state.remove_coordinator()
    assert state.coordinator is None

def test_clear_agents(mock_agent, mock_coordinator):
    """Test clearing all agents from the state."""
    state = AppState()
    state.add_agent(mock_agent)
    state.add_coordinator(mock_coordinator)
    state.clear_agents()
    assert len(state.agents) == 0
    assert state.coordinator is None

def test_add_message():
    """Test adding a message to the conversation history."""
    state = AppState()
    message = {"role": "user", "content": "Test message"}
    state.add_message(message)
    assert len(state.conversation_history) == 1
    assert state.conversation_history[0] == message

def test_clear_conversation():
    """Test clearing the conversation history."""
    state = AppState()
    message = {"role": "user", "content": "Test message"}
    state.add_message(message)
    state.clear_conversation()
    assert len(state.conversation_history) == 0

def test_update_streaming_message():
    """Test updating the streaming message."""
    state = AppState()
    message = "Test streaming message"
    state.update_streaming_message(message)
    assert state.current_streaming_message == message 