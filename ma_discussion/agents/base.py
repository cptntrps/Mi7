"""Base agent class implementation."""

import logging
from typing import Dict, Any, List, Optional, Callable

from ma_discussion.services.ollama import OllamaService
from ma_discussion.services.wikipedia import WikipediaService
from ma_discussion.utils.regex import extract_wiki_lookup_term

logger = logging.getLogger(__name__)

class CustomAgent:
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        name: str,
        role: str,
        base_prompt: str,
        model: str = "llama3:latest",
        ollama_service: Optional[OllamaService] = None,
        wikipedia_service: Optional[WikipediaService] = None
    ):
        """Initialize a custom agent.
        
        Args:
            name: Agent's name
            role: Agent's role description
            base_prompt: Base system prompt for the agent
            model: Name of the Ollama model to use
            ollama_service: Optional OllamaService instance
            wikipedia_service: Optional WikipediaService instance
            
        Raises:
            ValueError: If any required parameter is empty
        """
        if not name or not name.strip():
            raise ValueError("Agent name cannot be empty")
        if not role or not role.strip():
            raise ValueError("Agent role cannot be empty")
        if not base_prompt or not base_prompt.strip():
            raise ValueError("Agent base prompt cannot be empty")
        if not model or not model.strip():
            raise ValueError("Agent model cannot be empty")
            
        self.name = name
        self.role = role
        self.base_prompt = base_prompt
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        self.thinking = ""
        
        # Initialize services
        self.ollama = ollama_service or OllamaService()
        self.wikipedia = wikipedia_service or WikipediaService()
    
    def __eq__(self, other: object) -> bool:
        """Compare two agents for equality.
        
        Args:
            other: Another agent to compare with
            
        Returns:
            True if agents are equal, False otherwise
        """
        if not isinstance(other, CustomAgent):
            return False
        return (
            self.name == other.name and
            self.role == other.role and
            self.base_prompt == other.base_prompt and
            self.model == other.model
        )
    
    def __str__(self) -> str:
        """Get string representation of the agent.
        
        Returns:
            String representation including name, role, and model
        """
        return f"{self.name} ({self.role}) - {self.model}"
    
    def format_message(self, message: str) -> Dict[str, str]:
        """Format a message for the conversation.
        
        Args:
            message: Message content
            
        Returns:
            Formatted message dictionary
        """
        return {
            "role": "assistant",
            "content": message
        }
    
    def generate_response(self, conversation: List[Dict[str, str]], topic: str) -> str:
        """Generate a response based on conversation history and topic.
        
        Args:
            conversation: List of conversation messages
            topic: Current discussion topic
            
        Returns:
            Generated response
        """
        # Think about the topic first
        self.think(topic)
        
        # Generate response
        return self.respond(topic, {"conversation": conversation})
    
    def process_conversation(self, conversation: List[Dict[str, str]], topic: str) -> str:
        """Process a conversation and generate a response.
        
        Args:
            conversation: List of conversation messages
            topic: Current discussion topic
            
        Returns:
            Generated response
        """
        return self.generate_response(conversation, topic)
    
    def _stream_response(self, prompt: str, on_token: Optional[Callable[[str], None]] = None) -> str:
        """Stream a response from the language model.
        
        Args:
            prompt: Input prompt for the model
            on_token: Optional callback for token streaming
            
        Returns:
            Complete generated response
        """
        try:
            return self.ollama.stream_text(prompt, self.model, on_token)
        except Exception as e:
            logger.error(f"Error in _stream_response for {self.name}: {str(e)}")
            return f"I encountered an error while processing: {str(e)}"
    
    def think(self, topic: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Think privately about a topic.
        
        Args:
            topic: The topic to think about
            context: Optional context dictionary
            
        Returns:
            Thinking process output
        """
        ctx = str(context) if context else "No additional context"
        
        prompt = f"""You are an AI assistant named {self.name} with the role of {self.role}.
{self.base_prompt}

You are thinking privately about a topic or question. Your goal is to prepare your thoughts for a concise and meaningful contribution.

Topic: {topic}
Context: {ctx}

Think step by step:
1. What are the key aspects of this topic?
2. What unique perspective can you bring based on your role?
3. What questions or concerns should be addressed?
4. How can you contribute to moving the discussion forward?

Your thinking process:
"""
        try:
            self.thinking = self._stream_response(prompt)
            return self.thinking
        except Exception as e:
            logger.error(f"Error in think method for {self.name}: {str(e)}")
            self.thinking = f"I encountered an error while processing: {str(e)}"
            return self.thinking
    
    def respond(self, topic: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response to the topic.
        
        Args:
            topic: The topic to respond to
            context: Optional context dictionary
            
        Returns:
            Generated response
        """
        ctx = str(context) if context else "No additional context"
        
        # Check for Wikipedia lookup in thinking
        wiki_term = extract_wiki_lookup_term(self.thinking)
        if wiki_term:
            logger.info(f"Agent {self.name} triggering Wikipedia lookup for: '{wiki_term}'")
            summary = self.wikipedia.get_summary(wiki_term)
            if summary:
                if not context:
                    context = {}
                context["wikipedia_summary"] = summary
                ctx = str(context)
        
        prompt = f"""You are an AI assistant named {self.name} with the role of {self.role}.
{self.base_prompt}

Based on your thinking process:
{self.thinking}

Generate a response to:
Topic: {topic}
Context: {ctx}

Your response:"""
        
        try:
            return self._stream_response(prompt)
        except Exception as e:
            logger.error(f"Error in respond method for {self.name}: {str(e)}")
            return f"I encountered an error while processing: {str(e)}"
    
    def add_to_history(self, sender: str, message: str) -> None:
        """Add a message to the agent's conversation history.
        
        Args:
            sender: Name of the message sender
            message: Content of the message
        """
        self.conversation_history.append({
            "sender": sender,
            "message": message
        })
        
    def _get_wikipedia_summary(self, search_term: str) -> Optional[str]:
        """Get a summary from Wikipedia for a search term.
        
        Args:
            search_term: Term to search for on Wikipedia
            
        Returns:
            Summary text if found, None otherwise
        """
        try:
            return self.wikipedia.get_summary(search_term)
        except Exception as e:
            logger.error(f"Error getting Wikipedia summary for '{search_term}': {str(e)}")
            return None
            
    def streaming_respond(self, topic: str, context: Optional[Dict[str, Any]] = None, on_token: Optional[Callable[[str], None]] = None) -> str:
        """Generate a streaming response to the topic.
        
        Args:
            topic: The topic to respond to
            context: Optional context dictionary
            on_token: Optional callback for token streaming
            
        Returns:
            Generated response
        """
        ctx = str(context) if context else "No additional context"
        
        # Check for Wikipedia lookup in thinking
        wiki_term = extract_wiki_lookup_term(self.thinking)
        if wiki_term:
            logger.info(f"Agent {self.name} triggering Wikipedia lookup for: '{wiki_term}'")
            summary = self.wikipedia.get_summary(wiki_term)
            if summary:
                if not context:
                    context = {}
                context["wikipedia_summary"] = summary
                ctx = str(context)
        
        prompt = f"""You are an AI assistant named {self.name} with the role of {self.role}.
{self.base_prompt}

You are participating in a discussion. Your goal is to contribute meaningfully based on your role and expertise.

Topic: {topic}
Context: {ctx}

Your previous thinking:
{self.thinking}

Based on your role and the discussion context, provide a clear and focused response that:
1. Addresses the topic directly
2. Brings your unique perspective
3. Moves the discussion forward
4. Maintains a professional and constructive tone

Your response:
"""
        try:
            response = self._stream_response(prompt, on_token)
            self.add_to_history(self.name, response)
            return response
        except Exception as e:
            logger.error(f"Error in streaming_respond method for {self.name}: {str(e)}")
            error_msg = f"I encountered an error while formulating my response: {str(e)}"
            self.add_to_history(self.name, error_msg)
            return error_msg 