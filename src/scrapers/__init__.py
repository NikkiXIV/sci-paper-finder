"""
Scrapers para diferentes fontes de artigos científicos
"""

from .arxiv import ArxivScraper
from .pubmed import PubMedScraper

__all__ = ['ArxivScraper', 'PubMedScraper'] 