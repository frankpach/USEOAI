from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import logging
from typing import List, Dict, Any, Optional
from models.seo_models import AnalysisRequest
from services.batch_analyzer import BatchAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/batch",
    tags=["Batch SEO Analysis"],
    responses={404: {"description": "Not found"}}
)

# Initialize batch analyzer
batch_analyzer = BatchAnalyzer()


@router.post("/analyze")
async def analyze_batch(requests: List[AnalysisRequest]):
    """
    Analyze multiple URLs in a single batch request.
    
    This endpoint allows submitting multiple URLs for concurrent analysis,
    which is much more efficient than making separate requests.
    
    Returns results for all URLs, with success/failure status for each.
    """
    try:
        if not requests:
            raise HTTPException(status_code=400, detail="No URLs provided")
            
        if len(requests) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 URLs allowed per batch")
            
        logger.info(f"Batch analysis request for {len(requests)} URLs")
        results = await batch_analyzer.analyze_batch(requests)
        return results
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred during batch analysis: {str(e)}"
        )


@router.get("/sitemap")
async def analyze_sitemap(
    url: str,
    seo_goal: str,
    location: str,
    language: str = "es",
    max_urls: int = 50
):
    """
    Analyze all URLs from a website's sitemap.
    
    This endpoint automatically discovers and parses the sitemap,
    then performs SEO analysis on all found URLs up to the specified limit.
    
    Returns aggregated results with success/failure for each URL.
    """
    try:
        if max_urls > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 URLs allowed per sitemap analysis")
            
        logger.info(f"Sitemap analysis request for {url}")
        results = await batch_analyzer.analyze_sitemap(
            base_url=url,
            seo_goal=seo_goal,
            location=location,
            language=language,
            max_urls=max_urls
        )
        return results
    except Exception as e:
        logger.error(f"Sitemap analysis error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred during sitemap analysis: {str(e)}"
        )


@router.get("/crawl")
async def analyze_crawl(
    url: str,
    seo_goal: str,
    location: str,
    language: str = "es",
    max_depth: int = 2,
    max_urls: int = 50
):
    """
    Crawl a website and analyze all discovered pages.
    
    This endpoint performs a breadth-first crawl of the website,
    starting from the provided URL and following internal links
    up to the specified depth and URL limit.
    
    Returns aggregated results with success/failure for each URL.
    """
    try:
        if max_urls > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 URLs allowed per crawl")
            
        if max_depth > 3:
            raise HTTPException(status_code=400, detail="Maximum crawl depth is 3")
            
        logger.info(f"Crawl analysis request for {url}")
        results = await batch_analyzer.analyze_all_pages(
            start_url=url,
            seo_goal=seo_goal,
            location=location,
            language=language,
            max_depth=max_depth,
            max_urls=max_urls
        )
        return results
    except Exception as e:
        logger.error(f"Crawl analysis error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred during crawl analysis: {str(e)}"
        )