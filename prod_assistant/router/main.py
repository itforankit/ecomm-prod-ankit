"""
FastAPI router for scraping and vector database operations.
"""

from functools import lru_cache
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from prod_assistant.etl.scraping_service import ScrapingService


router = APIRouter(prefix="/api/v1/scraper", tags=["scraper"])


@lru_cache()
def get_scraping_service() -> ScrapingService:
    """
    Get or create a cached ScrapingService instance.

    Returns:
        Cached ScrapingService instance.
    """
    return ScrapingService()


class ScrapeRequest(BaseModel):
    """Request model for scraping data from websites."""

    source: Literal["flipkart"] = Field(
        default="flipkart",
        description="Source website to scrape from",
    )
    queries: list[str] = Field(
        ...,
        description="List of search queries",
        min_length=1,
    )
    max_products: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Maximum number of products per query",
    )
    review_count: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Number of reviews per product",
    )
    save_to_csv: bool = Field(
        default=True,
        description="Whether to save data to CSV file",
    )


class ScrapeResponse(BaseModel):
    """Response model for scraping operations."""

    status: str
    message: str
    scraped_count: int
    data: list[dict]


class VectorDBResponse(BaseModel):
    """Response model for vector database operations."""

    status: str
    message: str


class FullPipelineResponse(BaseModel):
    """Response model for the complete scraping and vector DB pipeline."""

    status: str
    message: str
    scraped_count: int
    data: list[dict]
    ingestion_result: dict


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_data(
    request: ScrapeRequest,
    service: ScrapingService = Depends(get_scraping_service),
) -> ScrapeResponse:
    """
    Scrape product data from a specified source website.

    This endpoint extracts product information including titles, prices,
    ratings, and reviews from the specified e-commerce website.
    """
    try:
        data = service.scrape_data(
            source=request.source,
            queries=request.queries,
            max_products=request.max_products,
            review_count=request.review_count,
            save_to_csv=request.save_to_csv,
        )

        return ScrapeResponse(
            status="success",
            message=f"Successfully scraped {len(data)} products",
            scraped_count=len(data),
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.post("/generate-vector-db", response_model=VectorDBResponse)
async def generate_vector_db(
    service: ScrapingService = Depends(get_scraping_service),
) -> VectorDBResponse:
    """
    Generate vector database from previously scraped data.

    This endpoint reads the scraped product data from CSV and ingests it
    into the AstraDB vector store for similarity search operations.
    """
    try:
        result = service.generate_vector_db()

        return VectorDBResponse(
            status=result["status"],
            message=result["message"],
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="No scraped data found. Please run scraping first.",
        )
    except EnvironmentError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Environment configuration error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vector DB generation failed: {str(e)}",
        )


@router.post("/scrape-and-generate", response_model=FullPipelineResponse)
async def scrape_and_generate_vector_db(
    request: ScrapeRequest,
    service: ScrapingService = Depends(get_scraping_service),
) -> FullPipelineResponse:
    """
    Complete pipeline: scrape data and generate vector database.

    This endpoint performs the full workflow of scraping product data from
    a website and then ingesting it into the vector database for use with
    the product assistant.
    """
    try:
        result = service.scrape_and_generate_vector_db(
            source=request.source,
            queries=request.queries,
            max_products=request.max_products,
            review_count=request.review_count,
        )

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])

        return FullPipelineResponse(
            status=result["status"],
            message=result["message"],
            scraped_count=result["scraped_count"],
            data=result["scraped_data"],
            ingestion_result=result["ingestion_result"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EnvironmentError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Environment configuration error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}",
        )


@router.get("/sources")
async def get_supported_sources() -> dict:
    """
    Get list of supported data sources for scraping.
    """
    return {
        "sources": ScrapingService.SUPPORTED_SOURCES,
        "description": "List of supported e-commerce websites for scraping",
    }
