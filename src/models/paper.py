"""
Data model for scientific papers.

This module defines the Paper class, which represents a scientific paper
with its metadata and content. The class uses Pydantic for data validation
and serialization.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class Paper(BaseModel):
    """
    Represents a scientific paper with its metadata and content.
    
    Attributes:
        title (str): The title of the paper
        authors (List[str]): List of author names
        abstract (str): The paper's abstract
        url (HttpUrl): URL to the paper's page
        published (datetime): Publication date
        source (str): Source of the paper (e.g., 'arxiv', 'pubmed')
        doi (Optional[str]): Digital Object Identifier
        keywords (Optional[List[str]]): List of keywords/tags
        summary (Optional[str]): Generated summary of the abstract
    """
    
    title: str
    authors: List[str]
    abstract: str
    url: HttpUrl
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