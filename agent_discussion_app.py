"""
agent_discussion_app.py
Multi-agent discussion system using Ollama LLMs
"""

import os
import re
import json
import time
import logging
import threading
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import requests
import streamlit as st

# Constants
OLLAMA_BASE_URL = "http://localhost:11434"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-system")

# Meta-prompt for generating scenario-specific prompts
META_PROMPT_TEMPLATE = """
You are a meta-prompt engineer. Your task is to create the best possible system prompt for generating a team of specialized agents to address this scenario:

{scenario}

The system prompt should:
1. Define the key roles needed for this scenario
2. Specify the personality traits and expertise required for each role
3. Include any specific constraints or requirements
4. Ensure the team works together effectively

Your response should be ONLY the system prompt, with no additional text or explanations."""

def generate_system_prompt(scenario: str, model="llama3:latest") -> str:
    """
    Generate a scenario-specific system prompt using the meta-prompt template.
    
    Args:
        scenario: The scenario or challenge description
        model: The Ollama model to use for generation
        
    Returns:
        The generated system prompt as a string
    """
    base_url = "http://localhost:11434/api"
    
    try:
        # Format the meta-prompt with the scenario
        meta_prompt = META_PROMPT_TEMPLATE.format(scenario=scenario)
        
        # Generate the system prompt
        response = requests.post(
            f"{base_url}/generate",
            json={
                "model": model,
                "prompt": meta_prompt,
                "stream": False
            },
            timeout=90
        )
        response.raise_for_status()
        system_prompt = response.json().get("response", "").strip()
        
        if not system_prompt:
            st.error("Failed to generate a system prompt")
            return ""
            
        return system_prompt
        
    except Exception as e:
        st.error(f"Failed to generate system prompt: {str(e)}")
        return ""

def generate_task_force(scenario: str, model="llama3:latest") -> Tuple[List[Dict], str]:
    """Generate a team of agents based on the given scenario."""
    try:
        # First, generate a scenario-specific prompt
        scenario_prompt = generate_system_prompt(scenario, model)
        
        # Then use that prompt to generate the agent team
        system_prompt = f"""You are a team formation expert. Create a team of 5-7 specialized agents to address this scenario:
        {scenario}
        
        Return ONLY a JSON array of agent objects, with each object having these exact fields:
        {{
            "name": string (agent's full name),
            "role": string (their specialized role),
            "prompt": string (their core directive)
        }}
        
        IMPORTANT:
        - Return ONLY the JSON array, with no additional text or explanations
        - Do not include any markdown formatting or code block markers
        - Ensure the JSON is properly formatted with all brackets and commas
        - The response must be a valid JSON array that can be parsed directly
        """
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": system_prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        response_text = response.json()["response"]
        
        # Clean the response string
        cleaned_response = response_text.strip()
        
        # Remove any markdown code block markers and explanatory text
        cleaned_response = re.sub(r'```json\s*|\s*```', '', cleaned_response)
        cleaned_response = re.sub(r'^.*?\[', '[', cleaned_response, flags=re.DOTALL)  # Remove text before first [
        cleaned_response = re.sub(r'\].*?$', ']', cleaned_response, flags=re.DOTALL)  # Remove text after last ]
        
        # Parse the JSON response
        try:
            agents = json.loads(cleaned_response)
            if not isinstance(agents, list):
                raise ValueError("Response is not a JSON array")
            
            # Validate each agent object
            for agent in agents:
                if not isinstance(agent, dict):
                    raise ValueError("Agent object is not a dictionary")
                required_fields = ["name", "role", "prompt"]
                for field in required_fields:
                    if field not in agent or not isinstance(agent[field], str):
                        raise ValueError(f"Agent missing required field: {field}")
            
            return agents, scenario_prompt
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent task force JSON. Error: {e}. Raw response was: {response_text}")
            logger.error(f"Cleaned response was: {cleaned_response}")
            raise ValueError(f"Could not parse agent task force JSON. Response was: {response_text}")
            
    except Exception as e:
        logger.error(f"Error generating task force: {str(e)}")
        raise

def determine_coordinator_archetype(scenario: str) -> str:
    """
    Determine the most appropriate coordinator archetype based on the scenario.
    
    Args:
        scenario: The scenario or task description
        
    Returns:
        The recommended archetype ("facilitator", "director", "strategist", or "catalyst")
    """
    # Convert scenario to lowercase for easier matching
    scenario_lower = scenario.lower()
    
    # Keywords that suggest different archetypes
    director_keywords = {
        "efficient", "quick", "fast", "timeline", "deadline", "urgent", "immediate",
        "action", "execute", "implement", "deliver", "produce", "create", "build",
        "project", "task", "assignment", "deliverable", "output", "result"
    }
    
    strategist_keywords = {
        "analyze", "evaluate", "assess", "review", "examine", "investigate", "research",
        "strategy", "plan", "approach", "methodology", "framework", "model",
        "quality", "accuracy", "precision", "thorough", "comprehensive", "detailed",
        "evidence", "data", "facts", "statistics", "metrics", "measurements"
    }
    
    catalyst_keywords = {
        "innovate", "create", "design", "develop", "invent", "discover", "explore",
        "creative", "original", "novel", "unique", "different", "new",
        "brainstorm", "ideate", "concept", "prototype", "experiment", "test",
        "art", "design", "writing", "music", "story", "narrative"
    }
    
    # Count keyword matches for each archetype
    director_score = sum(1 for word in director_keywords if word in scenario_lower)
    strategist_score = sum(1 for word in strategist_keywords if word in scenario_lower)
    catalyst_score = sum(1 for word in catalyst_keywords if word in scenario_lower)
    
    # Determine the highest scoring archetype
    scores = {
        "director": director_score,
        "strategist": strategist_score,
        "catalyst": catalyst_score,
        "facilitator": 0  # Default if no strong matches
    }
    
    # If no strong matches, default to facilitator
    if max(scores.values()) < 2:
        return "facilitator"
        
    return max(scores.items(), key=lambda x: x[1])[0]

class CustomAgent:
    """Base class for collaborative agents"""
    
    def __init__(self, name: str, role: str, base_prompt: str, model: str = "llama3:latest"):
        """
        Initialize an agent
        
        Args:
            name: Name of this agent instance
            role: Role of this agent
            base_prompt: Base instructions for this agent
            model: Ollama model to use
        """
        self.name = name
        self.role = role
        self.base_prompt = base_prompt
        self.model = model
        self.conversation_history = []
        self.base_url = "http://localhost:11434/api"
        self.thinking = ""
        # Add Wikipedia API User-Agent
        self.wikipedia_user_agent = f"MultiAgentDiscussionSystem/0.1 ({self.name}; https://github.com/yourusername/Mi7)"
        
    def _stream_response(self, prompt: str, on_token: callable = None) -> str:
        """
        Stream a response from the LLM, calling on_token for each token received.
        Args:
            prompt: The prompt to send to the LLM
            on_token: Optional callback function that receives each token as it arrives
        Returns:
            The complete response as a string
        """
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            token = chunk["response"]
                            full_response += token
                            if on_token:
                                on_token(token)
                    except json.JSONDecodeError:
                        continue
            
            return full_response
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            return f"I'm having trouble connecting to my knowledge base. Error: {str(e)}"
    
    def _get_wikipedia_summary(self, query: str, lang: str = "en") -> Optional[str]:
        """
        Searches Wikipedia for a query and returns the summary of the top hit.
        Args:
            query: The search term.
            lang: Wikipedia language code (e.g., "en" for English).
        Returns:
            The plain text summary of the Wikipedia page, or None if not found/error.
        """
        session = requests.Session()
        headers = {
            "User-Agent": self.wikipedia_user_agent
        }

        # Step 1: Search for the page title
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "utf8": 1,
        }
        
        try:
            search_url = f"https://{lang}.wikipedia.org/w/api.php"
            logger.info(f"Searching Wikipedia for '{query}' with User-Agent: {self.wikipedia_user_agent}")
            response = session.get(url=search_url, params=search_params, headers=headers, timeout=15)
            response.raise_for_status()
            search_data = response.json()

            if search_data.get("query", {}).get("search"):
                page_title = search_data["query"]["search"][0]["title"]
                logger.info(f"Wikipedia search for '{query}' found title: '{page_title}'")
            else:
                logger.info(f"Wikipedia search for '{query}' yielded no results.")
                return None

            # Step 2: Get the extract (summary) of that page
            extract_params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "redirects": 1,
                "utf8": 1,
            }
            response = session.get(url=search_url, params=extract_params, headers=headers, timeout=15)
            response.raise_for_status()
            extract_data = response.json()
            
            pages = extract_data.get("query", {}).get("pages", {})
            if not pages:
                logger.info(f"No pages found in extract data for '{page_title}'.")
                return None
                
            page_id = list(pages.keys())[0]

            if page_id != "-1" and "extract" in pages[page_id]:
                summary = pages[page_id]["extract"]
                # Limit summary length to avoid overly long context
                return (summary[:750] + '...') if len(summary) > 750 else summary
            else:
                logger.info(f"Could not find an extract for Wikipedia page '{page_title}'. Page data: {pages.get(page_id)}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Wikipedia API request failed for query '{query}': {e}")
            return None
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error parsing Wikipedia API response for query '{query}': {e}. Data received: {search_data if 'search_data' in locals() else 'N/A'}, {extract_data if 'extract_data' in locals() else 'N/A'}")
            return None
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/version", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection check failed: {e}")
            return False
    
    def think(self, topic: str, context: Dict[str, Any] = None) -> str:
        """Internal thinking process of agent - not shared with others"""
        ctx = json.dumps(context) if context else "No additional context"
        prompt = f"""You are an AI assistant named {self.name} with the role of {self.role}. 
{self.base_prompt}

You are thinking privately about a topic or question. Your goal is to prepare your thoughts for a concise and meaningful contribution.

TOPIC/QUESTION:
{topic}

CONTEXT:
{ctx}

Think step by step about how to approach this topic based on your role.
Your thinking should aim to build upon, refine, or constructively critique previous relevant points from the discussion (if any are present in the CONTEXT or your recent history) to collaboratively achieve the main discussion objective: '{topic}'.
If you identify a specific factual entity, concept, or event for which you lack sufficient information and believe an encyclopedic summary would be beneficial for your understanding before responding, state your intention to look it up using the EXACT phrase 'WIKI_LOOKUP: "search term"' on a new line in your private thinking. For example:
WIKI_LOOKUP: "Theory of Relativity"
Only use WIKI_LOOKUP for specific, well-defined terms or topics suitable for an encyclopedia. Do not use it for opinions or general questions.
After any WIKI_LOOKUP statement (if any), continue with your step-by-step thinking.
"""
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            thinking = result.get("response", "")
            self.thinking = thinking
            return thinking
        except Exception as e:
            logger.error(f"Error in thinking: {e}")
            return f"Error thinking: {str(e)}"
    
    def respond(self, topic: str, context: Dict[str, Any] = None) -> str:
        """Generate a response to a message"""
        # Prepare conversation history for context
        history_text = "\n".join([f"{entry['sender']}: {entry['message']}" 
                                for entry in self.conversation_history[-5:]])
        
        # Prepare context, including any Wikipedia summary
        ctx_list = []
        if context:
            for k, v in context.items():
                if k == "wikipedia_summary" and v:
                    ctx_list.append(f"Recently retrieved Wikipedia Summary for context: {v}")
                elif k not in ["wikipedia_summary"]: # Avoid duplicating if already handled
                    ctx_list.append(f"{k.replace('_', ' ').title()}: {json.dumps(v)}")

        additional_context_str = "\n".join(ctx_list) if ctx_list else "No additional context provided for this response."

        prompt = f"""You are an AI assistant named {self.name} with the role of {self.role}.
{self.base_prompt}

You are part of a collaborative agent system discussing a topic.

RECENT CONVERSATION HISTORY (last 5 messages):
{history_text}

YOUR PRIVATE THINKING (not shared with others, for your reference only):
{self.thinking}

ADDITIONAL CONTEXT FOR THIS RESPONSE:
{additional_context_str}

TOPIC/QUESTION FOR THIS RESPONSE:
{topic}

Based on all the above, including your role, recent conversation, your private thinking, and any provided Wikipedia summary or other context, formulate your response.
Refer to relevant points made by other agents (visible in RECENT CONVERSATION HISTORY or ADDITIONAL CONTEXT FOR THIS RESPONSE) and try to build upon them or offer constructive alternatives if appropriate.
Respond concisely while staying true to your role. Your goal is to contribute meaningfully to the discussion. If you used information from a Wikipedia summary, you can incorporate it naturally without necessarily citing "Wikipedia" unless it's a direct quote or specific data point.
"""
        return self._stream_response(prompt)
    
    def streaming_respond(self, topic: str, context: Dict[str, Any] = None, on_token: callable = None) -> str:
        """
        Generate a streaming response to a message, calling on_token for each token received.
        Args:
            topic: The topic to respond to
            context: Additional context for the response
            on_token: Callback function that receives each token as it arrives
        Returns:
            The complete response as a string
        """
        # Prepare conversation history for context
        history_text = "\n".join([f"{entry['sender']}: {entry['message']}" 
                                for entry in self.conversation_history[-5:]])
        
        # Prepare context, including any Wikipedia summary
        ctx_list = []
        if context:
            for k, v in context.items():
                if k == "wikipedia_summary" and v:
                    ctx_list.append(f"Recently retrieved Wikipedia Summary for context: {v}")
                elif k not in ["wikipedia_summary"]: # Avoid duplicating if already handled
                    ctx_list.append(f"{k.replace('_', ' ').title()}: {json.dumps(v)}")

        additional_context_str = "\n".join(ctx_list) if ctx_list else "No additional context provided for this response."

        prompt = f"""You are an AI assistant named {self.name} with the role of {self.role}.
{self.base_prompt}

You are part of a collaborative agent system discussing a topic.

RECENT CONVERSATION HISTORY (last 5 messages):
{history_text}

YOUR PRIVATE THINKING (not shared with others, for your reference only):
{self.thinking}

ADDITIONAL CONTEXT FOR THIS RESPONSE:
{additional_context_str}

TOPIC/QUESTION FOR THIS RESPONSE:
{topic}

Based on all the above, including your role, recent conversation, your private thinking, and any provided Wikipedia summary or other context, formulate your response.
Refer to relevant points made by other agents (visible in RECENT CONVERSATION HISTORY or ADDITIONAL CONTEXT FOR THIS RESPONSE) and try to build upon them or offer constructive alternatives if appropriate.
Respond concisely while staying true to your role. Your goal is to contribute meaningfully to the discussion. If you used information from a Wikipedia summary, you can incorporate it naturally without necessarily citing "Wikipedia" unless it's a direct quote or specific data point.
"""
        return self._stream_response(prompt, on_token)
    
    def add_to_history(self, sender: str, message: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "timestamp": time.time(),
            "sender": sender,
            "message": message
        })

class CoordinatorAgent(CustomAgent):
    """Agent responsible for coordinating the discussion and making final decisions"""
    
    # Define archetype-specific base prompts
    ARCHETYPE_PROMPTS = {
        "facilitator": """You are a discussion facilitator. Your role is to guide the conversation, ensure all voices are heard, and help the team reach a consensus. Focus on the topic: {original_topic}""",
        "strategist": """You are a strategic coordinator. Your role is to analyze the discussion from a strategic perspective, identify key patterns, and guide the team toward strategic objectives. Focus on the topic: {original_topic}""",
        "project_manager": """You are a project manager. Your role is to break down tasks, track progress, and ensure the discussion stays focused on actionable outcomes. Focus on the topic: {original_topic}"""
    }
    
    def __init__(self, name: str = "Coordinator", role: str = "Coordinator", 
                 archetype: str = "facilitator", base_prompt: str = "", model: str = "llama3:latest"):
        # Set coordinator-specific attributes first
        self.is_coordinator = True
        self.archetype = archetype.lower()
        self.project_plan = None
        self.progress_tracker = {}
        
        # Store the archetype template and custom override
        self.archetype_template = self.ARCHETYPE_PROMPTS.get(archetype.lower(), self.ARCHETYPE_PROMPTS["facilitator"])
        self.custom_base_prompt_override = base_prompt
        
        # Initialize with the template or override (will be formatted later)
        actual_base_prompt = self.custom_base_prompt_override or self.archetype_template
        
        # Call parent constructor
        super().__init__(name, role, actual_base_prompt, model)
        
    def _get_formatted_base_prompt(self, topic: str) -> str:
        """Helper method to format the base prompt with the topic."""
        try:
            if self.custom_base_prompt_override:
                return self.custom_base_prompt_override.format(original_topic=topic)
            return self.archetype_template.format(original_topic=topic)
        except KeyError:
            logger.warning(f"Coordinator {self.name} base_prompt has '{{original_topic}}' but it wasn't formatted. Using as is.")
            return self.base_prompt
    
    def think(self, topic: str, context: Dict[str, Any] = None) -> str:
        """Override think method to use formatted base prompt."""
        ctx = json.dumps(context) if context else "No additional context"
        
        # Get formatted base prompt
        effective_base_prompt = self._get_formatted_base_prompt(topic)
        
        prompt = f"""You are an AI assistant named {self.name} with the role of {self.role}. 
{effective_base_prompt}

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
            logger.error(f"Error in think method: {e}")
            self.thinking = "I encountered an error while thinking about this topic."
            return self.thinking
    
    def respond(self, topic: str, context: Dict[str, Any] = None) -> str:
        """Override respond method to use formatted base prompt."""
        ctx = json.dumps(context) if context else "No additional context"
        
        # Get formatted base prompt
        effective_base_prompt = self._get_formatted_base_prompt(topic)
        
        prompt = f"""You are an AI assistant named {self.name} with the role of {self.role}. 
{effective_base_prompt}

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
            response = self._stream_response(prompt)
            self.add_to_history(self.name, response)
            return response
        except Exception as e:
            logger.error(f"Error in respond method: {e}")
            error_msg = "I encountered an error while formulating my response."
            self.add_to_history(self.name, error_msg)
            return error_msg
    
    def streaming_respond(self, topic: str, context: Dict[str, Any] = None, on_token: callable = None) -> str:
        """Override streaming_respond method to use formatted base prompt."""
        ctx = json.dumps(context) if context else "No additional context"
        
        # Get formatted base prompt
        effective_base_prompt = self._get_formatted_base_prompt(topic)
        
        prompt = f"""You are an AI assistant named {self.name} with the role of {self.role}. 
{effective_base_prompt}

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
            logger.error(f"Error in streaming_respond method: {e}")
            error_msg = "I encountered an error while formulating my response."
            self.add_to_history(self.name, error_msg)
            return error_msg
    
    def generate_final_output(self, original_topic: str, full_conversation_history: List[Dict]) -> str:
        """Generate the final output based on the discussion."""
        # Get formatted base prompt
        effective_base_prompt = self._get_formatted_base_prompt(original_topic)
        
        # Format conversation history
        formatted_history = "\n".join([
            f"{msg['sender']}: {msg['message']}"
            for msg in full_conversation_history
            if not msg.get("is_thinking", False) and not msg.get("is_system", False)
        ])
        
        prompt = f"""You are {self.name}, the {self.role}.
{effective_base_prompt}

The multi-agent team has now concluded its discussion.
The **original request (the main task)** for this entire discussion was:
"{original_topic}"

The full conversation transcript follows:
---
{formatted_history}
---

Based on the original request and the full discussion, generate a comprehensive final output that:
1. Directly addresses the original request
2. Synthesizes the key points and insights from the discussion
3. Provides a clear, structured, and actionable response
4. Maintains a professional and constructive tone

Your final output:
"""
        try:
            return self._stream_response(prompt)
        except Exception as e:
            logger.error(f"Error in generate_final_output: {e}")
            return "I encountered an error while generating the final output."
    
    def streaming_generate_final_output(self, original_topic: str, full_conversation_history: List[Dict], on_token: callable = None) -> str:
        """Generate the final output with streaming support."""
        # Get formatted base prompt
        effective_base_prompt = self._get_formatted_base_prompt(original_topic)
        
        # Format conversation history
        formatted_history = "\n".join([
            f"{msg['sender']}: {msg['message']}"
            for msg in full_conversation_history
            if not msg.get("is_thinking", False) and not msg.get("is_system", False)
        ])
        
        prompt = f"""You are {self.name}, the {self.role}.
{effective_base_prompt}

The multi-agent team has now concluded its discussion.
The **original request (the main task)** for this entire discussion was:
"{original_topic}"

The full conversation transcript follows:
---
{formatted_history}
---

Based on the original request and the full discussion, generate a comprehensive final output that:
1. Directly addresses the original request
2. Synthesizes the key points and insights from the discussion
3. Provides a clear, structured, and actionable response
4. Maintains a professional and constructive tone

Your final output:
"""
        try:
            return self._stream_response(prompt, on_token)
        except Exception as e:
            logger.error(f"Error in streaming_generate_final_output: {e}")
            return "I encountered an error while generating the final output."

    def break_down_task(self, topic: str) -> Dict:
        """Break down a task into a structured project plan.
        
        Args:
            topic: The task or topic to break down
            
        Returns:
            A dictionary containing the project plan with objectives, timeline, resources, and risk management
        """
        if not self.is_coordinator or self.archetype != "project_manager":
            return None
            
        prompt = f"""You are {self.name}, a project manager breaking down a task into a structured plan.
The task is: "{topic}"

Create a detailed project plan in JSON format with the following structure:
{{
    "project_name": "string",
    "objectives": ["string"],
    "timeline": {{
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "milestones": [
            {{
                "name": "string",
                "description": "string",
                "due_date": "YYYY-MM-DD",
                "dependencies": ["string"]
            }}
        ]
    }},
    "resources": {{
        "required_skills": ["string"],
        "tools": ["string"],
        "constraints": ["string"]
    }},
    "risk_management": {{
        "potential_risks": [
            {{
                "description": "string",
                "impact": "string",
                "mitigation": "string"
            }}
        ]
    }}
}}

The plan should be realistic and actionable. Focus on breaking down the task into clear objectives, milestones, and required resources.
IMPORTANT: Respond ONLY with the JSON object, no additional text or explanation.
"""
        try:
            response = self._stream_response(prompt)
            # Try to parse the JSON from the response
            try:
                # Clean the response string
                cleaned_response = response.strip()
                # Remove any markdown code block markers
                cleaned_response = re.sub(r'```json\s*|\s*```', '', cleaned_response)
                # Remove any text before the first { and after the last }
                cleaned_response = re.sub(r'^.*?\{', '{', cleaned_response)
                cleaned_response = re.sub(r'\}.*?$', '}', cleaned_response)
                
                # Try to parse the cleaned JSON
                project_plan = json.loads(cleaned_response)
                
                # Validate the required structure
                required_keys = ["project_name", "objectives", "timeline", "resources", "risk_management"]
                if not all(key in project_plan for key in required_keys):
                    logger.error(f"Project plan missing required keys. Found: {list(project_plan.keys())}")
                    return None
                
                self.project_plan = project_plan  # Store for later use
                return project_plan
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse project plan JSON from response: {response}")
                return None
        except Exception as e:
            logger.error(f"Error in break_down_task: {e}")
            return None

    def track_progress(self, current_round: int, total_rounds: int) -> Dict:
        """Track the progress of the discussion and generate a progress report.
        
        Args:
            current_round: The current round number
            total_rounds: The total number of discussion rounds
            
        Returns:
            A dictionary containing the progress report with completion status, key points, and next steps
        """
        if not self.is_coordinator or self.archetype != "project_manager":
            return None
            
        # Get the project plan if it exists
        project_plan = getattr(self, 'project_plan', None)
        
        prompt = f"""You are {self.name}, a project manager tracking progress in a discussion.
Current Round: {current_round} of {total_rounds}

{self._get_formatted_base_prompt(self.conversation_history[-1]["message"] if self.conversation_history else "No topic available")}

Based on the discussion so far, create a progress report in JSON format with the following structure:
{{
    "completion_status": {{
        "overall_progress": "percentage",
        "completed_objectives": ["string"],
        "remaining_objectives": ["string"]
    }},
    "key_points": [
        {{
            "point": "string",
            "source": "string",
            "significance": "string"
        }}
    ],
    "next_steps": [
        {{
            "action": "string",
            "priority": "string",
            "assigned_to": "string"
        }}
    ],
    "risks_and_mitigations": [
        {{
            "risk": "string",
            "impact": "string",
            "mitigation": "string"
        }}
    ]
}}

The report should reflect the current state of the discussion and provide actionable next steps.
IMPORTANT: Respond ONLY with the JSON object, no additional text or explanation.
"""
        try:
            response = self._stream_response(prompt)
            # Try to parse the JSON from the response
            try:
                # Clean the response string
                cleaned_response = response.strip()
                # Remove any markdown code block markers
                cleaned_response = re.sub(r'```json\s*|\s*```', '', cleaned_response)
                # Remove any text before the first { and after the last }
                cleaned_response = re.sub(r'^.*?\{', '{', cleaned_response)
                cleaned_response = re.sub(r'\}.*?$', '}', cleaned_response)
                
                # Try to parse the cleaned JSON
                progress_report = json.loads(cleaned_response)
                
                # Validate the required structure
                required_keys = ["completion_status", "key_points", "next_steps", "risks_and_mitigations"]
                if not all(key in progress_report for key in required_keys):
                    logger.error(f"Progress report missing required keys. Found: {list(progress_report.keys())}")
                    return None
                
                return progress_report
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse progress report JSON from response: {response}")
                return None
        except Exception as e:
            logger.error(f"Error in track_progress: {e}")
            return None

    def adjust_plan(self, progress_report: Dict) -> Dict:
        """Adjust the project plan based on the progress report.
        
        Args:
            progress_report: The current progress report containing completion status, key points, and next steps
            
        Returns:
            A dictionary containing the plan adjustments with modified objectives, timeline, and resources
        """
        if not self.is_coordinator or self.archetype != "project_manager":
            return None
            
        # Get the current project plan
        current_plan = getattr(self, 'project_plan', None)
        if not current_plan:
            return None
            
        prompt = f"""You are {self.name}, a project manager adjusting the project plan based on progress.
Current Project Plan:
{json.dumps(current_plan, indent=2)}

Progress Report:
{json.dumps(progress_report, indent=2)}

Based on the progress report, create a plan adjustment in JSON format with the following structure:
{{
    "modified_objectives": [
        {{
            "original": "string",
            "modified": "string",
            "reason": "string"
        }}
    ],
    "timeline_adjustments": [
        {{
            "milestone": "string",
            "original_date": "YYYY-MM-DD",
            "new_date": "YYYY-MM-DD",
            "reason": "string"
        }}
    ],
    "resource_adjustments": [
        {{
            "type": "string (skills/tools/constraints)",
            "original": "string",
            "modified": "string",
            "reason": "string"
        }}
    ],
    "risk_adjustments": [
        {{
            "original_risk": "string",
            "modified_risk": "string",
            "reason": "string"
        }}
    ]
}}

The adjustments should be based on the progress report and should help keep the project on track.
IMPORTANT: Respond ONLY with the JSON object, no additional text or explanation.
"""
        try:
            response = self._stream_response(prompt)
            # Try to parse the JSON from the response
            try:
                # Clean the response string
                cleaned_response = response.strip()
                # Remove any markdown code block markers
                cleaned_response = re.sub(r'```json\s*|\s*```', '', cleaned_response)
                # Remove any text before the first { and after the last }
                cleaned_response = re.sub(r'^.*?\{', '{', cleaned_response)
                cleaned_response = re.sub(r'\}.*?$', '}', cleaned_response)
                
                # Try to parse the cleaned JSON
                plan_adjustments = json.loads(cleaned_response)
                
                # Validate the required structure
                required_keys = ["modified_objectives", "timeline_adjustments", "resource_adjustments", "risk_adjustments"]
                if not all(key in plan_adjustments for key in required_keys):
                    logger.error(f"Plan adjustments missing required keys. Found: {list(plan_adjustments.keys())}")
                    return None
                
                return plan_adjustments
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse plan adjustments JSON from response: {response}")
                return None
        except Exception as e:
            logger.error(f"Error in adjust_plan: {e}")
            return None

    def summarize_discussion(self) -> str:
        """Generate a comprehensive summary of the discussion.
        
        Returns:
            A string containing the discussion summary
        """
        # Format conversation history for the prompt
        formatted_history = "\n".join([
            f"{msg['sender']}: {msg['message']}"
            for msg in self.conversation_history
        ])
        
        prompt = f"""You are {self.name}, the discussion coordinator.
{self._get_formatted_base_prompt(self.conversation_history[-1]["message"] if self.conversation_history else "No topic available")}

The following is the complete discussion transcript:
---
{formatted_history}
---

Based on the discussion, provide a comprehensive summary that:
1. Captures the main points and key insights
2. Highlights areas of agreement and disagreement
3. Identifies any unresolved questions or concerns
4. Synthesizes the collective wisdom of the group
5. Maintains a professional and constructive tone

Your summary:
"""
        try:
            return self._stream_response(prompt)
        except Exception as e:
            logger.error(f"Error in summarize_discussion: {e}")
            return "I encountered an error while summarizing the discussion."
            
    def make_decision(self) -> str:
        """Generate a final assessment and decision based on the discussion.
        
        Returns:
            A string containing the final assessment and decision
        """
        # Format conversation history for the prompt
        formatted_history = "\n".join([
            f"{msg['sender']}: {msg['message']}"
            for msg in self.conversation_history
        ])
        
        prompt = f"""You are {self.name}, the {self.role}.
{self._get_formatted_base_prompt(self.conversation_history[-1]["message"] if self.conversation_history else "No topic available")}

The following is the complete discussion transcript:
---
{formatted_history}
---

Based on the discussion, provide a final assessment that:
1. Evaluates the quality and completeness of the discussion
2. Identifies the most valuable insights and contributions
3. Makes a clear decision or recommendation on the topic
4. Provides a rationale for your decision based on the discussion
5. Offers next steps or action items if applicable
6. Maintains a professional and constructive tone

Your final assessment and decision:
"""
        try:
            return self._stream_response(prompt)
        except Exception as e:
            logger.error(f"Error in make_decision: {e}")
            return "I encountered an error while making a final assessment."

def save_task_force(filename="taskforce.json"):
    """Save the current set of agents to a JSON file"""
    agents_out = []
    for agent in st.session_state.agents:
        agents_out.append({
            "name": agent.name,
            "role": agent.role,
            "prompt": agent.base_prompt,
            "model": agent.model,
            "is_coordinator": isinstance(agent, CoordinatorAgent)
        })
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", filename)
    
    with open(filepath, "w") as f:
        json.dump(agents_out, f, indent=2)
    st.success(f"Task force saved to {filepath}")

def load_task_force(filename="taskforce.json"):
    """Load a set of agents from a JSON file"""
    filepath = os.path.join("data", filename)
    try:
        with open(filepath) as f:
            agents_in = json.load(f)
        st.session_state.agents = []
        st.session_state.coordinator = None
        for ad in agents_in:
            if ad.get("is_coordinator"):
                agent = CoordinatorAgent(ad["name"], ad["role"], ad["prompt"], ad["model"])
                st.session_state.coordinator = agent
            else:
                agent = CustomAgent(ad["name"], ad["role"], ad["prompt"], ad["model"])
            st.session_state.agents.append(agent)
        st.success(f"Loaded {len(agents_in)} agents from {filepath}")
        st.rerun()
    except Exception as e:
        st.error(f"Failed to load: {e}")

# STREAMLIT APP
st.set_page_config(page_title="Multi-Agent Discussion System", layout="wide")

# Initialize session state
if "agents" not in st.session_state:
    st.session_state.agents = []
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "coordinator" not in st.session_state:
    st.session_state.coordinator = None
if "ollama_models" not in st.session_state:
    # Default models in case we can't fetch
    st.session_state.ollama_models = ["llama3:latest"]
    # Try to fetch available models
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            if "models" in models_data:
                st.session_state.ollama_models = [model["name"] for model in models_data["models"]]
    except:
        pass
if "last_system_prompt" not in st.session_state:
    st.session_state.last_system_prompt = ""
if "current_streaming_message" not in st.session_state:
    st.session_state.current_streaming_message = ""
if "coordinator_archetype" not in st.session_state:
    st.session_state.coordinator_archetype = "facilitator"

def on_token(token: str):
    """Callback for handling streaming tokens"""
    st.session_state.current_streaming_message += token
    # Removed st.rerun() to prevent loop interruption

# App title and description
st.title("🤖 Multi-Agent Discussion System")
st.markdown("""
Create a panel of AI agents with different roles and personalities to discuss any topic.
Each agent will think privately and respond based on their assigned role.
""")

# Sidebar for agent management
with st.sidebar:
    st.header("Agent Management")
    
    # Add coordinator archetype selector at the top
    st.subheader("Coordinator Settings")
    st.session_state.coordinator_archetype = st.selectbox(
        "Default Coordinator Style",
        options=["facilitator", "director", "strategist", "catalyst", "project_manager"],
        format_func=lambda x: x.title(),
        help="Choose the coordination style that best fits your needs:\n"
             "- Facilitator: Fosters collaboration and consensus\n"
             "- Director: Drives efficient, decisive action\n"
             "- Strategist: Ensures thorough analysis and quality\n"
             "- Catalyst: Encourages innovation and creativity\n"
             "- Project Manager: Breaks down tasks, tracks progress, and ensures delivery",
        index=["facilitator", "director", "strategist", "catalyst", "project_manager"].index(st.session_state.coordinator_archetype)
    )
    
    # Auto-generate task force
    with st.expander("Auto-Generate Task Force"):
        auto_team_topic = st.text_area(
            "Enter the topic or scenario for which to generate a specialized team",
            height=100,
            placeholder="e.g., Create a team to analyze the impact of artificial intelligence on healthcare"
        )
        
        auto_team_model = st.selectbox("Model for auto-generated team", options=st.session_state.ollama_models)
        
        if st.button("Generate Task Force"):
            if not auto_team_topic:
                st.error("Please enter a topic for the task force")
            else:
                try:
                    with st.spinner("Generating specialized task force..."):
                        # generate_task_force will handle generating the system_prompt internally
                        # and then use it to create the agents
                        agents_list, system_prompt_used = generate_task_force(auto_team_topic, auto_team_model)
                        st.session_state.last_system_prompt = system_prompt_used  # Store the actual system prompt used
                        
                    if agents_list:
                        st.session_state.agents = []  # Clear old agents
                        st.session_state.coordinator = None
                        for agent_dict in agents_list:
                            name = agent_dict.get("name") or agent_dict.get("role")
                            role = agent_dict.get("role", "Expert")
                            prompt = agent_dict.get("prompt", "You are a helpful expert.")
                            if "coordinator" in role.lower() or "facilitator" in role.lower() or "moderator" in role.lower() or "mediator" in role.lower():
                                archetype = agent_dict.get("archetype", "facilitator")
                                new_agent = CoordinatorAgent(
                                    name=name,
                                    role=role,
                                    archetype=archetype,
                                    base_prompt=prompt,
                                    model=auto_team_model
                                )
                                st.session_state.coordinator = new_agent
                                logger.info(f"Created {archetype.title()} coordinator: {name}")
                                st.success(f"Created {st.session_state.coordinator_archetype.title()} coordinator: {name}")
                            else:
                                new_agent = CustomAgent(name, role, prompt, auto_team_model)
                                logger.info(f"Created standard agent: {name}")
                                st.success(f"Added standard agent: {name}")
                            st.session_state.agents.append(new_agent)
                        st.success(f"Created specialized task force with {len(agents_list)} agents!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error generating task force: {str(e)}")
    
    # Show last used system prompt if available
    if st.session_state.last_system_prompt:
        with st.expander("Last prompt used to generate agents"):
            st.code(st.session_state.last_system_prompt, language="markdown")
    
    st.divider()
    
    # Manual agent creation form
    st.subheader("Create New Agent")
    
    # Add coordinator checkbox in the form
    is_coordinator = st.checkbox("Make this the coordinator agent")
    
    with st.form("create_agent_form"):
        agent_name = st.text_input("Agent Name", value="Agent " + str(len(st.session_state.agents) + 1))
        agent_role = st.text_input("Agent Role", value="Expert")
        
        # Predefined personalities to choose from
        role_templates = {
            "Custom": "",
            "Skeptic": "You are a skeptical thinker who questions assumptions and looks for flaws in arguments. You prioritize evidence and logical consistency.",
            "Optimist": "You are an optimistic thinker who looks for possibilities and positive outcomes. You emphasize opportunities and creative solutions.",
            "Analyst": "You are an analytical thinker who breaks down complex issues into components and examines them systematically.",
            "Devil's Advocate": "You deliberately take opposing viewpoints to test the strength of arguments. You challenge consensus to ensure all angles are considered.",
            "Synthesizer": "You look for ways to integrate diverse viewpoints and find common ground. You build bridges between different perspectives.",
            "Storyteller": "You use narratives and examples to illustrate points. You think in terms of human experiences and concrete scenarios.",
            "Futurist": "You consider long-term implications and emerging trends. You think about how current developments might unfold over time.",
            "Ethicist": "You focus on moral and ethical dimensions of issues. You consider principles, values, and potential impacts on different stakeholders.",
            "Coordinator": "You guide discussions, summarize key points, and help the group reach consensus. You maintain focus and highlight progress."
        }
        
        template_choice = st.selectbox("Personality Template", options=list(role_templates.keys()))
        
        agent_prompt = st.text_area(
            "Agent Instructions/Personality", 
            value=role_templates[template_choice],
            height=150
        )
        
        agent_model = st.selectbox("Ollama Model", options=st.session_state.ollama_models)
        
        submit_agent = st.form_submit_button("Add Agent")
        
        if submit_agent:
            try:
                if not agent_name:
                    st.error("Please enter an agent name")
                elif not agent_role:
                    st.error("Please enter an agent role")
                elif not agent_prompt:
                    st.error("Please enter agent instructions or select a personality template")
                else:
                    logger.info(f"Creating new agent: {agent_name} with role {agent_role}")
                    if is_coordinator:
                        new_agent = CoordinatorAgent(
                            name=agent_name,
                            role=agent_role,
                            archetype=st.session_state.coordinator_archetype,
                            base_prompt=agent_prompt,
                            model=agent_model
                        )
                        st.session_state.coordinator = new_agent
                        logger.info(f"Created coordinator agent: {agent_name} with archetype {st.session_state.coordinator_archetype}")
                        st.success(f"Created {st.session_state.coordinator_archetype.title()} coordinator: {agent_name}")
                    else:
                        new_agent = CustomAgent(agent_name, agent_role, agent_prompt, agent_model)
                        logger.info(f"Created standard agent: {agent_name}")
                        st.success(f"Added standard agent: {agent_name}")
                    
                    st.session_state.agents.append(new_agent)
                    st.success(f"Added agent: {agent_name}")
                    logger.info(f"Total agents after adding: {len(st.session_state.agents)}")
                    st.rerun()
            except Exception as e:
                logger.error(f"Error creating agent: {str(e)}")
                st.error(f"Failed to create agent: {str(e)}")
    
    # List of current agents
    st.subheader("Current Agents")
    for i, agent in enumerate(st.session_state.agents):
        is_coordinator = isinstance(agent, CoordinatorAgent) and agent == st.session_state.coordinator
        agent_type = f"Active Coordinator ({agent.archetype.title()})" if is_coordinator else "Standard"
        st.markdown(f"**{i+1}. {agent.name}** ({agent_type})")
        st.markdown(f"*Role:* {agent.role}")
        
        # Add expandable section for viewing and editing the prompt
        with st.expander("View/Edit Prompt"):
            edited_prompt = st.text_area(
                "Agent Prompt",
                value=agent.base_prompt,
                height=200,
                key=f"prompt_edit_{i}"
            )
            
            # Add buttons for updating prompt and removing agent
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Prompt", key=f"update_{i}"):
                    agent.base_prompt = edited_prompt
                    st.success(f"Updated prompt for {agent.name}")
                    st.rerun()
            
            with col2:
                if st.button(f"Remove {agent.name}", key=f"remove_{i}"):
                    # If removing coordinator, set to None
                    if agent == st.session_state.coordinator:
                        st.session_state.coordinator = None
                    st.session_state.agents.remove(agent)
                    st.rerun()
        
        st.markdown("---")
    
    if st.button("Clear All Agents"):
        st.session_state.agents = []
        st.session_state.coordinator = None
        st.session_state.conversation = []
        st.rerun()
    
    # Save/Load Task Force section
    st.subheader("💾 Save/Load Task Force")
    save_fn = st.text_input("Save as filename", value="taskforce.json")
    if st.button("Save Task Force"):
        if not st.session_state.agents:
            st.warning("No agents to save!")
        else:
            save_task_force(save_fn)
    
    load_fn = st.text_input("Load from filename", value="taskforce.json")
    if st.button("Load Task Force"):
        load_task_force(load_fn)

# Main area for discussion
col1, col2 = st.columns([2, 3])

with col1:
    st.header("Discussion Topic")
    
    discussion_topic = st.text_area(
        "Enter the topic or question for discussion",
        height=100,
        placeholder="e.g., What are the ethical implications of artificial general intelligence?"
    )
    
    if st.button("Start New Discussion"):
        st.session_state.conversation = []
        for agent in st.session_state.agents:
            agent.conversation_history = []
        st.success("Started new discussion")
    
    discussion_rounds = st.number_input("Number of discussion rounds", min_value=1, max_value=10, value=3)
    
    show_thinking = st.checkbox("Show agent thinking process", value=True)
    
    if st.button("Run Discussion"):
        if not st.session_state.agents:
            st.error("Please add at least one agent first")
        elif not discussion_topic:
            st.error("Please enter a discussion topic")
        else:
            # Add system message to start discussion
            system_message = {
                "timestamp": time.time(),
                "sender": "System",
                "message": f"Starting discussion on topic: {discussion_topic}",
                "is_system": True
            }
            st.session_state.conversation.append(system_message)

            # --- TEMPORARY DEBUG FOR COORDINATOR ---
            if st.session_state.coordinator:
                st.sidebar.info(f"Active Coordinator: {st.session_state.coordinator.name}\nArchetype: {getattr(st.session_state.coordinator, 'archetype', 'N/A')}\nType: {type(st.session_state.coordinator)}")
            else:
                st.sidebar.warning("No active Coordinator (st.session_state.coordinator is None). Project Manager features and final output might be skipped.")
            # --- END TEMPORARY DEBUG ---

            # Project Manager Initial Planning (before rounds start)
            if st.session_state.coordinator and hasattr(st.session_state.coordinator, 'archetype') and st.session_state.coordinator.archetype == "project_manager":
                with st.spinner(f"👑 {st.session_state.coordinator.name} is creating the project plan..."):
                    project_plan = st.session_state.coordinator.break_down_task(discussion_topic)
                    if project_plan:
                        st.session_state.conversation.append({
                            "timestamp": time.time(),
                            "sender": f"{st.session_state.coordinator.name} (Project Plan)",
                            "message": f"Project Plan Created:\n{json.dumps(project_plan, indent=2)}",
                            "is_system": True
                        })

            # Main Discussion Loop
            for round_num in range(discussion_rounds):
                round_info_context = {
                    "round_number": round_num + 1,
                    "total_rounds": discussion_rounds,
                    "participating_agents": [a.name for a in st.session_state.agents]
                }
                st.markdown(f"#### Round {round_num + 1}")

                # Agent Thinking Phase
                for agent in st.session_state.agents:
                    agent.think(discussion_topic, round_info_context.copy())
                    if show_thinking:
                        thinking_message = {
                            "timestamp": time.time(),
                            "sender": f"{agent.name} (thinking)",
                            "message": agent.thinking,
                            "is_thinking": True
                        }
                        st.session_state.conversation.append(thinking_message)

                # Agent Response Phase
                for agent in st.session_state.agents:
                    current_agent_response_context = round_info_context.copy()
                    
                    # Handle Wikipedia lookups
                    wiki_match = re.search(r"WIKI_LOOKUP:\s*(?:\"(.*?)\"|\'(.*?)\'|([^\"\']+))", agent.thinking)
                    if wiki_match:
                        search_term = wiki_match.group(1) or wiki_match.group(2) or wiki_match.group(3)
                        search_term = search_term.strip() if search_term else None
                        if search_term and search_term.upper() != "WIKI_LOOKUP:" and len(search_term) > 1:
                            with st.spinner(f"🤖 {agent.name} is looking up '{search_term}' on Wikipedia..."):
                                logger.info(f"Agent {agent.name} triggering Wikipedia lookup for: '{search_term}'")
                                summary = agent._get_wikipedia_summary(search_term)
                            if summary:
                                current_agent_response_context["wikipedia_summary"] = summary
                                st.info(f"📄 {agent.name} found a Wikipedia summary for '{search_term}'.")
                            else:
                                st.warning(f"⚠️ {agent.name} found no Wikipedia summary for '{search_term}'.")

                    # Create a placeholder for the streaming message
                    message_placeholder = st.empty()
                    st.session_state.current_streaming_message = ""
                    def on_token_update_placeholder(token: str):
                        st.session_state.current_streaming_message += token
                        message_placeholder.markdown(f"**{agent.name}**: {st.session_state.current_streaming_message}⏳")
                    # Generate response with streaming
                    response_text = agent.streaming_respond(discussion_topic, current_agent_response_context, on_token_update_placeholder)
                    # Update placeholder with final message
                    message_placeholder.markdown(f"**{agent.name}**: {response_text}")

                    # Add to conversation
                    response_message = {
                        "timestamp": time.time(),
                        "sender": agent.name,
                        "message": response_text,
                        "role": agent.role
                    }
                    st.session_state.conversation.append(response_message)
                    agent.add_to_history(agent.name, response_text)

                # Project Manager Progress Tracking (at end of each round except last)
                if st.session_state.coordinator and hasattr(st.session_state.coordinator, 'archetype') and st.session_state.coordinator.archetype == "project_manager":
                    if round_num < discussion_rounds - 1:
                        with st.spinner(f"👑 {st.session_state.coordinator.name} is tracking progress for round {round_num + 1}..."):
                            progress_report = st.session_state.coordinator.track_progress(round_num + 1, discussion_rounds)
                            if progress_report:
                                st.session_state.conversation.append({
                                    "timestamp": time.time(),
                                    "sender": f"{st.session_state.coordinator.name} (Progress Report R{round_num + 1})",
                                    "message": f"Progress Report (End of Round {round_num + 1}):\n{json.dumps(progress_report, indent=2)}",
                                    "is_system": True
                                })
                                plan_adjustments = st.session_state.coordinator.adjust_plan(progress_report)
                                if plan_adjustments:
                                    st.session_state.conversation.append({
                                        "timestamp": time.time(),
                                        "sender": f"{st.session_state.coordinator.name} (Plan Adjustments R{round_num + 1})",
                                        "message": f"Plan Adjustments (End of Round {round_num + 1}):\n{json.dumps(plan_adjustments, indent=2)}",
                                        "is_system": True
                                    })

            # Final Coordinator Phase (after all rounds)
            if st.session_state.coordinator:
                # Update coordinator's history with the full conversation
                st.session_state.coordinator.conversation_history = []
                for msg in st.session_state.conversation:
                    if not msg.get("is_thinking", False) and not msg.get("is_system", False) and not msg.get("is_summary", False) and not msg.get("is_decision", False):
                        st.session_state.coordinator.add_to_history(msg["sender"], msg["message"])

                # Generate summary
                with st.spinner(f"👑 {st.session_state.coordinator.name} is preparing the summary..."):
                    summary = st.session_state.coordinator.summarize_discussion()
                summary_message = {
                    "timestamp": time.time(),
                    "sender": f"{st.session_state.coordinator.name} (Discussion Summary)",
                    "message": summary,
                    "is_summary": True
                }
                st.session_state.conversation.append(summary_message)

                # Generate final assessment
                with st.spinner(f"👑 {st.session_state.coordinator.name} is making a final assessment..."):
                    # Add a check to prevent AttributeError if make_decision method is missing
                    if hasattr(st.session_state.coordinator, 'make_decision'):
                        decision = st.session_state.coordinator.make_decision()
                    else:
                        # Fallback to summarize_discussion if make_decision is not available
                        logger.error("make_decision method not found in coordinator agent. Using summarize_discussion as fallback.")
                        decision = st.session_state.coordinator.summarize_discussion() + "\n\nNote: This is a summary rather than a full assessment due to a technical limitation."
                decision_message = {
                    "timestamp": time.time(),
                    "sender": f"{st.session_state.coordinator.name} (Discussion Assessment)",
                    "message": decision,
                    "is_decision": True
                }
                st.session_state.conversation.append(decision_message)

                # Generate final output
                st.markdown("---")
                st.subheader("✨ Final Generated Output ✨")
                
                final_output_placeholder = st.empty()
                st.session_state.current_streaming_message = ""
                def on_token_update_final_output(token: str):
                    st.session_state.current_streaming_message += token
                    final_output_placeholder.markdown(f"{st.session_state.current_streaming_message}⏳")
                with st.spinner(f"👑 {st.session_state.coordinator.name} is compiling the final output based on the original request..."):
                    final_output_text = st.session_state.coordinator.streaming_generate_final_output(
                        original_topic=discussion_topic,
                        full_conversation_history=st.session_state.conversation,
                        on_token=on_token_update_final_output
                    )
                
                final_output_placeholder.markdown(final_output_text)
                st.success("Final output generated!")

            st.success(f"Completed {discussion_rounds} rounds of discussion")

with col2:
    st.header("Conversation")
    
    # Display the conversation
    for i, msg in enumerate(st.session_state.conversation):
        is_thinking = msg.get("is_thinking", False)
        is_system = msg.get("is_system", False)
        is_summary = msg.get("is_summary", False)
        is_decision = msg.get("is_decision", False)
        
        if is_system:
            st.info(msg["message"])
        elif is_thinking:
            with st.expander(f"🧠 {msg['sender']}"):
                st.markdown(msg["message"])
        elif is_summary:
            st.subheader("Discussion Summary")
            st.success(msg["message"])
        elif is_decision:
            st.subheader("Discussion Assessment")
            st.warning(msg["message"])
        else:
            st.markdown(f"**{msg['sender']}**")
            st.markdown(msg["message"])
            st.markdown("---")

# Information and help
with st.expander("ℹ️ About this app"):
    st.markdown("""
    ### Multi-Agent Discussion System
    
    This app lets you create a panel of AI agents, each with different personalities, roles, and perspectives, to discuss any topic of your choice.
    
    **Requirements:**
    - Ollama must be running locally at http://localhost:11434
    - At least one model must be available in Ollama (e.g., llama3:latest)
    
    **How to use:**
    1. Create agents in the sidebar with different roles and personalities
    2. Or use the Auto-Generate Task Force feature to create a specialized team of agents for your topic
    3. Enter a discussion topic in the main panel
    4. Set the number of discussion rounds
    5. Click "Run Discussion" to start the conversation
    6. Optionally designate a coordinator agent to summarize and conclude
    
    **Features:**
    - **Dynamic Agent Generation**: The system uses a meta-prompt approach to create specialized agent teams tailored to any topic
    - **Custom Agent Roles**: Create manually or auto-generate agent teams for any domain
    - **Multi-Round Discussions**: See how agents interact and debate over multiple rounds
    - **Thinking Visibility**: View each agent's internal reasoning process
    - **Save/Load Teams**: Save your favorite agent combinations for later use
    
    **Tips:**
    - For complex topics, use 3-5 rounds of discussion
    - Include a coordinator agent to get summaries and conclusions
    - Try different agent combinations for diverse perspectives
    """) 