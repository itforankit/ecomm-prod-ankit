"""
Scraping service module that orchestrates web scraping and vector database operations.
"""

import os
from typing import Any, Literal

from prod_assistant.etl.base_scraper import BaseScraper
from prod_assistant.etl.data_scrapper import FlipkartScraper
from prod_assistant.etl.data_ingestion import DataIngestion


class ScrapingService:
    """
    Service class that orchestrates web scraping and vector database generation.
    Provides a unified interface for extracting data from websites and storing
    it in a vector database.
    """

    SUPPORTED_SOURCES = ["flipkart"]

    def __init__(self, output_dir: str = "data"):
        """
        Initialize the scraping service.

        Args:
            output_dir: Directory to store scraped data files.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self._scrapers: dict[str, BaseScraper] = {}

    def _get_scraper(self, source: str) -> BaseScraper:
        """
        Get or create a scraper for the specified source.

        Args:
            source: Source website identifier.

        Returns:
            BaseScraper instance for the specified source.

        Raises:
            ValueError: If the source is not supported.
        """
        if source not in self.SUPPORTED_SOURCES:
            raise ValueError(
                f"Unsupported source: {source}. "
                f"Supported sources: {self.SUPPORTED_SOURCES}"
            )

        if source not in self._scrapers:
            if source == "flipkart":
                self._scrapers[source] = FlipkartScraper(output_dir=self.output_dir)

        return self._scrapers[source]

    def scrape_data(
        self,
        source: Literal["flipkart"],
        queries: list[str],
        max_products: int = 1,
        review_count: int = 2,
        save_to_csv: bool = True,
        filename: str = "product_reviews.csv",
    ) -> list[dict[str, Any]]:
        """
        Scrape data from a specified source website.

        Args:
            source: Source website to scrape from.
            queries: List of search queries.
            max_products: Maximum number of products per query.
            review_count: Number of reviews per product.
            save_to_csv: Whether to save the data to CSV.
            filename: Name of the output CSV file.

        Returns:
            List of scraped data dictionaries.
        """
        scraper = self._get_scraper(source)
        all_data: list[dict[str, Any]] = []

        for query in queries:
            results = scraper.scrape(
                query,
                max_products=max_products,
                review_count=review_count,
            )
            all_data.extend(results)

        # Remove duplicates based on product_id
        unique_products: dict[str, dict[str, Any]] = {}
        for item in all_data:
            product_id = item.get("product_id")
            if product_id and product_id not in unique_products:
                unique_products[product_id] = item

        final_data = list(unique_products.values())

        if save_to_csv and final_data:
            # Convert dict format back to list format for CSV saving
            csv_data = [
                [
                    item["product_id"],
                    item["product_title"],
                    item["rating"],
                    item["total_reviews"],
                    item["price"],
                    item["top_reviews"],
                ]
                for item in final_data
            ]
            filepath = os.path.join(self.output_dir, filename)
            scraper.save_to_csv(csv_data, filepath)

        return final_data

    def generate_vector_db(self) -> dict[str, Any]:
        """
        Generate vector database from the scraped data.

        Returns:
            Dictionary containing information about the ingestion result.

        Raises:
            Exception: If ingestion fails.
        """
        ingestion = DataIngestion()
        ingestion.run_pipeline()

        return {
            "status": "success",
            "message": "Data successfully ingested to vector database.",
        }

    def scrape_and_generate_vector_db(
        self,
        source: Literal["flipkart"],
        queries: list[str],
        max_products: int = 1,
        review_count: int = 2,
        filename: str = "product_reviews.csv",
    ) -> dict[str, Any]:
        """
        Complete pipeline: scrape data from website and generate vector database.

        Args:
            source: Source website to scrape from.
            queries: List of search queries.
            max_products: Maximum number of products per query.
            review_count: Number of reviews per product.
            filename: Name of the output CSV file.

        Returns:
            Dictionary containing scraping and ingestion results.
        """
        # Step 1: Scrape data
        scraped_data = self.scrape_data(
            source=source,
            queries=queries,
            max_products=max_products,
            review_count=review_count,
            save_to_csv=True,
            filename=filename,
        )

        if not scraped_data:
            return {
                "status": "error",
                "message": "No data was scraped.",
                "scraped_count": 0,
            }

        # Step 2: Generate vector database
        ingestion_result = self.generate_vector_db()

        return {
            "status": "success",
            "message": "Data scraped and ingested successfully.",
            "scraped_count": len(scraped_data),
            "scraped_data": scraped_data,
            "ingestion_result": ingestion_result,
        }
