# Scientific Paper Scraper

A Python tool for scraping and analyzing scientific papers from arXiv and PubMed. The tool uses natural language processing techniques to generate summaries of paper abstracts.

## Features

- Asynchronous paper search from multiple sources:
  - arXiv
  - PubMed
- Automatic text summarization using NLP techniques
- Clean and modular architecture
- Easy to extend for additional sources
- Simple command-line interface
- Automatic saving of search results in JSON format

## Project Structure

```
paper-scraper/
├── src/
│   ├── models/          # Data models
│   ├── scrapers/        # Source-specific scrapers
│   ├── utils/           # Utility functions
│   ├── config.py        # Configuration settings
│   └── paper_scraper.py # Main scraper logic
├── main.py             # Command-line interface
├── data/               # Data storage
│   ├── processed/      # Processed search results in JSON format
│   └── raw/           # Raw data storage
└── logs/               # Log files
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/paper-scraper.git
cd paper-scraper
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Usage

The script can be run in several ways:

1. Default execution (searches for "artificial intelligence" with 5 results per source):
```bash
python main.py
```

2. Search for a specific topic:
```bash
python main.py -s "machine learning"
# or
python main.py --search "machine learning"
```

3. Specify maximum number of results per source:
```bash
python main.py -m 10
# or
python main.py --max 10
```

4. Combine both options:
```bash
python main.py -s "deep learning" -m 7
```

5. View help and available options:
```bash
python main.py --help
```

Example output:
```
Searching for articles about: artificial intelligence
--------------------------------------------------

Searching on arXiv...
Searching on PubMed...

Found X articles:
--------------------------------------------------

Article 1:
Title: Example Paper Title
Authors: Author 1, Author 2
Source: arxiv
URL: http://example.com

Summary:
Brief summary of the paper's abstract...

Resultados salvos em: data/processed/search_artificial_intelligence_20240321_123456.json
```

## Configuration

The project uses a centralized configuration system in `src/config.py`. Key settings include:

- API endpoints and parameters
- Text processing parameters
- Logging configuration

## Dependencies

Main dependencies:
- aiohttp: For asynchronous HTTP requests
- beautifulsoup4: For HTML parsing
- nltk: For natural language processing
- pydantic: For data validation
- python-dotenv: For environment variables
- tenacity: For retry logic

## Directory Structure

- `src/models/`: Contains data models for papers
- `src/scrapers/`: Source-specific scraper implementations
- `src/utils/`: Utility functions for text processing and logging
- `main.py`: Command-line interface
- `data/`: Storage for downloaded papers and metadata
- `logs/`: Log files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Data Storage

Search results are automatically saved in the `data/processed` directory in JSON format. Each file is named with the following pattern:
```
search_[query]_[timestamp].json
```

For example:
- `search_artificial_intelligence_20240321_123456.json`
- `search_machine_learning_20240321_124500.json`

The JSON files contain all paper information including:
- Title
- Authors
- Abstract
- URL
- Source
- Summary (if available) 