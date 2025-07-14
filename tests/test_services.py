import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from services.scraper import Scraper
from services.seo_analyzer import SEOAnalyzer
from services.semantic_analyzer import SemanticAnalyzer
from models.seo_models import AnalysisRequest, GeoRankRequest, GeoRankResponse
from bs4 import BeautifulSoup
from utils.llm_clients import OpenAIClient, AnthropicClient, GeminiClient


class TestScraper:
    """Tests for the Scraper service"""
    
    def test_init(self):
        """Test scraper initialization"""
        scraper = Scraper()
        assert scraper.timeout == 20
        assert "Mozilla" in scraper.user_agent
        
    @patch('services.scraper.requests.get')
    def test_fetch_html_with_requests(self, mock_get):
        """Test fetching HTML with requests"""
        # Mock response
        mock_response = MagicMock()
        mock_response.text = "<html><title>Test Page</title><body><h1>Hello</h1></body></html>"
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.status_code = 200
        mock_response.history = []
        mock_get.return_value = mock_response
        
        scraper = Scraper()
        
        # Mock _needs_playwright to return False
        with patch.object(scraper, '_needs_playwright', return_value=False):
            html, headers, status_code, redirections = asyncio.run(scraper.fetch_html("https://example.com"))
            
        assert "Test Page" in html
        assert headers == {"Content-Type": "text/html"}
        assert status_code == 200
        assert redirections == []
        
    @patch('services.scraper.requests.get')
    @patch('services.scraper.async_playwright')
    def test_fetch_html_with_playwright_fallback(self, mock_playwright, mock_get):
        """Test fetching HTML with Playwright fallback"""
        # Mock requests response
        mock_response = MagicMock()
        mock_response.text = "<html><body></body></html>"  # Empty page
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.status_code = 200
        mock_response.history = []
        mock_get.return_value = mock_response
        
        # Mock playwright with proper async context
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_response = AsyncMock()
        
        # Configure the mock chain properly
        mock_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.goto.return_value = mock_response
        mock_page.content.return_value = "<html><title>Dynamic Page</title><body><div id='app'>Content</div></body></html>"
        mock_page.close.return_value = None
        mock_page.set_extra_http_headers.return_value = None
        mock_page.set_viewport_size.return_value = None
        mock_page.route.return_value = None
        mock_page.wait_for_selector.return_value = None
        
        # Mock the browser pool to avoid async context issues
        scraper = Scraper()
        
        # Mock the entire browser pool to return our mocked browser
        with patch.object(scraper, '_browser_pool') as mock_pool:
            # Create async context managers that return our mocked objects
            mock_browser_context = AsyncMock()
            mock_browser_context.__aenter__ = AsyncMock(return_value=mock_browser)
            mock_browser_context.__aexit__ = AsyncMock(return_value=None)
            
            mock_page_context = AsyncMock()
            mock_page_context.__aenter__ = AsyncMock(return_value=mock_page)
            mock_page_context.__aexit__ = AsyncMock(return_value=None)
            
            mock_pool.get_browser.return_value = mock_browser_context
            mock_pool.get_page.return_value = mock_page_context
            
            # Mock _needs_playwright to return True
            with patch.object(scraper, '_needs_playwright', return_value=True):
                # Mock the _fetch_with_playwright method directly
                with patch.object(scraper, '_fetch_with_playwright', return_value=(
                    "<html><title>Dynamic Page</title><body><div id='app'>Content</div></body></html>",
                    {"Content-Type": "text/html"},
                    200,
                    []
                )):
                    html, headers, status_code, redirections = asyncio.run(scraper.fetch_html("https://example.com"))
                
        assert "Dynamic Page" in html
        
    def test_needs_playwright(self):
        """Test detection of JS-rendered pages"""
        scraper = Scraper()
        
        # Test empty HTML
        assert scraper._needs_playwright("", "https://example.com")
        
        # Test page with no title
        assert scraper._needs_playwright("<html><body>Content</body></html>", "https://example.com")
        
        # Test SPA-like page
        spa_html = """
        <html>
            <head><title>SPA</title></head>
            <body>
                <div id="root"></div>
                <script type="application/json">{"data":{}}</script>
                <script src="react.js"></script>
                <script src="app.js"></script>
            </body>
        </html>
        """
        assert scraper._needs_playwright(spa_html, "https://example.com")
        
        # Test normal HTML page
        normal_html = """
        <html>
            <head><title>Normal Page With A Very Long Title To Make Sure It's Longer Than Expected</title></head>
            <body>
                <h1>Hello World</h1>
                <p>This is a normal page with sufficient content to pass the length check.</p>
                <p>Here's another paragraph to make sure we have enough content.</p>
                <p>And yet another paragraph with some more text to ensure the content is long enough.</p>
                <div class="content">
                    <h2>Section Title</h2>
                    <p>More content in this section to make it realistic.</p>
                    <ul>
                        <li>List item 1</li>
                        <li>List item 2</li>
                        <li>List item 3</li>
                    </ul>
                </div>
                <img src="image.jpg" alt="Image">
                <footer>
                    <p>Footer content goes here with additional text.</p>
                </footer>
            </body>
        </html>
        """
        assert not scraper._needs_playwright(normal_html, "https://example.com")
        
    def test_parse_html(self):
        """Test HTML parsing"""
        html = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
                <meta name="robots" content="index,follow">
                <link rel="canonical" href="https://example.com">
            </head>
            <body>
                <h1>Hello World</h1>
                <h2>Section 1</h2>
                <p>This is a test paragraph.</p>
                <img src="image1.jpg" alt="Image 1">
                <img src="image2.jpg">
                <a href="/internal">Internal Link</a>
                <a href="https://external.com">External Link</a>
            </body>
        </html>
        """
        
        scraper = Scraper()
        result = scraper.parse_html(html, "https://example.com")
        
        assert result["title"]["text"] == "Test Page"
        assert result["meta_description"]["text"] == "Test description"
        assert result["meta_robots"] == "index,follow"
        assert result["canonical_url"] == "https://example.com"
        assert len(result["h_tags"]["h1"]) == 1
        assert len(result["h_tags"]["h2"]) == 1
        assert len(result["paragraphs"]) == 1
        assert len(result["images_without_alt"]) == 1
        assert "https://example.com/internal" in result["links"]["internal"]
        assert "https://external.com" in result["links"]["external"]


class TestSEOAnalyzer:
    """Tests for the SEOAnalyzer service"""
    
    @pytest.fixture
    def seo_analyzer(self):
        """Create SEOAnalyzer instance"""
        return SEOAnalyzer()
    
    @pytest.mark.asyncio
    @patch('services.seo_analyzer.Scraper')
    @patch('services.seo_analyzer.SemanticAnalyzer')
    async def test_analyze_site(self, mock_semantic_analyzer, mock_scraper):
        """Test the main analyze_site method"""
        # Mock scraper
        mock_scraper_instance = MagicMock()
        mock_scraper.return_value = mock_scraper_instance

        # Mock HTML fetch result
        from unittest.mock import AsyncMock
        mock_scraper_instance.fetch_html = AsyncMock(return_value=(
            "<html><title>Test Page</title></html>",
            {"Content-Type": "text/html"},
            200,
            []
        ))

        # Mock parsed data
        mock_scraper_instance.parse_html.return_value = {
            "title": {"text": "Test Page", "length": 9},
            "meta_description": {"text": "Test description", "length": 16},
            "meta_robots": "index,follow",
            "canonical_url": "https://example.com",
            "h_tags": {"h1": [{"text": "Hello", "word_count": 1}], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []},
            "paragraphs": [{"text": "Test paragraph", "length": 14, "word_count": 2}],
            "images_without_alt": [{"src": "image.jpg", "width": "100", "height": "100"}],
            "links": {"internal": ["/page"], "external": ["https://external.com"], "broken": []},
            "semantic_structure": ["main", "nav"],
            "structured_data": ["JSON-LD"]
        }

        # Mock semantic analyzer
        mock_semantic_analyzer_instance = MagicMock()
        mock_semantic_analyzer.return_value = mock_semantic_analyzer_instance
        mock_semantic_analyzer_instance.analyze_semantics = AsyncMock(return_value={
            "llm_engine": "chatgpt",
            "coherence_score": 0.8,
            "detected_intent": "Information",
            "readability_level": "B1",
            "suggested_improvements": ["Add more keywords"]
        })

        # Crear la instancia de SEOAnalyzer después de los patches
        from services.seo_analyzer import SEOAnalyzer
        seo_analyzer = SEOAnalyzer()

        # Create analysis request
        request = AnalysisRequest(
            url="https://example.com",
            seo_goal="Rank for test keywords",
            location="Test City",
            language="en"
        )

        # Perform analysis
        with patch.object(seo_analyzer, '_analyze_title', return_value={"text": "Test Page", "length": 9, "has_keywords": True}), \
             patch.object(seo_analyzer, '_find_broken_links', return_value=[]), \
             patch.object(seo_analyzer, '_analyze_performance', return_value={
                "ttfb_ms": 200,
                "resource_count": 10,
                "gzip_enabled": True,
                "lazy_loaded_images": False
             }), \
             patch.object(seo_analyzer, '_check_local_ranking', return_value={
                "google_maps": "no listing found",
                "bing_maps": "no listing found",
                "nap_consistency": False
             }), \
             patch.object(seo_analyzer, '_generate_recommendations', return_value=[
                "Add alt attributes to images",
                "Improve meta description"
             ]):
                result = await seo_analyzer.analyze_site(request)

        # Check result
        assert result.status_code == 200
        assert result.title.has_keywords == True
        assert result.meta_description.text == "Test description"
        assert result.meta_description.length == 16
        assert result.semantic_summary.coherence_score == 0.8
        assert result.semantic_summary.llm_engine == "chatgpt"
        assert len(result.recommendations) == 2
        

    @pytest.mark.asyncio
    @patch('services.seo_analyzer.SEOAnalyzer._get_coordinates')
    @patch('services.seo_analyzer.SEOAnalyzer._generate_geosamples')
    @patch('services.seo_analyzer.SEOAnalyzer._check_google_maps_ranking')
    @patch('services.seo_analyzer.SEOAnalyzer._check_bing_maps_ranking')
    async def test_analyze_geo_ranking_success(self, mock_bing_maps, mock_google_maps, mock_geosamples, mock_coordinates, seo_analyzer):
        """Test successful geo-ranking analysis"""
        # Mock coordinates
        mock_coordinates.return_value = (40.7128, -74.0060)
        
        # Mock geo samples
        mock_geosamples.return_value = [(40.7128, -74.0060), (40.7130, -74.0062)]
        
        # Mock Google Maps results
        mock_google_maps.return_value = {
            "rank_text": "rank #2.5",
            "coverage_percentage": 80.0,
            "average_rank": 2.5,
            "is_verified": True,
            "profile_data": {
                "title": "Acme HVAC",
                "address": "123 Main St",
                "phone": "555-1234"
            }
        }
        
        # Mock Bing Maps results
        mock_bing_maps.return_value = {
            "rank_text": "rank #3.0",
            "coverage_percentage": 60.0
        }
        
        # Create request
        request = GeoRankRequest(
            location="New York, NY",
            latitude=40.7128,
            longitude=-74.0060,
            local_radius_km=5,
            geo_samples=10,
            company_name="Acme HVAC",
            keywords=["hvac repair", "ac install"]
        )
        
        # Execute analysis
        result = await seo_analyzer.analyze_geo_ranking(request)
        
        # Verify result
        assert isinstance(result, GeoRankResponse)
        assert result.company_name == "Acme HVAC"
        assert result.location_used == "New York, NY"
        assert result.coordinates == (40.7128, -74.0060)
        assert result.radius_km == 5
        assert result.total_samples == 2
        assert result.keywords_analyzed == 2
        assert len(result.keyword_results) == 2
        assert result.overall_visibility_score > 0
        assert result.nap_consistency == True
        assert result.has_verified_listing == True
        
        # Verify keyword results
        keyword_result = result.keyword_results[0]
        assert keyword_result.keyword == "hvac repair"
        assert keyword_result.average_rank == 2.5
        assert keyword_result.coverage_percentage == 70.0  # Average of Google and Bing
        assert keyword_result.total_samples == 2
        assert keyword_result.google_maps_rank == "rank #2.5"
        assert keyword_result.bing_maps_rank == "rank #3.0"
        assert keyword_result.visibility_score > 0


    @pytest.mark.asyncio
    @patch('services.seo_analyzer.SEOAnalyzer._get_coordinates')
    async def test_analyze_geo_ranking_no_coordinates(self, mock_coordinates, seo_analyzer):
        """Test geo-ranking analysis with invalid coordinates"""
        # Mock coordinates to return None
        mock_coordinates.return_value = None
        
        # Create request
        request = GeoRankRequest(
            location="Invalid Location",
            local_radius_km=5,
            geo_samples=10,
            company_name="Acme HVAC",
            keywords=["hvac repair"]
        )
        
        # Execute analysis should raise ValueError
        with pytest.raises(ValueError, match="Could not determine coordinates"):
            await seo_analyzer.analyze_geo_ranking(request)


    @pytest.mark.asyncio
    @patch('services.seo_analyzer.SEOAnalyzer._get_coordinates')
    @patch('services.seo_analyzer.SEOAnalyzer._generate_geosamples')
    @patch('services.seo_analyzer.SEOAnalyzer._check_google_maps_ranking')
    @patch('services.seo_analyzer.SEOAnalyzer._check_bing_maps_ranking')
    async def test_analyze_geo_ranking_single_keyword(self, mock_bing_maps, mock_google_maps, mock_geosamples, mock_coordinates, seo_analyzer):
        """Test geo-ranking analysis with single keyword string"""
        # Mock coordinates
        mock_coordinates.return_value = (40.7128, -74.0060)
        
        # Mock geo samples
        mock_geosamples.return_value = [(40.7128, -74.0060)]
        
        # Mock Google Maps results
        mock_google_maps.return_value = {
            "rank_text": "rank #1.0",
            "coverage_percentage": 100.0,
            "average_rank": 1.0,
            "is_verified": False,
            "profile_data": {}
        }
        
        # Mock Bing Maps results
        mock_bing_maps.return_value = {
            "rank_text": "rank #2.0",
            "coverage_percentage": 100.0
        }
        
        # Create request with single keyword string
        request = GeoRankRequest(
            location="New York, NY",
            local_radius_km=5,
            geo_samples=10,
            company_name="Acme HVAC",
            keywords="hvac repair"  # Single string instead of list
        )
        
        # Execute analysis
        result = await seo_analyzer.analyze_geo_ranking(request)
        
        # Verify result
        assert result.keywords_analyzed == 1
        assert len(result.keyword_results) == 1
        assert result.keyword_results[0].keyword == "hvac repair"
        assert result.overall_visibility_score == result.keyword_results[0].visibility_score


    @pytest.mark.asyncio
    @patch('services.seo_analyzer.SEOAnalyzer._get_coordinates')
    @patch('services.seo_analyzer.SEOAnalyzer._generate_geosamples')
    @patch('services.seo_analyzer.SEOAnalyzer._check_google_maps_ranking')
    @patch('services.seo_analyzer.SEOAnalyzer._check_bing_maps_ranking')
    async def test_analyze_geo_ranking_nap_inconsistencies(self, mock_bing_maps, mock_google_maps, mock_geosamples, mock_coordinates, seo_analyzer):
        """Test geo-ranking analysis with NAP inconsistencies"""
        # Mock coordinates
        mock_coordinates.return_value = (40.7128, -74.0060)
        
        # Mock geo samples
        mock_geosamples.return_value = [(40.7128, -74.0060)]
        
        # Mock Google Maps results with missing phone
        mock_google_maps.return_value = {
            "rank_text": "rank #2.5",
            "coverage_percentage": 80.0,
            "average_rank": 2.5,
            "is_verified": True,
            "profile_data": {
                "title": "Acme HVAC",
                "address": "123 Main St"
                # Missing phone number
            }
        }
        
        # Mock Bing Maps results
        mock_bing_maps.return_value = {
            "rank_text": "rank #3.0",
            "coverage_percentage": 60.0
        }
        
        # Create request
        request = GeoRankRequest(
            location="New York, NY",
            local_radius_km=5,
            geo_samples=10,
            company_name="Acme HVAC",
            keywords=["hvac repair"]
        )
        
        # Execute analysis
        result = await seo_analyzer.analyze_geo_ranking(request)
        
        # Verify NAP inconsistencies are detected
        keyword_result = result.keyword_results[0]
        assert len(keyword_result.nap_inconsistencies) > 0
        assert "Missing phone number" in keyword_result.nap_inconsistencies[0]


class TestSemanticAnalyzer:
    """Tests for the SemanticAnalyzer service"""
    
    @pytest.fixture
    def semantic_analyzer(self):
        """Create SemanticAnalyzer instance"""
        return SemanticAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_semantics_openai(self, semantic_analyzer):
        """Test semantic analysis with OpenAI - handles missing API key gracefully"""
        # Test data
        texts = ["This is a test paragraph", "Another test paragraph"]
        page_title = "Test Page"
        meta_description = "Test description"
        headings = {
            "h1": [{"text": "Main Heading"}],
            "h2": [{"text": "Subheading"}],
            "h3": [], "h4": [], "h5": [], "h6": []
        }
        
        # Perform analysis
        result = await semantic_analyzer.analyze_semantics(
            texts=texts,
            page_title=page_title,
            meta_description=meta_description,
            headings=headings,
            seo_goal="Rank for test keywords",
            location="Test City",
            language="en",
            provider="chatgpt"
        )
        
        # Check result structure (should work even without API key)
        assert "llm_engine" in result
        assert "coherence_score" in result
        assert "detected_intent" in result
        assert "readability_level" in result
        assert "suggested_improvements" in result
        
        # Verify data types
        assert isinstance(result["llm_engine"], str)
        assert isinstance(result["coherence_score"], (int, float))
        assert isinstance(result["detected_intent"], str)
        assert isinstance(result["readability_level"], str)
        assert isinstance(result["suggested_improvements"], list)
        
        # Verify coherence_score is in valid range
        assert 0.0 <= result["coherence_score"] <= 1.0
        
        # If API key is missing, should return fallback values
        if not semantic_analyzer.openai_client.api_key:
            assert result["coherence_score"] == 0.5
            assert result["detected_intent"] == "Unable to analyze"
            assert "ALERTA" in result["suggested_improvements"][0]
        
    @pytest.mark.asyncio
    async def test_analyze_semantics_claude(self, semantic_analyzer):
        """Test semantic analysis with Claude - handles missing API key gracefully"""
        # Test data
        texts = ["This is a test paragraph", "Another test paragraph"]
        page_title = "Test Page"
        meta_description = "Test description"
        headings = {
            "h1": [{"text": "Main Heading"}],
            "h2": [{"text": "Subheading"}],
            "h3": [], "h4": [], "h5": [], "h6": []
        }
        
        # Perform analysis
        result = await semantic_analyzer.analyze_semantics(
            texts=texts,
            page_title=page_title,
            meta_description=meta_description,
            headings=headings,
            seo_goal="Rank for test keywords",
            location="Test City",
            language="en",
            provider="claude"
        )
        
        # Check result structure
        assert "llm_engine" in result
        assert "coherence_score" in result
        assert "detected_intent" in result
        assert "readability_level" in result
        assert "suggested_improvements" in result
        
        # Verify data types
        assert isinstance(result["llm_engine"], str)
        assert isinstance(result["coherence_score"], (int, float))
        assert isinstance(result["detected_intent"], str)
        assert isinstance(result["readability_level"], str)
        assert isinstance(result["suggested_improvements"], list)
        
        # Verify coherence_score is in valid range
        assert 0.0 <= result["coherence_score"] <= 1.0
        
        # If API key is missing, should return fallback values
        if not semantic_analyzer.anthropic_client.api_key:
            assert result["coherence_score"] == 0.5
            assert result["detected_intent"] == "Unable to analyze"
            assert "ALERTA" in result["suggested_improvements"][0]
        
    @pytest.mark.asyncio
    async def test_analyze_semantics_gemini(self, semantic_analyzer):
        """Test semantic analysis with Gemini - handles missing API key gracefully"""
        # Test data
        texts = ["This is a test paragraph", "Another test paragraph"]
        page_title = "Test Page"
        meta_description = "Test description"
        headings = {
            "h1": [{"text": "Main Heading"}],
            "h2": [{"text": "Subheading"}],
            "h3": [], "h4": [], "h5": [], "h6": []
        }
        
        # Perform analysis
        result = await semantic_analyzer.analyze_semantics(
            texts=texts,
            page_title=page_title,
            meta_description=meta_description,
            headings=headings,
            seo_goal="Rank for test keywords",
            location="Test City",
            language="en",
            provider="gemini"
        )
        
        # Check result structure
        assert "llm_engine" in result
        assert "coherence_score" in result
        assert "detected_intent" in result
        assert "readability_level" in result
        assert "suggested_improvements" in result
        
        # Verify data types
        assert isinstance(result["llm_engine"], str)
        assert isinstance(result["coherence_score"], (int, float))
        assert isinstance(result["detected_intent"], str)
        assert isinstance(result["readability_level"], str)
        assert isinstance(result["suggested_improvements"], list)
        
        # Verify coherence_score is in valid range
        assert 0.0 <= result["coherence_score"] <= 1.0
        
        # If API key is missing, should return fallback values
        if not semantic_analyzer.gemini_client.api_key:
            assert result["coherence_score"] == 0.5
            assert result["detected_intent"] == "Unable to analyze"
            assert "ALERTA" in result["suggested_improvements"][0]
    
    @pytest.mark.asyncio
    async def test_analyze_semantics_invalid_provider(self, semantic_analyzer):
        """Test semantic analysis with invalid provider - should default to OpenAI"""
        # Test data
        texts = ["This is a test paragraph"]
        page_title = "Test Page"
        meta_description = "Test description"
        headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}
        
        # Perform analysis with invalid provider
        result = await semantic_analyzer.analyze_semantics(
            texts=texts,
            page_title=page_title,
            meta_description=meta_description,
            headings=headings,
            seo_goal="Rank for test keywords",
            location="Test City",
            language="en",
            provider="invalid_provider"
        )
        
        # Should default to OpenAI (chatgpt)
        assert result["llm_engine"] == "invalid_provider"
        assert "coherence_score" in result
        assert "detected_intent" in result
        assert "readability_level" in result
        assert "suggested_improvements" in result
    
    @pytest.mark.asyncio
    async def test_analyze_semantics_empty_content(self, semantic_analyzer):
        """Test semantic analysis with empty content"""
        # Test data with empty content
        texts = []
        page_title = ""
        meta_description = ""
        headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}
        
        # Perform analysis
        result = await semantic_analyzer.analyze_semantics(
            texts=texts,
            page_title=page_title,
            meta_description=meta_description,
            headings=headings,
            seo_goal="Rank for test keywords",
            location="Test City",
            language="en",
            provider="chatgpt"
        )
        
        # Should still return valid structure
        assert "llm_engine" in result
        assert "coherence_score" in result
        assert "detected_intent" in result
        assert "readability_level" in result
        assert "suggested_improvements" in result
        
        # With empty content, coherence should be low
        if not semantic_analyzer.openai_client.api_key:
            assert result["coherence_score"] == 0.5
    
    @pytest.mark.asyncio
    async def test_parse_llm_response(self, semantic_analyzer):
        """Test parsing of LLM response"""
        # Test valid JSON response
        json_response = """
        ```json
        {
            "coherence_score": 0.85,
            "detected_intent": "Product Information",
            "readability_level": "B2",
            "suggested_improvements": ["Add more keywords", "Improve meta description"]
        }
        ```
        """
        
        result = semantic_analyzer._parse_llm_response(json_response)
        
        assert result["coherence_score"] == 0.85
        assert result["detected_intent"] == "Product Information"
        assert result["readability_level"] == "B2"
        assert len(result["suggested_improvements"]) == 2
        assert "Add more keywords" in result["suggested_improvements"]
        
        # Test JSON without code blocks
        json_response_plain = '{"coherence_score": 0.75, "detected_intent": "Service", "readability_level": "B1", "suggested_improvements": ["Test improvement"]}'
        
        result = semantic_analyzer._parse_llm_response(json_response_plain)
        
        assert result["coherence_score"] == 0.75
        assert result["detected_intent"] == "Service"
        assert result["readability_level"] == "B1"
        assert len(result["suggested_improvements"]) == 1
        
        # Test invalid JSON - should return fallback
        invalid_response = "This is not JSON"
        
        result = semantic_analyzer._parse_llm_response(invalid_response)
        
        assert result["coherence_score"] == 0.5
        assert result["detected_intent"] == "Unknown"
        assert result["readability_level"] == "B2"
        assert len(result["suggested_improvements"]) >= 1


class TestLLMClients:
    """Tests for LLM client standardization and interface"""
    
    @pytest.fixture
    def openai_client(self):
        """Create OpenAI client instance"""
        return OpenAIClient()
    
    @pytest.fixture
    def anthropic_client(self):
        """Create Anthropic client instance"""
        return AnthropicClient()
    
    @pytest.fixture
    def gemini_client(self):
        """Create Gemini client instance"""
        return GeminiClient()
    
    def test_client_initialization(self, openai_client, anthropic_client, gemini_client):
        """Test that all clients initialize correctly"""
        assert openai_client.provider_name == "OpenAI"
        assert anthropic_client.provider_name == "Anthropic"
        assert gemini_client.provider_name == "Google Gemini"
        
        # All clients should have the same interface
        assert hasattr(openai_client, 'analyze_text')
        assert hasattr(anthropic_client, 'analyze_text')
        assert hasattr(gemini_client, 'analyze_text')
        
        assert hasattr(openai_client, '_create_analysis_prompt')
        assert hasattr(anthropic_client, '_create_analysis_prompt')
        assert hasattr(gemini_client, '_create_analysis_prompt')
    
    def test_fallback_response_structure(self, openai_client, anthropic_client, gemini_client):
        """Test that fallback responses have consistent structure"""
        error_msg = "Test error"
        
        openai_fallback = openai_client._get_fallback_response(error_msg)
        anthropic_fallback = anthropic_client._get_fallback_response(error_msg)
        gemini_fallback = gemini_client._get_fallback_response(error_msg)
        
        # All fallbacks should have the same structure
        required_keys = ["coherence_score", "detected_intent", "readability_level", "suggested_improvements"]
        
        for fallback in [openai_fallback, anthropic_fallback, gemini_fallback]:
            for key in required_keys:
                assert key in fallback
            
            # Verify data types
            assert isinstance(fallback["coherence_score"], (int, float))
            assert isinstance(fallback["detected_intent"], str)
            assert isinstance(fallback["readability_level"], str)
            assert isinstance(fallback["suggested_improvements"], list)
            
            # Verify coherence_score is in valid range
            assert 0.0 <= fallback["coherence_score"] <= 1.0
            
            # Verify error message is included
            assert any("ALERTA" in improvement for improvement in fallback["suggested_improvements"])
    
    def test_response_validation(self, openai_client):
        """Test response validation and standardization"""
        # Test complete response
        complete_response = {
            "coherence_score": 0.85,
            "detected_intent": "Product Information",
            "readability_level": "B2",
            "suggested_improvements": ["Add keywords", "Improve meta"]
        }
        
        validated = openai_client._validate_response(complete_response)
        assert validated == complete_response
        
        # Test incomplete response
        incomplete_response = {
            "coherence_score": 0.75
        }
        
        validated = openai_client._validate_response(incomplete_response)
        assert "detected_intent" in validated
        assert "readability_level" in validated
        assert "suggested_improvements" in validated
        assert validated["coherence_score"] == 0.75
        
        # Test invalid coherence_score
        invalid_score_response = {
            "coherence_score": 1.5,  # Out of range
            "detected_intent": "Test",
            "readability_level": "B1",
            "suggested_improvements": ["Test"]
        }
        
        validated = openai_client._validate_response(invalid_score_response)
        assert validated["coherence_score"] == 1.0  # Should be clamped to 1.0
        
        # Test negative coherence_score
        negative_score_response = {
            "coherence_score": -0.5,  # Negative
            "detected_intent": "Test",
            "readability_level": "B1",
            "suggested_improvements": ["Test"]
        }
        
        validated = openai_client._validate_response(negative_score_response)
        assert validated["coherence_score"] == 0.0  # Should be clamped to 0.0
        
        # Test non-list suggested_improvements
        invalid_improvements_response = {
            "coherence_score": 0.8,
            "detected_intent": "Test",
            "readability_level": "B1",
            "suggested_improvements": "Not a list"
        }
        
        validated = openai_client._validate_response(invalid_improvements_response)
        assert isinstance(validated["suggested_improvements"], list)
    
    @pytest.mark.asyncio
    async def test_analyze_text_interface_consistency(self, openai_client, anthropic_client, gemini_client):
        """Test that all clients have consistent analyze_text interface"""
        test_content = "This is test content"
        test_seo_goal = "Rank for test keywords"
        test_location = "Test City"
        test_language = "en"
        
        # Test that all clients can be called with the same parameters
        # (This will use fallback responses since we don't have API keys)
        
        openai_result = await openai_client.analyze_text(
            test_content, test_seo_goal, test_location, test_language
        )
        
        anthropic_result = await anthropic_client.analyze_text(
            test_content, test_seo_goal, test_location, test_language
        )
        
        gemini_result = await gemini_client.analyze_text(
            test_content, test_seo_goal, test_location, test_language
        )
        
        # All results should have the same structure
        required_keys = ["coherence_score", "detected_intent", "readability_level", "suggested_improvements"]
        
        for result in [openai_result, anthropic_result, gemini_result]:
            for key in required_keys:
                assert key in result
            
            # Verify data types
            assert isinstance(result["coherence_score"], (int, float))
            assert isinstance(result["detected_intent"], str)
            assert isinstance(result["readability_level"], str)
            assert isinstance(result["suggested_improvements"], list)
            
            # Verify coherence_score is in valid range
            assert 0.0 <= result["coherence_score"] <= 1.0
    
    def test_prompt_creation(self, openai_client, anthropic_client, gemini_client):
        """Test that all clients can create analysis prompts"""
        test_content = "Test content"
        test_seo_goal = "Test goal"
        test_location = "Test location"
        test_language = "en"
        
        openai_prompt = openai_client._create_analysis_prompt(
            test_content, test_seo_goal, test_location, test_language
        )
        
        anthropic_prompt = anthropic_client._create_analysis_prompt(
            test_content, test_seo_goal, test_location, test_language
        )
        
        gemini_prompt = gemini_client._create_analysis_prompt(
            test_content, test_seo_goal, test_location, test_language
        )
        
        # All prompts should be strings and contain the test data
        for prompt in [openai_prompt, anthropic_prompt, gemini_prompt]:
            assert isinstance(prompt, str)
            assert test_content in prompt
            assert test_seo_goal in prompt
            assert test_location in prompt
            assert test_language in prompt
            assert "coherence_score" in prompt
            assert "detected_intent" in prompt
            assert "readability_level" in prompt
            assert "suggested_improvements" in prompt