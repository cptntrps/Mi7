"""Wrapper service for Wikipedia API interactions."""

import logging
from typing import Optional
import wikipediaapi

from ma_discussion.services.settings import ServiceSettings, get_settings

logger = logging.getLogger(__name__)

class WikipediaService:
    """Service class for interacting with Wikipedia API."""
    
    def __init__(self, settings: Optional[ServiceSettings] = None):
        """Initialize the Wikipedia service with optional settings."""
        self.settings = settings or get_settings()
        self.wiki = wikipediaapi.Wikipedia(
            user_agent=self.settings.wikipedia_user_agent,
            language=self.settings.wikipedia_language
        )
    
    def get_summary(self, query: str, lang: Optional[str] = None) -> Optional[str]:
        """Get a Wikipedia page summary for the given query.
        
        Args:
            query: The search term
            lang: Optional language override
            
        Returns:
            Page summary if found, None otherwise
        """
        if lang:
            wiki = wikipediaapi.Wikipedia(
                user_agent=self.settings.wikipedia_user_agent,
                language=lang
            )
        else:
            wiki = self.wiki
            
        try:
            # First try exact match
            page = wiki.page(query)
            if page.exists():
                return page.summary
                
            # If no exact match, try search
            search_results = wiki.search(query)
            if search_results:
                # Get first result's page
                first_result = wiki.page(search_results[0])
                if first_result.exists():
                    logger.info(f"Wikipedia search for '{query}' found title: '{first_result.title}'")
                    return first_result.summary
                    
            logger.warning(f"No Wikipedia results found for: {query}")
            return None
            
        except Exception as e:
            logger.error(f"Wikipedia API error for query '{query}': {str(e)}")
            return None 