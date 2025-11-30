"""
Base web scraper module providing an abstract interface for web scraping operations.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseScraper(ABC):
    """
    Abstract base class for web scrapers.
    Provides a common interface for scraping data from different websites.
    """

    def __init__(self, output_dir: str = "data"):
        """
        Initialize the base scraper.

        Args:
            output_dir: Directory to store scraped data files.
        """
        self.output_dir = output_dir

    @abstractmethod
    def scrape(self, query: str, **kwargs) -> list[dict[str, Any]]:
        """
        Scrape data based on a search query.

        Args:
            query: Search query string.
            **kwargs: Additional scraping parameters.

        Returns:
            List of dictionaries containing scraped data.
        """
        pass

    @abstractmethod
    def save_to_csv(self, data: list, filename: str) -> str:
        """
        Save scraped data to a CSV file.

        Args:
            data: List of scraped data items.
            filename: Name of the output CSV file.

        Returns:
            Path to the saved CSV file.
        """
        pass
