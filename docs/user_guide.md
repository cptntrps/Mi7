# User Guide

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Ollama running locally (`http://localhost:11434`)
- At least one model available in Ollama (e.g., `llama3:latest`)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/cptntrps/Mi7.git
cd Mi7
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Streamlit app:
```bash
streamlit run agent_discussion_app.py
```

2. Access the app in your browser:
- Local URL: `http://localhost:8501`
- Network URL: Will be displayed in the terminal

## Using the Application

### Creating Agents

#### Manual Agent Creation
1. In the sidebar, click "Add New Agent"
2. Fill in the agent details:
   - Name: A unique identifier
   - Role: The agent's expertise or perspective
   - Instructions: Specific guidance for the agent
3. Choose a personality template or create a custom one
4. Click "Create Agent" to add it to the discussion

#### Auto-Generate Task Force
1. Enter your discussion topic
2. Click "Auto-Generate Task Force"
3. The system will create a specialized team of agents
4. Review and modify the generated agents if needed

### Setting Up Discussions

1. Enter your discussion topic in the main panel
2. Set the number of discussion rounds (3-5 recommended)
3. Toggle "Show Agent Thinking" for detailed insights
4. Designate a coordinator agent (optional but recommended)
5. Click "Run Discussion" to begin

### Managing Discussions

#### During Discussion
- Watch agents interact and debate
- See their thinking process (if enabled)
- View Wikipedia lookups and research
- Monitor progress through discussion rounds

#### Coordinator Functions
- Summarizes the discussion
- Makes final assessments
- Generates structured outputs
- Tracks progress and adjusts plans

### Saving and Loading Teams

#### Save a Team
1. Create your desired agents
2. Click "Save Current Team"
3. Enter a name for the team
4. Click "Save"

#### Load a Team
1. Click "Load Team"
2. Select a saved team from the dropdown
3. Click "Load"

## Best Practices

### Agent Creation
- Give agents clear, focused roles
- Provide specific, detailed instructions
- Use diverse perspectives for rich discussions
- Include domain experts for technical topics

### Discussion Setup
- Use 3-5 rounds for complex topics
- Enable agent thinking for deeper insights
- Include a coordinator for structured output
- Start with clear, specific topics

### Team Composition
- Balance expertise levels
- Mix different viewpoints
- Include both specialists and generalists
- Consider topic requirements

## Example Use Cases

### 1. Technical Planning
```
Topic: Design a new mobile app architecture
Agents:
- Frontend Developer
- Backend Engineer
- UX Designer
- Security Expert
- Project Manager (Coordinator)
Rounds: 4
```

### 2. Creative Brainstorming
```
Topic: Generate marketing campaign ideas
Agents:
- Creative Director
- Market Researcher
- Social Media Expert
- Brand Strategist
- Campaign Manager (Coordinator)
Rounds: 3
```

### 3. Problem Solving
```
Topic: Improve customer service response time
Agents:
- Customer Service Manager
- Process Analyst
- Technology Consultant
- Training Specialist
- Operations Director (Coordinator)
Rounds: 5
```

## Troubleshooting

### Common Issues

1. Connection Error
```
Error: Could not connect to Ollama server
Solution: Ensure Ollama is running at http://localhost:11434
```

2. Model Not Found
```
Error: Model not available
Solution: Pull the required model using 'ollama pull model_name'
```

3. Agent Creation Failed
```
Error: Invalid agent configuration
Solution: Check name uniqueness and role requirements
```

### Performance Tips

1. Memory Management
- Clear conversation history periodically
- Limit the number of active agents
- Use appropriate discussion rounds

2. Response Speed
- Choose efficient models
- Optimize prompt lengths
- Use streaming responses

3. Wikipedia Lookups
- Be specific with search terms
- Handle rate limiting
- Cache common lookups

## Advanced Features

### Custom Agent Templates
```python
{
    "name": "Template Name",
    "base_prompt": "Role and behavior definition",
    "personality_traits": ["trait1", "trait2"],
    "expertise_areas": ["area1", "area2"]
}
```

### Project Management
```python
{
    "project_tracking": {
        "milestones": ["m1", "m2"],
        "progress": "percentage",
        "adjustments": ["adj1", "adj2"]
    }
}
```

### API Integration
```python
{
    "services": {
        "ollama": "text generation",
        "wikipedia": "information lookup",
        "custom": "your_service"
    }
}
```

## Support and Resources

### Getting Help
- Check the technical documentation
- Review example use cases
- Search common issues
- Contact support team

### Additional Resources
- API Documentation
- Configuration Guide
- Development Guide
- Best Practices Guide 