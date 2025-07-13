import pytest
from unittest.mock import patch, MagicMock
from services.scraper import Scraper
from services.seo_analyzer import SEOAnalyzer
from services.semantic_analyzer import SemanticAnalyzer
from models.seo_models import AnalysisRequest
from bs4 import BeautifulSoup


class TestScraper:
    """Tests for the Scraper service"""
    
    def test_init(self):
        """Test scraper initialization"""
        scraper = Scraper()
        assert scraper.timeout == 20
        assert "Mozilla" in scraper.user_agent
        
    @patch('app.services.scraper.requests.get')
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
        
        # Mock _needs_puppeteer to return False
        with patch.object(scraper, '_needs_puppeteer', return_value=False):
            html, headers, status_code, redirections = asyncio.run(scraper.fetch_html("https://example.com"))
            
        assert "Test Page" in html
        assert headers == {"Content-Type": "text/html"}
        assert status_code == 200
        assert redirections == []
        
    @patch('app.services.scraper.requests.get')
    @patch('app.services.scraper.asyncio.run')
    def test_fetch_html_with_puppeteer_fallback(self, mock_run, mock_get):
        """Test fetching HTML with Puppeteer fallback"""
        # Mock requests response
        mock_response = MagicMock()
        mock_response.text = "<html><body></body></html>"  # Empty page
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.status_code = 200
        mock_response.history = []
        mock_get.return_value = mock_response
        
        # Mock Puppeteer response
        mock_run.return_value = (
            "<html><title>Dynamic Page</title><body><div id='app'>Content</div></body></html>",
            {"Content-Type": "text/html"}
        )
        
        scraper = Scraper()
        
        # Mock _needs_puppeteer to return True
        with patch.object(scraper, '_needs_puppeteer', return_value=True):
            html, headers, status_code, redirections = asyncio.run(scraper.fetch_html("https://example.com"))
            
        assert "Dynamic Page" in html
        assert mock_run.called
        
    def test_needs_puppeteer(self):
        """Test detection of JS-rendered pages"""
        scraper = Scraper()
        
        # Test empty HTML
        assert scraper._needs_puppeteer("", "https://example.com")
        
        # Test page with no title
        assert scraper._needs_puppeteer("<html><body>Content</body></html>", "https://example.com")
        
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
        assert scraper._needs_puppeteer(spa_html, "https://example.com")
        
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
        assert not scraper._needs_puppeteer(normal_html, "https://example.com")
        
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
        assert "/internal" in result["links"]["internal"]
        assert "https://external.com" in result["links"]["external"]


class TestSEOAnalyzer:
    """Tests for the SEOAnalyzer service"""
    
    @pytest.fixture
    def seo_analyzer(self):
        """Create SEOAnalyzer instance"""
        return SEOAnalyzer()
    
    @patch('services.seo_analyzer.Scraper')
    @patch('services.seo_analyzer.SemanticAnalyzer')
    async def test_analyze_site(self, mock_semantic_analyzer, mock_scraper, seo_analyzer):
        """Test the main analyze_site method"""
        # Mock scraper
        mock_scraper_instance = MagicMock()
        mock_scraper.return_value = mock_scraper_instance
        
        # Mock HTML fetch result
        mock_scraper_instance.fetch_html.return_value = (
            "<html><title>Test Page</title></html>",
            {"Content-Type": "text/html"},
            200,
            []
        )
        
        # Mock parsed data
        mock_scraper_instance.parse_html.return_value = {
            "title": {"text": "Test Page", "length": 9},
            "meta_description": {"text": "Test description", "length": 16},
            "meta_robots": "index,follow",
            "canonical_url": "https://example.com",
            "h_tags": {"h1": [{"text": "Hello"}], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []},
            "paragraphs": [{"text": "Test paragraph", "length": 14}],
            "images_without_alt": [{"src": "image.jpg"}],
            "links": {"internal": ["/page"], "external": ["https://external.com"]},
            "semantic_structure": ["main", "nav"],
            "structured_data": ["JSON-LD"]
        }
        
        # Mock semantic analyzer
        mock_semantic_analyzer_instance = MagicMock()
        mock_semantic_analyzer.return_value = mock_semantic_analyzer_instance
        mock_semantic_analyzer_instance.analyze_semantics.return_value = {
            "llm_engine": "chatgpt",
            "coherence_score": 0.8,
            "detected_intent": "Information",
            "readability_level": "B1",
            "suggested_improvements": ["Add more keywords"]
        }
        
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
        assert result.semantic_summary.coherence_score == 0.8
        assert result.semantic_summary.llm_engine == "chatgpt"
        assert len(result.recommendations) == 2
        

class TestSemanticAnalyzer:
    """Tests for the SemanticAnalyzer service"""
    
    @pytest.fixture
    def semantic_analyzer(self):
        """Create SemanticAnalyzer instance"""
        return SemanticAnalyzer()
    
    @patch('services.semantic_analyzer.OpenAIClient')
    async def test_analyze_semantics_openai(self, mock_openai, semantic_analyzer):
        """Test semantic analysis with OpenAI"""
        # Mock OpenAI client
        mock_openai_instance = MagicMock()
        mock_openai.return_value = mock_openai_instance
        mock_openai_instance.analyze_text.return_value = {
            "coherence_score": 0.85,
            "detected_intent": "Product Information",
            "readability_level": "B2",
            "suggested_improvements": ["Add more specific details", "Use more keywords"]
        }
        
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
        
        # Check result
        assert result["llm_engine"] == "chatgpt"
        assert result["coherence_score"] == 0.85
        assert result["detected_intent"] == "Product Information"
        assert result["readability_level"] == "B2"
        assert len(result["suggested_improvements"]) == 2
        
    @patch('services.semantic_analyzer.AnthropicClient')
    async def test_analyze_semantics_claude(self, mock_anthropic, semantic_analyzer):
        """Test semantic analysis with Claude"""
        # Mock Anthropic client
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        mock_anthropic_instance.analyze_text.return_value = {
            "coherence_score": 0.75,
            "detected_intent": "Service Offering",
            "readability_level": "B1",
            "suggested_improvements": ["Improve clarity", "Add call to action"]
        }
        
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
        
        # Check result
        assert result["llm_engine"] == "claude"
        assert result["coherence_score"] == 0.75
        assert result["detected_intent"] == "Service Offering"
        assert result["readability_level"] == "B1"
        assert len(result["suggested_improvements"]) == 2
        
    @patch('services.semantic_analyzer.GeminiClient')
    async def test_analyze_semantics_gemini(self, mock_gemini, semantic_analyzer):
        """Test semantic analysis with Gemini"""
        # Mock Gemini client
        mock_gemini_instance = MagicMock()
        mock_gemini.return_value = mock_gemini_instance
        mock_gemini_instance.analyze_text.return_value = {
            "coherence_score": 0.9,
            "detected_intent": "Educational Content",
            "readability_level": "A2",
            "suggested_improvements": ["Add more examples", "Include FAQs"]
        }
        
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
        
        # Check result
        assert result["llm_engine"] == "gemini"
        assert result["coherence_score"] == 0.9
        assert result["detected_intent"] == "Educational Content"
        assert result["readability_level"] == "A2"
        assert len(result["suggested_improvements"]) == 2
        
    async def test_parse_llm_response(self, semantic_analyzer):
        """Test parsing LLM responses"""
        # Test valid JSON
        json_response = '{"coherence_score": 0.8, "detected_intent": "Test", "readability_level": "B1", "suggested_improvements": ["Test 1", "Test 2"]}'
        result = semantic_analyzer._parse_llm_response(json_response)
        assert result["coherence_score"] == 0.8
        assert result["detected_intent"] == "Test"
        
        # Test JSON in code block
        json_in_block = '```json\n{"coherence_score": 0.7, "detected_intent": "Test Block", "readability_level": "A2", "suggested_improvements": ["Test 3", "Test 4"]}\n```'
        result = semantic_analyzer._parse_llm_response(json_in_block)
        assert result["coherence_score"] == 0.7
        assert result["detected_intent"] == "Test Block"
        
        # Test invalid JSON (fallback)
        invalid_json = 'coherence_score: 0.9, detected_intent: "Invalid Format", readability_level: B2, suggested_improvements: ["Test 5"]'
        result = semantic_analyzer._parse_llm_response(invalid_json)
        assert "coherence_score" in result
        assert "detected_intent" in result
        assert "readability_level" in result
        assert "suggested_improvements" in result