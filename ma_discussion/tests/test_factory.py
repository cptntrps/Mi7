"""Tests for the agent factory functionality."""

import pytest
from unittest.mock import MagicMock

from ma_discussion.agents.factory import (
    determine_coordinator_archetype,
    generate_system_prompt,
    generate_task_force,
    create_agent,
    create_coordinator
)
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

def test_create_basic_agent(wikipedia_service):
    """Test creating a basic agent with minimal parameters."""
    agent = create_agent("Test Agent", "Expert", wikipedia_service=wikipedia_service)
    assert agent.name == "Test Agent"
    assert agent.role == "Expert"
    assert agent.model == "llama3:latest"
    assert agent.conversation_history == []

def test_create_agent_with_custom_prompt(wikipedia_service):
    """Test creating an agent with a custom system prompt."""
    custom_prompt = "You are a specialized expert."
    agent = create_agent("Test Agent", "Expert", base_prompt=custom_prompt, wikipedia_service=wikipedia_service)
    assert agent.name == "Test Agent"
    assert agent.role == "Expert"
    assert agent.base_prompt == custom_prompt

def test_create_coordinator(wikipedia_service):
    """Test creating a coordinator agent."""
    coordinator = create_coordinator("Test Coordinator", "facilitator", wikipedia_service=wikipedia_service)
    assert coordinator.name == "Test Coordinator"
    assert coordinator.archetype == "facilitator"
    assert coordinator.model == "llama3:latest"
    assert coordinator.conversation_history == []

def test_create_coordinator_with_custom_prompt(wikipedia_service):
    """Test creating a coordinator with a custom system prompt."""
    custom_prompt = "You are a specialized coordinator."
    coordinator = create_coordinator("Test Coordinator", "facilitator", base_prompt=custom_prompt, wikipedia_service=wikipedia_service)
    assert coordinator.name == "Test Coordinator"
    assert coordinator.archetype == "facilitator"
    assert coordinator.base_prompt == custom_prompt

def test_invalid_agent_parameters(wikipedia_service):
    """Test that creating an agent with invalid parameters raises appropriate errors."""
    with pytest.raises(ValueError):
        create_agent("", "Expert", wikipedia_service=wikipedia_service)
    
    with pytest.raises(ValueError):
        create_agent("Test Agent", "", wikipedia_service=wikipedia_service)

def test_invalid_coordinator_parameters(wikipedia_service):
    """Test that creating a coordinator with invalid parameters raises appropriate errors."""
    with pytest.raises(ValueError):
        create_coordinator("", "facilitator", wikipedia_service=wikipedia_service)
    
    with pytest.raises(ValueError):
        create_coordinator("Test Coordinator", "invalid_archetype", wikipedia_service=wikipedia_service)

def test_determine_coordinator_archetype():
    """Test determining coordinator archetype based on scenario."""
    # Test facilitator archetype
    assert determine_coordinator_archetype("discuss climate change") == "facilitator"
    assert determine_coordinator_archetype("brainstorm ideas") == "facilitator"
    
    # Test strategist archetype
    assert determine_coordinator_archetype("plan project timeline") == "strategist"
    assert determine_coordinator_archetype("develop strategy") == "strategist"
    
    # Test mediator archetype
    assert determine_coordinator_archetype("resolve conflict") == "mediator"
    assert determine_coordinator_archetype("mediate discussion") == "facilitator"  # Default case

def test_generate_system_prompt():
    """Test system prompt generation."""
    role = "Expert"
    topic = "Climate Change"
    prompt = generate_system_prompt(role, topic)
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert role in prompt
    assert topic in prompt

def test_generate_task_force():
    """Test task force generation."""
    scenario = "Discuss climate change solutions"
    ollama_service = OllamaService()
    ollama_service.generate_text = MagicMock(return_value="""[
        {
            "name": "Dr. Climate Expert",
            "role": "Climate Scientist",
            "prompt": "You are a climate science expert"
        },
        {
            "name": "Policy Advisor",
            "role": "Policy Expert",
            "prompt": "You are a policy expert"
        }
    ]""")
    agents, prompt = generate_task_force(scenario, ollama_service=ollama_service)
    
    assert isinstance(agents, list)
    assert len(agents) > 0
    for agent in agents:
        assert isinstance(agent, dict)
        assert "name" in agent
        assert "role" in agent
        assert "prompt" in agent
        assert isinstance(agent["name"], str)
        assert isinstance(agent["role"], str)
        assert isinstance(agent["prompt"], str)
        assert len(agent["name"]) > 0
        assert len(agent["role"]) > 0
        assert len(agent["prompt"]) > 0

def test_generate_task_force_invalid_response():
    """Test handling of invalid task force generation response."""
    ollama_service = OllamaService()
    ollama_service.generate_text = MagicMock(return_value="invalid json")
    
    with pytest.raises(ValueError):
        generate_task_force("test scenario", ollama_service=ollama_service)

def test_generate_task_force_missing_fields():
    """Test handling of task force response with missing fields."""
    ollama_service = OllamaService()
    ollama_service.generate_text = MagicMock(return_value='[{"name": "Test"}]')
    
    with pytest.raises(ValueError):
        generate_task_force("test scenario", ollama_service=ollama_service) 