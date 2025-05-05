"""
arXiv scraper module.

This module implements the arXiv paper scraper, which searches and retrieves
papers from the arXiv API.
"""

from typing import List
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib.parse

from .base import BaseScraper
from src.models.paper import Paper
from src.config import API_CONFIG

class ArxivScraper(BaseScraper):
    """
    Scraper for arXiv papers.
    
    This class implements the arXiv-specific paper scraping functionality,
    including search and parsing of arXiv XML responses.
    """
    
    def __init__(self):
        """Initialize the arXiv scraper."""
        super().__init__('arxiv')
    
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for papers on arXiv.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Paper]: List of matching papers
        """
        # Prepare search parameters
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': min(max_results, self.config['max_results']),
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        # Make request to arXiv API
        response_text = await self._make_request(
            self.config['base_url'],
            params
        )
        
        # Parse XML response
        root = ET.fromstring(response_text)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Extract papers
        papers = []
        for entry in root.findall('.//atom:entry', namespace):
            try:
                paper_data = {
                    'title': entry.find('atom:title', namespace).text,
                    'authors': [
                        author.find('atom:name', namespace).text
                        for author in entry.findall('atom:author', namespace)
                    ],
                    'abstract': entry.find('atom:summary', namespace).text,
                    'url': entry.find('atom:id', namespace).text,
                    'published': datetime.strptime(
                        entry.find('atom:published', namespace).text,
                        '%Y-%m-%dT%H:%M:%SZ'
                    ),
                    'source': 'arxiv'
                }
                papers.append(self._parse_paper(paper_data))
            except (AttributeError, ValueError) as e:
                print(f"Error parsing paper: {e}")
                continue
            
        return papers[:max_results]
    
    def _parse_paper(self, data: dict) -> Paper:
        """
        Parse arXiv paper data into Paper object.
        
        Args:
            data (dict): Raw paper data from arXiv
            
        Returns:
            Paper: Parsed paper object
        """
        return Paper(
            title=data['title'],
            authors=data['authors'],
            abstract=data['abstract'],
            url=data['url'],
            published=data['published'],
            source=data['source']
        ) 