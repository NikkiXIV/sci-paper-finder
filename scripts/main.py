"""
Main script to run the scientific paper scraper.
"""

import asyncio
import argparse
from src.paper_scraper import PaperScraper

async def main(query: str = "artificial intelligence", max_results: int = 5):
    # Initialize the scraper
    scraper = PaperScraper()
    
    print(f"\nSearching for articles about: {query}")
    print("-" * 50)
    
    # Search arXiv papers
    print("\nSearching on arXiv...")
    arxiv_papers = await scraper.search_arxiv(query, max_results=max_results)
    
    # Search PubMed papers
    print("\nSearching on PubMed...")
    pubmed_papers = await scraper.search_pubmed(query, max_results=max_results)
    
    # Combine results
    all_papers = arxiv_papers + pubmed_papers
    
    # Display results
    print(f"\nFound {len(all_papers)} articles:")
    print("-" * 50)
    
    for i, paper in enumerate(all_papers, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {paper.title}")
        print(f"Authors: {', '.join(paper.authors)}")
        print(f"Source: {paper.source}")
        print(f"URL: {paper.url}")
        
        # Generate abstract summary
        if paper.abstract:
            summary = scraper.generate_summary(paper.abstract)
            print(f"\nSummary:")
            print(summary)
        else:
            print("\nSummary not available")
        
        print("-" * 50)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Search for scientific papers in arXiv and PubMed"
    )
    parser.add_argument(
        "-s", "--search",
        type=str,
        default="artificial intelligence",
        help="Search query (default: 'artificial intelligence')"
    )
    parser.add_argument(
        "-m", "--max",
        type=int,
        default=5,
        help="Maximum number of results per source (default: 5)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the script
    asyncio.run(main(args.search, args.max)) 