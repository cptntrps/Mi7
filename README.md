# Multi-Agent Discussion System

A powerful system for orchestrating discussions between multiple AI agents, enabling collaborative problem-solving and complex task completion.

## Features

- **Multi-Agent Coordination**: Orchestrate discussions between multiple AI agents with different roles and expertise
- **Task Breakdown**: Automatically break down complex tasks into manageable subtasks
- **Dynamic Team Formation**: Create and manage teams of agents based on task requirements
- **Real-time Discussion**: Stream agent responses in real-time for interactive discussions
- **Wikipedia Integration**: Agents can look up information from Wikipedia to enhance their knowledge
- **State Management**: Robust state management for tracking discussions and agent configurations
- **Modern UI**: Clean and intuitive Streamlit-based user interface

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/cptntrps/Mi7.git
cd Mi7
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run agent_discussion_app.py
```

4. Open your browser and navigate to `http://localhost:8501`

## Prerequisites

- Python 3.8+
- Ollama server running locally (default: http://localhost:11434)
- Internet connection for Wikipedia lookups

## Documentation

- [User Guide](docs/user_guide.md) - How to use the system
- [Technical Documentation](docs/technical.md) - System architecture and implementation details
- [Development Guide](docs/development.md) - Contributing and development workflow

## Example Usage

1. Create a task force:
   - Add a coordinator agent
   - Add specialist agents based on task requirements
   - Configure agent roles and capabilities

2. Start a discussion:
   - Input your task or question
   - Watch agents collaborate in real-time
   - Review and iterate on the solutions

3. Manage discussions:
   - Track conversation history
   - Export discussion results
   - Save and load agent configurations

## Project Structure

```
Mi7/
├── docs/                    # Documentation
├── ma_discussion/          # Main package
│   ├── agents/            # Agent implementations
│   ├── services/         # External services
│   ├── ui/              # User interface
│   ├── utils/           # Utilities
│   └── tests/           # Test files
├── agent_discussion_app.py  # Main entry point
├── requirements.txt         # Dependencies
└── pyproject.toml          # Project configuration
```

## Contributing

We welcome contributions! Please see our [Development Guide](docs/development.md) for details on:
- Setting up your development environment
- Our coding standards
- The development workflow
- How to submit pull requests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Issue Tracker](https://github.com/cptntrps/Mi7/issues)
- [Documentation](docs/)

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Ollama](https://ollama.ai/)
- Wikipedia integration via [Wikipedia-API](https://wikipedia-api.readthedocs.io/) 