# OpenSAFELY Projects Semantic Search

A Streamlit web application that scrapes approved projects from [OpenSAFELY](https://www.opensafely.org/approved-projects/) and enables semantic search using AI-powered embeddings.

## Features

- 🔄 **Web Scraping**: Automatically scrapes all approved projects from OpenSAFELY
- 🔍 **Semantic Search**: Uses sentence transformers to understand query meaning, not just keywords
- 🎯 **Relevance Scoring**: Shows how relevant each result is to your query
- 💾 **Caching**: Saves scraped data and search index for fast subsequent searches
- 🎨 **Clean UI**: Modern Streamlit interface for easy interaction

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or navigate to the repository:
```bash
cd opensafely-project-rag
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Streamlit App

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

### First Time Setup

1. Click **"Scrape Projects"** in the sidebar to fetch all projects from OpenSAFELY
2. Wait for the scraping and indexing to complete (may take a few minutes)
3. Start searching!

### Searching

- Enter natural language queries like:
  - "COVID-19 vaccine effectiveness in elderly patients"
  - "Mental health outcomes during pandemic"
  - "Diabetes medication adherence"

- The search understands context and meaning, so you can search by:
  - Topic or condition
  - Research methods
  - Patient populations
  - Outcomes of interest

### Using the Scraper Standalone

To scrape projects without the Streamlit UI:

```bash
python scraper.py
```

This will save projects to `opensafely_projects.json`

### Using Semantic Search Standalone

To test the search engine in the terminal:

```bash
python semantic_search.py
```

## Project Structure

```
opensafely-project-rag/
├── app.py                      # Main Streamlit application
├── scraper.py                  # Web scraper for OpenSAFELY projects
├── semantic_search.py          # Semantic search engine
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── opensafely_projects.json    # Scraped projects (generated)
└── search_index.pkl           # Search index cache (generated)
```

## How It Works

### 1. Web Scraping

The scraper (`scraper.py`) uses:
- `requests` with proper headers to fetch pages
- `BeautifulSoup` to parse HTML
- Retry logic for reliability
- Rate limiting to be respectful to the server

### 2. Semantic Search

The search engine (`semantic_search.py`) uses:
- **Sentence Transformers**: Converts text to numerical embeddings
- **Model**: `all-MiniLM-L6-v2` (fast and accurate)
- **Cosine Similarity**: Finds semantically similar projects
- **Caching**: Stores embeddings for fast subsequent searches

### 3. Streamlit Interface

The app (`app.py`) provides:
- Data management (scrape/load)
- Search interface
- Results display with relevance scores
- Project details and metadata

## Troubleshooting

### Scraping Issues

If scraping fails:
- The website might be blocking automated requests
- Check your internet connection
- The website structure might have changed
- You may need to adjust the scraper code

### Search Not Working

If search isn't working:
- Make sure you've scraped or loaded projects first
- Check that `opensafely_projects.json` exists and contains data
- Try re-indexing by scraping again

### Dependencies Issues

If you have issues installing dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## Technical Details

### Dependencies

- **streamlit**: Web interface framework
- **beautifulsoup4**: HTML parsing
- **requests**: HTTP client
- **sentence-transformers**: Semantic embeddings
- **numpy**: Numerical operations
- **pandas**: Data manipulation (if needed)
- **chromadb**: Vector database (optional future enhancement)

### Model Information

The default model is `all-MiniLM-L6-v2`:
- **Size**: ~80MB
- **Speed**: Fast (~3000 sentences/sec on CPU)
- **Quality**: Good balance for semantic search
- **Embeddings**: 384 dimensions

You can change the model in `semantic_search.py` by modifying the `model_name` parameter.

## Future Enhancements

Potential improvements:
- [ ] Use ChromaDB for scalable vector storage
- [ ] Add filters (date, status, authors)
- [ ] Export search results
- [ ] Highlight matching sections in results
- [ ] Add more metadata extraction
- [ ] Implement incremental updates
- [ ] Add project comparison feature
- [ ] Support for multiple languages

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## Acknowledgments

- [OpenSAFELY](https://www.opensafely.org/) for making project data accessible
- [Sentence Transformers](https://www.sbert.net/) for the semantic search models
- [Streamlit](https://streamlit.io/) for the web framework
