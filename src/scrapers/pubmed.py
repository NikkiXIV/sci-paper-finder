"""
PubMed scraper module.

This module implements the PubMed paper scraper, which searches and retrieves
papers from the PubMed API using E-utilities.
"""

from typing import List
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib.parse
import json

from .base import BaseScraper
from src.models.paper import Paper
from src.config import API_CONFIG
from src.utils.text_processing import generate_summary, setup_nltk

class PubMedScraper(BaseScraper):
    """
    Scraper for PubMed papers.
    
    This class implements the PubMed-specific paper scraping functionality,
    including search and parsing of PubMed XML responses.
    """
    
    def __init__(self):
        """Initialize the PubMed scraper."""
        super().__init__('pubmed')
        # Setup NLTK resources
        setup_nltk()
    
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for papers on PubMed.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Paper]: List of matching papers
        """
        # First, search for paper IDs with improved relevance
        search_params = {
            'db': 'pubmed',
            'term': f'({query}[Title/Abstract]) AND (hasabstract[text])',  # Search in title/abstract and require abstract
            'retmax': min(max_results * 2, self.config['max_results']),  # Get more results for better filtering
            'retmode': 'json',
            'sort': 'relevance'  # Sort by relevance instead of date
        }
        
        search_response_text = await self._make_request(
            f"{self.config['base_url']}/esearch.fcgi",
            search_params
        )
        
        # Parse JSON response
        search_response = json.loads(search_response_text)
        
        # Extract paper IDs
        paper_ids = search_response['esearchresult']['idlist']
        
        if not paper_ids:
            return []
        
        # Then, fetch details for each paper
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(paper_ids),
            'retmode': 'xml'
        }
        
        fetch_response_text = await self._make_request(
            f"{self.config['base_url']}/efetch.fcgi",
            fetch_params
        )
        
        # Parse XML response
        root = ET.fromstring(fetch_response_text)
        namespace = {'pubmed': 'http://www.ncbi.nlm.nih.gov/pubmed'}
        
        # Extract papers
        papers = []
        for article in root.findall('.//pubmed:PubmedArticle', namespace):
            try:
                paper_data = self._extract_paper_data(article, namespace)
                
                # Skip papers with very short abstracts
                if not paper_data['abstract'] or len(paper_data['abstract'].split()) < 10:
                    continue
                    
                papers.append(self._parse_paper(paper_data))
            except (AttributeError, ValueError) as e:
                print(f"Error parsing paper: {e}")
                continue
        
        # Sort papers by relevance (title match first, then abstract match)
        papers.sort(key=lambda p: (
            query.lower() not in p.title.lower(),  # True comes after False
            query.lower() not in p.abstract.lower()
        ))
            
        return papers[:max_results]
    
    def _extract_paper_data(self, article: ET.Element, namespace: dict) -> dict:
        """
        Extract paper data from PubMed XML element.
        
        Args:
            article (ET.Element): XML element containing paper data
            namespace (dict): XML namespace mapping
            
        Returns:
            dict: Extracted paper data
        """
        # Extract basic information
        title = article.find('.//pubmed:ArticleTitle', namespace).text
        abstract = article.find('.//pubmed:AbstractText', namespace).text or ''
        
        # Extract authors
        authors = []
        for author in article.findall('.//pubmed:Author', namespace):
            last_name = author.find('pubmed:LastName', namespace)
            fore_name = author.find('pubmed:ForeName', namespace)
            if last_name is not None and fore_name is not None:
                authors.append(f"{last_name.text} {fore_name.text}")
        
        # Extract publication date
        pub_date = article.find('.//pubmed:PubDate', namespace)
        year = pub_date.find('pubmed:Year', namespace).text
        month = pub_date.find('pubmed:Month', namespace).text
        day = pub_date.find('pubmed:Day', namespace).text or '01'
        published = datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d')
        
        # Extract URL
        pmid = article.find('.//pubmed:PMID', namespace).text
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        
        return {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'url': url,
            'published': published,
            'source': 'pubmed',
            'summary': generate_summary(abstract) if abstract else None
        }
    
    def _parse_paper(self, data: dict) -> Paper:
        """
        Parse PubMed paper data into Paper object.
        
        Args:
            data (dict): Raw paper data from PubMed
            
        Returns:
            Paper: Parsed paper object
        """
        return Paper(
            title=data['title'],
            authors=data['authors'],
            abstract=data['abstract'],
            url=data['url'],
            published=data['published'],
            source=data['source'],
            summary=data.get('summary')
        ) 