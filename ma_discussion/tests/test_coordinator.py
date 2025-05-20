"""Tests for the coordinator agent."""

import json
import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException

from ma_discussion.agents.coordinator import CoordinatorAgent
from ma_discussion.services.ollama import OllamaService
from ma_discussion.services.wikipedia import WikipediaService

@pytest.fixture
def mock_ollama_service():
    """Create a mock Ollama service."""
    service = MagicMock(spec=OllamaService)
    service.generate_text.return_value = "Mock response"
    service.stream_text.return_value = "Mock streaming response"
    return service

@pytest.fixture
def mock_wikipedia_service():
    """Create a mock Wikipedia service."""
    service = MagicMock(spec=WikipediaService)
    service.get_summary.return_value = "Mock wiki summary"
    return service

@pytest.fixture
def coordinator(mock_ollama_service, mock_wikipedia_service):
    """Create a coordinator instance for testing."""
    return CoordinatorAgent(
        name="TestCoordinator",
        archetype="facilitator",
        model="test-model",
        ollama_service=mock_ollama_service,
        wikipedia_service=mock_wikipedia_service
    )

def test_coordinator_initialization():
    coordinator = CoordinatorAgent("TestCoordinator", "facilitator", model="llama2")
    assert coordinator.name == "TestCoordinator"
    assert coordinator.role == "Coordinator (facilitator)"
    assert coordinator.archetype == "facilitator"
    assert coordinator.model == "llama2"
    assert coordinator.is_coordinator is True
    assert coordinator.project_plan is None
    assert coordinator.progress_tracking == {}

def test_coordinator_invalid_archetype():
    """Test coordinator initialization with invalid archetype."""
    with pytest.raises(ValueError):
        CoordinatorAgent(name="Test", archetype="")

def test_generate_base_prompt_facilitator():
    """Test base prompt generation for facilitator."""
    coordinator = CoordinatorAgent(name="Test", archetype="facilitator")
    prompt = coordinator._generate_base_prompt()
    assert "facilitator" in prompt.lower()
    assert "guide the conversation" in prompt.lower()

def test_generate_base_prompt_mediator():
    """Test base prompt generation for mediator."""
    coordinator = CoordinatorAgent(name="Test", archetype="mediator")
    prompt = coordinator._generate_base_prompt()
    assert "mediator" in prompt.lower()
    assert "resolve conflicts" in prompt.lower()

def test_generate_base_prompt_strategist():
    """Test base prompt generation for strategist."""
    coordinator = CoordinatorAgent(name="Test", archetype="strategist")
    prompt = coordinator._generate_base_prompt()
    assert "strategic" in prompt.lower()
    assert "actionable outcomes" in prompt.lower()

def test_generate_base_prompt_project_manager():
    """Test base prompt generation for project manager."""
    coordinator = CoordinatorAgent(name="Test", archetype="project_manager")
    prompt = coordinator._generate_base_prompt()
    assert "project management" in prompt.lower()
    assert "track progress" in prompt.lower()

def test_generate_base_prompt_unknown():
    """Test base prompt generation for unknown archetype."""
    coordinator = CoordinatorAgent(name="Test", archetype="unknown")
    prompt = coordinator._generate_base_prompt()
    assert "coordinator" in prompt.lower()
    assert "guide the conversation" in prompt.lower()

def test_summarize_discussion(coordinator):
    """Test discussion summarization."""
    coordinator.conversation_history = [
        {"sender": "Agent1", "message": "First message"},
        {"sender": "Agent2", "message": "Second message"}
    ]
    result = coordinator.summarize_discussion()
    assert isinstance(result, str)
    assert len(result) > 0

def test_make_decision(coordinator):
    """Test decision making."""
    coordinator.conversation_history = [
        {"sender": "Agent1", "message": "First message"},
        {"sender": "Agent2", "message": "Second message"}
    ]
    result = coordinator.make_decision()
    assert isinstance(result, str)
    assert len(result) > 0

def test_streaming_generate_final_output(coordinator):
    """Test final output generation."""
    conversation_history = [
        {"sender": "Agent1", "message": "First message", "is_thinking": False},
        {"sender": "Agent2", "message": "Second message", "is_thinking": False},
        {"sender": "System", "message": "System message", "is_system": True}
    ]
    result = coordinator.streaming_generate_final_output(
        original_topic="Test topic",
        full_conversation_history=conversation_history
    )
    assert isinstance(result, str)
    assert len(result) > 0

def test_break_down_task(coordinator):
    """Test task breakdown."""
    coordinator.archetype = "project_manager"
    
    # Mock the Ollama service response
    def mock_stream_text(prompt, model, on_token=None):
        return """{
    "project_name": "Simple Web Application",
    "objectives": ["Create a basic web interface", "Implement core functionality"],
    "timeline": {
        "start_date": "2024-03-20",
        "end_date": "2024-04-20",
        "milestones": [
            {
                "name": "Initial Setup",
                "description": "Set up development environment",
                "due_date": "2024-03-25",
                "dependencies": []
            }
        ]
    },
    "resources": {
        "required_skills": ["Python", "HTML", "CSS"],
        "tools": ["VS Code", "Git"],
        "constraints": ["Time", "Budget"]
    },
    "risk_management": {
        "potential_risks": [
            {
                "description": "Technical issues",
                "impact": "Medium",
                "mitigation": "Regular testing"
            }
        ]
    }
}"""
    
    coordinator.ollama.stream_text = mock_stream_text
    result = coordinator.break_down_task("Create a simple web application")
    assert isinstance(result, dict)
    if "error" in result:
        assert False, f"Expected project plan, got error: {result['error']}"
    assert "project_name" in result
    assert "objectives" in result
    assert "timeline" in result
    assert "resources" in result
    assert "risk_management" in result

def test_track_progress(coordinator):
    """Test progress tracking."""
    coordinator.archetype = "project_manager"
    coordinator.project_plan = {
        "objectives": ["Objective 1"],
        "timeline": {"milestones": [{"name": "M1"}]}
    }
    coordinator.conversation_history = [
        {"sender": "Agent1", "message": "Progress update"}
    ]
    
    result = coordinator.track_progress(1, 3)
    assert isinstance(result, dict)
    assert "completion_percentage" in result

def test_adjust_plan(coordinator):
    """Test plan adjustment."""
    coordinator.archetype = "project_manager"
    coordinator.project_plan = {
        "objectives": ["Original objective"],
        "timeline": {"milestones": [{"name": "Original milestone"}]}
    }
    
    progress = {
        "completion_percentage": 30,
        "completed_objectives": [],
        "remaining_objectives": ["Original objective"],
        "at_risk_objectives": ["Original objective"]
    }
    
    result = coordinator.adjust_plan(progress)
    assert isinstance(result, dict)

def test_summarize_discussion_error():
    coordinator = CoordinatorAgent("TestCoordinator", "facilitator", model="invalid_model")
    result = coordinator.summarize_discussion()
    assert "I encountered an error while processing" in result

def test_make_decision_error():
    coordinator = CoordinatorAgent("TestCoordinator", "facilitator", model="invalid_model")
    result = coordinator.make_decision()
    assert "I encountered an error while processing" in result

def test_streaming_generate_final_output_error():
    coordinator = CoordinatorAgent("TestCoordinator", "facilitator", model="invalid_model")
    result = coordinator.streaming_generate_final_output("Test topic", [{"sender": "User", "message": "Test message"}])
    assert "I encountered an error while processing" in result

def test_track_progress_error():
    coordinator = CoordinatorAgent("TestCoordinator", "facilitator", model="invalid_model")
    result = coordinator.track_progress(1, 5)
    assert isinstance(result, dict)
    assert "error" in result
    assert "No project plan available" in result["error"]

def test_adjust_plan_error():
    coordinator = CoordinatorAgent("TestCoordinator", "facilitator", model="invalid_model")
    result = coordinator.adjust_plan({"progress": 50})
    assert isinstance(result, dict)
    assert "error" in result
    assert "No project plan available" in result["error"]

def test_break_down_task_error():
    coordinator = CoordinatorAgent("TestCoordinator", "facilitator", model="llama2")
    result = coordinator.break_down_task("Test task")
    assert isinstance(result, dict)
    assert "error" in result
    assert "Only project manager coordinators can break down tasks" in result["error"] 