"""State management for the Streamlit UI."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

from ma_discussion.agents.base import CustomAgent
from ma_discussion.agents.coordinator import CoordinatorAgent

class AppState(BaseModel):
    """Application state model."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    agents: List[CustomAgent] = []
    coordinator: Optional[CoordinatorAgent] = None
    coordinator_archetype: str = "facilitator"
    conversation_history: List[Dict[str, Any]] = []
    current_streaming_message: str = ""
    last_system_prompt: str = ""
    ollama_models: List[str] = []

    def add_agent(self, agent: CustomAgent) -> None:
        """Add an agent to the state.

        Args:
            agent: Agent to add
        """
        self.agents.append(agent)

    def add_coordinator(self, coordinator: CoordinatorAgent) -> None:
        """Add a coordinator to the state.

        Args:
            coordinator: Coordinator to add
        """
        self.coordinator = coordinator
        self.coordinator_archetype = coordinator.archetype

    def remove_agent(self, agent_name: str) -> None:
        """Remove an agent from the state.

        Args:
            agent_name: Name of the agent to remove
        """
        self.agents = [a for a in self.agents if a.name != agent_name]

    def remove_coordinator(self) -> None:
        """Remove the coordinator from the state."""
        self.coordinator = None
        self.coordinator_archetype = "facilitator"

    def clear_agents(self) -> None:
        """Clear all agents and coordinator from the state."""
        self.agents = []
        self.coordinator = None
        self.coordinator_archetype = "facilitator"

    def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message to the conversation history.

        Args:
            message: Message dictionary containing role, content, and optional avatar
        """
        self.conversation_history.append(message)

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []

    def update_streaming_message(self, message: str) -> None:
        """Update the current streaming message.

        Args:
            message: New streaming message
        """
        self.current_streaming_message = message 