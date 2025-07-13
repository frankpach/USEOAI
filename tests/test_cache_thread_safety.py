import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.seo_analyzer import SEOAnalyzer
from app.models.seo_models import AnalysisRequest


@pytest.mark.asyncio
class TestSEOAnalyzerCacheThreadSafety:
    """Tests for thread-safe cache operations in SEOAnalyzer"""
    
    @pytest.fixture
    def seo_analyzer(self):
        """Create SEOAnalyzer instance"""
        return SEOAnalyzer()
    
    def test_cache_lock_creation(self, seo_analyzer):
        """Test that cache locks are created correctly"""
        url1 = "https://example1.com"
        url2 = "https://example2.com"
        
        # Get locks for different URLs
        lock1 = seo_analyzer._get_cache_lock(url1)
        lock2 = seo_analyzer._get_cache_lock(url2)
        
        # Different URLs should have different locks
        assert lock1 is not lock2
        
        # Same URL should return same lock
        lock1_again = seo_analyzer._get_cache_lock(url1)
        assert lock1 is lock1_again
    
    async def test_concurrent_cache_access_same_url(self, seo_analyzer):
        """Test concurrent access to cache with same URL"""
        url = "https://example.com"
        
        # Mock scraper
        mock_scraper = MagicMock()
        mock_scraper.fetch_html = AsyncMock(return_value=(
            "<html><title>Test Page</title><body><h1>Hello</h1></body></html>",
            {"Content-Type": "text/html"},
            200,
            []
        ))
        mock_scraper.parse_html.return_value = {
            "title": {"text": "Test Page", "length": 9},
            "meta_description": {"text": "Test description", "length": 16},
            "meta_robots": "index,follow",
            "canonical_url": "https://example.com",
            "h_tags": {"h1": [{"text": "Hello"}], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []},
            "paragraphs": [{"text": "Test paragraph", "length": 14}],
            "images_without_alt": [],
            "links": {"internal": [], "external": []},
            "semantic_structure": [],
            "structured_data": []
        }
        
        # Mock semantic analyzer
        mock_semantic_analyzer = AsyncMock()
        mock_semantic_analyzer.analyze_semantics = AsyncMock(return_value={
            "llm_engine": "chatgpt",
            "coherence_score": 0.8,
            "detected_intent": "Information",
            "readability_level": "B1",
            "suggested_improvements": ["Add more keywords"]
        })
        
        # Replace instances
        seo_analyzer.scraper = mock_scraper
        seo_analyzer.semantic_analyzer = mock_semantic_analyzer
        
        # Create analysis request
        request = AnalysisRequest(
            url=url,
            seo_goal="Rank for test keywords",
            location="Test City",
            language="en"
        )
        
        # Mock other methods to avoid complex dependencies
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
             patch.object(seo_analyzer, '_generate_recommendations', return_value=[]):
            
            # Run concurrent analyses on the same URL
            tasks = [seo_analyzer.analyze_site(request) for _ in range(5)]
            results = await asyncio.gather(*tasks)
            
            # All analyses should complete successfully
            assert len(results) == 5
            for result in results:
                assert result.status_code == 200
                assert result.title.text == "Test Page"
            
            # Cache should contain the URL
            assert url in seo_analyzer._html_cache
            # Only one lock should be created for the URL
            assert len([k for k in seo_analyzer._cache_locks.keys() if k == url]) == 1
    
    async def test_concurrent_cache_access_different_urls(self, seo_analyzer):
        """Test concurrent access to cache with different URLs"""
        urls = ["https://example1.com", "https://example2.com", "https://example3.com"]
        
        # Mock scraper
        mock_scraper = MagicMock()
        mock_scraper.fetch_html = AsyncMock(return_value=(
            "<html><title>Test Page</title><body><h1>Hello</h1></body></html>",
            {"Content-Type": "text/html"},
            200,
            []
        ))
        mock_scraper.parse_html.return_value = {
            "title": {"text": "Test Page", "length": 9},
            "meta_description": {"text": "Test description", "length": 16},
            "meta_robots": "index,follow",
            "canonical_url": "https://example.com",
            "h_tags": {"h1": [{"text": "Hello"}], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []},
            "paragraphs": [{"text": "Test paragraph", "length": 14}],
            "images_without_alt": [],
            "links": {"internal": [], "external": []},
            "semantic_structure": [],
            "structured_data": []
        }
        
        # Mock semantic analyzer
        mock_semantic_analyzer = AsyncMock()
        mock_semantic_analyzer.analyze_semantics = AsyncMock(return_value={
            "llm_engine": "chatgpt",
            "coherence_score": 0.8,
            "detected_intent": "Information",
            "readability_level": "B1",
            "suggested_improvements": ["Add more keywords"]
        })
        
        # Replace instances
        seo_analyzer.scraper = mock_scraper
        seo_analyzer.semantic_analyzer = mock_semantic_analyzer
        
        # Create analysis requests for different URLs
        requests = [
            AnalysisRequest(
                url=url,
                seo_goal="Rank for test keywords",
                location="Test City",
                language="en"
            ) for url in urls
        ]
        
        # Mock other methods to avoid complex dependencies
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
             patch.object(seo_analyzer, '_generate_recommendations', return_value=[]):
            
            # Run concurrent analyses on different URLs
            tasks = [seo_analyzer.analyze_site(request) for request in requests]
            results = await asyncio.gather(*tasks)
            
            # All analyses should complete successfully
            assert len(results) == 3
            for result in results:
                assert result.status_code == 200
                assert result.title.text == "Test Page"
            
            # Cache should contain all URLs
            for url in urls:
                assert url in seo_analyzer._html_cache
            
            # Each URL should have its own lock
            assert len(seo_analyzer._cache_locks) == 3
            for url in urls:
                assert url in seo_analyzer._cache_locks
    
    async def test_cache_operations_atomicity(self, seo_analyzer):
        """Test that cache operations are atomic"""
        url = "https://example.com"
        
        # Mock HTML content
        html_content = "<html><title>Test</title></html>"
        
        # Simulate concurrent cache writes
        async def write_to_cache():
            async with seo_analyzer._get_cache_lock(url):
                # Simulate some processing time
                await asyncio.sleep(0.001)  # Small delay to test race conditions
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'lxml')
                seo_analyzer._html_cache[url] = soup
        
        # Simulate concurrent cache reads
        async def read_from_cache():
            async with seo_analyzer._get_cache_lock(url):
                if url in seo_analyzer._html_cache:
                    return seo_analyzer._html_cache[url]
                return None
        
        # Run multiple concurrent operations
        write_tasks = [write_to_cache() for _ in range(3)]
        read_tasks = [read_from_cache() for _ in range(3)]
        
        # Mix write and read operations
        all_tasks = write_tasks + read_tasks
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # No exceptions should occur
        for result in results:
            assert not isinstance(result, Exception)
        
        # Cache should be consistent
        assert url in seo_analyzer._html_cache
        cached_soup = seo_analyzer._html_cache[url]
        assert cached_soup is not None
        assert cached_soup.title.string == "Test"