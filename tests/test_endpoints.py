import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from main import app
from services.seo_analyzer import SEOAnalyzer
from models.seo_models import AnalysisResponse, AnalysisRequest, GeoRankRequest, GeoRankResponse


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
@patch('api.analyzer.seo_analyzer.analyze_site')
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
@patch('api.analyzer.seo_analyzer.analyze_site')
async def test_analyze_endpoint_error(mock_analyze_site):
    """Test error handling in analysis endpoint"""
    # Configure mock to raise an exception
    mock_analyze_site.side_effect = ValueError("Invalid URL")
    
    # Test request with valid format but invalid URL
    request_data = {
        "url": "https://invalid-url-that-will-cause-error.com",
        "seo_goal": "Rank for test keywords",
        "location": "Test City",
        "language": "en"
    }
    
    # Send request
    response = client.post(
        "/api/analyze",
        json=request_data
    )
    
    # Check response - should be 400 for validation error
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


@pytest.mark.asyncio
@patch('api.analyzer.seo_analyzer.analyze_site')
async def test_analyze_endpoint_with_geo_analysis(mock_analyze_site):
    """Test analysis endpoint with geolocation analysis enabled"""
    # Create mock response with geolocation data
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
            "google_maps": "rank #2.5",
            "bing_maps": "rank #3.0",
            "nap_consistency": True
        },
        "recommendations": [
            "Add alt attributes to images",
            "Improve meta description"
        ]
    }
    
    # Configure mock
    mock_analyze_site.return_value = AnalysisResponse(**mock_response)
    
    # Test request with all geolocation parameters
    request_data = {
        "url": "https://example.com",
        "seo_goal": "Rank for test keywords",
        "location": "Test City",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "local_radius_km": 5,
        "geo_samples": 10,
        "language": "en"
    }
    
    # Send request
    response = client.post(
        "/api/analyze",
        json=request_data
    )
    
    # Check response
    assert response.status_code == 200
    result = response.json()
    assert result["local_rank_check"]["google_maps"] == "rank #2.5"
    assert result["local_rank_check"]["nap_consistency"] == True
    
    # Verify mock was called correctly
    mock_analyze_site.assert_called_once()
    called_with_arg = mock_analyze_site.call_args[0][0]
    assert isinstance(called_with_arg, AnalysisRequest)
    assert called_with_arg.latitude == 40.7128
    assert called_with_arg.longitude == -74.0060
    assert called_with_arg.local_radius_km == 5
    assert called_with_arg.geo_samples == 10


@pytest.mark.asyncio
@patch('api.analyzer.seo_analyzer.analyze_site')
async def test_analyze_endpoint_without_geo_analysis(mock_analyze_site):
    """Test analysis endpoint without geolocation analysis (missing parameters)"""
    # Create mock response without geolocation data
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
            "google_maps": "unavailable",
            "bing_maps": "unavailable",
            "nap_consistency": False
        },
        "recommendations": [
            "Add alt attributes to images",
            "Improve meta description"
        ]
    }
    
    # Configure mock
    mock_analyze_site.return_value = AnalysisResponse(**mock_response)
    
    # Test request without geolocation parameters
    request_data = {
        "url": "https://example.com",
        "seo_goal": "Rank for test keywords",
        "location": "Test City",
        "language": "en"
        # Missing: local_radius_km, geo_samples
    }
    
    # Send request
    response = client.post(
        "/api/analyze",
        json=request_data
    )
    
    # Check response
    assert response.status_code == 200
    result = response.json()
    assert result["local_rank_check"]["google_maps"] == "unavailable"
    assert result["local_rank_check"]["nap_consistency"] == False
    
    # Verify mock was called correctly
    mock_analyze_site.assert_called_once()
    called_with_arg = mock_analyze_site.call_args[0][0]
    assert isinstance(called_with_arg, AnalysisRequest)
    assert called_with_arg.local_radius_km == 5  # Default value
    assert called_with_arg.geo_samples == 10  # Default value


@pytest.mark.asyncio
@patch('api.analyzer.seo_analyzer.analyze_geo_ranking')
async def test_geo_rank_analysis_endpoint_success(mock_analyze_geo_ranking):
    """Test successful geo-rank analysis"""
    # Create mock response
    mock_response = {
        "company_name": "Acme HVAC",
        "location_used": "Medellín, Colombia",
        "coordinates": [6.2442, -75.5812],
        "radius_km": 5,
        "total_samples": 10,
        "keywords_analyzed": 2,
        "keyword_results": [
            {
                "keyword": "hvac repair",
                "average_rank": 2.5,
                "coverage_percentage": 80.0,
                "total_samples": 10,
                "found_in_samples": 8,
                "google_maps_rank": "rank #2.5",
                "bing_maps_rank": "rank #3.0",
                "nap_inconsistencies": [],
                "visibility_score": 80.0
            },
            {
                "keyword": "ac install",
                "average_rank": 4.2,
                "coverage_percentage": 60.0,
                "total_samples": 10,
                "found_in_samples": 6,
                "google_maps_rank": "rank #4.2",
                "bing_maps_rank": "rank #5.0",
                "nap_inconsistencies": ["Missing phone number in Google Maps listing"],
                "visibility_score": 60.0
            }
        ],
        "overall_visibility_score": 70.0,
        "nap_consistency": True,
        "has_verified_listing": True,
        "analysis_timestamp": "2024-01-15 14:30:25 UTC"
    }
    
    # Configure mock
    mock_analyze_geo_ranking.return_value = GeoRankResponse(**mock_response)
    
    # Test request
    request_data = {
        "location": "Medellín, Colombia",
        "latitude": 6.2442,
        "longitude": -75.5812,
        "local_radius_km": 5,
        "geo_samples": 10,
        "company_name": "Acme HVAC",
        "keywords": ["hvac repair", "ac install"]
    }
    
    # Send request
    response = client.post(
        "/api/geo-rank-analysis",
        json=request_data
    )
    
    # Check response
    assert response.status_code == 200
    result = response.json()
    assert result["company_name"] == "Acme HVAC"
    assert result["location_used"] == "Medellín, Colombia"
    assert result["keywords_analyzed"] == 2
    assert len(result["keyword_results"]) == 2
    assert result["keyword_results"][0]["keyword"] == "hvac repair"
    assert result["keyword_results"][0]["coverage_percentage"] == 80.0
    assert result["overall_visibility_score"] == 70.0
    
    # Verify mock was called correctly
    mock_analyze_geo_ranking.assert_called_once()
    called_with_arg = mock_analyze_geo_ranking.call_args[0][0]
    assert isinstance(called_with_arg, GeoRankRequest)
    assert called_with_arg.company_name == "Acme HVAC"
    assert called_with_arg.keywords == ["hvac repair", "ac install"]


@pytest.mark.asyncio
@patch('api.analyzer.seo_analyzer.analyze_geo_ranking')
async def test_geo_rank_analysis_endpoint_error(mock_analyze_geo_ranking):
    """Test error handling in geo-rank analysis endpoint"""
    # Configure mock to raise an exception
    mock_analyze_geo_ranking.side_effect = ValueError("Could not determine coordinates")
    
    # Test request with valid format but invalid location
    request_data = {
        "location": "Invalid Location That Will Cause Error",
        "local_radius_km": 5,
        "geo_samples": 10,
        "company_name": "Acme HVAC",
        "keywords": ["hvac repair"]
    }
    
    # Send request
    response = client.post(
        "/api/geo-rank-analysis",
        json=request_data
    )
    
    # Check response - should be 400 for validation error
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "Could not determine coordinates" in result["detail"]


@pytest.mark.asyncio
async def test_geo_rank_analysis_validation():
    """Test input validation for geo-rank analysis"""
    # Test with missing required fields
    request_data = {
        "company_name": "Acme HVAC"
        # Missing location/coordinates, local_radius_km, geo_samples, keywords
    }
    
    response = client.post(
        "/api/geo-rank-analysis",
        json=request_data
    )
    
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with invalid radius
    request_data = {
        "location": "Medellín, Colombia",
        "local_radius_km": 100,  # Too large
        "geo_samples": 10,
        "company_name": "Acme HVAC",
        "keywords": ["hvac repair"]
    }
    
    response = client.post(
        "/api/geo-rank-analysis",
        json=request_data
    )
    
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test with empty keywords
    request_data = {
        "location": "Medellín, Colombia",
        "local_radius_km": 5,
        "geo_samples": 10,
        "company_name": "Acme HVAC",
        "keywords": []
    }
    
    response = client.post(
        "/api/geo-rank-analysis",
        json=request_data
    )
    
    assert response.status_code == 422  # Unprocessable Entity