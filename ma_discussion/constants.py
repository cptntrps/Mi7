"""Constants used throughout the ma_discussion package."""

# Service URLs and endpoints
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATE_ENDPOINT = "/api/generate"
OLLAMA_TAGS_ENDPOINT = "/api/tags"

# Default model settings
DEFAULT_MODEL = "llama3:latest"
DEFAULT_MODELS = [DEFAULT_MODEL]

# Agent configuration
DEFAULT_COORDINATOR_ARCHETYPE = "facilitator"
COORDINATOR_ARCHETYPES = ["facilitator", "director", "strategist", "catalyst", "project_manager"]

# Regex patterns
WIKI_LOOKUP_PATTERN = r"\[\[(.*?)\]\]"
JSON_BLOCK_START_PATTERN = r"```(?:json)?\s*"
JSON_BLOCK_END_PATTERN = r"\s*```"
JSON_ARRAY_START_PATTERN = r"^.*?\["
JSON_ARRAY_END_PATTERN = r"\].*?$"

# UI configuration
PAGE_TITLE = "Multi-Agent Discussion System"
PAGE_LAYOUT = "wide"

# File paths
DATA_DIR = "data"
DEFAULT_TASKFORCE_FILE = "taskforce.json"

# API configuration
WIKIPEDIA_USER_AGENT = "MultiAgentDiscussionSystem/0.1"
REQUEST_TIMEOUT = 30  # seconds

# Logging configuration
LOG_FORMAT = "%(levelname)s:%(name)s:%(message)s"
LOG_LEVEL = "INFO"
