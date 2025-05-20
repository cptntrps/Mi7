"""Pre-compiled regex patterns used throughout the package."""

import re
from ma_discussion.constants import (
    WIKI_LOOKUP_PATTERN,
    JSON_BLOCK_START_PATTERN,
    JSON_BLOCK_END_PATTERN,
    JSON_ARRAY_START_PATTERN,
    JSON_ARRAY_END_PATTERN,
)

# Compile patterns for better performance
WIKI_LOOKUP_RE = re.compile(WIKI_LOOKUP_PATTERN)
JSON_BLOCK_START_RE = re.compile(JSON_BLOCK_START_PATTERN)
JSON_BLOCK_END_RE = re.compile(JSON_BLOCK_END_PATTERN)
JSON_ARRAY_START_RE = re.compile(JSON_ARRAY_START_PATTERN)
JSON_ARRAY_END_RE = re.compile(JSON_ARRAY_END_PATTERN)

def extract_wiki_lookup_term(text: str) -> str:
    """Extract the search term from a WIKI_LOOKUP command in text.
    
    Args:
        text: Text containing a WIKI_LOOKUP command
        
    Returns:
        Extracted search term or empty string if not found
    """
    match = WIKI_LOOKUP_RE.search(text)
    if match:
        # Return the first non-None group (quoted or unquoted term)
        return next((g for g in match.groups() if g is not None), "").strip()
    return "" 