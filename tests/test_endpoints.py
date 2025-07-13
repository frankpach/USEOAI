import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from app.main import app
from app.services.seo_analyzer import SEOAnalyzer
from app.models.seo_models import AnalysisResponse, AnalysisRequest


# Create test client
client = TestClient(app)


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["service"] == "USEOAI Backend"


@pytest.mark.asyncio
@patch('app.api.analyzer.seo_analyzer.analyze_site')
async def test_analyze_endpoint_success(mock_analyze_site):
    """Test successful analysis"""
    # Create mock response
    mock_response = {
        "status_code": 200,
        "redirections": [],
        "title": {
            "text": "Test Page",
            "length": 9,
            "has_keywords": True
        },
        "meta_description": {
            "text": "Test description",
            "length": 16
        },
        "meta_robots": "index,follow",
        "canonical_url": "https://example.com",
        "h_tags": {
            "h1": [{"text": "Main Heading"}],
            "h2": [{"text": "Subheading"}],
            "h3": [], "h4": [], "h5": [], "h6": []
        },
        "paragraphs": [
            {"text": "Test paragraph", "length": 14}
        ],
        "semantic_summary": {
            "llm_engine": "chatgpt",
            "coherence_score": 0.8,
            "detected_intent": "Information",
            "readability_level": "B1",
            "suggested_improvements": ["Add more keywords"]
        },
        "images_without_alt": [
            {"src": "image.jpg"}
        ],
        "links": {
            "internal": ["/page"],
            "external": ["https://external.com"],
            "broken": []
        },
        "semantic_structure": ["main", "nav"],
        "structured_data": ["JSON-LD"],
        "speed_metrics": {
            "ttfb_ms": 200,
            "resource_count": 10,
            "gzip_enabled": True,
            "lazy_loaded_images": False
        },
        "local_rank_check": {
            "google_maps": "no listing found",
            "bing_maps": "no listing found",
            "nap_consistency": False
        },
        "recommendations": [
            "Add alt attributes to images",
            "Improve meta description"
        ]
    }
    
    # Configure mock
    mock_analyze_site.return_value = AnalysisResponse(**mock_response)
    
    # Test request
    request_data = {
        "url": "https://example.com",
        "seo_goal": "Rank for test keywords",
        "location": "Test City",
        "language": "en",
        "local_radius_km": 5,
        "geo_samples": 10
    }
    
    # Send request
    response = client.post(
        "/api/analyze",
        json=request_data
    )
    
    # Check response
    assert response.status_code == 200
    result = response.json()
    assert result["title"]["text"] == "Test Page"
    assert result["semantic_summary"]["llm_engine"] == "chatgpt"
    assert len(result["recommendations"]) == 2
    
    # Verify mock was called correctly
    mock_analyze_site.assert_called_once()
    called_with_arg = mock_analyze_site.call_args[0][0]
    assert isinstance(called_with_arg, AnalysisRequest)
    assert called_with_arg.url == "https://example.com"
    assert called_with_arg.seo_goal == "Rank for test keywords"


@pytest.mark.asyncio
@patch('app.api.analyzer.seo_analyzer.analyze_site')
async def test_analyze_endpoint_error(mock_analyze_site):
    """Test error handling in analysis endpoint"""
    # Configure mock to raise an exception
    mock_analyze_site.side_effect = ValueError("Invalid URL")
    
    # Test request
    request_data = {
        "url": "invalid-url",
        "seo_goal": "Rank for test keywords",
        "location": "Test City",
        "language": "en"
    }
    
    # Send request
    response = client.post(
        "/api/analyze",
        json=request_data
    )
    
    # Check response
    assert response.status_code == 400  # Bad request
    result = response.json()
    assert "detail" in result
    assert "Invalid URL" in result["detail"]


@pytest.mark.asyncio
async def test_api_status_endpoint():
    """Test the API status endpoint"""
    # Mock environment variables
    with patch.dict('os.environ', {
        "OPENAI_API_KEY": "test_key",
        "ANTHROPIC_API_KEY": "test_key",
        "GOOGLE_API_KEY": "test_key"
    }):
        response = client.get("/api/status")
        
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "online"
    assert "llm_providers_available" in result


@pytest.mark.asyncio
async def test_validation():
    """Test input validation"""
    # Test with missing required fields
    request_data = {
        "url": "https://example.com"
        # Missing seo_goal and location
    }
    
    response = client.post(
        "/api/analyze",
        json=request_data
    )
    
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with invalid URL format
    request_data = {
        "url": "invalid-url-format",
        "seo_goal": "Rank for test keywords",
        "location": "Test City",
        "language": "en"
    }
    
    response = client.post(
        "/api/analyze",
        json=request_data
    )
    
    assert response.status_code == 422  # Unprocessable Entity