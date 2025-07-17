import asyncio
import logging
import re
import time
import hashlib
from typing import Dict, Optional, Tuple, Union, List, Set
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, ParseResult
import aiohttp
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleScraper:
    """
    Simplified web scraper that works without browser dependencies.
    Uses only requests and BeautifulSoup for basic HTML scraping.
    """

    def __init__(self, timeout: int = 20, user_agent: Optional[str] = None):
        """
        Initialize the scraper.

        Args:
            timeout: Maximum time in seconds for scraping operations
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67"
        )
        self._url_cache = {}  # Simple in-memory cache

    async def fetch_html(self, url: str) -> Tuple[str, Dict, int, List[str]]:
        """
        Fetch HTML content from URL using requests.

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
            # Use requests with proper headers
            start_time = time.time()
            response = requests.get(
                url,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                },
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

            logger.info(f"Status code: {status_code}, Content length: {len(html_content)}")

        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return "", {}, 0, []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "", {}, 0, []

        # Cache the result
        result = (html_content, headers, status_code, redirections)
        self._url_cache[cache_key] = result
        return result

    def _generate_cache_key(self, url: str) -> str:
        """Generate a cache key for a URL"""
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def parse_html(self, html: str, base_url: str) -> Dict:
        """
        Parse HTML content and extract SEO-relevant information.

        Args:
            html: HTML content to parse
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary with parsed SEO data
        """
        if not html:
            return {}

        try:
            soup = BeautifulSoup(html, 'lxml')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return {}

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
            "structured_data": self._extract_structured_data(soup)
        }

    def _extract_title(self, soup: BeautifulSoup) -> Dict:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title_text = title_tag.string.strip()
            return {
                "text": title_text,
                "length": len(title_text)
            }
        return {"text": "", "length": 0}

    def _extract_meta_description(self, soup: BeautifulSoup) -> Dict:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc_text = meta_desc['content'].strip()
            return {
                "text": desc_text,
                "length": len(desc_text)
            }
        return {"text": "", "length": 0}

    def _extract_meta_robots(self, soup: BeautifulSoup) -> str:
        """Extract meta robots tag"""
        meta_robots = soup.find('meta', attrs={'name': 'robots'})
        return meta_robots.get('content', '') if meta_robots else ''

    def _extract_canonical(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract canonical URL"""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical and canonical.get('href'):
            return urljoin(base_url, canonical['href'])
        return base_url

    def _extract_headings(self, soup: BeautifulSoup) -> Dict:
        """Extract all heading tags"""
        headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}

        for i in range(1, 7):
            tag_name = f"h{i}"
            for heading in soup.find_all(tag_name):
                if heading.string:
                    headings[tag_name].append({
                        "text": heading.string.strip(),
                        "length": len(heading.string.strip())
                    })

        return headings

    def _extract_paragraphs(self, soup: BeautifulSoup) -> list:
        """Extract paragraph content"""
        paragraphs = []
        for p in soup.find_all('p'):
            if p.string and p.string.strip():
                text = p.string.strip()
                paragraphs.append({
                    "text": text,
                    "length": len(text)
                })
        return paragraphs

    def _extract_images_without_alt(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract images without alt attributes"""
        images_without_alt = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and not img.get('alt'):
                full_url = urljoin(base_url, src)
                images_without_alt.append({
                    "src": full_url,
                    "title": img.get('title', '')
                })
        return images_without_alt

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Extract internal and external links"""
        internal_links = []
        external_links = []

        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue

            full_url = urljoin(base_url, href)

            try:
                parsed_url = urlparse(full_url)
                parsed_base = urlparse(base_url)

                if parsed_url.netloc == parsed_base.netloc:
                    internal_links.append(full_url)
                else:
                    external_links.append(full_url)
            except Exception:
                continue

        return {
            "internal": list(set(internal_links)),  # Remove duplicates
            "external": list(set(external_links))
        }

    def _extract_semantic_structure(self, soup: BeautifulSoup) -> List[str]:
        """Extract semantic HTML structure"""
        semantic_elements = []

        semantic_tags = [
            'main', 'nav', 'header', 'footer', 'aside', 'article', 'section',
            'figure', 'figcaption', 'time', 'mark', 'cite', 'blockquote'
        ]

        for tag in semantic_tags:
            if soup.find(tag):
                semantic_elements.append(tag)

        return semantic_elements

    def _extract_structured_data(self, soup: BeautifulSoup) -> List[str]:
        """Extract structured data (JSON-LD, Microdata, RDFa)"""
        structured_data = []

        # Check for JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            structured_data.append('JSON-LD')

        # Check for Microdata
        microdata_elements = soup.find_all(attrs={'itemtype': True})
        if microdata_elements:
            structured_data.append('Microdata')

        # Check for RDFa
        rdfa_elements = soup.find_all(attrs={'typeof': True})
        if rdfa_elements:
            structured_data.append('RDFa')

        return structured_data

    def close(self):
        """Clean up resources"""
        self._url_cache.clear()
