"""
Main script to run the scientific paper scraper.
"""

import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path
from src.scrapers.arxiv import ArxivScraper
from src.scrapers.pubmed import PubMedScraper
from src.config import DATA_DIR

def save_results(papers, query):
    """Salva os resultados da pesquisa em um arquivo JSON."""
    # Cria o diretório se não existir
    output_dir = DATA_DIR / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Gera nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_{query.replace(' ', '_')}_{timestamp}.json"
    output_file = output_dir / filename
    
    # Converte os papers para dicionário usando o método model_dump_json
    papers_data = [paper.model_dump_json() for paper in papers]
    
    # Salva em JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(papers_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nResultados salvos em: {output_file}")

async def main():
    parser = argparse.ArgumentParser(description='Search for scientific papers')
    parser.add_argument('-s', '--search', default="artificial intelligence",
                      help='Search term (default: "artificial intelligence")')
    parser.add_argument('-m', '--max', type=int, default=5,
                      help='Maximum number of results per source (default: 5)')
    
    args = parser.parse_args()
    
    print(f"Searching for articles about: {args.search}")
    print("-" * 50)
    
    # Initialize scrapers
    arxiv_scraper = ArxivScraper()
    pubmed_scraper = PubMedScraper()
    
    try:
        # Search papers
        print("Searching on arXiv...")
        arxiv_papers = await arxiv_scraper.search(args.search, args.max)
        
        print("Searching on PubMed...")
        pubmed_papers = await pubmed_scraper.search(args.search, args.max)
        
        # Combine results
        all_papers = arxiv_papers + pubmed_papers
        
        print(f"\nFound {len(all_papers)} articles:")
        print("-" * 50)
        
        # Display results
        for i, paper in enumerate(all_papers, 1):
            print(f"\nArticle {i}:")
            print(f"Title: {paper.title}")
            print(f"Authors: {', '.join(paper.authors)}")
            print(f"Source: {paper.source}")
            print(f"URL: {paper.url}")
            if paper.summary:
                print("\nSummary:")
                print(paper.summary)
            print("-" * 50)
        
        # Save results
        save_results(all_papers, args.search)
    
    finally:
        # Ensure scrapers are properly closed
        await arxiv_scraper.close()
        await pubmed_scraper.close()

if __name__ == "__main__":
    asyncio.run(main()) 