from fastapi import APIRouter, HTTPException, Depends
import logging
from app.models.seo_models import AnalysisRequest, AnalysisResponse
from app.services.seo_analyzer import SEOAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api",
    tags=["SEO Analysis"],
    responses={404: {"description": "Not found"}}
)

# Initialize SEO analyzer
seo_analyzer = SEOAnalyzer()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_site(request: AnalysisRequest):
    """
    Analyze a website for SEO factors based on provided URL and parameters.
    
    This endpoint performs:
    - Technical SEO analysis
    - HTML structure analysis
    - Link analysis
    - Semantic content analysis using LLMs
    - Speed metrics calculation
    - Local SEO ranking check
    
    Returns a comprehensive analysis with recommendations.
    """
    try:
        logger.info(f"Analysis request for URL: {request.url}")
        result = await seo_analyzer.analyze_site(request)
        return result
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred during analysis: {str(e)}"
        )


@router.get("/status")
async def api_status():
    """
    Check API status and available LLM providers
    """
    from app.utils.llm_clients import OpenAIClient, AnthropicClient, GeminiClient
    import os
    
    # Check which LLM providers are configured
    llm_status = {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "google": bool(os.getenv("GOOGLE_API_KEY"))
    }
    
    return {
        "status": "online",
        "llm_providers_available": llm_status
    }