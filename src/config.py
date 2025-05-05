"""
Configuration module for the scientific paper scraper.

This module provides centralized configuration settings for the application,
including API endpoints, timeouts, and other parameters.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
LOG_DIR = BASE_DIR / 'logs'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# API Configuration
API_CONFIG: Dict[str, Any] = {
    'arxiv': {
        'base_url': 'http://export.arxiv.org/api/query',
        'max_results': 100,
        'timeout': 30,
        'retry_attempts': 3,
        'retry_delay': 5
    },
    'pubmed': {
        'base_url': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils',
        'max_results': 100,
        'timeout': 30,
        'retry_attempts': 3,
        'retry_delay': 5
    }
}

# Text Processing Configuration
TEXT_PROCESSING_CONFIG: Dict[str, Any] = {
    'summary': {
        'num_sentences': 3,
        'min_sentence_length': 10,
        'max_sentence_length': 100
    },
    'keywords': {
        'num_keywords': 10,
        'min_word_length': 3
    }
}

# Logging Configuration
LOGGING_CONFIG: Dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'filename': str(LOG_DIR / 'scraper.log')
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
} 