"""Coordinator agent implementation."""

import json
import logging
from typing import Dict, Any, List, Optional, Callable

from ma_discussion.agents.base import CustomAgent
from ma_discussion.services.ollama import OllamaService
from ma_discussion.services.wikipedia import WikipediaService
from ma_discussion.utils.json_io import extract_json_object

logger = logging.getLogger(__name__)

class CoordinatorAgent(CustomAgent):
    """Coordinator agent that manages discussions and generates summaries."""
    
    def __init__(
        self,
        name: str,
        archetype: str,
        model: str = "llama2",
        base_prompt: Optional[str] = None,
        ollama_service: Optional[OllamaService] = None,
        wikipedia_service: Optional[WikipediaService] = None
    ):
        """Initialize a coordinator agent.
        
        Args:
            name: Agent's name
            archetype: Coordinator's archetype (e.g., facilitator, mediator)
            model: Name of the Ollama model to use
            base_prompt: Optional custom base prompt
            ollama_service: Optional OllamaService instance
            wikipedia_service: Optional WikipediaService instance
            
        Raises:
            ValueError: If any required parameter is empty
        """
        if not archetype or not archetype.strip():
            raise ValueError("Coordinator archetype cannot be empty")
            
        self.archetype = archetype
        self.is_coordinator = True
        
        # Generate base prompt based on archetype if not provided
        if not base_prompt:
            base_prompt = self._generate_base_prompt()
            
        super().__init__(
            name=name,
            role=f"Coordinator ({archetype})",
            base_prompt=base_prompt,
            model=model,
            ollama_service=ollama_service,
            wikipedia_service=wikipedia_service
        )
        
        self.project_plan = None
        self.progress_tracking = {}
        self.conversation_history = []
        
    def _generate_base_prompt(self) -> str:
        """Generate a base prompt based on the coordinator's archetype.
        
        Returns:
            Generated base prompt
        """
        if self.archetype == "facilitator":
            return """You are a skilled discussion facilitator. Your role is to:
- Guide the conversation in a productive direction
- Ensure all participants have a chance to contribute
- Keep the discussion focused on the main topic
- Summarize key points and insights
- Help the group reach meaningful conclusions"""
        elif self.archetype == "mediator":
            return """You are an experienced mediator. Your role is to:
- Help resolve conflicts and disagreements
- Find common ground between different viewpoints
- Ensure discussions remain respectful and constructive
- Guide participants toward mutual understanding
- Facilitate compromise when needed"""
        elif self.archetype == "strategist":
            return """You are a strategic discussion leader. Your role is to:
- Identify key strategic implications
- Guide discussions toward actionable outcomes
- Help participants think long-term
- Connect different perspectives to form coherent strategies
- Ensure discussions lead to practical recommendations"""
        elif self.archetype == "project_manager":
            return """You are a project management expert. Your role is to:
- Break down complex tasks into manageable steps
- Track progress and identify potential issues
- Ensure discussions stay focused on project goals
- Help participants develop actionable plans
- Monitor and adjust plans based on progress"""
        else:
            return """You are a discussion coordinator. Your role is to:
- Guide the conversation effectively
- Ensure productive discussion
- Help participants reach meaningful conclusions
- Summarize key points and insights
- Facilitate decision-making"""
            
    def summarize_discussion(self) -> str:
        """Generate a summary of the discussion.
        
        Returns:
            Discussion summary
        """
        messages = [f"{msg['sender']}: {msg['message']}" for msg in self.conversation_history]
        conversation_text = "\n".join(messages)
        
        prompt = f"""As a {self.archetype} coordinator, review the following discussion and provide a comprehensive summary:

{conversation_text}

Your summary should:
1. Highlight the main points discussed
2. Identify key insights and conclusions
3. Note areas of agreement and disagreement
4. Suggest potential next steps

Summary:"""
        
        try:
            return self._stream_response(prompt)
        except Exception as e:
            logger.error(f"Error generating discussion summary: {str(e)}")
            return f"I encountered an error while processing: {str(e)}"
            
    def make_decision(self) -> str:
        """Make a final decision or assessment based on the discussion.
        
        Returns:
            Final decision or assessment
        """
        messages = [f"{msg['sender']}: {msg['message']}" for msg in self.conversation_history]
        conversation_text = "\n".join(messages)
        
        prompt = f"""As a {self.archetype} coordinator, review the following discussion and provide a final assessment:

{conversation_text}

Your assessment should:
1. Evaluate the quality and depth of the discussion
2. Identify the most valuable contributions
3. Assess whether the discussion achieved its goals
4. Provide recommendations for future discussions

Assessment:"""
        
        try:
            return self._stream_response(prompt)
        except Exception as e:
            logger.error(f"Error generating final assessment: {str(e)}")
            return f"I encountered an error while processing: {str(e)}"
            
    def streaming_generate_final_output(
        self,
        original_topic: str,
        full_conversation_history: List[Dict[str, str]],
        on_token: Optional[Callable[[str], None]] = None
    ) -> str:
        """Generate a final output based on the original request and discussion.
        
        Args:
            original_topic: The original discussion topic or request
            full_conversation_history: Complete conversation history
            on_token: Optional callback for token streaming
            
        Returns:
            Generated final output
        """
        messages = []
        for msg in full_conversation_history:
            if not msg.get("is_thinking", False) and not msg.get("is_system", False):
                sender = msg.get("sender", "Unknown")
                content = msg.get("message", "")
                messages.append(f"{sender}: {content}")
        
        conversation_text = "\n".join(messages)
        
        prompt = f"""As a {self.archetype} coordinator, you need to generate a final output that directly addresses the original request:

Original Request: {original_topic}

The discussion that took place:
{conversation_text}

Based on this discussion, generate a clear, well-structured, and comprehensive response to the original request.
Your response should:
1. Directly address all aspects of the original request
2. Incorporate relevant insights from the discussion
3. Provide practical and actionable information
4. Be well-organized and easy to understand

Final Output:"""
        
        try:
            return self._stream_response(prompt, on_token)
        except Exception as e:
            logger.error(f"Error generating final output: {str(e)}")
            return f"I encountered an error while processing: {str(e)}"
            
    def break_down_task(self, task: str) -> Dict[str, Any]:
        """Break down a task into a structured project plan.
        
        Args:
            task: The task to break down
            
        Returns:
            Project plan as a dictionary
        """
        try:
            if not self.is_coordinator or self.archetype != "project_manager":
                return {"error": "Only project manager coordinators can break down tasks"}
            
            prompt = f"""As a project management coordinator, break down the following task into a detailed project plan.

Task: {task}

IMPORTANT: You must respond with ONLY a valid JSON object. No other text, explanations, or markdown formatting.
The response must start with {{ and end with }}. Do not include ```json or any other formatting.

Required JSON structure:
{{
    "project_name": "Name of the project",
    "objectives": [
        "First objective",
        "Second objective"
    ],
    "timeline": {{
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "milestones": [
            {{
                "name": "First milestone",
                "description": "Description of first milestone",
                "due_date": "YYYY-MM-DD",
                "dependencies": ["Dependency 1", "Dependency 2"]
            }}
        ]
    }},
    "resources": {{
        "required_skills": ["Skill 1", "Skill 2"],
        "tools": ["Tool 1", "Tool 2"],
        "constraints": ["Constraint 1", "Constraint 2"]
    }},
    "risk_management": {{
        "potential_risks": [
            {{
                "description": "Risk description",
                "impact": "Risk impact",
                "mitigation": "Mitigation strategy"
            }}
        ]
    }}
}}

Remember:
1. The response must be a single JSON object
2. No text before or after the JSON
3. No markdown formatting or code blocks
4. Must start with {{ and end with }}
5. Use proper JSON formatting with quotes around strings
6. Arrays should use square brackets []
7. Objects should use curly braces {{}}"""
            
            response = self._stream_response(prompt)
            
            # Clean up the response
            cleaned_response = response.strip()
            
            # Extract the JSON object
            start = cleaned_response.find('{')
            end = cleaned_response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = cleaned_response[start:end]
                
                # Remove any remaining formatting
                json_str = (
                    json_str
                    .replace('\n', '')  # Remove newlines
                    .replace('\\n', '')  # Remove escaped newlines
                    .replace('\t', '')  # Remove tabs
                    .replace('\\t', '')  # Remove escaped tabs
                    .replace('  ', ' ')  # Normalize spaces
                )
                
                try:
                    plan = json.loads(json_str)
                    if isinstance(plan, dict):
                        required_keys = {"project_name", "objectives", "timeline", "resources", "risk_management"}
                        if all(key in plan for key in required_keys):
                            self.project_plan = plan
                            return plan
                        else:
                            return {"error": "Missing required keys in project plan"}
                    else:
                        return {"error": "Project plan must be a JSON object"}
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse project plan JSON: {str(e)}")
                    logger.error(f"JSON string was: {json_str}")
                    return {"error": f"Invalid JSON format: {str(e)}"}
            else:
                return {"error": "No valid JSON object found in response"}
        except Exception as e:
            logger.error(f"Error breaking down task: {str(e)}")
            return {"error": f"Error breaking down task: {str(e)}"}
            
    def track_progress(self, current_round: int, total_rounds: int) -> Dict[str, Any]:
        """Track progress of the discussion.
        
        Args:
            current_round: Current round number
            total_rounds: Total number of rounds
            
        Returns:
            Progress tracking dictionary
        """
        try:
            if not self.project_plan:
                return {"error": "No project plan available"}
            
            progress = {
                "round": current_round,
                "total_rounds": total_rounds,
                "completion_percentage": (current_round / total_rounds) * 100,
                "objectives_status": {},
                "timeline_status": {
                    "on_track": True,
                    "delayed_milestones": []
                },
                "resource_status": {
                    "available": [],
                    "missing": []
                },
                "risk_status": {
                    "active_risks": [],
                    "mitigated_risks": []
                }
            }
            
            # Update progress tracking
            self.progress_tracking = progress
            return progress
        except Exception as e:
            logger.error(f"Error tracking progress: {str(e)}")
            return {"error": f"Error tracking progress: {str(e)}"}
        
    def adjust_plan(self, progress: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust the project plan based on progress.
        
        Args:
            progress: Progress tracking dictionary
            
        Returns:
            Updated project plan
        """
        try:
            if not self.project_plan:
                return {"error": "No project plan available"}
            
            prompt = f"""As a project management coordinator, review the current progress and suggest adjustments.

Current Project Plan:
{json.dumps(self.project_plan, indent=2)}

Progress Report:
{json.dumps(progress, indent=2)}

IMPORTANT: You must respond with ONLY a valid JSON object. No other text, explanations, or markdown formatting.
The response must start with {{ and end with }}. Do not include ```json or any other formatting.

Required JSON structure:
{{
    "modified_objectives": [
        {{
            "original": "Original objective text",
            "modified": "Modified objective text",
            "reason": "Reason for modification"
        }}
    ],
    "timeline_adjustments": [
        {{
            "milestone": "Milestone name",
            "original_date": "YYYY-MM-DD",
            "new_date": "YYYY-MM-DD",
            "reason": "Reason for adjustment"
        }}
    ],
    "resource_adjustments": [
        {{
            "type": "Resource type (e.g., skill, tool)",
            "original": "Original resource",
            "modified": "Modified resource",
            "reason": "Reason for adjustment"
        }}
    ],
    "risk_adjustments": [
        {{
            "original_risk": "Original risk description",
            "modified_risk": "Modified risk description",
            "reason": "Reason for adjustment"
        }}
    ]
}}

Remember:
1. The response must be a single JSON object
2. No text before or after the JSON
3. No markdown formatting or code blocks
4. Must start with {{ and end with }}
5. Use proper JSON formatting with quotes around strings
6. Arrays should use square brackets []
7. Objects should use curly braces {{}}"""
            
            response = self._stream_response(prompt)
            
            # Clean up the response
            cleaned_response = response.strip()
            
            # Extract the JSON object
            start = cleaned_response.find('{')
            end = cleaned_response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = cleaned_response[start:end]
                
                # Remove any remaining formatting
                json_str = (
                    json_str
                    .replace('\n', '')  # Remove newlines
                    .replace('\\n', '')  # Remove escaped newlines
                    .replace('\t', '')  # Remove tabs
                    .replace('\\t', '')  # Remove escaped tabs
                    .replace('  ', ' ')  # Normalize spaces
                )
                
                try:
                    adjustments = json.loads(json_str)
                    if isinstance(adjustments, dict):
                        required_keys = {"modified_objectives", "timeline_adjustments", "resource_adjustments", "risk_adjustments"}
                        if all(key in adjustments for key in required_keys):
                            return adjustments
                        else:
                            return {"error": "Missing required keys in plan adjustments"}
                    else:
                        return {"error": "Plan adjustments must be a JSON object"}
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse plan adjustments JSON: {str(e)}")
                    logger.error(f"JSON string was: {json_str}")
                    return {"error": f"Invalid JSON format: {str(e)}"}
            else:
                return {"error": "No valid JSON object found in response"}
        except Exception as e:
            logger.error(f"Error adjusting plan: {str(e)}")
            return {"error": f"Error adjusting plan: {str(e)}"} 