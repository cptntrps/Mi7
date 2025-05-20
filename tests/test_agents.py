import pytest
from ma_discussion.agents.base import CustomAgent
from ma_discussion.agents.factory import generate_task_force

def test_custom_agent_init():
    """Test that a CustomAgent can be initialized with basic attributes."""
    agent = CustomAgent(
        name="Test Agent",
        role="Test Role",
        base_prompt="You are a test agent.",
        model="llama3:latest"
    )
    assert agent.name == "Test Agent"
    assert agent.role == "Test Role"
    assert agent.base_prompt == "You are a test agent."
    assert agent.model == "llama3:latest"
    assert agent.conversation_history == []

def test_custom_agent_think():
    """Test that an agent can think about a topic."""
    agent = CustomAgent(
        name="Test Agent",
        role="Test Role",
        base_prompt="You are a test agent.",
        model="llama3:latest"
    )
    topic = "Test topic"
    context = {"round_number": 1, "total_rounds": 3}
    
    # Mock the _stream_response method to avoid actual API calls
    agent._stream_response = lambda prompt, on_token=None: "Test thinking output"
    
    thinking = agent.think(topic, context)
    assert thinking == "Test thinking output"
    assert agent.thinking == "Test thinking output"

def test_generate_task_force():
    """Test that task force generation returns expected structure."""
    scenario = "Create a plan for a small project"
    agents_list, system_prompt = generate_task_force(scenario)
    
    assert isinstance(agents_list, list)
    assert isinstance(system_prompt, str)
    assert len(agents_list) > 0
    
    # Check first agent has required fields
    first_agent = agents_list[0]
    assert "name" in first_agent
    assert "role" in first_agent
    assert "prompt" in first_agent 