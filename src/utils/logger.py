"""
Módulo de logging para o projeto
"""
import logging
import sys
from pathlib import Path

def setup_logger():
    """Configura e retorna um logger para o projeto"""
    logger = logging.getLogger('paper_scraper')
    logger.setLevel(logging.INFO)
    
    # Criar diretório de logs se não existir
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_dir / 'scraper.log')
    file_handler.setLevel(logging.INFO)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formato do log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Adicionar handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 