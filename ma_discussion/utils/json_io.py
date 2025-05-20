"""Utilities for handling JSON parsing and cleaning."""

import json
import re
import logging
import os
from typing import Any, Optional, Union, Dict, List

from ma_discussion.constants import (
    JSON_BLOCK_START_PATTERN,
    JSON_BLOCK_END_PATTERN,
    JSON_ARRAY_START_PATTERN,
    JSON_ARRAY_END_PATTERN,
)

logger = logging.getLogger(__name__)

def clean_json_block(text: str) -> str:
    """Clean a text block containing JSON by removing markdown and explanatory text.
    
    Args:
        text: Raw text that may contain JSON within markdown code blocks
        
    Returns:
        Cleaned JSON string
    """
    # Remove markdown code block markers
    text = re.sub(JSON_BLOCK_START_PATTERN, "", text)
    text = re.sub(JSON_BLOCK_END_PATTERN, "", text)
    
    # Strip whitespace
    text = text.strip()
    
    # If text appears to be a JSON array, clean array markers
    if text.startswith("[") and text.endswith("]"):
        text = re.sub(JSON_ARRAY_START_PATTERN, "[", text)
        text = re.sub(JSON_ARRAY_END_PATTERN, "]", text)
    
    return text

def safe_load(text: str, default: Any = None) -> Optional[Union[Dict, List, Any]]:
    """Safely parse JSON from text, with fallback to default value.
    
    Args:
        text: Text containing JSON
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON object or default value
    """
    try:
        # First try parsing as is
        return json.loads(text)
    except json.JSONDecodeError:
        # Clean and try again
        cleaned = clean_json_block(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON after cleaning: {str(e)}")
            return default

def extract_json_array(text: str) -> Optional[List]:
    """Extract a JSON array from text that may contain other content.
    
    Args:
        text: Text that may contain a JSON array
        
    Returns:
        Extracted JSON array or None if not found/invalid
    """
    # Find content between first [ and last ]
    array_match = re.search(r"\[(.*)\]", text, re.DOTALL)
    if not array_match:
        return None
        
    try:
        array_text = f"[{array_match.group(1)}]"
        return json.loads(array_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON array: {str(e)}")
        return None

def extract_json_object(text: str) -> Optional[Dict]:
    """Extract a JSON object from text that may contain other content.
    
    Args:
        text: Text that may contain a JSON object
        
    Returns:
        Extracted JSON object or None if not found/invalid
    """
    # Find content between first { and last }
    object_match = re.search(r"\{(.*)\}", text, re.DOTALL)
    if not object_match:
        return None
        
    try:
        object_text = f"{{{object_match.group(1)}}}"
        return json.loads(object_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON object: {str(e)}")
        return None

def save_json(data: Union[Dict, List], filepath: str) -> None:
    """Save data to a JSON file.
    
    Args:
        data: Data to save
        filepath: Path to save the file
        
    Raises:
        Exception: If saving fails
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save JSON to {filepath}: {str(e)}")
        raise

def load_json(filepath: str) -> Optional[Union[Dict, List]]:
    """Load data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Loaded data or None if loading fails
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"JSON file not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {filepath}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {str(e)}")
        return None 