"""Tests for the base agent class."""

import pytest
from unittest.mock import Mock, patch
from ma_discussion.agents.base import CustomAgent
from ma_discussion.services.ollama import OllamaService
from ma_discussion.services.wikipedia import WikipediaService
from ma_discussion.services.settings import ServiceSettings

@pytest.fixture
def settings():
    """Create test settings with proper user agent."""
    return ServiceSettings(
        wikipedia_user_agent="MultiAgentDiscussionSystem/0.1 (Test Suite; https://github.com/yourusername/ma_discussion)",
        wikipedia_language="en"
    )

@pytest.fixture
def wikipedia_service(settings):
    """Create a real Wikipedia service instance."""
    return WikipediaService(settings=settings)

@pytest.fixture
def mock_wikipedia():
    wiki = Mock(spec=WikipediaService)
    wiki.get_summary.return_value = "Mock wiki summary"
    return wiki

@pytest.fixture
def mock_ollama():
    ollama = Mock(spec=OllamaService)
    ollama.stream_text.return_value = "Mock streaming response"
    ollama.generate_text.return_value = "Mock response"
    return ollama

@pytest.fixture
def mock_agent(mock_wikipedia, mock_ollama):
    agent = CustomAgent(
        name="Test Agent",
        role="Test Role",
        base_prompt="Test prompt",
        ollama_service=mock_ollama,
        wikipedia_service=mock_wikipedia
    )
    return agent

def test_agent_initialization(settings):
    """Test agent initialization with required parameters."""
    agent = CustomAgent(
        name="TestAgent",
        role="tester",
        base_prompt="You are a test agent.",
        model="llama2"
    )
    assert agent.name == "TestAgent"
    assert agent.role == "tester"
    assert agent.base_prompt == "You are a test agent."
    assert agent.model == "llama2"
    assert agent.conversation_history == []
    assert agent.thinking == ""

def test_agent_format_message(agent):
    """Test message formatting."""
    message = agent.format_message("Hello")
    assert message == {"role": "assistant", "content": "Hello"}

def test_agent_generate_response(agent):
    """Test agent's ability to generate responses."""
    conversation = [{"role": "user", "content": "Hello"}]
    topic = "Test topic"
    response = agent.generate_response(conversation, topic)
    assert isinstance(response, str)
    assert len(response) > 0

def test_agent_process_conversation(agent):
    """Test agent's conversation processing."""
    conversation = [{"role": "user", "content": "Hello"}]
    topic = "Test topic"
    response = agent.process_conversation(conversation, topic)
    assert isinstance(response, str)
    assert len(response) > 0

def test_invalid_agent_initialization():
    """Test that invalid initialization raises appropriate errors."""
    with pytest.raises(ValueError):
        CustomAgent(name="", role="tester", base_prompt="You are a test agent.", model="llama2")
    with pytest.raises(ValueError):
        CustomAgent(name="TestAgent", role="", base_prompt="You are a test agent.", model="llama2")
    with pytest.raises(ValueError):
        CustomAgent(name="TestAgent", role="tester", base_prompt="", model="llama2")
    with pytest.raises(ValueError):
        CustomAgent(name="TestAgent", role="tester", base_prompt="You are a test agent.", model="")

def test_agent_equality(agent):
    """Test agent equality comparison."""
    agent2 = CustomAgent(
        name="TestAgent",
        role="tester",
        base_prompt="You are a test agent.",
        model="llama2",
        ollama_service=agent.ollama,
        wikipedia_service=agent.wikipedia
    )
    agent3 = CustomAgent(
        name="DifferentAgent",
        role="tester",
        base_prompt="You are a test agent.",
        model="llama2",
        ollama_service=agent.ollama,
        wikipedia_service=agent.wikipedia
    )
    assert agent == agent2
    assert agent != agent3
    assert agent != "not an agent"

def test_agent_string_representation(agent):
    """Test string representation of agent."""
    expected_str = "TestAgent (tester) - llama2"
    assert str(agent) == expected_str

def test_streaming_respond(agent):
    """Test streaming response generation."""
    result = agent.streaming_respond("Test topic", {"key": "value"})
    assert isinstance(result, str)
    assert len(result) > 0

def test_streaming_respond_with_wiki_lookup(agent):
    """Test streaming response with Wikipedia lookup."""
    agent.thinking = "Let me check [[Python programming]]"
    result = agent.streaming_respond("Test topic")
    assert isinstance(result, str)
    assert len(result) > 0

def test_streaming_respond_error(agent):
    """Test error handling in streaming response."""
    # Simulate error by using an invalid model
    agent.model = "invalid_model"
    result = agent.streaming_respond("Test topic")
    assert "I encountered an error while processing" in result

def test_add_to_history(agent):
    """Test adding message to conversation history."""
    agent.add_to_history("User", "Test message")
    assert len(agent.conversation_history) == 1
    assert agent.conversation_history[0]["sender"] == "User"
    assert agent.conversation_history[0]["message"] == "Test message"

def test_add_to_history_multiple(agent):
    """Test adding multiple messages to conversation history."""
    agent.add_to_history("User", "First message")
    agent.add_to_history("Agent", "Second message")
    assert len(agent.conversation_history) == 2
    assert agent.conversation_history[0]["sender"] == "User"
    assert agent.conversation_history[1]["sender"] == "Agent"

def test_think_error(agent):
    """Test error handling in think method."""
    # Simulate error by using an invalid model
    agent.model = "invalid_model"
    result = agent.think("Test topic")
    assert "I encountered an error while processing" in result

def test_respond_error(agent):
    """Test error handling in respond method."""
    # Simulate error by using an invalid model
    agent.model = "invalid_model"
    result = agent.respond("Test topic")
    assert "I encountered an error while processing" in result

def test_add_to_history_error(agent):
    """Test error handling in add_to_history method."""
    # Simulate a list that can't be appended to
    agent.conversation_history = None
    with pytest.raises(AttributeError):
        agent.add_to_history("Test", "Test message")

def test_streaming_respond_error_with_callback(agent):
    """Test error handling in streaming_respond with callback."""
    # Simulate error by using an invalid model
    agent.model = "invalid_model"
    callback = lambda x: None
    result = agent.streaming_respond("Test topic", on_token=callback)
    assert "I encountered an error while processing" in result 