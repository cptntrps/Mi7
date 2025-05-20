"""Tests for the Wikipedia service."""

import pytest
from unittest.mock import MagicMock, patch

from ma_discussion.services.wikipedia import WikipediaService
from ma_discussion.services.settings import ServiceSettings

@pytest.fixture
def settings():
    """Create test settings with proper user agent."""
    return ServiceSettings(
        wikipedia_user_agent="MultiAgentDiscussionSystem/0.1 (Test Suite; https://github.com/yourusername/ma_discussion)",
        wikipedia_language="en"
    )

@pytest.fixture
def wikipedia_service(settings):
    """Create a Wikipedia service instance with test settings."""
    return WikipediaService(settings=settings)

def test_init_with_settings(settings):
    """Test initializing service with custom settings."""
    service = WikipediaService(settings=settings)
    assert service.settings.wikipedia_user_agent == settings.wikipedia_user_agent
    assert service.settings.wikipedia_language == settings.wikipedia_language

def test_init_without_settings():
    """Test initializing service without settings."""
    service = WikipediaService()
    assert service.settings is not None
    assert service.settings.wikipedia_language == "en"

def test_get_summary_exact_match(wikipedia_service):
    """Test getting summary with exact page match."""
    # Mock the Wikipedia page
    mock_page = MagicMock()
    mock_page.exists.return_value = True
    mock_page.summary = "Test summary"
    wikipedia_service.wiki.page = MagicMock(return_value=mock_page)
    
    summary = wikipedia_service.get_summary("Test Page")
    assert summary == "Test summary"

def test_get_summary_search_match(wikipedia_service):
    """Test getting summary through search."""
    # Mock the Wikipedia page for initial query (no exact match)
    mock_no_match = MagicMock()
    mock_no_match.exists.return_value = False
    
    # Mock the search result and subsequent page
    mock_search_page = MagicMock()
    mock_search_page.exists.return_value = True
    mock_search_page.title = "Search Result"
    mock_search_page.summary = "Search summary"
    
    # Set up the mocks
    wikipedia_service.wiki.page = MagicMock(side_effect=[mock_no_match, mock_search_page])
    wikipedia_service.wiki.search = MagicMock(return_value=["Search Result"])
    
    summary = wikipedia_service.get_summary("Test Query")
    assert summary == "Search summary"

def test_get_summary_no_results(wikipedia_service):
    """Test getting summary with no results."""
    # Mock no exact match and no search results
    mock_page = MagicMock()
    mock_page.exists.return_value = False
    wikipedia_service.wiki.page = MagicMock(return_value=mock_page)
    wikipedia_service.wiki.search = MagicMock(return_value=[])
    
    summary = wikipedia_service.get_summary("Nonexistent Page")
    assert summary is None

def test_get_summary_with_language_override(wikipedia_service):
    """Test getting summary with language override."""
    # Mock the Wikipedia page
    mock_page = MagicMock()
    mock_page.exists.return_value = True
    mock_page.summary = "Test summary in Spanish"
    
    with patch("wikipediaapi.Wikipedia") as mock_wiki:
        mock_wiki.return_value.page.return_value = mock_page
        summary = wikipedia_service.get_summary("Test Page", lang="es")
        assert summary == "Test summary in Spanish"
        # Verify the language was used
        mock_wiki.assert_called_once()
        assert mock_wiki.call_args[1]["language"] == "es"

def test_get_summary_api_error(wikipedia_service):
    """Test handling of API errors."""
    wikipedia_service.wiki.page = MagicMock(side_effect=Exception("API Error"))
    
    summary = wikipedia_service.get_summary("Test Page")
    assert summary is None

def test_get_summary_search_error(wikipedia_service):
    """Test handling of search errors."""
    # Mock no exact match and search error
    mock_page = MagicMock()
    mock_page.exists.return_value = False
    wikipedia_service.wiki.page = MagicMock(return_value=mock_page)
    wikipedia_service.wiki.search = MagicMock(side_effect=Exception("Search Error"))
    
    summary = wikipedia_service.get_summary("Test Page")
    assert summary is None 