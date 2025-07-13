import asyncio
import logging
import re
import time
import hashlib
from typing import Dict, Optional, Tuple, Union, List, Set
import requests
from bs4 import BeautifulSoup
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page
from pyppeteer.errors import TimeoutError, NetworkError, PageError
from urllib.parse import urljoin, urlparse, ParseResult
import aiohttp
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserPool:
    """Manage a pool of browser instances for concurrent scraping"""
    
    def __init__(self, max_browsers: int = 3):
        self.max_browsers = max_browsers
        self._browsers: List[Browser] = []
        self._semaphore = asyncio.Semaphore(max_browsers)
        self._initialization_lock = asyncio.Lock()
        
    async def get_browser(self) -> Browser:
        """Get an available browser from the pool or create a new one"""
        async with self._semaphore:
            if not self._browsers:
                async with self._initialization_lock:
                    if not self._browsers:
                        for _ in range(self.max_browsers):
                            browser = await launch(
                                headless=True,
                                args=[
                                    '--no-sandbox',
                                    '--disable-setuid-sandbox',
                                    '--disable-dev-shm-usage',
                                    '--disable-accelerated-2d-canvas',
                                    '--disable-gpu'
                                ],
                                ignoreHTTPSErrors=True,
                                handleSIGINT=False,
                                handleSIGTERM=False,
                                handleSIGHUP=False
                            )
                            self._browsers.append(browser)
            
            # Return the first available browser
            return self._browsers[0]
    
    async def close_all(self):
        """Close all browser instances"""
        for browser in self._browsers:
            try:
                await browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
        self._browsers = []


class Scraper:
    """
    Enhanced web scraper with intelligent fallback between requests and Puppeteer,
    caching, and performance optimizations.
    """
    
    def __init__(self, timeout: int = 20, user_agent: Optional[str] = None, max_browsers: int = 3):
        """
        Initialize the scraper.
        
        Args:
            timeout: Maximum time in seconds for scraping operations
            user_agent: Custom user agent string
            max_browsers: Maximum number of concurrent browser instances
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67"
        )
        self._browser_pool = BrowserPool(max_browsers=max_browsers)
        self._url_cache = {}  # Simple in-memory cache
        self._broken_links_cache = {}  # Cache for broken links check
        
    async def fetch_html(self, url: str) -> Tuple[str, Dict, int, List[str]]:
        """
        Fetch HTML content from URL using requests first.
        If inadequate content is detected, fallback to puppeteer.
        
        Args:
            url: URL to scrape
        
        Returns:
            Tuple of (html_content, headers, status_code, redirections)
        """
        cache_key = self._generate_cache_key(url)
        
        # Check cache first
        if cache_key in self._url_cache:
            logger.info(f"Using cached result for {url}")
            return self._url_cache[cache_key]
        
        logger.info(f"Fetching URL: {url}")
        redirections = []
        html_content = ""
        headers = {}
        status_code = 0

        try:
            # First attempt with requests
            start_time = time.time()
            response = requests.get(
                url,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout,
                allow_redirects=True
            )
            
            request_time = time.time() - start_time
            logger.info(f"Request completed in {request_time:.2f} seconds")

            if response.history:
                redirections = [r.url for r in response.history]
                logger.info(f"Redirections: {redirections}")

            html_content = response.text
            headers = dict(response.headers)
            status_code = response.status_code
            
            # Don't process further if we got an error status code
            if status_code >= 400:
                logger.warning(f"Received error status code: {status_code}")
                result = (html_content, headers, status_code, redirections)
                self._url_cache[cache_key] = result
                return result

            if self._needs_puppeteer(html_content, url):
                logger.info("Static HTML insufficient, switching to Puppeteer")
                html_content, headers, status_code, puppeteer_redirects = await self._fetch_with_puppeteer(url)
                # Combine redirections from both methods
                for redirect in puppeteer_redirects:
                    if redirect not in redirections:
                        redirections.append(redirect)

        except (requests.RequestException, Exception) as e:
            logger.error(f"Requests error: {e}, trying Puppeteer")
            try:
                html_content, headers, status_code, redirections = await self._fetch_with_puppeteer(url)
            except Exception as e:
                logger.error(f"Puppeteer error: {e}")
                return "", {}, 0, redirections
                
        # Cache the result
        result = (html_content, headers, status_code, redirections)
        self._url_cache[cache_key] = result
        return result
    
    def _generate_cache_key(self, url: str) -> str:
        """Generate a cache key for a URL"""
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def _needs_puppeteer(self, html_content: str, url: str) -> bool:
        """
        Determine if the page needs JavaScript rendering using advanced heuristics.
        
        Args:
            html_content: Raw HTML content
            url: Original URL for context
            
        Returns:
            Boolean indicating if Puppeteer should be used
        """
        if not html_content or len(html_content) < 500:
            logger.info("Content too short or empty, needs Puppeteer")
            return True
            
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Check for title
        if not soup.title:
            logger.info("No title found, needs Puppeteer")
            return True
            
        # Check for essential content
        if not soup.find('h1') and not soup.find('main') and not soup.find('div', {'class': ['content', 'main', 'container']}):
            logger.info("No main content elements found, needs Puppeteer")
            return True
            
        # Count content vs script ratio
        script_count = len(soup.find_all('script'))
        div_count = len(soup.find_all('div'))
        content_tags = len(soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table']))
        
        # High ratio of scripts to content could indicate SPA
        if script_count > 8 and content_tags < 5 and div_count > 30:
            logger.info(f"Script-heavy page detected ({script_count} scripts, {content_tags} content elements), needs Puppeteer")
            return True
            
        # Check for application/json scripts (common in React, Vue apps)
        json_scripts = soup.find_all('script', {'type': 'application/json'})
        if json_scripts:
            logger.info("JSON scripts found, likely a SPA, needs Puppeteer")
            return True
            
        # Look for common JS framework identifiers
        js_frameworks = ['react', 'vue', 'angular', 'next', 'nuxt', 'ember', 'backbone', 'svelte']
        for script in soup.find_all('script', {'src': True}):
            src = script.get('src', '').lower()
            if any(framework in src for framework in js_frameworks):
                logger.info(f"JS framework detected in script sources, needs Puppeteer")
                return True
                
        # Check for SPA-specific HTML patterns
        if soup.find('div', {'id': ['root', 'app', '__next', 'application']}):
            logger.info("SPA root element found, needs Puppeteer")
            return True
            
        # Check if content seems incomplete
        if content_tags < 3 and div_count > 15:
            logger.info("Very little content with many divs, may need Puppeteer")
            return True
            
        return False
    
    async def _fetch_with_puppeteer(self, url: str) -> Tuple[str, Dict, int, List[str]]:
        """
        Fetch HTML content using Puppeteer (for JS-rendered pages).
        
        Args:
            url: URL to scrape
            
        Returns:
            Tuple of (html_content, headers, status_code, redirections)
        """
        browser = None
        page = None
        status_code = 0
        redirections = []
        
        try:
            # Get browser from pool
            browser = await self._browser_pool.get_browser()
            
            # Create a new page
            page = await browser.newPage()
            
            # Configure page
            await page.setUserAgent(self.user_agent)
            await page.setViewport({'width': 1920, 'height': 1080})
            
            # Set request interception for improved performance and redirect tracking
            await page.setRequestInterception(True)
            
            # Track redirects and block unnecessary resources
            redirects = []
            
            async def intercept_request(request):
                # Track potential redirections
                if request.isNavigationRequest() and request.redirectChain():
                    for redirect in request.redirectChain():
                        redirect_url = redirect.url
                        if redirect_url not in redirects:
                            redirects.append(redirect_url)
                
                # Block unnecessary resources to speed up loading
                if request.resourceType in ['image', 'media', 'font', 'websocket']:
                    await request.abort()
                else:
                    await request.continue_()
            
            page.on('request', intercept_request)
            
            # Set timeout
            page_timeout = self.timeout * 1000  # Convert to ms
            
            # Navigate with timeout
            response = await page.goto(url, {
                'waitUntil': 'networkidle2',
                'timeout': page_timeout
            })
            
            # Extract headers and status
            headers = {}
            if response:
                headers = await response.allHeaders()
                status_code = response.status
            else:
                logger.warning("No response object returned by Puppeteer")
                
            # Wait for body content
            try:
                await page.waitForSelector('body', {'timeout': 3000})
            except Exception as e:
                logger.warning(f"No body selector visible: {e}")
                
            # Wait a bit for any final JS execution
            await asyncio.sleep(1)
                
            # Get the HTML content
            html_content = await page.content()
            
            # Handle potential CAPTCHA (simple detection)
            if self._is_captcha_page(html_content):
                logger.warning("CAPTCHA detected, attempting bypass")
                html_content = await self._try_captcha_bypass(page, html_content)
                
            return html_content, headers, status_code, redirects
            
        except (TimeoutError, NetworkError, PageError) as e:
            logger.error(f"Puppeteer error: {e}")
            return "", {}, 0, redirections
            
        finally:
            # Clean up
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")
    
    def _is_captcha_page(self, html_content: str) -> bool:
        """Check if the page contains a CAPTCHA"""
        soup = BeautifulSoup(html_content, 'lxml')
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'hcaptcha',
            'security check',
            'verify you are human',
            'bot check',
            'cloudflare'
        ]
        
        page_text = soup.get_text().lower()
        
        # Check for captcha in text
        if any(indicator in page_text for indicator in captcha_indicators):
            return True
            
        # Check for captcha in element IDs and classes
        for element in soup.find_all(True):
            element_id = element.get('id', '').lower()
            element_class = ' '.join(element.get('class', [])).lower()
            
            if any(indicator in element_id or indicator in element_class for indicator in captcha_indicators):
                return True
                
        return False
    
    async def _try_captcha_bypass(self, page: Page, html_content: str) -> str:
        """
        Basic attempt to bypass simple CAPTCHAs
        For complex CAPTCHAs, consider integrating with external solving services
        """
        try:
            # Look for common CAPTCHA forms or buttons
            captcha_buttons = await page.JJ('button, input[type="submit"]')
            
            for button in captcha_buttons:
                button_text = await page.evaluate('(element) => element.textContent', button)
                if button_text and any(text in button_text.lower() for text in ['continue', 'verify', 'proceed', 'submit']):
                    await button.click()
                    await page.waitForNavigation({'timeout': 5000})
                    return await page.content()
                    
            # Try to find "I'm not a robot" checkbox
            checkboxes = await page.JJ('input[type="checkbox"]')
            for checkbox in checkboxes:
                await checkbox.click()
                await asyncio.sleep(2)
                return await page.content()
                    
        except Exception as e:
            logger.warning(f"CAPTCHA bypass attempt failed: {e}")
            
        return html_content
    
    async def close(self):
        """Close all resources"""
        await self._browser_pool.close_all()
    
    def parse_html(self, html: str, base_url: str) -> Dict:
        """
        Parse HTML content with BeautifulSoup.
        
        Args:
            html: HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            Dictionary with parsed data
        """
        if not html:
            logger.error("Empty HTML content")
            return {}
            
        soup = BeautifulSoup(html, 'lxml')
        
        # Set base URL for link resolution
        if not base_url.startswith(('http://', 'https://')):
            base_url = f"https://{base_url}"
        
        parsed_url = urlparse(base_url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        return {
            "title": self._extract_title(soup),
            "meta_description": self._extract_meta_description(soup),
            "meta_robots": self._extract_meta_robots(soup),
            "canonical_url": self._extract_canonical(soup, base_url),
            "h_tags": self._extract_headings(soup),
            "paragraphs": self._extract_paragraphs(soup),
            "images_without_alt": self._extract_images_without_alt(soup, base_url),
            "links": self._extract_links(soup, base_url),
            "semantic_structure": self._extract_semantic_structure(soup),
            "structured_data": self._extract_structured_data(soup),
            "page_metrics": self._extract_page_metrics(soup, html),
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> Dict:
        """Extract page title"""
        title_tag = soup.title
        title_text = title_tag.get_text().strip() if title_tag else ""
        return {
            "text": title_text,
            "length": len(title_text),
        }
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> Dict:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        content = meta_desc.get('content', '').strip() if meta_desc else ""
        return {
            "text": content,
            "length": len(content)
        }
    
    def _extract_meta_robots(self, soup: BeautifulSoup) -> str:
        """Extract meta robots"""
        meta_robots = soup.find('meta', attrs={'name': 'robots'})
        return meta_robots.get('content', 'index,follow') if meta_robots else "index,follow"
    
    def _extract_canonical(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract canonical URL"""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical and canonical.get('href'):
            # Convert relative URLs to absolute
            return urljoin(base_url, canonical.get('href'))
        return ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict:
        """Extract all heading tags (h1-h6)"""
        headings = {}
        for level in range(1, 7):
            h_tags = soup.find_all(f'h{level}')
            headings[f'h{level}'] = [
                {
                    "text": tag.get_text().strip(),
                    "word_count": len(tag.get_text().strip().split())
                }
                for tag in h_tags
            ]
        return headings
    
    def _extract_paragraphs(self, soup: BeautifulSoup) -> list:
        """Extract paragraphs"""
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:  # Skip empty paragraphs
                paragraphs.append({
                    "text": text,
                    "length": len(text),
                    "word_count": len(text.split())
                })
        return paragraphs
    
    def _extract_images_without_alt(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract images missing alt text"""
        images = []
        for img in soup.find_all('img'):
            if not img.get('alt'):
                src = img.get('src', '')
                if src:
                    full_src = urljoin(base_url, src)
                    images.append({
                        "src": full_src,
                        "width": img.get('width', 'unknown'),
                        "height": img.get('height', 'unknown')
                    })
        return images
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Extract and categorize links"""
        internal = []
        external = []
        broken = []
        
        # Get base domain for internal/external classification
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc
        
        # Gather all unique links
        links_found = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            
            # Skip anchors, javascript, mailto links
            if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
                
            # Convert to absolute URL
            full_url = urljoin(base_url, href)
            
            # Skip if we've already processed this URL
            if full_url in links_found:
                continue
                
            links_found.add(full_url)
            
            # Parse the URL
            parsed_url = urlparse(full_url)
            
            # Check if internal or external
            if parsed_url.netloc == base_domain or not parsed_url.netloc:
                internal.append(full_url)
            else:
                external.append(full_url)
            
            # Check broken status (implement as a separate async process)
            if self._is_link_broken_cached(full_url):
                broken.append(full_url)
                
        return {
            "internal": internal,
            "external": external,
            "broken": broken
        }
    
    @lru_cache(maxsize=1000)
    def _is_link_broken_cached(self, url: str) -> bool:
        """Check if a link is broken (with caching)"""
        # Check the cache first
        if url in self._broken_links_cache:
            return self._broken_links_cache[url]
            
        try:
            response = requests.head(
                url, 
                timeout=5,
                headers={"User-Agent": self.user_agent},
                allow_redirects=True
            )
            is_broken = response.status_code >= 400
            
        except requests.RequestException:
            is_broken = True
            
        # Cache the result
        self._broken_links_cache[url] = is_broken
        return is_broken
    
    async def check_broken_links_async(self, links: List[str]) -> List[str]:
        """
        Check broken links asynchronously (use for many links)
        """
        broken_links = []
        
        async def check_link(url):
            if self._is_link_broken_cached(url):
                broken_links.append(url)
                
        async with aiohttp.ClientSession() as session:
            tasks = []
            for link in links:
                task = asyncio.create_task(check_link(link))
                tasks.append(task)
                
            await asyncio.gather(*tasks)
            
        return broken_links
    
    def _extract_semantic_structure(self, soup: BeautifulSoup) -> List[str]:
        """Extract semantic HTML5 elements"""
        semantic_tags = [
            'header', 'nav', 'main', 'article', 'section', 
            'aside', 'footer', 'figure', 'figcaption', 'time',
            'details', 'summary', 'mark'
        ]
        
        found_tags = []
        for tag in semantic_tags:
            if soup.find(tag):
                found_tags.append(tag)
                
        return found_tags
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[str]:
        """Extract structured data types"""
        structured_data_types = []
        
        # Check for JSON-LD
        if soup.find_all('script', {'type': 'application/ld+json'}):
            structured_data_types.append('JSON-LD')
            
        # Check for Open Graph
        if soup.find('meta', {'property': re.compile(r'^og:')}):
            structured_data_types.append('OpenGraph')
            
        # Check for Twitter Card
        if soup.find('meta', {'name': re.compile(r'^twitter:')}):
            structured_data_types.append('TwitterCard')
            
        # Check for microdata
        if soup.find(itemscope=True):
            structured_data_types.append('Microdata')
            
        # Check for RDFa
        if soup.find(attrs={"vocab": True}) or soup.find(attrs={"typeof": True}):
            structured_data_types.append('RDFa')
            
        return structured_data_types
        
    def _extract_page_metrics(self, soup: BeautifulSoup, html: str) -> Dict:
        """Extract page metrics for performance analysis"""
        # Count resources
        scripts = len(soup.find_all('script'))
        external_scripts = len([s for s in soup.find_all('script', src=True) if s.get('src', '').startswith(('http', '//'))])
        
        styles = len(soup.find_all('link', rel='stylesheet'))
        inline_styles = len(soup.find_all('style'))
        
        images = len(soup.find_all('img'))
        lazy_images = len([img for img in soup.find_all('img') if img.get('loading') == 'lazy'])
        
        # Check for resource optimization hints
        preload_resources = len(soup.find_all('link', rel='preload'))
        prefetch_resources = len(soup.find_all('link', rel='prefetch'))
        
        # Calculate HTML size
        html_size_kb = len(html) / 1024
        
        return {
            "resource_counts": {
                "scripts_total": scripts,
                "scripts_external": external_scripts,
                "styles_total": styles + inline_styles,
                "styles_external": styles,
                "images_total": images,
                "images_lazy_loaded": lazy_images
            },
            "optimization_hints": {
                "preload_resources": preload_resources,
                "prefetch_resources": prefetch_resources
            },
            "html_size_kb": round(html_size_kb, 2),
            "has_lazy_loading": lazy_images > 0
        }   