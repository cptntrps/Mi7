# Multi-Agent Discussion System

A sophisticated multi-agent discussion system that enables AI agents with different personalities, roles, and perspectives to engage in meaningful conversations on any topic.

## Features

- **Dynamic Agent Generation**: Create specialized agent teams tailored to any topic
- **Custom Agent Roles**: Create manually or auto-generate agent teams for any domain
- **Multi-Round Discussions**: See how agents interact and debate over multiple rounds
- **Thinking Visibility**: View each agent's internal reasoning process
- **Save/Load Teams**: Save your favorite agent combinations for later use
- **Project Management**: Coordinator agents can break down tasks and track progress
- **Wikipedia Integration**: Agents can look up information during discussions

## Requirements

- Python 3.8+
- Ollama running locally at http://localhost:11434
- At least one model available in Ollama (e.g., llama3:latest)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Mi7.git
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

## Usage

1. Start the Streamlit app:
```bash
streamlit run agent_discussion_app.py
```

2. Access the app in your browser at http://localhost:8501

3. Create agents in the sidebar with different roles and personalities, or use the Auto-Generate Task Force feature

4. Enter a discussion topic and set the number of discussion rounds

5. Click "Run Discussion" to start the conversation

## Project Structure

- `ma_discussion/`: Main package directory
  - `agents/`: Agent implementations
  - `services/`: External service integrations (Ollama, Wikipedia)
  - `ui/`: Streamlit UI components
  - `utils/`: Utility functions
- `tests/`: Test files
- `agent_discussion_app.py`: Main application entry point

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Example Agents

Here are some example agent configurations you might want to try:

1. **Skeptic**
   - Role: Critical Thinker
   - Personality: Questions assumptions, requires evidence, finds flaws in arguments

2. **Optimist**
   - Role: Possibility Thinker  
   - Personality: Focuses on opportunities, creative solutions, and positive outcomes

3. **Devil's Advocate**
   - Role: Challenger
   - Personality: Takes opposing viewpoints to test the strength of arguments

4. **Coordinator**
   - Role: Discussion Leader
   - Personality: Guides conversation, summarizes points, helps reach conclusions

## Tips

- For complex topics, use 3-5 rounds of discussion
- Include a variety of perspectives for richer discussions
- The coordinator agent is optional but helpful for summarizing
- Experiment with different personality combinations

## Acknowledgments

- Based on a collaborative agent framework for document classification
- Uses Ollama for local LLM inference 