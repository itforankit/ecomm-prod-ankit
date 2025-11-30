"""
ETL module for data extraction, transformation, and loading operations.
"""

from prod_assistant.etl.base_scraper import BaseScraper
from prod_assistant.etl.data_scrapper import FlipkartScraper
from prod_assistant.etl.data_ingestion import DataIngestion
from prod_assistant.etl.scraping_service import ScrapingService

__all__ = [
    "BaseScraper",
    "FlipkartScraper",
    "DataIngestion",
    "ScrapingService",
]
