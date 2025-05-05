# Paper Finder

A powerful Python tool for discovering and analyzing scientific papers from multiple academic sources. This tool helps researchers and academics find relevant papers and automatically generates summaries of their abstracts using advanced Natural Language Processing (NLP) techniques.

## 🌟 Features

- **Multi-source Search**: Simultaneously search across multiple academic databases:
  - arXiv
  - PubMed
- **Smart Summarization**: Automatically generates concise summaries of paper abstracts using NLP
- **Asynchronous Processing**: Fast and efficient paper retrieval using async/await
- **Intelligent Relevance Scoring**: Papers are ranked based on relevance to your search query
- **Data Export**: Results are automatically saved in structured JSON format
- **Extensible Architecture**: Easy to add new paper sources and features

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/NikkiXIV/sci-paper-finder
cd sci-paper-finder
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

Search for papers with a simple command:

```bash
python main.py -s "machine learning" -m 10
```

Options:
- `-s, --search`: Search query (default: "artificial intelligence")
- `-m, --max`: Maximum results per source (default: 5)

## 📁 Project Structure

```
paper-finder/
├── src/
│   ├── models/          # Data models
│   ├── scrapers/        # Source-specific scrapers
│   ├── utils/           # Utility functions
│   └── config.py        # Configuration settings
├── data/               # Data storage
│   ├── processed/      # Processed results
│   └── raw/           # Raw data
└── logs/              # Log files
```

## 🔧 Configuration

The project uses a centralized configuration system in `src/config.py` for:
- API endpoints and parameters
- Text processing settings
- Logging configuration

## 📦 Dependencies

Main dependencies:
- `aiohttp`: Asynchronous HTTP requests
- `beautifulsoup4`: HTML parsing
- `nltk`: Natural language processing
- `pydantic`: Data validation
- `python-dotenv`: Environment variables
- `tenacity`: Retry logic

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📊 Data Storage

Search results are automatically saved in the `data/processed` directory in JSON format with the following naming pattern:
```
search_[query]_[timestamp].json
```

Each JSON file contains comprehensive paper information including:
- Title
- Authors
- Abstract
- URL
- Source
- Generated Summary
- Relevance Score 
