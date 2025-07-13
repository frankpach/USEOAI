import asyncio
import logging
from typing import List, Dict, Any
from app.services.scraper import Scraper
from app.models.seo_models import AnalysisRequest, AnalysisResponse
from app.services.seo_analyzer import SEOAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchAnalyzer:
    """
    Service for performing batch analysis of multiple URLs concurrently
    using asyncio.gather for maximum performance.
    """
    
    def __init__(self, max_concurrent: int = 5):
        """
        Initialize the batch analyzer.
        
        Args:
            max_concurrent: Maximum number of concurrent analyses
        """
        self.max_concurrent = max_concurrent
        self.seo_analyzer = SEOAnalyzer()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def analyze_batch(self, requests: List[AnalysisRequest]) -> List[Dict[str, Any]]:
        """
        Analyze multiple URLs concurrently.
        
        Args:
            requests: List of AnalysisRequest objects
            
        Returns:
            List of analysis results
        """
        logger.info(f"Starting batch analysis of {len(requests)} URLs")
        
        async def analyze_with_semaphore(request: AnalysisRequest) -> Dict[str, Any]:
            """Analyze a single URL with semaphore for concurrency control"""
            async with self.semaphore:
                try:
                    logger.info(f"Analyzing {request.url}")
                    result = await self.seo_analyzer.analyze_site(request)
                    return {
                        "url": request.url,
                        "success": True,
                        "result": result.dict() if result else None
                    }
                except Exception as e:
                    logger.error(f"Error analyzing {request.url}: {e}")
                    return {
                        "url": request.url,
                        "success": False,
                        "error": str(e)
                    }
        
        # Create tasks for all URLs
        tasks = [analyze_with_semaphore(request) for request in requests]
        
        # Execute all tasks concurrently with gather
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def analyze_sitemap(self, base_url: str, seo_goal: str, location: str, 
                              language: str = "es", max_urls: int = 50) -> Dict[str, Any]:
        """
        Analyze all URLs from a sitemap.
        
        Args:
            base_url: Base URL of the website
            seo_goal: SEO goal for analysis
            location: Target location
            language: Content language
            max_urls: Maximum number of URLs to analyze
            
        Returns:
            Dictionary with analysis results
        """
        # Create scraper to fetch sitemap
        scraper = Scraper()
        
        try:
            # Try common sitemap locations
            sitemap_urls = [
                f"{base_url}/sitemap.xml",
                f"{base_url}/sitemap_index.xml",
                f"{base_url}/sitemap/sitemap.xml"
            ]
            
            sitemap_content = ""
            for sitemap_url in sitemap_urls:
                try:
                    content, _, status_code, _ = await scraper.fetch_html(sitemap_url)
                    if status_code == 200 and "urlset" in content:
                        sitemap_content = content
                        logger.info(f"Found sitemap at {sitemap_url}")
                        break
                except Exception:
                    continue
            
            if not sitemap_content:
                logger.warning(f"No sitemap found for {base_url}")
                return {"success": False, "error": "No sitemap found"}
                
            # Parse sitemap
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(sitemap_content, 'xml')
            url_tags = soup.find_all('url')
            
            urls = []
            for url_tag in url_tags[:max_urls]:  # Limit to max_urls
                loc = url_tag.find('loc')
                if loc and loc.text:
                    urls.append(loc.text.strip())
            
            logger.info(f"Found {len(urls)} URLs in sitemap")
            
            # Create analysis requests
            requests = [
                AnalysisRequest(
                    url=url,
                    seo_goal=seo_goal,
                    location=location,
                    language=language
                )
                for url in urls
            ]
            
            # Analyze all URLs
            results = await self.analyze_batch(requests)
            
            # Aggregate results
            summary = {
                "total_urls": len(urls),
                "successful_analyses": sum(1 for r in results if r.get("success", False)),
                "failed_analyses": sum(1 for r in results if not r.get("success", False)),
                "results": results
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error analyzing sitemap: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_all_pages(self, start_url: str, seo_goal: str, location: str,
                               language: str = "es", max_depth: int = 2, max_urls: int = 50) -> Dict[str, Any]:
        """
        Crawl and analyze all pages on a website up to a certain depth.
        
        Args:
            start_url: Starting URL
            seo_goal: SEO goal for analysis
            location: Target location
            language: Content language
            max_depth: Maximum crawl depth
            max_urls: Maximum number of URLs to analyze
            
        Returns:
            Dictionary with analysis results
        """
        # Create scraper
        scraper = Scraper()
        
        # Queue of URLs to crawl
        to_crawl = [(start_url, 0)]  # (url, depth)
        
        # Set of visited URLs
        visited = set()
        
        # List of URLs to analyze
        analyze_urls = []
        
        # Normalize URL for comparison
        def normalize_url(url):
            url = url.lower()
            url = url.rstrip('/')
            if url.startswith('http://'):
                url = 'https://' + url[7:]
            return url
        
        # Get base domain
        from urllib.parse import urlparse
        parsed_url = urlparse(start_url)
        base_domain = parsed_url.netloc
        
        try:
            # Crawl until we hit max_urls or run out of URLs
            while to_crawl and len(analyze_urls) < max_urls:
                url, depth = to_crawl.pop(0)
                
                # Skip if already visited
                norm_url = normalize_url(url)
                if norm_url in visited:
                    continue
                    
                visited.add(norm_url)
                
                logger.info(f"Crawling {url} at depth {depth}")
                
                # Add to analysis list
                analyze_urls.append(url)
                
                # If we've hit max depth, don't crawl further
                if depth >= max_depth:
                    continue
                    
                # Fetch page
                try:
                    content, _, status_code, _ = await scraper.fetch_html(url)
                    if status_code != 200:
                        continue
                        
                    # Parse links
                    soup = BeautifulSoup(content, 'lxml')
                    links = soup.find_all('a', href=True)
                    
                    # Queue internal links for crawling
                    for link in links:
                        href = link['href'].strip()
                        
                        # Skip non-HTTP links, fragments, etc.
                        if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                            continue
                            
                        # Convert to absolute URL
                        from urllib.parse import urljoin
                        full_url = urljoin(url, href)
                        
                        # Skip external domains
                        parsed_href = urlparse(full_url)
                        if parsed_href.netloc != base_domain:
                            continue
                            
                        # Add to crawl queue
                        norm_href = normalize_url(full_url)
                        if norm_href not in visited:
                            to_crawl.append((full_url, depth + 1))
                            
                except Exception as e:
                    logger.error(f"Error crawling {url}: {e}")
                    
            # Limit the number of URLs to analyze
            analyze_urls = analyze_urls[:max_urls]
            
            logger.info(f"Found {len(analyze_urls)} URLs to analyze")
            
            # Create analysis requests
            requests = [
                AnalysisRequest(
                    url=url,
                    seo_goal=seo_goal,
                    location=location,
                    language=language
                )
                for url in analyze_urls
            ]
            
            # Analyze all URLs
            results = await self.analyze_batch(requests)
            
            # Aggregate results
            summary = {
                "total_urls": len(analyze_urls),
                "successful_analyses": sum(1 for r in results if r.get("success", False)),
                "failed_analyses": sum(1 for r in results if not r.get("success", False)),
                "crawl_depth": max_depth,
                "results": results
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in crawl analysis: {e}")
            return {"success": False, "error": str(e)}