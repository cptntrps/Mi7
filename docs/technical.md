# Technical Documentation

## System Architecture

The Multi-Agent Discussion System is built using a modular architecture with the following main components:

### 1. Core Components

#### Agents (`ma_discussion/agents/`)
- `base.py`: Base agent class with core functionality
- `coordinator.py`: Special coordinator agent for managing discussions
- `factory.py`: Factory class for creating different types of agents

#### Services (`ma_discussion/services/`)
- `ollama.py`: Integration with Ollama for text generation
- `wikipedia.py`: Integration with Wikipedia for information lookup
- `settings.py`: Service configuration settings

#### UI Components (`ma_discussion/ui/`)
- `main.py`: Main discussion interface
- `sidebar.py`: Agent management interface
- `state.py`: Application state management

#### Utilities (`ma_discussion/utils/`)
- `json_io.py`: JSON handling utilities
- `regex.py`: Regular expression utilities

### 2. Agent System

#### Base Agent (`CustomAgent`)
- Handles basic agent functionality
- Manages conversation history
- Processes responses and thinking
- Integrates with Ollama and Wikipedia services

#### Coordinator Agent (`CoordinatorAgent`)
- Extends base agent functionality
- Manages project planning and tracking
- Provides discussion summaries and assessments
- Generates final outputs

#### Agent Factory
- Creates specialized agents based on roles
- Manages agent configurations
- Handles auto-generation of task forces

### 3. External Services

#### Ollama Integration
- Base URL: `http://localhost:11434`
- Endpoints:
  - `/api/generate`: Text generation
  - `/api/tags`: Model listing
- Streaming support for real-time responses

#### Wikipedia Integration
- Provides information lookup capability
- Supports agent research during discussions
- Handles search and summary retrieval

### 4. User Interface

#### Main Discussion Interface
- Topic input and configuration
- Discussion round management
- Real-time conversation display
- Agent thinking visualization

#### Sidebar Interface
- Agent creation and management
- Task force generation
- Agent role and personality configuration
- Team saving/loading

### 5. State Management

#### Application State
- Manages active agents
- Tracks conversation history
- Handles coordinator designation
- Maintains discussion configuration

## Implementation Details

### 1. Agent Response Flow
1. Agent receives discussion topic and context
2. Processes through thinking phase
3. Performs Wikipedia lookups if needed
4. Generates response using Ollama
5. Updates conversation history

### 2. Coordinator Functions
1. Project Planning
```json
{
    "project_name": "string",
    "objectives": ["string"],
    "timeline": {
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "milestones": [
            {
                "name": "string",
                "description": "string",
                "due_date": "YYYY-MM-DD",
                "dependencies": ["string"]
            }
        ]
    }
}
```

2. Progress Tracking
```json
{
    "round": "integer",
    "total_rounds": "integer",
    "completion_percentage": "float",
    "objectives_status": {},
    "timeline_status": {
        "on_track": "boolean",
        "delayed_milestones": []
    }
}
```

### 3. Error Handling
- JSON parsing with cleanup and validation
- Service connection error management
- Agent creation validation
- State consistency checks

### 4. Performance Considerations
- Streaming responses for real-time feedback
- Efficient Wikipedia lookup caching
- Optimized JSON processing
- Memory management for conversation history

## API Reference

### Agent API

```python
class CustomAgent:
    def __init__(self, name: str, role: str, base_prompt: str = None)
    def think(self, topic: str, context: dict) -> str
    def respond(self, topic: str, context: dict) -> str
    def streaming_respond(self, topic: str, context: dict, on_token: Callable) -> str
```

### Coordinator API

```python
class CoordinatorAgent(CustomAgent):
    def break_down_task(self, task: str) -> Dict[str, Any]
    def track_progress(self, current_round: int, total_rounds: int) -> Dict[str, Any]
    def adjust_plan(self, progress: Dict[str, Any]) -> Dict[str, Any]
    def summarize_discussion(self) -> str
    def make_decision(self) -> str
```

### Service API

```python
class OllamaService:
    def generate_text(self, prompt: str, model: str = "llama2") -> str
    def stream_text(self, prompt: str, model: str = "llama2") -> Iterator[str]

class WikipediaService:
    def search(self, query: str) -> Optional[str]
    def get_summary(self, title: str) -> Optional[str]
```

## Configuration

### Service Settings
```python
class ServiceSettings:
    ollama_url: str = "http://localhost:11434"
    ollama_timeout: int = 30
    ollama_model: str = "llama2"
    wikipedia_user_agent: str = "MultiAgentDiscussionSystem/0.1"
```

### Environment Variables
- `MADISC_OLLAMA_URL`: Ollama server URL
- `MADISC_OLLAMA_TIMEOUT`: Request timeout
- `MADISC_OLLAMA_MODEL`: Default model
- `MADISC_WIKIPEDIA_USER_AGENT`: User agent for Wikipedia API 