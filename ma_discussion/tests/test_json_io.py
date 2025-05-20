"""Tests for JSON I/O utilities."""

import json
import os
import pytest
from ma_discussion.utils.json_io import (
    clean_json_block,
    safe_load,
    extract_json_array,
    extract_json_object,
    save_json,
    load_json
)

def test_clean_json_block():
    """Test cleaning JSON blocks from text."""
    # Test markdown code block
    text = "```json\n{\"key\": \"value\"}\n```"
    assert clean_json_block(text) == '{"key": "value"}'
    
    # Test array with markers
    text = "[1, 2, 3]"
    assert clean_json_block(text) == "[1, 2, 3]"
    
    # Test whitespace
    text = "  \n{\"key\": \"value\"}\n  "
    assert clean_json_block(text) == '{"key": "value"}'

def test_safe_load():
    """Test safe JSON loading."""
    # Test valid JSON
    assert safe_load('{"key": "value"}') == {"key": "value"}
    
    # Test invalid JSON with default
    assert safe_load("invalid", default=[]) == []
    
    # Test JSON in markdown
    text = "```json\n{\"key\": \"value\"}\n```"
    assert safe_load(text) == {"key": "value"}

def test_extract_json_array():
    """Test JSON array extraction."""
    # Test valid array
    text = "Some text [1, 2, 3] more text"
    assert extract_json_array(text) == [1, 2, 3]
    
    # Test nested array
    text = "Text [[1, 2], [3, 4]] text"
    assert extract_json_array(text) == [[1, 2], [3, 4]]
    
    # Test invalid array
    assert extract_json_array("No array here") is None
    assert extract_json_array("[invalid, json]") is None

def test_extract_json_object():
    """Test JSON object extraction."""
    # Test valid object
    text = 'Text {"key": "value"} text'
    assert extract_json_object(text) == {"key": "value"}
    
    # Test nested object
    text = 'Text {"outer": {"inner": "value"}} text'
    assert extract_json_object(text) == {"outer": {"inner": "value"}}
    
    # Test invalid object
    assert extract_json_object("No object here") is None
    assert extract_json_object("{invalid: json}") is None

def test_save_and_load_json(tmp_path):
    """Test saving and loading JSON files."""
    # Test dictionary
    data = {"key": "value", "nested": {"inner": "value"}}
    filepath = os.path.join(tmp_path, "test.json")
    
    save_json(data, filepath)
    loaded = load_json(filepath)
    assert loaded == data
    
    # Test array
    data = [1, 2, {"key": "value"}]
    save_json(data, filepath)
    loaded = load_json(filepath)
    assert loaded == data

def test_save_json_creates_directory(tmp_path):
    """Test that save_json creates directories if needed."""
    filepath = os.path.join(tmp_path, "subdir", "test.json")
    data = {"key": "value"}
    
    save_json(data, filepath)
    assert os.path.exists(filepath)
    assert load_json(filepath) == data

def test_load_json_error_cases(tmp_path):
    """Test error handling in load_json."""
    # Test non-existent file
    assert load_json(os.path.join(tmp_path, "nonexistent.json")) is None
    
    # Test invalid JSON
    filepath = os.path.join(tmp_path, "invalid.json")
    with open(filepath, 'w') as f:
        f.write("invalid json")
    assert load_json(filepath) is None

def test_save_json_error(tmp_path):
    """Test error handling in save_json."""
    # Test permission error by creating a readonly directory
    readonly_dir = os.path.join(tmp_path, "readonly")
    os.makedirs(readonly_dir)
    os.chmod(readonly_dir, 0o444)  # Read-only
    
    filepath = os.path.join(readonly_dir, "test.json")
    with pytest.raises(Exception):
        save_json({"key": "value"}, filepath) 