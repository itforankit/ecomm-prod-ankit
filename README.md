# E-Commerce Product Assistant

A product assistant application that extracts data from e-commerce websites and stores it in a vector database for intelligent product recommendations and queries.

## Features

- **Web Scraping**: Extract product data including titles, prices, ratings, and reviews from e-commerce websites
- **Vector Database Integration**: Store scraped data in AstraDB vector store for similarity search
- **REST API**: FastAPI endpoints for scraping and vector database operations
- **Streamlit UI**: User-friendly interface for scraping and data management

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Configuration

Set the following environment variables (or create a `.env` file):

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
ASTRA_DB_API_ENDPOINT=your_astradb_endpoint
ASTRA_DB_APPLICATION_TOKEN=your_astradb_token
ASTRA_DB_KEYSPACE=your_keyspace
```

## Usage

### API Server

Start the FastAPI server:

```bash
uvicorn prod_assistant.api:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Scrape Data
```http
POST /api/v1/scraper/scrape
Content-Type: application/json

{
    "source": "flipkart",
    "queries": ["iphone 16", "samsung galaxy"],
    "max_products": 2,
    "review_count": 3,
    "save_to_csv": true
}
```

#### Generate Vector Database
```http
POST /api/v1/scraper/generate-vector-db
```

#### Complete Pipeline (Scrape + Vector DB)
```http
POST /api/v1/scraper/scrape-and-generate
Content-Type: application/json

{
    "source": "flipkart",
    "queries": ["laptop"],
    "max_products": 5,
    "review_count": 2
}
```

#### Get Supported Sources
```http
GET /api/v1/scraper/sources
```

### Streamlit UI

Run the Streamlit application:

```bash
streamlit run scrapper_ui.py
```

### Python SDK

```python
from prod_assistant.etl import ScrapingService

# Initialize the service
service = ScrapingService()

# Scrape data from Flipkart
data = service.scrape_data(
    source="flipkart",
    queries=["iphone 16"],
    max_products=2,
    review_count=3
)

# Generate vector database
service.generate_vector_db()

# Or run the complete pipeline
result = service.scrape_and_generate_vector_db(
    source="flipkart",
    queries=["laptop", "phone"],
    max_products=3,
    review_count=2
)
```

## Project Structure

```
prod_assistant/
├── api.py                 # FastAPI application entry point
├── etl/
│   ├── base_scraper.py    # Abstract base class for scrapers
│   ├── data_scrapper.py   # Flipkart scraper implementation
│   ├── data_ingestion.py  # Vector database ingestion
│   └── scraping_service.py # Orchestration service
├── router/
│   └── main.py            # API router with endpoints
├── retriever/
│   └── retrieval.py       # Vector store retrieval
├── utils/
│   ├── config_loader.py   # Configuration management
│   └── model_loader.py    # Model loading utilities
└── config/
    └── config.yaml        # Application configuration
```

## Extending the Scraper

To add support for a new e-commerce website, create a new scraper class that extends `BaseScraper`:

```python
from prod_assistant.etl.base_scraper import BaseScraper

class NewSiteScraper(BaseScraper):
    def scrape(self, query: str, **kwargs) -> list[dict]:
        # Implement scraping logic
        pass

    def save_to_csv(self, data: list, filename: str) -> str:
        # Implement CSV saving logic
        pass
```

Then register it in `ScrapingService`:

```python
# In scraping_service.py
SUPPORTED_SOURCES = ["flipkart", "newsite"]

def _get_scraper(self, source: str) -> BaseScraper:
    if source == "newsite":
        return NewSiteScraper(output_dir=self.output_dir)
    # ...
```

## License

Proprietary
