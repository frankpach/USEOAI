#!/usr/bin/env python3
"""
Test script to verify proper resource management in browser pools
"""
import asyncio
import logging
from unittest.mock import Mock, MagicMock, patch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock the browser and page objects
class MockBrowser:
    def __init__(self):
        self.connection = Mock()
        self.connection.closed = False
        self.pages = []
        
    async def newPage(self):
        page = MockPage()
        self.pages.append(page)
        return page
        
    async def close(self):
        self.connection.closed = True
        for page in self.pages:
            await page.close()

class MockPage:
    def __init__(self):
        self.closed = False
        
    async def close(self):
        self.closed = True
        logger.info("Page closed")

async def test_scraper_browser_pool():
    """Test the scraper BrowserPool with mocked browser"""
    from services.scraper import BrowserPool
    
    # Mock the launch function
    with patch('services.scraper.launch') as mock_launch:
        # Create mock browser
        mock_browser = MockBrowser()
        mock_launch.return_value = mock_browser
        
        # Create pool and test context manager
        pool = BrowserPool(max_browsers=1)
        
        logger.info("Testing scraper BrowserPool...")
        
        # Test that get_browser works as context manager
        async with pool.get_browser() as browser:
            logger.info("✓ Browser acquired from pool")
            assert browser is mock_browser
            
            # Test the page context manager
            async with pool.get_page(browser) as page:
                logger.info("✓ Page acquired from browser")
                assert isinstance(page, MockPage)
                assert not page.closed
                
            # Page should be closed after context manager
            assert page.closed
            logger.info("✓ Page properly closed after context manager")
            
        logger.info("✓ Browser returned to pool")
        
        # Close the pool
        await pool.close_all()
        assert mock_browser.connection.closed
        logger.info("✓ Pool closed successfully")

async def test_seo_browser_pool():
    """Test the SEO BrowserPool with mocked browser"""
    from services.seo_analyzer import BrowserPool
    
    # Mock the launch function
    with patch('services.seo_analyzer.launch') as mock_launch:
        # Create mock browser
        mock_browser = MockBrowser()
        mock_launch.return_value = mock_browser
        
        # Create pool and test context manager
        pool = BrowserPool(pool_size=1)
        
        logger.info("Testing SEO BrowserPool...")
        
        # Test that get_browser works as context manager
        async with pool.get_browser() as browser:
            logger.info("✓ Browser acquired from pool")
            assert browser is mock_browser
            
            # Test the page context manager
            async with pool.get_page(browser) as page:
                logger.info("✓ Page acquired from browser")
                assert isinstance(page, MockPage)
                assert not page.closed
                
            # Page should be closed after context manager
            assert page.closed
            logger.info("✓ Page properly closed after context manager")
            
        logger.info("✓ Browser returned to pool")
        
        # Close the pool
        await pool.close()
        assert mock_browser.connection.closed
        logger.info("✓ Pool closed successfully")

async def test_error_handling():
    """Test that resources are properly cleaned up even when exceptions occur"""
    from services.scraper import BrowserPool
    
    with patch('services.scraper.launch') as mock_launch:
        mock_browser = MockBrowser()
        mock_launch.return_value = mock_browser
        
        pool = BrowserPool(max_browsers=1)
        
        logger.info("Testing error handling in resource management...")
        
        # Test that page is closed even if an exception occurs
        page = None
        try:
            async with pool.get_browser() as browser:
                async with pool.get_page(browser) as page:
                    assert not page.closed
                    raise Exception("Test exception")
        except Exception as e:
            logger.info(f"Expected exception caught: {e}")
            
        # Page should still be closed despite the exception
        assert page.closed
        logger.info("✓ Page properly closed even after exception")
        
        await pool.close_all()
        logger.info("✓ Pool closed successfully after exception")

async def main():
    """Run all tests"""
    logger.info("Starting resource management tests...")
    
    await test_scraper_browser_pool()
    await test_seo_browser_pool()
    await test_error_handling()
    
    logger.info("All tests passed! ✓")

if __name__ == "__main__":
    asyncio.run(main())