import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from app.services.seo_analyzer import SEOAnalyzer
from app.models.seo_models import AnalysisRequest


class TestDynamicPerformanceAnalysis:
    """Tests for the new dynamic performance analysis functionality"""
    
    @pytest.fixture
    def seo_analyzer(self):
        """Create SEO analyzer instance for testing"""
        return SEOAnalyzer()
    
    @pytest.fixture
    def mock_requests(self):
        """Mock network requests for testing"""
        return [
            {'url': 'https://example.com', 'resourceType': 'document', 'method': 'GET'},
            {'url': 'https://example.com/script1.js', 'resourceType': 'script', 'method': 'GET'},
            {'url': 'https://example.com/script2.js', 'resourceType': 'script', 'method': 'GET'},
            {'url': 'https://example.com/style.css', 'resourceType': 'stylesheet', 'method': 'GET'},
            {'url': 'https://example.com/image1.jpg', 'resourceType': 'image', 'method': 'GET'},
            {'url': 'https://example.com/image2.png', 'resourceType': 'image', 'method': 'GET'},
            {'url': 'https://example.com/font.woff2', 'resourceType': 'font', 'method': 'GET'},
            {'url': 'https://example.com/api/data', 'resourceType': 'fetch', 'method': 'GET'},
        ]
    
    def test_process_dynamic_requests(self, seo_analyzer, mock_requests):
        """Test the _process_dynamic_requests method"""
        result = seo_analyzer._process_dynamic_requests(mock_requests)
        
        # Verify the structure
        assert 'total_count' in result
        assert 'scripts' in result
        assert 'images' in result
        assert 'stylesheets' in result
        assert 'fonts' in result
        assert 'fetch_requests' in result
        assert 'by_type' in result
        
        # Verify counts (excluding document)
        assert result['total_count'] == 7  # All except document
        assert result['scripts'] == 2
        assert result['images'] == 2
        assert result['stylesheets'] == 1
        assert result['fonts'] == 1
        assert result['fetch_requests'] == 1
        
        # Verify by_type breakdown
        assert result['by_type']['script'] == 2
        assert result['by_type']['image'] == 2
        assert result['by_type']['stylesheet'] == 1
        assert result['by_type']['font'] == 1
        assert result['by_type']['fetch'] == 1
        assert result['by_type']['document'] == 1
    
    @pytest.mark.asyncio
    async def test_analyze_performance_static_fallback(self, seo_analyzer):
        """Test that static analysis works as fallback"""
        # Mock the HTTP client
        mock_response = AsyncMock()
        mock_response.headers = {'Content-Encoding': 'gzip'}
        mock_response.text = AsyncMock(return_value="""
            <html>
                <head>
                    <script src="script1.js"></script>
                    <script>console.log('inline');</script>
                    <link rel="stylesheet" href="style.css">
                    <style>body { color: red; }</style>
                </head>
                <body>
                    <img src="image1.jpg" alt="Image 1">
                    <img src="image2.png" alt="Image 2" loading="lazy">
                </body>
            </html>
        """)
        
        # Mock the context manager behavior
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        with patch.object(seo_analyzer.http_client, 'get', return_value=mock_response):
            with patch('time.time', side_effect=[0, 0.1]):  # Mock time for TTFB calculation
                result = await seo_analyzer._analyze_performance_static("https://example.com")
        
        # Verify basic metrics
        assert result['ttfb_ms'] >= 0  # Should be 100ms from mock
        assert result['gzip_enabled'] is True
        assert result['lazy_loaded_images'] is True
        assert result['resource_count'] > 0
        
        # Verify new fields are present with default values
        assert 'resource_types' in result
        assert 'scripts_count' in result
        assert 'images_count' in result
        assert 'stylesheets_count' in result
        assert 'fonts_count' in result
        assert 'fetch_requests_count' in result
        assert 'total_requests' in result
        
        # Verify specific counts
        assert result['scripts_count'] == 2  # 1 external + 1 inline
        assert result['images_count'] == 2
        assert result['stylesheets_count'] == 1
        assert result['fonts_count'] == 0
        assert result['fetch_requests_count'] == 0
        assert result['total_requests'] == 0
    
    @pytest.mark.asyncio
    async def test_analyze_performance_dynamic_success(self, seo_analyzer, mock_requests):
        """Test successful dynamic performance analysis"""
        # Mock the _process_dynamic_requests to return expected results
        mock_process_result = {
            'total_count': 7,
            'scripts': 2,
            'images': 2,
            'stylesheets': 1,
            'fonts': 1,
            'fetch_requests': 1,
            'by_type': {
                'script': 2,
                'image': 2,
                'stylesheet': 1,
                'font': 1,
                'fetch': 1,
                'document': 1
            }
        }
        
        # Mock browser pool and page interactions
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_response = AsyncMock()
        mock_response.headers = {'content-encoding': 'gzip'}
        
        mock_browser.newPage.return_value = mock_page
        mock_page.goto.return_value = mock_response
        mock_page.evaluate.return_value = True  # lazy loading detected
        mock_page.setRequestInterception = AsyncMock()
        mock_page.on = Mock()  # Just record the event handler
        mock_page.close = AsyncMock()
        
        # Mock browser pool context manager
        browser_context = AsyncMock()
        browser_context.__aenter__.return_value = mock_browser
        browser_context.__aexit__.return_value = None
        
        with patch.object(seo_analyzer.browser_pool, 'get_browser', return_value=browser_context):
            with patch.object(seo_analyzer, '_process_dynamic_requests', return_value=mock_process_result):
                with patch('time.time', side_effect=[0, 0.1]):  # Mock time for TTFB
                    result = await seo_analyzer._analyze_performance_dynamic("https://example.com")
        
        # Verify results
        assert result['ttfb_ms'] == 100  # 0.1 seconds = 100ms
        assert result['gzip_enabled'] is True
        assert result['lazy_loaded_images'] is True
        assert result['resource_count'] == 7
        assert result['scripts_count'] == 2
        assert result['images_count'] == 2
        assert result['stylesheets_count'] == 1
        assert result['fonts_count'] == 1
        assert result['fetch_requests_count'] == 1
        assert 'resource_types' in result
        assert 'total_requests' in result
        
        # Verify that browser methods were called
        mock_page.setRequestInterception.assert_called_once_with(True)
        mock_page.on.assert_called_once()
        mock_page.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_performance_fallback_to_static(self, seo_analyzer):
        """Test that dynamic analysis falls back to static analysis on failure"""
        # Mock dynamic analysis to fail
        with patch.object(seo_analyzer, '_analyze_performance_dynamic', side_effect=Exception("Browser failed")):
            with patch.object(seo_analyzer, '_analyze_performance_static') as mock_static:
                mock_static.return_value = {
                    "ttfb_ms": 100,
                    "resource_count": 5,
                    "gzip_enabled": False,
                    "lazy_loaded_images": False,
                    "resource_types": {},
                    "scripts_count": 2,
                    "images_count": 1,
                    "stylesheets_count": 1,
                    "fonts_count": 0,
                    "fetch_requests_count": 0,
                    "total_requests": 0
                }
                
                result = await seo_analyzer._analyze_performance("https://example.com")
                
                # Verify fallback was called
                mock_static.assert_called_once_with("https://example.com")
                
                # Verify result
                assert result['ttfb_ms'] == 100
                assert result['resource_count'] == 5
                assert result['gzip_enabled'] is False
    
    def test_get_default_performance_metrics(self, seo_analyzer):
        """Test that default metrics include all required fields"""
        result = seo_analyzer._get_default_performance_metrics()
        
        # Verify all fields are present
        expected_fields = [
            'ttfb_ms', 'resource_count', 'gzip_enabled', 'lazy_loaded_images',
            'resource_types', 'scripts_count', 'images_count', 'stylesheets_count',
            'fonts_count', 'fetch_requests_count', 'total_requests'
        ]
        
        for field in expected_fields:
            assert field in result
        
        # Verify default values
        assert result['ttfb_ms'] == 999
        assert result['resource_count'] == 0
        assert result['gzip_enabled'] is False
        assert result['lazy_loaded_images'] is False
        assert result['resource_types'] == {}
        assert result['scripts_count'] == 0
        assert result['images_count'] == 0
        assert result['stylesheets_count'] == 0
        assert result['fonts_count'] == 0
        assert result['fetch_requests_count'] == 0
        assert result['total_requests'] == 0