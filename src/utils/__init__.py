"""
Pacote de utilitários
"""

from .text_processing import (
    setup_nltk,
    clean_text,
    extract_keywords,
    calculate_sentence_scores,
    generate_summary
)

__all__ = [
    'setup_nltk',
    'clean_text',
    'extract_keywords',
    'calculate_sentence_scores',
    'generate_summary'
] 