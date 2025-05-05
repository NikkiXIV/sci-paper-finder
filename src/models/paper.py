"""
Data model for scientific papers.

This module defines the Paper class, which represents a scientific paper
with its metadata and content. The class uses Pydantic for data validation
and serialization.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class Paper(BaseModel):
    """
    Represents a scientific paper with its metadata and content.
    
    Attributes:
        title (str): The title of the paper
        authors (List[str]): List of author names
        abstract (str): The paper's abstract
        url (str): URL to the paper's page
        published (datetime): Publication date
        source (str): Source of the paper (e.g., 'arxiv', 'pubmed')
        doi (Optional[str]): Digital Object Identifier
        keywords (Optional[List[str]]): List of keywords/tags
        summary (Optional[str]): Generated summary of the abstract
    """
    
    title: str
    authors: List[str]
    abstract: str
    url: str
    published: datetime
    source: str
    doi: Optional[str] = None
    keywords: Optional[List[str]] = None
    summary: Optional[str] = None

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    def model_dump_json(self) -> dict:
        """
        Convert the paper object to a JSON-serializable dictionary.
        
        Returns:
            dict: JSON-serializable dictionary representation of the paper
        """
        return {
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'url': self.url,
            'published': self.published.isoformat(),
            'source': self.source,
            'doi': self.doi,
            'keywords': self.keywords,
            'summary': self.summary
        } 