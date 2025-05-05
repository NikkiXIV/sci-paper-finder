"""
Base scraper module for scientific papers.

This module provides the base class for all paper scrapers, defining the common
interface and functionality that all scrapers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import aiohttp
import asyncio
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

from src.models.paper import Paper
from src.config import API_CONFIG

class BaseScraper(ABC):
    """
    Abstract base class for paper scrapers.
    
    This class defines the interface and common functionality for all paper scrapers.
    It handles HTTP requests, retries, and basic error handling.
    
    Attributes:
        source_name (str): Name of the source (e.g., 'arxiv', 'pubmed')
        config (dict): Configuration for this scraper
        session (Optional[aiohttp.ClientSession]): HTTP session for requests
    """
    
    def __init__(self, source_name: str):
        """
        Initialize the scraper.
        
        Args:
            source_name (str): Name of the source to scrape
        """
        self.source_name = source_name
        self.config = API_CONFIG[source_name]
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Create HTTP session when entering async context."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close HTTP session when exiting async context."""
        if self.session:
            await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(self, url: str, params: dict) -> dict:
        """
        Make HTTP request with retry logic.
        
        Args:
            url (str): URL to request
            params (dict): Query parameters
            
        Returns:
            dict: Response data
            
        Raises:
            aiohttp.ClientError: If request fails after retries
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for papers matching the query.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Paper]: List of matching papers
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement search()")
    
    @abstractmethod
    def _parse_paper(self, data: dict) -> Paper:
        """
        Parse raw paper data into Paper object.
        
        Args:
            data (dict): Raw paper data from source
            
        Returns:
            Paper: Parsed paper object
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _parse_paper()") 