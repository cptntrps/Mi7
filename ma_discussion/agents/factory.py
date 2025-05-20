"""Factory functions for creating agents and task forces."""

import logging
from typing import Tuple, List, Dict, Optional

from ma_discussion.services.ollama import OllamaService
from ma_discussion.services.wikipedia import WikipediaService
from ma_discussion.utils.json_io import extract_json_array
from ma_discussion.constants import DEFAULT_MODEL
from ma_discussion.agents.base import CustomAgent
from ma_discussion.agents.coordinator import CoordinatorAgent

logger = logging.getLogger(__name__)

def determine_coordinator_archetype(scenario: str) -> str:
    """Determine the most appropriate coordinator archetype based on the scenario.
    
    Args:
        scenario: The scenario description
        
    Returns:
        The coordinator archetype (facilitator, strategist, mediator)
    """
    scenario = scenario.lower()
    
    if any(word in scenario for word in ["discuss", "brainstorm", "conversation"]):
        return "facilitator"
    elif any(word in scenario for word in ["plan", "strategy", "timeline", "project"]):
        return "strategist"
    elif any(word in scenario for word in ["conflict", "resolve", "mediate"]):
        return "mediator"
    
    return "facilitator"  # Default to facilitator

def generate_system_prompt(role: str, topic: str) -> str:
    """Generate a system prompt for an agent.
    
    Args:
        role: The agent's role
        topic: The discussion topic
        
    Returns:
        The system prompt
    """
    return f"""You are a {role} participating in a discussion about {topic}.
Your goal is to contribute meaningfully to the conversation while staying true to your role.
Consider the topic carefully and provide insights based on your expertise."""

def generate_task_force(
    scenario: str,
    model: str = DEFAULT_MODEL,
    ollama_service: Optional[OllamaService] = None
) -> Tuple[List[Dict], str]:
    """Generate a specialized task force for a given scenario.
    
    Args:
        scenario: The scenario or task description
        model: Optional model override
        ollama_service: Optional OllamaService instance
        
    Returns:
        Tuple of (list of agent dictionaries, system prompt used)
        
    Raises:
        ValueError: If the response cannot be parsed or is invalid
    """
    ollama = ollama_service or OllamaService()
    system_prompt = """You are a team composition expert. Your task is to create a specialized team of AI agents to handle this scenario:

"{0}"

Create a JSON array of agent objects. Each agent should have:
1. "name": A creative, professional name
2. "role": A clear role description
3. "prompt": Detailed instructions/personality for the agent

The team should be diverse and complementary, with each agent bringing unique expertise.
One agent must be designated as the coordinator/facilitator.

Format the response as a valid JSON array of objects with these exact fields:
[
    {{
        "name": "string",
        "role": "string",
        "prompt": "string"
    }}
]

IMPORTANT: Respond ONLY with the JSON array, no additional text or explanation.""".format(scenario)

    try:
        response = ollama.generate_text(system_prompt, model)
        agents_list = extract_json_array(response)
        
        if not agents_list:
            raise ValueError("Failed to parse agents list from response")
            
        # Validate each agent has required fields
        for agent in agents_list:
            if not all(key in agent for key in ["name", "role", "prompt"]):
                raise ValueError(f"Agent missing required fields: {agent}")
                
        return agents_list, system_prompt
        
    except Exception as e:
        logger.error(f"Error generating task force: {e}")
        raise 

def create_agent(
    name: str,
    role: str,
    model: str = DEFAULT_MODEL,
    base_prompt: Optional[str] = None,
    ollama_service: Optional[OllamaService] = None,
    wikipedia_service: Optional[WikipediaService] = None
) -> CustomAgent:
    """Create a new agent.
    
    Args:
        name: Agent name
        role: Agent role
        model: Optional model override
        base_prompt: Optional custom base prompt
        ollama_service: Optional OllamaService instance
        wikipedia_service: Optional WikipediaService instance
        
    Returns:
        The created agent
        
    Raises:
        ValueError: If any required parameters are invalid
    """
    if not name or not role:
        raise ValueError("Name and role are required")
        
    if not base_prompt:
        base_prompt = generate_system_prompt(role, "general discussion")
        
    return CustomAgent(
        name=name,
        role=role,
        model=model,
        base_prompt=base_prompt,
        ollama_service=ollama_service or OllamaService(),
        wikipedia_service=wikipedia_service or WikipediaService()
    )

def create_coordinator(
    name: str,
    archetype: str,
    model: str = DEFAULT_MODEL,
    base_prompt: Optional[str] = None,
    ollama_service: Optional[OllamaService] = None,
    wikipedia_service: Optional[WikipediaService] = None
) -> CoordinatorAgent:
    """Create a new coordinator agent.
    
    Args:
        name: Coordinator name
        archetype: Coordinator archetype (facilitator, strategist, mediator)
        model: Optional model override
        base_prompt: Optional custom base prompt
        ollama_service: Optional OllamaService instance
        wikipedia_service: Optional WikipediaService instance
        
    Returns:
        The created coordinator
        
    Raises:
        ValueError: If any required parameters are invalid
    """
    if not name:
        raise ValueError("Name is required")
        
    if archetype not in ["facilitator", "strategist", "mediator"]:
        raise ValueError("Invalid archetype")
        
    if not base_prompt:
        base_prompt = generate_system_prompt("Coordinator", f"{archetype} for discussion")
        
    return CoordinatorAgent(
        name=name,
        archetype=archetype,
        model=model,
        base_prompt=base_prompt,
        ollama_service=ollama_service or OllamaService(),
        wikipedia_service=wikipedia_service or WikipediaService()
    ) 