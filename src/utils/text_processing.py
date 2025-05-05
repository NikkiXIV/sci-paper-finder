"""
Text processing utilities for scientific papers.

This module provides functions for processing and analyzing text from scientific papers,
including text cleaning, keyword extraction, and summary generation using NLP techniques.
"""

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from typing import List, Dict, Tuple
import re
import os

def setup_nltk():
    """
    Download required NLTK resources.
    
    Downloads:
    - punkt: For sentence tokenization
    - stopwords: For common word filtering
    - averaged_perceptron_tagger: For part-of-speech tagging
    """
    # Desabilita mensagens de download
    nltk.downloader._show_info = lambda *args, **kwargs: None
    
    # Lista de recursos necessários
    resources = ['punkt', 'stopwords', 'averaged_perceptron_tagger']
    
    # Baixa cada recurso silenciosamente
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            print(f"Aviso: Erro ao baixar recurso {resource}: {e}")
            continue

def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text (str): Input text to clean
        
    Returns:
        str: Cleaned text with:
            - Converted to lowercase
            - Removed special characters
            - Normalized whitespace
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text

def extract_keywords(text: str, num_keywords: int = 10) -> List[str]:
    """
    Extract key terms from text using frequency analysis.
    
    Args:
        text (str): Input text
        num_keywords (int): Number of keywords to extract
        
    Returns:
        List[str]: List of extracted keywords
    """
    # Tokenize and clean
    words = word_tokenize(clean_text(text))
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if w not in stop_words]
    
    # Calculate word frequencies
    fdist = FreqDist(words)
    
    # Return most common words
    return [word for word, _ in fdist.most_common(num_keywords)]

def calculate_sentence_scores(sentences: List[str], keywords: List[str]) -> Dict[str, float]:
    """
    Calculate relevance scores for sentences based on keyword presence.
    
    Args:
        sentences (List[str]): List of sentences to score
        keywords (List[str]): List of keywords to look for
        
    Returns:
        Dict[str, float]: Dictionary mapping sentences to their scores
    """
    scores = {}
    
    for sentence in sentences:
        score = 0
        words = word_tokenize(clean_text(sentence))
        
        # Calculate score based on keyword presence
        for word in words:
            if word in keywords:
                score += 1
                
        # Normalize by sentence length
        scores[sentence] = score / len(words) if words else 0
        
    return scores

def generate_summary(text: str, num_sentences: int = 3) -> str:
    """
    Generate a summary of the input text using extractive summarization.
    
    Args:
        text (str): Input text to summarize
        num_sentences (int): Number of sentences in the summary
        
    Returns:
        str: Generated summary
    """
    # Tokenize into sentences
    sentences = sent_tokenize(text)
    
    # Extract keywords
    keywords = extract_keywords(text)
    
    # Calculate sentence scores
    scores = calculate_sentence_scores(sentences, keywords)
    
    # Select top sentences
    top_sentences = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    
    # Reconstruct summary maintaining original order
    summary_sentences = [s for s, _ in sorted(top_sentences, key=lambda x: sentences.index(x[0]))]
    
    return ' '.join(summary_sentences) 