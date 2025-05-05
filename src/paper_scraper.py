import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import os
from pathlib import Path
from dotenv import load_dotenv
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field
import arxiv
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor
import lxml
import re
import string

# Configuração do logger
logger.add("paper_scraper.log", rotation="500 MB")

class Paper(BaseModel):
    """Modelo para representar um paper científico"""
    title: str
    authors: List[str]
    abstract: str
    url: str
    published: str
    source: str
    categories: Optional[List[str]] = None
    relevance_score: Optional[float] = None
    citations: Optional[int] = None
    summary: Optional[str] = None

class PaperScraper:
    def __init__(self):
        """
        Inicializa o scraper com configurações necessárias
        """
        # Configuração do NLTK
        self._setup_nltk()
        
        # Configuração do cache
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Configuração do executor para operações paralelas
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _setup_nltk(self):
        """Configura recursos necessários do NLTK"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')

    def _clean_text(self, text: str) -> str:
        """Limpa o texto removendo caracteres especiais e normalizando espaços"""
        # Remove caracteres especiais e números
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        # Remove espaços extras
        text = ' '.join(text.split())
        return text.lower()

    def _extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extrai as palavras-chave mais relevantes do texto"""
        # Tokeniza e limpa o texto
        words = word_tokenize(self._clean_text(text))
        stop_words = set(stopwords.words('english'))
        
        # Remove stopwords e palavras muito curtas
        words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Calcula frequência das palavras
        fdist = FreqDist(words)
        
        # Retorna as palavras mais frequentes
        return [word for word, _ in fdist.most_common(num_keywords)]

    def _calculate_sentence_scores(self, sentences: List[str], keywords: List[str]) -> Dict[str, float]:
        """Calcula a pontuação de cada sentença baseada em palavras-chave e posição"""
        sentence_scores = {}
        
        for i, sentence in enumerate(sentences):
            # Pontuação baseada em palavras-chave
            keyword_score = sum(1 for word in word_tokenize(sentence.lower()) if word in keywords)
            
            # Pontuação baseada na posição (primeiras sentenças são mais importantes)
            position_score = 1.0 / (i + 1)
            
            # Pontuação baseada no comprimento (sentenças muito curtas ou muito longas são penalizadas)
            length_score = 1.0 / (abs(len(sentence.split()) - 15) + 1)
            
            # Pontuação final
            sentence_scores[sentence] = keyword_score * 0.5 + position_score * 0.3 + length_score * 0.2
        
        return sentence_scores

    def generate_summary(self, text: str, num_sentences: int = 3) -> str:
        """
        Gera um resumo do texto usando técnicas de NLP
        """
        try:
            # Divide o texto em sentenças
            sentences = sent_tokenize(text)
            
            if len(sentences) <= num_sentences:
                return text
            
            # Extrai palavras-chave
            keywords = self._extract_keywords(text)
            
            # Calcula pontuação para cada sentença
            sentence_scores = self._calculate_sentence_scores(sentences, keywords)
            
            # Seleciona as sentenças com maior pontuação
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
            
            # Ordena as sentenças na ordem original
            summary_sentences = [sentence for sentence, _ in sorted(top_sentences, key=lambda x: sentences.index(x[0]))]
            
            return ' '.join(summary_sentences)
        except Exception as e:
            logger.error(f"Erro ao gerar resumo NLP: {str(e)}")
            return text[:500] + "..."  # Retorna os primeiros 500 caracteres em caso de erro

    def _safe_get_text(self, element, default=""):
        """Extrai texto de um elemento BeautifulSoup de forma segura"""
        if element and hasattr(element, 'text'):
            return element.text.strip()
        return default

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def search_arxiv(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Busca assíncrona de artigos no arXiv
        """
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )

            papers = []
            for result in search.results():
                try:
                    paper = Paper(
                        title=result.title,
                        authors=[author.name for author in result.authors],
                        abstract=result.summary,
                        url=result.entry_id,
                        published=result.published.isoformat(),
                        categories=result.categories,
                        source='arxiv'
                    )
                    papers.append(paper)
                except Exception as e:
                    logger.error(f"Erro ao processar artigo do arXiv: {str(e)}")
                    continue
            
            return papers
        except Exception as e:
            logger.error(f"Erro ao buscar no arXiv: {str(e)}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def search_pubmed(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Busca assíncrona de artigos no PubMed
        """
        try:
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
            search_url = f"{base_url}esearch.fcgi"
            
            async with aiohttp.ClientSession() as session:
                params = {
                    'db': 'pubmed',
                    'term': query,
                    'retmax': max_results,
                    'retmode': 'json',
                    'sort': 'date'
                }
                
                async with session.get(search_url, params=params) as response:
                    data = await response.json()
                
                papers = []
                for pmid in data['esearchresult']['idlist']:
                    try:
                        fetch_url = f"{base_url}efetch.fcgi"
                        fetch_params = {
                            'db': 'pubmed',
                            'id': pmid,
                            'retmode': 'xml'
                        }
                        
                        async with session.get(fetch_url, params=fetch_params) as paper_response:
                            text = await paper_response.text()
                            soup = BeautifulSoup(text, 'lxml-xml')
                            
                            # Extrai informações de forma segura
                            title = self._safe_get_text(soup.find('ArticleTitle'))
                            if not title:  # Pula se não encontrar título
                                continue
                                
                            authors = []
                            for author in soup.find_all('Author'):
                                last_name = self._safe_get_text(author.find('LastName'))
                                fore_name = self._safe_get_text(author.find('ForeName'))
                                if last_name or fore_name:
                                    authors.append(f"{last_name} {fore_name}".strip())
                            
                            abstract = self._safe_get_text(soup.find('AbstractText'))
                            published = self._safe_get_text(soup.find('PubDate'))
                            
                            paper = Paper(
                                title=title,
                                authors=authors if authors else ["Autor Desconhecido"],
                                abstract=abstract if abstract else "Resumo não disponível",
                                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                                published=published if published else "Data não disponível",
                                source='pubmed'
                            )
                            papers.append(paper)
                    except Exception as e:
                        logger.error(f"Erro ao processar artigo do PubMed {pmid}: {str(e)}")
                        continue
                
                return papers
        except Exception as e:
            logger.error(f"Erro ao buscar no PubMed: {str(e)}")
            return []

    def calculate_relevance(self, papers: List[Paper], query: str) -> List[Paper]:
        """
        Calcula a relevância dos papers baseado na similaridade do texto
        """
        if not papers:
            return papers
            
        try:
            vectorizer = TfidfVectorizer()
            texts = [paper.abstract for paper in papers]
            tfidf_matrix = vectorizer.fit_transform([query] + texts)
            
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            
            for i, paper in enumerate(papers):
                paper.relevance_score = float(similarities[0][i])
            
            return sorted(papers, key=lambda x: x.relevance_score, reverse=True)
        except Exception as e:
            logger.error(f"Erro ao calcular relevância: {str(e)}")
            return papers

    def save_to_json(self, papers: List[Paper], filename: str):
        """
        Salva os papers em um arquivo JSON
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([paper.model_dump() for paper in papers], f, ensure_ascii=False, indent=2)
            logger.info(f"Papers salvos em {filename}")
        except Exception as e:
            logger.error(f"Erro ao salvar papers: {str(e)}")

async def main():
    # Configuração do scraper
    scraper = PaperScraper()
    
    # Lista de queries para busca
    queries = [
        "artificial intelligence machine learning",
        "technology innovation",
        "computer science",
        "software engineering",
        "data science",
        "robotics automation",
        "cybersecurity",
        "cloud computing",
        "internet of things",
        "blockchain technology"
    ]
    
    all_papers = []
    
    # Busca assíncrona em múltiplas fontes para cada query
    for query in queries:
        logger.info(f"\nBuscando artigos sobre: {query}")
        
        arxiv_papers, pubmed_papers = await asyncio.gather(
            scraper.search_arxiv(query),
            scraper.search_pubmed(query)
        )
        
        logger.info(f"Encontrados {len(arxiv_papers)} artigos no arXiv")
        logger.info(f"Encontrados {len(pubmed_papers)} artigos no PubMed")
        
        # Combina resultados
        query_papers = arxiv_papers + pubmed_papers
        
        if query_papers:
            # Calcula relevância
            relevant_papers = scraper.calculate_relevance(query_papers, query)
            all_papers.extend(relevant_papers)
    
    if not all_papers:
        logger.warning("Nenhum artigo encontrado")
        return
    
    # Remove duplicatas baseado no título
    seen_titles = set()
    unique_papers = []
    for paper in all_papers:
        if paper.title.lower() not in seen_titles:
            seen_titles.add(paper.title.lower())
            unique_papers.append(paper)
    
    # Ordena todos os papers por relevância
    unique_papers.sort(key=lambda x: x.relevance_score or 0, reverse=True)
    
    # Gera resumos para os top 5 papers
    for i, paper in enumerate(unique_papers[:5]):
        logger.info(f"\nPaper {i+1}:")
        logger.info(f"Título: {paper.title}")
        logger.info(f"Fonte: {paper.source}")
        logger.info(f"Score de Relevância: {paper.relevance_score:.2f}")
        
        # Gera resumo
        paper.summary = scraper.generate_summary(paper.abstract)
        logger.info(f"Resumo gerado: {paper.summary}")
        logger.info("-" * 80)
    
    # Salva resultados
    scraper.save_to_json(unique_papers, "papers_results.json")

if __name__ == "__main__":
    asyncio.run(main()) 