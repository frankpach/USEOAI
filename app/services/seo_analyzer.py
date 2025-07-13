# Importaciones necesarias para el módulo de posicionamiento geográfico
import asyncio
import random
import re
import math
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from contextlib import asynccontextmanager
import ipaddress
import socket
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from geopy.geocoders import Nominatim
from pyppeteer import launch
from pyppeteer.browser import Browser
import json
import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.scraper import Scraper
from app.models.seo_models import AnalysisRequest, AnalysisResponse
from app.services.semantic_analyzer import SemanticAnalyzer
from config.config import SEOAnalyzerConfig

# Configure logging
config = SEOAnalyzerConfig.get_instance()
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class SafeIPValidator:
    """Validates IP addresses to prevent SSRF attacks"""
    
    @classmethod
    def is_safe_ip(cls, ip_str: str) -> bool:
        """Check if IP address is safe to connect to"""
        try:
            ip = ipaddress.ip_address(ip_str)
            
            # Block private, loopback, link-local, and multicast addresses
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
                return False
            
            # Block specific dangerous networks
            for network_str in config.DANGEROUS_NETWORKS:
                network = ipaddress.ip_network(network_str)
                if ip in network:
                    return False
            
            # Block reserved addresses
            if ip.is_reserved:
                return False
                
            return True
        except (ValueError, ipaddress.AddressValueError):
            return False


class BrowserPool:
    """Manages a pool of browser instances for concurrent operations"""
    
    def __init__(self, pool_size: Optional[int] = None):
        self.pool_size = pool_size or config.BROWSER_POOL_SIZE
        self.browsers: List[Browser] = []
        self.semaphore = asyncio.Semaphore(self.pool_size)
        self.initialized = False
        self.lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the browser pool"""
        async with self.lock:
            if self.initialized:
                return
            
            try:
                for i in range(self.pool_size):
                    browser = await launch(
                        headless=True,
                        args=config.BROWSER_LAUNCH_ARGS
                    )
                    self.browsers.append(browser)
                    logger.info(f"Browser {i+1}/{self.pool_size} initialized")
                
                self.initialized = True
                logger.info("Browser pool initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize browser pool: {e}")
                await self.close()
                raise
    
    @asynccontextmanager
    async def get_browser(self):
        """Get a browser instance from the pool"""
        if not self.initialized:
            await self.initialize()
        
        async with self.semaphore:
            if not self.browsers:
                raise RuntimeError("No browsers available in pool")
            
            browser = self.browsers.pop()
            try:
                yield browser
            finally:
                # Return browser to pool if still open
                if browser and not browser.connection.closed:
                    self.browsers.append(browser)
    
    async def close(self):
        """Close all browsers in the pool"""
        async with self.lock:
            close_tasks = []
            for browser in self.browsers:
                if browser and not browser.connection.closed:
                    close_tasks.append(browser.close())
            
            if close_tasks:
                await asyncio.gather(*close_tasks, return_exceptions=True)
            
            self.browsers.clear()
            self.initialized = False
            logger.info("Browser pool closed")


class AsyncHTTPClient:
    """Async HTTP client wrapper with safety features"""
    
    def __init__(self, timeout: Optional[int] = None):
        self.timeout = aiohttp.ClientTimeout(total=timeout or config.HTTP_TIMEOUT)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={'User-Agent': config.DEFAULT_USER_AGENT}
            )
        return self.session
    
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make GET request"""
        session = await self.get_session()
        return await session.get(url, **kwargs)
    
    async def head(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make HEAD request"""
        session = await self.get_session()
        return await session.head(url, **kwargs)
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()


class SEOAnalyzer:
    """
    Service for performing comprehensive SEO analysis on websites.
    """
    
    def __init__(self, timeout: Optional[int] = None, user_agent: Optional[str] = None, 
                 max_concurrent_requests: Optional[int] = None):
        """Initialize the SEO analyzer with configurable parameters"""
        self.config = config
        
        # Initialize components
        self.scraper = Scraper(timeout=timeout or self.config.DEFAULT_TIMEOUT)
        self.semantic_analyzer = SemanticAnalyzer()
        self.browser_pool = BrowserPool(pool_size=self.config.BROWSER_POOL_SIZE)
        self.http_client = AsyncHTTPClient(timeout=self.config.HTTP_TIMEOUT)
        
        # Thread pool for blocking operations
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.THREAD_POOL_MAX_WORKERS)
        
        # Configure user agent
        self.user_agent = user_agent or self.config.DEFAULT_USER_AGENT
        
        # Configure parameters
        self.max_concurrent_requests = max_concurrent_requests or self.config.MAX_CONCURRENT_REQUESTS
        
        # Cache for parsed HTML to avoid re-parsing
        self._html_cache: Dict[str, BeautifulSoup] = {}
        
    async def analyze_site(self, analysis_request: AnalysisRequest) -> AnalysisResponse:
        """
        Main method to analyze a website.
        
        Args:
            analysis_request: AnalysisRequest object containing URL and parameters
            
        Returns:
            AnalysisResponse object with complete SEO analysis
        """
        # Validate and sanitize URL
        url = await self._validate_and_sanitize_url(analysis_request.url)
        logger.info(f"Starting analysis for {url}")
        
        # Fetch HTML content
        html, headers, status_code, redirections = await self.scraper.fetch_html(url)
        
        # Parse HTML once and cache it
        if self.config.ENABLE_HTML_CACHE:
            soup = BeautifulSoup(html, 'lxml')
            self._html_cache[url] = soup
        
        # Parse HTML using cached soup
        parsed_data = self.scraper.parse_html(html, url)
        if not parsed_data:
            logger.error(f"Failed to parse HTML for {url}")
            raise ValueError(f"Could not analyze {url}. Check if the URL is valid.")
            
        # Check for title and important data
        if not parsed_data.get("title", {}).get("text"):
            logger.error(f"No title found for {url}")
            raise ValueError(f"Could not extract title from {url}")
        
        # Analyze keywords in title
        title_data = self._analyze_title(parsed_data["title"]["text"], analysis_request.seo_goal)
        
        # Validate links and check for broken ones
        links_data = parsed_data["links"]
        if self.config.ENABLE_BROKEN_LINKS_CHECK:
            links_data["broken"] = await self._find_broken_links(links_data["internal"] + links_data["external"])
        else:
            links_data["broken"] = []
        
        # Perform speed and performance analysis
        if self.config.ENABLE_PERFORMANCE_CHECK:
            speed_metrics = await self._analyze_performance(url)
        else:
            speed_metrics = self._get_default_performance_metrics()
        
        # Check local ranking
        local_rank = await self._check_local_ranking(
            url, 
            analysis_request.location,
            analysis_request.latitude if hasattr(analysis_request, 'latitude') else None,
            analysis_request.longitude if hasattr(analysis_request, 'longitude') else None, 
            analysis_request.local_radius_km,
            analysis_request.geo_samples
        )
        
        # Perform semantic analysis
        texts = self._prepare_texts_for_semantic_analysis(parsed_data)
        semantic_summary = await self.semantic_analyzer.analyze_semantics(
            texts=texts,
            page_title=parsed_data["title"]["text"],
            meta_description=parsed_data["meta_description"]["text"],
            headings=parsed_data["h_tags"],
            seo_goal=analysis_request.seo_goal,
            location=analysis_request.location,
            language=analysis_request.language,
            provider=analysis_request.llm_provider if hasattr(analysis_request, 'llm_provider') else "chatgpt"
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(parsed_data, speed_metrics, local_rank)
        
        # Construct response
        return AnalysisResponse(
            status_code=status_code,
            redirections=redirections,
            title=title_data,
            meta_description=parsed_data["meta_description"],
            meta_robots=parsed_data["meta_robots"],
            canonical_url=parsed_data["canonical_url"],
            h_tags=parsed_data["h_tags"],
            paragraphs=parsed_data["paragraphs"],
            semantic_summary=semantic_summary,
            images_without_alt=parsed_data["images_without_alt"],
            links=links_data,
            semantic_structure=parsed_data["semantic_structure"],
            structured_data=parsed_data["structured_data"],
            speed_metrics=speed_metrics,
            local_rank_check=local_rank,
            recommendations=recommendations
        )
    
    async def _validate_and_sanitize_url(self, url: str) -> str:
        """
        Validate and sanitize URL to prevent SSRF and other attacks.
        
        Args:
            url: Raw URL string
            
        Returns:
            Sanitized and validated URL
            
        Raises:
            ValueError: If URL is invalid or not allowed
        """
        if not url:
            raise ValueError("URL cannot be empty")
        
        # Strip whitespace
        url = url.strip()
        
        # Check if URL starts with allowed schemes
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        # Basic URL structure validation
        try:
            parsed = urlparse(url)
            
            # Validate scheme
            if parsed.scheme not in ('http', 'https'):
                raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
            
            # Validate netloc (domain)
            if not parsed.netloc:
                raise ValueError("URL must have a valid domain")
            
            # Check for private/local IP addresses (SSRF protection)
            hostname = parsed.hostname
            if hostname:
                # Use thread pool for blocking DNS resolution
                loop = asyncio.get_event_loop()
                try:
                    ip = await loop.run_in_executor(
                        self.thread_pool, 
                        socket.gethostbyname, 
                        hostname
                    )
                    
                    if not SafeIPValidator.is_safe_ip(ip):
                        raise ValueError(f"URL points to unsafe IP address: {ip}")
                        
                except socket.gaierror:
                    # If we can't resolve the hostname, continue (might be a valid domain)
                    pass
            
            return url
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Invalid URL format: {str(e)}")
    
    def _extract_domain_safely(self, url: str) -> str:
        """
        Safely extract domain from URL.
        
        Args:
            url: Validated URL
            
        Returns:
            Domain name without www prefix
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception as e:
            logger.error(f"Error extracting domain from {url}: {e}")
            # Fallback to old method with additional safety
            try:
                parts = url.split('//')
                if len(parts) >= 2:
                    domain_part = parts[1].split('/')[0]
                    if domain_part.startswith('www.'):
                        domain_part = domain_part[4:]
                    return domain_part
                else:
                    raise ValueError("Invalid URL structure")
            except Exception:
                raise ValueError(f"Could not extract domain from URL: {url}")
    
    def _analyze_title(self, title: str, seo_goal: str) -> Dict[str, Union[str, int, bool]]:
        """Analyze if title contains relevant keywords for the SEO goal"""
        
        # Convert to lowercase for case-insensitive comparison
        title_lower = title.lower()
        seo_goal_lower = seo_goal.lower()
        
        # Extract key terms from SEO goal
        goal_terms = re.findall(r'\b\w{3,}\b', seo_goal_lower)
        
        # Check if key terms are in the title
        has_keywords = any(term in title_lower for term in goal_terms if len(term) > 3)
        
        return {
            "text": title,
            "length": len(title),
            "has_keywords": has_keywords
        }

    async def _analyze_performance(self, url: str) -> Dict[str, Union[int, bool]]:
        """Analyze page performance metrics using async HTTP client"""
        start_time = time.time()
        
        try:
            response = await self.http_client.get(url)
            async with response:
                ttfb_ms = int((time.time() - start_time) * 1000)
                
                # Check if gzip is enabled
                gzip_enabled = 'gzip' in response.headers.get('Content-Encoding', '').lower()
                
                # Get HTML content
                html_content = await response.text()
                
                # Use cached soup if available, otherwise parse
                if self.config.ENABLE_HTML_CACHE and url in self._html_cache:
                    soup = self._html_cache[url]
                else:
                    soup = BeautifulSoup(html_content, 'lxml')
                
                # Count resources (more accurate)
                scripts = len(soup.find_all('script'))
                styles = len(soup.find_all('link', rel='stylesheet'))
                images = len(soup.find_all('img'))
                
                # Count inline styles and scripts
                inline_styles = len(soup.find_all('style'))
                # Fix: Use proper way to find inline scripts
                inline_scripts = len([s for s in soup.find_all('script') if not s.get('src')])
                scripts += inline_scripts
                
                resource_count = scripts + styles + images + inline_styles
                
                # Check for lazy loading
                lazy_loaded_images = False
                for img in soup.find_all('img'):
                    if isinstance(img, Tag) and img.get('loading') == 'lazy':
                        lazy_loaded_images = True
                        break
                
                return {
                    "ttfb_ms": ttfb_ms,
                    "resource_count": resource_count,
                    "gzip_enabled": gzip_enabled,
                    "lazy_loaded_images": lazy_loaded_images
                }
                
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return self._get_default_performance_metrics()
    
    def _get_default_performance_metrics(self) -> Dict[str, Union[int, bool]]:
        """Get default performance metrics when analysis fails"""
        return {
            "ttfb_ms": 999,
            "resource_count": 0,
            "gzip_enabled": False,
            "lazy_loaded_images": False
        }
    
    def _prepare_texts_for_semantic_analysis(self, parsed_data: Dict) -> List[str]:
        """Prepare text content for semantic analysis"""
        texts = []
        
        # Add paragraphs
        for p in parsed_data.get("paragraphs", []):
            texts.append(p["text"])
            
        # Add headings for context
        for level in range(1, 7):
            for h in parsed_data.get("h_tags", {}).get(f"h{level}", []):
                texts.append(h["text"])
                
        return texts
    
    def _generate_recommendations(self, parsed_data: Dict, speed_metrics: Dict, local_rank: Dict) -> List[str]:
        """Generate SEO recommendations based on analysis"""
        recommendations = []
        
        # Title recommendations
        title_length = parsed_data["title"].get("length", 0)
        if title_length == 0:
            recommendations.append("Add a page title")
        elif title_length < self.config.TITLE_MIN_LENGTH:
            recommendations.append(f"Title is too short, aim for {self.config.TITLE_MIN_LENGTH}-{self.config.TITLE_MAX_LENGTH} characters")
        elif title_length > self.config.TITLE_MAX_LENGTH:
            recommendations.append(f"Title is too long, keep it under {self.config.TITLE_MAX_LENGTH} characters")
            
        # Meta description recommendations
        meta_desc_length = parsed_data["meta_description"].get("length", 0)
        if meta_desc_length == 0:
            recommendations.append("Add a meta description")
        elif meta_desc_length < self.config.META_DESC_MIN_LENGTH:
            recommendations.append(f"Meta description is too short, aim for {self.config.META_DESC_MIN_LENGTH}-{self.config.META_DESC_MAX_LENGTH} characters")
        elif meta_desc_length > self.config.META_DESC_MAX_LENGTH:
            recommendations.append(f"Meta description is too long, keep it under {self.config.META_DESC_MAX_LENGTH} characters")
            
        # Heading recommendations
        h1_tags = parsed_data["h_tags"]["h1"]
        if not h1_tags:
            recommendations.append("Add an H1 heading")
        elif len(h1_tags) > 1:
            recommendations.append("Multiple H1 tags detected, use only one main H1")
            
        # Image recommendations
        if parsed_data["images_without_alt"]:
            recommendations.append("Add alt attributes to all images")
            
        # Performance recommendations
        if speed_metrics["ttfb_ms"] > self.config.TTFB_THRESHOLD_MS:
            recommendations.append("Improve server response time (TTFB)")
        if not speed_metrics["gzip_enabled"]:
            recommendations.append("Enable GZIP compression")
        if not speed_metrics["lazy_loaded_images"]:
            recommendations.append("Implement lazy loading for images")
            
        # Local SEO recommendations
        if local_rank.get("google_maps_rank") == "not found":
            recommendations.append("Register business on Google Maps")
        if not local_rank.get("nap_consistency", False):
            recommendations.append("Ensure NAP (Name, Address, Phone) consistency across listings")
            
        return recommendations

    async def _find_broken_links(self, links: List[str]) -> List[str]:
        """Check for broken links asynchronously with thread-safe operations"""
        broken_links = []
        
        # Limit to configured number of links for performance
        links_to_check = links[:self.config.MAX_LINKS_TO_CHECK] if len(links) > self.config.MAX_LINKS_TO_CHECK else links
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        # Thread-safe lock for modifying broken_links
        lock = asyncio.Lock()
        
        async def check_link(link: str):
            if not link.startswith(('http://', 'https://')):
                return
                
            async with semaphore:
                try:
                    response = await self.http_client.head(link, allow_redirects=True)
                    async with response:
                        if response.status >= 400:
                            async with lock:
                                broken_links.append(link)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    logger.warning(f"Error checking link {link}: {e}")
                    async with lock:
                        broken_links.append(link)
                except Exception as e:
                    logger.error(f"Unexpected error checking link {link}: {e}")
                    async with lock:
                        broken_links.append(link)
        
        # Create tasks for all links
        tasks = [check_link(link) for link in links_to_check]
        
        # Execute all tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
                
        return broken_links
    
    async def _check_local_ranking(
        self, 
        url: str, 
        location: str, 
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: int = 5, 
        samples: int = 10
    ) -> Dict[str, Union[str, bool, int, float]]:
        """
        Check local ranking on maps and search results.
        
        Args:
            url: Website URL to check
            location: Location string (e.g., "Medellín, Colombia")
            latitude: Optional latitude coordinate
            longitude: Optional longitude coordinate
            radius_km: Radius in kilometers for geo samples
            samples: Number of geo samples to generate
            
        Returns:
            Dictionary with local ranking check results
        """
        logger.info(f"Checking local ranking for {url} in {location}")
        
        # Get the business name from the site
        business_name = await self._extract_business_name(url)
        if not business_name:
            logger.warning(f"Could not extract business name from {url}")
            business_name = self._extract_domain_safely(url)
        
        # Extract domain for search - safe extraction
        domain = self._extract_domain_safely(url)
        
        # 1. Get coordinates from location if not provided
        coords = await self._get_coordinates(location, latitude, longitude)
        if not coords:
            logger.error(f"Could not get coordinates for {location}")
            return self._get_default_local_rank_results(checked=0)
        
        # 2. Generate geo samples around the location
        geo_points = self._generate_geosamples(coords[0], coords[1], radius_km, "km", samples)
        
        # 3. Check local ranking on maps
        google_results = {}
        bing_results = {}
        
        if self.config.ENABLE_GOOGLE_MAPS_CHECK:
            google_results = await self._check_google_maps_ranking(business_name, domain, geo_points)
        
        if self.config.ENABLE_BING_MAPS_CHECK:
            bing_results = await self._check_bing_maps_ranking(business_name, domain, geo_points)
        
        # 4. Extract NAP from website
        nap_data = await self._extract_nap_data(url)
        
        # 5. Check NAP consistency with maps listing
        nap_consistency = await self._check_nap_consistency(
            business_name, domain, nap_data, google_results.get("profile_data", {})
        )
        
        # Prepare the response
        result = {
            "google_maps_rank": google_results.get("rank_text", "unavailable"),
            "bing_maps_rank": bing_results.get("rank_text", "unavailable"),
            "apple_maps_rank": "unavailable",  # Apple Maps is difficult without iOS
            "nap_consistency": nap_consistency,
            "sample_locations_checked": len(geo_points),
            "geo_coverage_percentage": google_results.get("coverage_percentage", 0),
            "has_verified_listing": google_results.get("is_verified", False)
        }
        
        return result
        
    def _get_default_local_rank_results(self, checked: int = 0) -> Dict[str, Union[str, bool, int, float]]:
        """Get default local rank results when checks fail"""
        return {
            "google_maps_rank": "unavailable",
            "bing_maps_rank": "unavailable",
            "apple_maps_rank": "unavailable",
            "nap_consistency": False,
            "sample_locations_checked": checked,
            "geo_coverage_percentage": 0.0,
            "has_verified_listing": False
        }
        
    async def _get_coordinates(
        self, 
        location: str, 
        latitude: Optional[float] = None, 
        longitude: Optional[float] = None
    ) -> Optional[Tuple[float, float]]:
        """
        Get coordinates from location string or use provided coordinates.
        
        Args:
            location: Location string (e.g., "Medellín, Colombia")
            latitude: Optional latitude coordinate
            longitude: Optional longitude coordinate
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        try:
            # Use provided coordinates if available
            if latitude is not None and longitude is not None:
                return (float(latitude), float(longitude))
                
            # Otherwise, geocode the location using thread pool
            loop = asyncio.get_event_loop()
            
            def geocode_location():
                geolocator = Nominatim(user_agent=self.config.GEOCODING_USER_AGENT)
                return geolocator.geocode(location)
            
            location_data = await loop.run_in_executor(self.thread_pool, geocode_location)
            
            if location_data:
                logger.info(f"Geocoded {location} to {location_data.latitude}, {location_data.longitude}")
                return (location_data.latitude, location_data.longitude)
                
            return None
            
        except Exception as e:
            logger.error(f"Error during geocoding: {e}")
            return None
    
    def _generate_geosamples(
        self, 
        lat: float, 
        lon: float, 
        radius: float, 
        unit: str = "km",
        n: int = 10
    ) -> List[Tuple[float, float]]:
        """
        Generate geographically distributed sample points around a center point.
        Optimized version with caching and better distribution.
        
        Args:
            lat: Center latitude
            lon: Center longitude
            radius: Radius
            unit: Unit of radius ("km" or "mi")
            n: Number of sample points
            
        Returns:
            List of (latitude, longitude) tuples
        """
        # Convert radius to kilometers if in miles
        if unit.lower() == "mi":
            radius_km = radius * 1.60934
        else:
            radius_km = radius
            
        # Earth's radius in km
        R = 6371.0
        
        samples = []
        
        # Add the center point
        samples.append((lat, lon))
        
        # Calculate number of rings and points per ring
        if n <= 1:
            return samples
            
        num_rings = min(3, max(1, (n - 1) // 4))
        points_per_ring = (n - 1) // num_rings
        
        # Generate points in rings for better distribution
        for ring in range(1, num_rings + 1):
            # Distribute radius between rings
            ring_radius = (radius_km * ring) / num_rings
            
            # Calculate points on this ring
            for i in range(points_per_ring):
                # Distribute points evenly around the circle
                bearing = (360 * i / points_per_ring) * (math.pi / 180)
                
                # Add controlled jitter to avoid grid patterns
                jitter_factor = 0.1 * (ring_radius / 10)
                jitter = random.uniform(-jitter_factor, jitter_factor)
                ring_radius_jittered = max(0.1, ring_radius + jitter)
                
                # Calculate new point using spherical geometry
                lat_rad = math.radians(lat)
                lon_rad = math.radians(lon)
                
                # Calculate new coordinates
                new_lat_rad = math.asin(
                    math.sin(lat_rad) * math.cos(ring_radius_jittered / R) +
                    math.cos(lat_rad) * math.sin(ring_radius_jittered / R) * math.cos(bearing)
                )
                
                new_lon_rad = lon_rad + math.atan2(
                    math.sin(bearing) * math.sin(ring_radius_jittered / R) * math.cos(lat_rad),
                    math.cos(ring_radius_jittered / R) - math.sin(lat_rad) * math.sin(new_lat_rad)
                )
                
                # Convert back to degrees
                new_lat = math.degrees(new_lat_rad)
                new_lon = math.degrees(new_lon_rad)
                
                samples.append((new_lat, new_lon))
                
        return samples[:n]  # Limit to n samples
        
    async def _extract_business_name(self, url: str) -> str:
        """
        Extract business name from website using cached soup.
        
        Args:
            url: Website URL
            
        Returns:
            Business name or domain name
        """
        try:
            # Use cached soup if available
            if self.config.ENABLE_HTML_CACHE and url in self._html_cache:
                soup = self._html_cache[url]
            else:
                # Fetch the page
                html, _, _, _ = await self.scraper.fetch_html(url)
                soup = BeautifulSoup(html, 'lxml')
                if self.config.ENABLE_HTML_CACHE:
                    self._html_cache[url] = soup
            
            # Try different sources for business name
            
            # 1. Check schema.org data
            schema_data = soup.find('script', {'type': 'application/ld+json'})
            if isinstance(schema_data, Tag) and schema_data.string:
                try:
                    data = json.loads(schema_data.string)
                    if isinstance(data, list) and data:
                        data = data[0]
                    
                    # Check different schema formats
                    if isinstance(data, dict) and '@type' in data:
                        if data.get('@type') in self.config.BUSINESS_SCHEMA_TYPES:
                            name = data.get('name')
                            if name and isinstance(name, str):
                                return name.strip()
                    
                    # Check for nested organization
                    if isinstance(data, dict) and 'publisher' in data and isinstance(data['publisher'], dict):
                        name = data['publisher'].get('name')
                        if name and isinstance(name, str):
                            return name.strip()
                        
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    logger.warning(f"Error parsing schema.org data: {e}")
            
            # 2. Try meta tags
            meta_og_site_name = soup.find('meta', {'property': 'og:site_name'})
            if isinstance(meta_og_site_name, Tag):
                content = meta_og_site_name.get('content')
                if content and isinstance(content, str):
                    return content.strip()
            
            # 3. Try title tag
            if soup.title and isinstance(soup.title, Tag) and soup.title.string:
                title = soup.title.string.strip()
                # Remove common suffixes
                for suffix in [' | ', ' - ', ' – ', ' — ', ' » ']:
                    if suffix in title:
                        return title.split(suffix)[0].strip()
                return title
            
            # 4. Try first h1
            h1 = soup.find('h1')
            if isinstance(h1, Tag):
                text = h1.get_text(strip=True)
                if text:
                    return text
                
            # 5. Try first strong text in header
            header = soup.find('header')
            if isinstance(header, Tag):
                strong = header.find('strong')
                if isinstance(strong, Tag):
                    text = strong.get_text(strip=True)
                    if text:
                        return text
                
                # Try first link in header
                link = header.find('a')
                if isinstance(link, Tag):
                    text = link.get_text(strip=True)
                    if text:
                        return text
            
            # Fallback to domain
            return self._extract_domain_safely(url)
            
        except Exception as e:
            logger.error(f"Error extracting business name: {e}")
            return self._extract_domain_safely(url)
            
    async def _check_google_maps_ranking(
        self, 
        business_name: str, 
        domain: str,
        geo_points: List[Tuple[float, float]]
    ) -> Dict[str, Union[str, float, bool, Dict]]:
        """
        Check ranking on Google Maps from different geo points with improved resource management.
        
        Args:
            business_name: Business name to search for
            domain: Domain to check in results
            geo_points: List of geo points to check from
            
        Returns:
            Dictionary with ranking results
        """
        try:
            ranks = []
            found_count = 0
            profile_data = {}
            is_verified = False
            
            # Check a maximum of configured points to avoid abuse
            sample_points = geo_points[:self.config.MAX_GEO_POINTS]
            
            async with self.browser_pool.get_browser() as browser:
                # Create a new page with proper resource management
                page = await browser.newPage()
                
                try:
                    # Set user agent
                    await page.setUserAgent(self.user_agent)
                    
                    # Enable request interception to block unnecessary resources
                    await page.setRequestInterception(True)
                    
                    async def intercept_request(request):
                        # Block unnecessary resources for performance
                        if request.resourceType in self.config.BLOCK_RESOURCE_TYPES:
                            await request.abort()
                        else:
                            await request.continue_()
                    
                    page.on('request', intercept_request)
                    
                    for i, (lat, lon) in enumerate(sample_points):
                        # Prepare search query
                        search_query = business_name.replace(' ', '+')
                        
                        # Open Google Maps with geolocation
                        maps_url = f"https://www.google.com/maps/search/{search_query}/@{lat},{lon},15z"
                        
                        logger.info(f"Checking Google Maps at point {i+1}/{len(sample_points)}: {lat}, {lon}")
                        
                        try:
                            # Navigate to Google Maps
                            await page.goto(maps_url, {'timeout': self.config.BROWSER_TIMEOUT})
                            
                            # Wait for results to load
                            await asyncio.sleep(3)
                            await page.waitForSelector(
                                self.config.GOOGLE_MAPS_SELECTORS['feed'], 
                                {'timeout': self.config.SELECTOR_TIMEOUT}
                            )
                            
                            # Extract results
                            results = await page.evaluate('''
                            () => {
                                const results = [];
                                const items = document.querySelectorAll('div[role="feed"] a[href*="maps/place"]');
                                for (let i = 0; i < Math.min(items.length, 15); i++) {
                                    const item = items[i];
                                    const titleElement = item.querySelector('div[class*="fontHeadlineSmall"]');
                                    if (titleElement) {
                                        results.push({
                                            title: titleElement.textContent || '',
                                            position: i + 1,
                                            url: item.href || ''
                                        });
                                    }
                                }
                                return results;
                            }
                            ''')
                            
                            # Find our domain or business name in results
                            found = False
                            for result in results:
                                if not result.get('title'):
                                    continue
                                    
                                result_title = result['title'].lower()
                                if domain.lower() in result_title or business_name.lower() in result_title:
                                    found = True
                                    ranks.append(result['position'])
                                    
                                    # If first check, try to get more info about the listing
                                    if i == 0:
                                        try:
                                            # Click on result to get more info
                                            await page.click(f'div[role="feed"] a[href*="maps/place"]:nth-child({result["position"]})')
                                            await page.waitForSelector(
                                                self.config.GOOGLE_MAPS_SELECTORS['page_title'], 
                                                {'timeout': 5000}
                                            )
                                            
                                            # Extract profile data
                                            profile_data = await page.evaluate('''
                                            () => {
                                                const data = {};
                                                const titleElement = document.querySelector('h1[data-attrid="title"]');
                                                data.title = titleElement ? titleElement.textContent : '';
                                                
                                                // Check for verification
                                                const verified = document.querySelector('img[src*="verified"]');
                                                data.verified = !!verified;
                                                
                                                // Get address
                                                const addressElement = document.querySelector('button[data-item-id="address"]');
                                                data.address = addressElement ? addressElement.textContent : '';
                                                
                                                // Get phone
                                                const phoneElement = document.querySelector('button[data-item-id="phone"]');
                                                data.phone = phoneElement ? phoneElement.textContent : '';
                                                
                                                return data;
                                            }
                                            ''')
                                            
                                            is_verified = profile_data.get('verified', False)
                                            
                                        except Exception as e:
                                            logger.warning(f"Error getting profile data: {e}")
                                    break
                            
                            if found:
                                found_count += 1
                                
                        except Exception as e:
                            logger.warning(f"Error checking Google Maps at point {i+1}: {e}")
                            
                        # Add delay between requests to avoid detection
                        await asyncio.sleep(self.config.REQUEST_DELAY)
                        
                finally:
                    # Always close the page
                    await page.close()
                
        except Exception as e:
            logger.error(f"Error in Google Maps check: {e}")
            return self._get_default_google_maps_result()
        
        # Calculate results
        return self._format_maps_results(ranks, found_count, sample_points, profile_data, is_verified)
        
    async def _check_bing_maps_ranking(
        self, 
        business_name: str, 
        domain: str,
        geo_points: List[Tuple[float, float]]
    ) -> Dict[str, Union[str, float, bool]]:
        """
        Check ranking on Bing Maps from different geo points.
        Using Bing Maps REST API if available or fallback to scraping.
        
        Args:
            business_name: Business name to search for
            domain: Domain to check in results
            geo_points: List of geo points to check from
            
        Returns:
            Dictionary with ranking results
        """
        # Try to get Bing Maps API key from environment
        bing_maps_key = self.config.BING_MAPS_API_KEY
        
        ranks = []
        found_count = 0
        
        # Check a maximum of 5 points to avoid abuse
        sample_points = geo_points[:min(5, len(geo_points))]
        
        if bing_maps_key:
            # Use Bing Maps REST API
            try:
                for i, (lat, lon) in enumerate(sample_points):
                    query = business_name.replace(' ', '%20')
                    url = f"https://dev.virtualearth.net/REST/v1/LocalSearch/?query={query}&userLocation={lat},{lon}&key={bing_maps_key}"
                    
                    logger.info(f"Checking Bing Maps API at point {i+1}/{len(sample_points)}: {lat}, {lon}")
                    
                    try:
                        async with self.http_client.get(url) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                resource_sets = data.get('resourceSets', [])
                                if resource_sets and resource_sets[0].get('resources'):
                                    resources = resource_sets[0]['resources']
                                    
                                    # Find our domain or business name in results
                                    found = False
                                    for j, resource in enumerate(resources[:15]):  # Limit to top 15
                                        name = resource.get('name', '').lower()
                                        website = resource.get('Website', '').lower()
                                        
                                        if (domain.lower() in name or 
                                            domain.lower() in website or 
                                            business_name.lower() in name):
                                            found = True
                                            ranks.append(j + 1)
                                            break
                                            
                                    if found:
                                        found_count += 1
                    except Exception as e:
                        logger.warning(f"Error checking Bing Maps API at point {i+1}: {e}")
                        
                    # Add delay between requests
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error using Bing Maps API: {e}")
                # Fallback to scraping if API fails
                return await self._check_bing_maps_scraping(business_name, domain, geo_points)
        else:
            # Fallback to scraping if no API key
            return await self._check_bing_maps_scraping(business_name, domain, geo_points)
        
        # Format results
        return self._format_maps_results(ranks, found_count, sample_points)
        
    async def _check_bing_maps_scraping(
        self, 
        business_name: str, 
        domain: str,
        geo_points: List[Tuple[float, float]]
    ) -> Dict[str, Union[str, float, bool]]:
        """
        Fallback method to check Bing Maps using browser scraping.
        
        Args:
            business_name: Business name to search for
            domain: Domain to check in results
            geo_points: List of geo points to check from
            
        Returns:
            Dictionary with ranking results
        """
        try:
            ranks = []
            found_count = 0
            
            # Check a maximum of 3 points to avoid abuse
            sample_points = geo_points[:min(3, len(geo_points))]
            
            async with self.browser_pool.get_browser() as browser:
                page = await browser.newPage()
                
                try:
                    # Set user agent
                    await page.setUserAgent(self.user_agent)
                    
                    # Enable request interception
                    await page.setRequestInterception(True)
                    
                    async def intercept_request(request):
                        if request.resourceType in self.config.BLOCK_RESOURCE_TYPES:
                            await request.abort()
                        else:
                            await request.continue_()
                    
                    page.on('request', intercept_request)
                    
                    for i, (lat, lon) in enumerate(sample_points):
                        search_query = business_name.replace(' ', '+')
                        maps_url = f"https://www.bing.com/maps?q={search_query}&cp={lat}~{lon}"
                        
                        logger.info(f"Checking Bing Maps at point {i+1}/{len(sample_points)}: {lat}, {lon}")
                        
                        try:
                            await page.goto(maps_url, {'timeout': self.config.BROWSER_TIMEOUT})
                            await asyncio.sleep(3)
                            await page.waitForSelector(
                                self.config.BING_MAPS_SELECTORS['results'], 
                                {'timeout': self.config.SELECTOR_TIMEOUT}
                            )
                            
                            # Extract results
                            results = await page.evaluate('''
                            () => {
                                const results = [];
                                const items = document.querySelectorAll('.listViewCard');
                                for (let i = 0; i < Math.min(items.length, 15); i++) {
                                    const item = items[i];
                                    const titleElement = item.querySelector('.b_dataList h2');
                                    if (titleElement) {
                                        results.push({
                                            title: titleElement.textContent || '',
                                            position: i + 1,
                                            url: item.querySelector('a')?.href || ''
                                        });
                                    }
                                }
                                return results;
                            }
                            ''')
                            
                            # Find our domain or business name in results
                            found = False
                            for result in results:
                                if not result.get('title'):
                                    continue
                                    
                                result_title = result['title'].lower()
                                if domain.lower() in result_title or business_name.lower() in result_title:
                                    found = True
                                    ranks.append(result['position'])
                                    break
                                    
                            if found:
                                found_count += 1
                                
                        except Exception as e:
                            logger.warning(f"Error checking Bing Maps at point {i+1}: {e}")
                            
                        await asyncio.sleep(self.config.REQUEST_DELAY)
                        
                finally:
                    await page.close()
                
        except Exception as e:
            logger.error(f"Error in Bing Maps scraping: {e}")
            return self._get_default_bing_maps_result()
        
        return self._format_maps_results(ranks, found_count, sample_points)
        
    def _format_maps_results(
        self, 
        ranks: List[int], 
        found_count: int, 
        sample_points: List[Tuple[float, float]], 
        profile_data: Optional[Dict[str, Any]] = None,
        is_verified: bool = False
    ) -> Dict[str, Union[str, float, bool, Dict[str, Any]]]:
        """Format maps ranking results consistently"""
        if ranks:
            avg_rank = sum(ranks) / len(ranks)
            if avg_rank <= self.config.RANK_GREEN_THRESHOLD:
                rank_color = "green"
            elif avg_rank <= self.config.RANK_YELLOW_THRESHOLD:
                rank_color = "yellow"
            else:
                rank_color = "red"
            
            rank_text = f"rank #{round(avg_rank, 1)}"
        else:
            rank_text = "not found"
            rank_color = "gray"
            avg_rank = None
            
        # Calculate coverage percentage
        coverage_percentage = (found_count / len(sample_points)) * 100 if sample_points else 0
        
        result = {
            "rank_text": rank_text,
            "rank_color": rank_color,
            "average_rank": round(avg_rank, 1) if avg_rank else None,
            "coverage_percentage": round(coverage_percentage, 1)
        }
        
        # Add profile data if available (Google Maps specific)
        if profile_data is not None:
            result["profile_data"] = profile_data
            result["is_verified"] = is_verified
            
        return result
        
    def _get_default_google_maps_result(self) -> Dict[str, Union[str, float, bool, Dict[str, Any]]]:
        """Default Google Maps result when check fails"""
        return {
            "rank_text": "unavailable",
            "rank_color": "gray",
            "average_rank": None,
            "coverage_percentage": 0.0,
            "profile_data": {},
            "is_verified": False
        }
        
    def _get_default_bing_maps_result(self) -> Dict[str, Union[str, float, bool]]:
        """Default Bing Maps result when check fails"""
        return {
            "rank_text": "unavailable",
            "rank_color": "gray",
            "average_rank": None,
            "coverage_percentage": 0.0
        }
        
    async def _extract_nap_data(self, url: str) -> Dict[str, Optional[str]]:
        """
        Extract NAP (Name, Address, Phone) data from website using cached soup.
        
        Args:
            url: Website URL
            
        Returns:
            Dictionary with NAP data
        """
        try:
            # Use cached soup if available
            if self.config.ENABLE_HTML_CACHE and url in self._html_cache:
                soup = self._html_cache[url]
            else:
                # Fetch and cache the page
                html, _, _, _ = await self.scraper.fetch_html(url)
                soup = BeautifulSoup(html, 'lxml')
                if self.config.ENABLE_HTML_CACHE:
                    self._html_cache[url] = soup
            
            nap = {
                "name": await self._extract_business_name(url),
                "address": None,
                "phone": None,
            }
            
            # Try schema.org data first
            schema_data = soup.find('script', {'type': 'application/ld+json'})
            if isinstance(schema_data, Tag) and schema_data.string:
                try:
                    data = json.loads(schema_data.string)
                    if isinstance(data, list) and data:
                        data = data[0]
                    
                    if isinstance(data, dict):
                        # Check for address
                        if 'address' in data:
                            address_data = data['address']
                            if isinstance(address_data, dict):
                                address_parts = []
                                for key in ['streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'addressCountry']:
                                    if key in address_data and address_data[key]:
                                        address_parts.append(str(address_data[key]))
                                if address_parts:
                                    nap['address'] = ', '.join(address_parts)
                            elif isinstance(address_data, str):
                                nap['address'] = address_data
                        
                        # Check for phone
                        if 'telephone' in data and isinstance(data['telephone'], str):
                            nap['phone'] = data['telephone']
                            
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    logger.warning(f"Error parsing schema.org data for NAP: {e}")
                    
            # If no schema data, try regex patterns
            if not nap['address']:
                address_candidates = self._extract_address_candidates(soup)
                if address_candidates:
                    # Use the highest scoring candidate
                    address_candidates.sort(key=lambda x: x[1], reverse=True)
                    nap['address'] = address_candidates[0][0]
            
            # Try to find phone if not found yet
            if not nap['phone']:
                nap['phone'] = self._extract_phone_number(soup)
            
            return nap
            
        except Exception as e:
            logger.error(f"Error extracting NAP data: {e}")
            return {
                "name": self._extract_domain_safely(url),
                "address": None,
                "phone": None
            }
            
    def _extract_address_candidates(self, soup: BeautifulSoup) -> List[Tuple[str, int]]:
        """Extract address candidates from soup with scoring"""
        address_candidates = []
        
        for element in soup.find_all(['p', 'div', 'span', 'address']):
            if isinstance(element, Tag):
                text = element.get_text(strip=True)
                
                if (self.config.MIN_ADDRESS_LENGTH < len(text) < self.config.MAX_ADDRESS_LENGTH):
                    score = 0
                    
                    # Score based on address patterns
                    # Look for postal codes
                    postal_match = re.search(r'\b\d{5}(?:[-\s]\d{4})?\b', text)  # US format
                    if postal_match:
                        score += 5
                        
                    # Look for common address patterns
                    if re.search(r'\b(calle|carrera|avenida|av|cra|cll|street|st|avenue|ave|road|rd|boulevard|blvd)\b', 
                                text.lower()):
                        score += 4
                        
                    # Look for city, state patterns
                    if re.search(r'\w+,\s*\w{2}', text):  # City, State format
                        score += 3
                        
                    # Look for numbers with street
                    if re.search(r'\d+\s+\w+(?:\s+\w+){1,3}', text):
                        score += 2
                    
                    if score > 0:
                        address_candidates.append((text, score))
        
        return address_candidates
            
    def _normalize_address(self, address: str) -> str:
        """Normalize address for comparison"""
        if not address:
            return ""
            
        # Convert to lowercase
        address = address.lower()
        
        # Replace common abbreviations
        replacements = [
            ('street', 'st'), ('avenue', 'ave'), ('boulevard', 'blvd'),
            ('road', 'rd'), ('drive', 'dr'), ('lane', 'ln'),
            ('suite', 'ste'), ('apartment', 'apt'), ('building', 'bldg'),
            ('calle', 'c'), ('avenida', 'av'), ('carrera', 'cra'),
        ]
        
        for full, abbr in replacements:
            address = address.replace(full, abbr)
            address = address.replace(abbr + '.', abbr)
        
        # Remove punctuation except for postal codes
        address = re.sub(r'[^\w\s-]', '', address)
        
        # Remove extra whitespace
        address = ' '.join(address.split())
        
        return address
        
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison"""
        if not phone:
            return ""
            
        # Keep only digits
        digits_only = re.sub(r'\D', '', phone)
        
        # Handle international format
        if digits_only.startswith('00'):
            digits_only = digits_only[2:]
        if digits_only.startswith('1') and len(digits_only) > 10:
            digits_only = digits_only[1:]
            
        return digits_only[-10:] if len(digits_only) >= 10 else digits_only
            
    async def _check_nap_consistency(
        self, 
        business_name: str, 
        domain: str,
        nap_data: Dict[str, Optional[str]], 
        maps_data: Dict[str, Any]
    ) -> bool:
        """
        Check NAP consistency between website and maps listing.
        
        Args:
            business_name: Business name from website
            domain: Website domain
            nap_data: NAP data extracted from website
            maps_data: Data from maps listing
            
        Returns:
            Boolean indicating NAP consistency
        """
        # If we don't have maps data, we can't check consistency
        if not maps_data:
            return False
            
        # Check name consistency
        name_match = False
        if maps_data.get('title'):
            maps_name = maps_data['title'].lower()
            site_name = business_name.lower()
            
            # Check if either name contains the other
            if maps_name in site_name or site_name in maps_name or domain.lower() in maps_name:
                name_match = True
        
        # Check address consistency if we have both addresses
        address_match = False
        if nap_data.get('address') and maps_data.get('address'):
            site_address = self._normalize_address(nap_data['address'])
            maps_address = self._normalize_address(maps_data['address'])
            
            # Check for substantial overlap
            common_words = set(site_address.split()) & set(maps_address.split())
            if len(common_words) >= 3:  # At least 3 words in common
                address_match = True
                
        # Check phone consistency if we have both phone numbers
        phone_match = False
        if nap_data.get('phone') and maps_data.get('phone'):
            site_phone = self._normalize_phone(nap_data['phone'])
            maps_phone = self._normalize_phone(maps_data['phone'])
            
            if site_phone == maps_phone:
                phone_match = True
        
        # Consider NAP consistent if at least name and one other field match
        if name_match and (address_match or phone_match):
            return True
            
        return False
        
    def _extract_phone_number(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract phone number from soup using regex patterns"""
        phone_patterns = [
            r'\+\d{1,3}\s?[\d\s-]{7,15}',  # International format
            r'\(\d{3}\)\s?\d{3}-\d{4}',     # US format (123) 456-7890
            r'\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4}',  # 123-456-7890
            r'\d{2}[-\.\s]?\d{2}[-\.\s]?\d{2}[-\.\s]?\d{2}[-\.\s]?\d{2}'  # European formats
        ]
        
        for pattern in phone_patterns:
            for element in soup.find_all(text=True):
                if isinstance(element, str):
                    match = re.search(pattern, element)
                    if match:
                        return match.group(0)
        
        return None