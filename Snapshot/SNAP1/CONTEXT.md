# Multi-Agent Discussion System Context

## Overview
This is a Streamlit-based multi-agent discussion system that uses Ollama LLMs to create and manage teams of AI agents that can discuss any topic. The system is designed to be flexible, allowing users to create custom agents with specific roles and behaviors.

## Core Components

### 1. Agent System Architecture

#### Base Agent Class (`CustomAgent`)
- **Features**:
  - Name and role assignment
  - Custom base prompts/instructions
  - Conversation history tracking
  - Private thinking process
  - Response generation
  - Ollama integration
  - Error handling and retries

#### Coordinator Agent (`CoordinatorAgent`)
- **Features**:
  - Discussion summarization
  - Consensus building
  - Final decision making
  - Inherits all base agent capabilities

### 2. Task Force Generation

#### Meta-Prompt System
- Two-stage agent generation:
  1. Generates scenario-specific prompt using meta-prompt
  2. Uses generated prompt to create agent team
- Outputs JSON-formatted agent configurations
- Supports 3-7 diverse agents per team

#### Agent Configuration
- Each agent has:
  - Unique name
  - Specific role/title
  - Custom behavioral prompt
  - Model selection (defaults to llama3:latest)

### 3. User Interface (Streamlit)

#### Main Features
- Agent creation and management
- Topic/discussion input
- Real-time conversation display
- Agent interaction controls
- Coordinator summary and decisions
- Expandable agent thoughts

#### Session Management
- Persistent agent configurations
- Conversation history
- State management
- Error handling

### 4. Integration Points

#### Ollama Integration
- Local API endpoint (http://localhost:11434/api)
- Model selection support
- Request timeout handling
- Error recovery

#### Data Persistence
- Task force configurations
- Conversation history
- Agent states

## Technical Details

### Dependencies
- streamlit
- requests
- logging
- json
- typing
- enum

### Error Handling
- Connection retries
- Timeout management
- JSON parsing validation
- User feedback

### Performance Considerations
- Conversation history windowing
- Request timeout limits
- Response caching
- State management

## Usage Flow

1. **Setup**
   - Start Ollama server
   - Launch Streamlit app
   - Configure agents

2. **Discussion**
   - Input topic
   - Run discussion rounds
   - View agent interactions
   - Get coordinator summaries

3. **Management**
   - Add/remove agents
   - Modify agent behaviors
   - Save/load configurations
   - Monitor system status

## Future Enhancements

### Planned Features
- Multi-round debates
- Agent voting systems
- Enhanced memory systems
- Custom model support
- Advanced prompt engineering
- Performance optimizations

### Potential Improvements
- Real-time collaboration
- WebSocket integration
- Advanced error recovery
- Extended model support
- Enhanced UI/UX
- Analytics and insights

## Development Notes

### Best Practices
- Error handling
- Logging
- Code organization
- Type hints
- Documentation

### Known Limitations
- Ollama dependency
- Single-threaded execution
- Memory constraints
- Model limitations

## Security Considerations

### Current Measures
- Local API access
- Error message sanitization
- Input validation
- State management

### Future Security
- Authentication
- Rate limiting
- Input sanitization
- Access control 