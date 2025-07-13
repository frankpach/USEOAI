# Importaciones necesarias para el módulo de posicionamiento geográfico
import asyncio
import random
import re
import math
import logging
from typing import Dict, List, Tuple, Optional, Any
import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
import aiohttp
from geopy.geocoders import Nominatim
from pyppeteer import launch
from pyppeteer.browser import Browser
import json
import os
import time


from app.services.scraper import Scraper
from app.models.seo_models import AnalysisRequest, AnalysisResponse
from app.services.semantic_analyzer import SemanticAnalyzer


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOAnalyzer:
    """
    Service for performing comprehensive SEO analysis on websites.
    """
    
    def __init__(self, timeout: int = 20, user_agent: Optional[str] = None, max_concurrent_requests: int = 5):
        """Initialize the SEO analyzer with configurable parameters"""
        self.scraper = Scraper(timeout=timeout)
        self.semantic_analyzer = SemanticAnalyzer()
        self.browser_pool = None  # Lazy initialization for browser pool
        self.max_concurrent_requests = max_concurrent_requests
        
        # Configure user agent
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = os.getenv(
                "SEO_ANALYZER_USER_AGENT",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        
        # Configure other parameters from environment
        self.max_links_to_check = int(os.getenv("SEO_MAX_LINKS_CHECK", "20"))
        self.max_geo_points = int(os.getenv("SEO_MAX_GEO_POINTS", "5"))
        self.request_delay = float(os.getenv("SEO_REQUEST_DELAY", "2.0"))
        
    async def analyze_site(self, analysis_request: AnalysisRequest) -> AnalysisResponse:
        """
        Main method to analyze a website.
        
        Args:
            analysis_request: AnalysisRequest object containing URL and parameters
            
        Returns:
            AnalysisResponse object with complete SEO analysis
        """
        # Validate and sanitize URL
        url = self._validate_and_sanitize_url(analysis_request.url)
        logger.info(f"Starting analysis for {url}")
        
        # Fetch HTML content
        html, headers, status_code, redirections = await self.scraper.fetch_html(url)
        
        # Parse HTML
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
        links_data["broken"] = await self._find_broken_links(links_data["internal"] + links_data["external"])
        
        # Perform speed and performance analysis
        speed_metrics = await self._analyze_performance(url)
        
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
    
    def _validate_and_sanitize_url(self, url: str) -> str:
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
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            
            # Validate scheme
            if parsed.scheme not in ('http', 'https'):
                raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
            
            # Validate netloc (domain)
            if not parsed.netloc:
                raise ValueError("URL must have a valid domain")
            
            # Check for private/local IP addresses (SSRF protection)
            import socket
            try:
                host = parsed.hostname
                if host:
                    ip = socket.gethostbyname(host)
                    import ipaddress
                    if ipaddress.ip_address(ip).is_private:
                        raise ValueError(f"URL points to private IP address: {ip}")
                    if ipaddress.ip_address(ip).is_loopback:
                        raise ValueError(f"URL points to loopback address: {ip}")
            except (socket.gaierror, ValueError):
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
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
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
    
    def _analyze_title(self, title: str, seo_goal: str) -> Dict:
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

    async def _analyze_performance(self, url: str) -> Dict:
        """Analyze page performance metrics (el conteo de recursos es real, no simulado)"""
        # Start timing for TTFB
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=10)
            ttfb_ms = int((time.time() - start_time) * 1000)
            
            # Check if gzip is enabled
            gzip_enabled = 'gzip' in response.headers.get('Content-Encoding', '').lower()
            
            # Count resources (real, not simulated)
            soup = BeautifulSoup(response.text, 'lxml')
            scripts = len(soup.find_all('script'))
            styles = len(soup.find_all('link', rel='stylesheet'))
            images = len(soup.find_all('img'))
            resource_count = scripts + styles + images
            
            # Check for lazy loading - safe BeautifulSoup handling with type checking
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
        elif title_length < 30:
            recommendations.append("Title is too short, aim for 50-60 characters")
        elif title_length > 70:
            recommendations.append("Title is too long, keep it under 60 characters")
            
        # Meta description recommendations
        meta_desc_length = parsed_data["meta_description"].get("length", 0)
        if meta_desc_length == 0:
            recommendations.append("Add a meta description")
        elif meta_desc_length < 100:
            recommendations.append("Meta description is too short, aim for 150-160 characters")
        elif meta_desc_length > 160:
            recommendations.append("Meta description is too long, keep it under 160 characters")
            
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
        if speed_metrics["ttfb_ms"] > 500:
            recommendations.append("Improve server response time (TTFB)")
        if not speed_metrics["gzip_enabled"]:
            recommendations.append("Enable GZIP compression")
        if not speed_metrics["lazy_loaded_images"]:
            recommendations.append("Implement lazy loading for images")
            
        # Local SEO recommendations
        if local_rank["google_maps"] == "no listing found":
            recommendations.append("Register business on Google Maps")
        if not local_rank["nap_consistency"]:
            recommendations.append("Ensure NAP (Name, Address, Phone) consistency across listings")
            
        return recommendations

    
    async def _find_broken_links(self, links: List[str]) -> List[str]:
        """Check for broken links asynchronously with proper error handling"""
        broken_links = []
        
        # Limit to configured number of links for performance
        links_to_check = links[:self.max_links_to_check] if len(links) > self.max_links_to_check else links
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        async def check_link(link: str):
            if not link.startswith(('http://', 'https://')):
                return
                
            async with semaphore:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.head(link, timeout=5, allow_redirects=True) as response:
                            if response.status >= 400:
                                broken_links.append(link)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    logger.warning(f"Error checking link {link}: {e}")
                    broken_links.append(link)
                except Exception as e:
                    logger.error(f"Unexpected error checking link {link}: {e}")
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
    ) -> Dict:
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
        google_results = await self._check_google_maps_ranking(business_name, domain, geo_points)
        bing_results = await self._check_bing_maps_ranking(business_name, domain, geo_points)
        
        # 4. Extract NAP from website
        nap_data = await self._extract_nap_data(url)
        
        # 5. Check NAP consistency with maps listing
        nap_consistency = await self._check_nap_consistency(
            business_name, domain, nap_data, google_results.get("profile_data", {})
        )
        
        # Prepare the response
        result = {
            "google_maps_rank": google_results.get("rank_text", "not found"),
            "bing_maps_rank": bing_results.get("rank_text", "not found"),
            "apple_maps_rank": "unavailable",  # Apple Maps is difficult without iOS
            "nap_consistency": nap_consistency,
            "sample_locations_checked": len(geo_points),
            "geo_coverage_percentage": google_results.get("coverage_percentage", 0),
            "has_verified_listing": google_results.get("is_verified", False)
        }
        
        return result
        
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
                
            # Otherwise, geocode the location
            geolocator = Nominatim(user_agent="useoai")
            location_data = geolocator.geocode(location)
            
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
            
        num_rings = min(3, n // 4 + 1)
        points_per_ring = (n - 1) // num_rings
        
        for ring in range(1, num_rings + 1):
            # Distribute radius between rings
            ring_radius = (radius_km * ring) / num_rings
            
            # Calculate points on this ring
            for i in range(points_per_ring):
                # Distribute points evenly around the circle
                bearing = (360 * i / points_per_ring) * (math.pi / 180)
                
                # Add some jitter to avoid grid patterns
                jitter = random.uniform(-0.1, 0.1) * (ring_radius / 10)
                ring_radius_jittered = ring_radius + jitter
                
                # Calculate new point
                lat_rad = lat * (math.pi / 180)
                lon_rad = lon * (math.pi / 180)
                
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
                new_lat = new_lat_rad * (180 / math.pi)
                new_lon = new_lon_rad * (180 / math.pi)
                
                samples.append((new_lat, new_lon))
                
        return samples[:n]  # Limit to n samples
        
    async def _extract_business_name(self, url: str) -> str:
        """
        Extract business name from website.
        
        Args:
            url: Website URL
            
        Returns:
            Business name or domain name
        """
        try:
            # Fetch the page
            html, _, _, _ = await self.scraper.fetch_html(url)
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Try different sources for business name
            
            # 1. Check schema.org data - safe JSON handling with type checking
            schema_data = soup.find('script', {'type': 'application/ld+json'})
            if isinstance(schema_data, Tag) and schema_data.string:
                try:
                    data = json.loads(schema_data.string)
                    if isinstance(data, list):
                        data = data[0]
                    
                    # Check different schema formats
                    if '@type' in data:
                        if data.get('@type') in ['LocalBusiness', 'Organization', 'Restaurant', 'Store']:
                            return data.get('name', '')
                    
                    # Check for nested organization
                    if 'publisher' in data and isinstance(data['publisher'], dict):
                        return data['publisher'].get('name', '')
                        
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    logger.warning(f"Error parsing schema.org data: {e}")
                    pass
            
            # 2. Try meta tags - safe BeautifulSoup handling with type checking
            meta_og_site_name = soup.find('meta', {'property': 'og:site_name'})
            if isinstance(meta_og_site_name, Tag) and meta_og_site_name.get('content'):
                content = meta_og_site_name.get('content')
                if isinstance(content, str):
                    return content
            
            # 3. Try title tag - safe BeautifulSoup handling with type checking
            if soup.title and isinstance(soup.title, Tag) and soup.title.text:
                title = soup.title.text.strip()
                # Remove common suffixes like "| Home" or "- Official Site"
                for suffix in [' | ', ' - ', ' – ', ' — ', ' » ']:
                    if suffix in title:
                        return title.split(suffix)[0].strip()
                return title
            
            # 4. Try first h1 - safe BeautifulSoup handling with type checking
            h1 = soup.find('h1')
            if isinstance(h1, Tag) and h1.get_text():
                return h1.get_text().strip()
                
            # 5. Try first strong text in header - safe BeautifulSoup handling with type checking
            header = soup.find('header')
            if isinstance(header, Tag):
                strong = header.find('strong')
                if isinstance(strong, Tag) and strong.get_text():
                    return strong.get_text().strip()
                
                # Try first link in header
                link = header.find('a')
                if isinstance(link, Tag) and link.get_text():
                    return link.get_text().strip()
            
            # Fallback to domain - safe extraction
            return self._extract_domain_safely(url)
            
        except Exception as e:
            logger.error(f"Error extracting business name: {e}")
            return self._extract_domain_safely(url)
            
    async def _initialize_browser_pool(self):
        """Initialize browser pool for scraping with proper resource management"""
        if self.browser_pool is None:
            try:
                self.browser_pool = []
                browser = await launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                self.browser_pool.append(browser)
                logger.info("Browser pool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize browser pool: {e}")
                raise
        return self.browser_pool[0]
    
    async def _check_google_maps_ranking(
        self, 
        business_name: str, 
        domain: str,
        geo_points: List[Tuple[float, float]]
    ) -> Dict:
        """
        Check ranking on Google Maps from different geo points with proper error handling.
        
        Args:
            business_name: Business name to search for
            domain: Domain to check in results
            geo_points: List of geo points to check from
            
        Returns:
            Dictionary with ranking results
        """
        browser = None
        page = None
        
        try:
            browser = await self._initialize_browser_pool()
            
            ranks = []
            found_count = 0
            profile_data = {}
            is_verified = False
            
            # Check a maximum of configured points to avoid abuse
            sample_points = geo_points[:self.max_geo_points]
            
            # Create a new page
            page = await browser.newPage()
            
            # Set user agent from configuration
            await page.setUserAgent(self.user_agent)
            
            # Enable request interception to block unnecessary resources
            await page.setRequestInterception(True)
            
            async def intercept_request(request):
                # Block unnecessary resources
                if request.resourceType in ['image', 'media', 'font', 'stylesheet']:
                    await request.abort()
                else:
                    await request.continue_()
            
            page.on('request', intercept_request)
            
            for i, (lat, lon) in enumerate(sample_points):
                # Prepare search query
                search_query = f"{business_name}"
                
                # Open Google Maps with geolocation
                maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}/@{lat},{lon},15z"
                
                logger.info(f"Checking Google Maps at point {i+1}/{len(sample_points)}: {lat}, {lon}")
                
                try:
                    # Navigate to Google Maps
                    await page.goto(maps_url, {'timeout': 20000})
                    
                    # Wait for results to load
                    await asyncio.sleep(3)
                    await page.waitForSelector('div[role="feed"]', {'timeout': 10000})
                    
                    # Extract results
                    results = await page.evaluate('''
                    () => {
                        const results = [];
                        const items = document.querySelectorAll('div[role="feed"] a[href^="https://www.google.com/maps/place"]');
                        for (let i = 0; i < Math.min(items.length, 15); i++) {
                            const item = items[i];
                            const title = item.querySelector('div[class*="fontHeadlineSmall"]');
                            if (title) {
                                results.push({
                                    title: title.textContent,
                                    position: i + 1,
                                    url: item.href
                                });
                            }
                        }
                        return results;
                    }
                    ''')
                    
                    # Find our domain or business name in results
                    found = False
                    for result in results:
                        result_title = result['title'].lower()
                        if domain in result_title or business_name.lower() in result_title:
                            found = True
                            ranks.append(result['position'])
                            
                            # If first check, try to get more info about the listing
                            if i == 0:
                                # Click on result to get more info
                                try:
                                    await page.click(f'div[role="feed"] a[href^="https://www.google.com/maps/place"]:nth-child({result["position"]})')
                                    await page.waitForSelector('div[data-attrid="title"]', {'timeout': 5000})
                                    
                                    # Extract profile data
                                    profile_data = await page.evaluate('''
                                    () => {
                                        const data = {};
                                        data.title = document.querySelector('div[data-attrid="title"]')?.textContent || '';
                                        
                                        // Check for verification
                                        const verified = document.querySelector('img[src*="verified"]');
                                        data.verified = !!verified;
                                        
                                        // Get address
                                        const addressElement = document.querySelector('button[data-item-id="address"]');
                                        data.address = addressElement?.textContent || '';
                                        
                                        // Get phone
                                        const phoneElement = document.querySelector('button[data-item-id="phone"]');
                                        data.phone = phoneElement?.textContent || '';
                                        
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
                await asyncio.sleep(self.request_delay)
                
        except Exception as e:
            logger.error(f"Error in Google Maps check: {e}")
        finally:
            # Ensure page is closed
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")
        
        # Calculate average rank and format result
        if ranks:
            avg_rank = sum(ranks) / len(ranks)
            if avg_rank <= 2:
                rank_color = "green"
            elif avg_rank <= 3:
                rank_color = "yellow"
            else:
                rank_color = "red"
            
            rank_text = f"rank #{round(avg_rank, 1)}"
        else:
            rank_text = "not found"
            rank_color = "gray"
            
        # Calculate coverage percentage
        coverage_percentage = (found_count / len(sample_points)) * 100 if sample_points else 0
        
        return {
            "rank_text": rank_text,
            "rank_color": rank_color,
            "average_rank": round(sum(ranks) / len(ranks), 1) if ranks else None,
            "coverage_percentage": round(coverage_percentage, 1),
            "profile_data": profile_data,
            "is_verified": is_verified
        }
        
    async def _check_bing_maps_ranking(
        self, 
        business_name: str, 
        domain: str,
        geo_points: List[Tuple[float, float]]
    ) -> Dict:
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
        bing_maps_key = os.getenv("BING_MAPS_API_KEY")
        
        ranks = []
        found_count = 0
        
        # Check a maximum of 5 points to avoid abuse
        sample_points = geo_points[:5]
        
        if bing_maps_key:
            # Use Bing Maps REST API
            try:
                async with aiohttp.ClientSession() as session:
                    for i, (lat, lon) in enumerate(sample_points):
                        query = business_name.replace(' ', '%20')
                        url = f"https://dev.virtualearth.net/REST/v1/LocalSearch/?query={query}&userLocation={lat},{lon}&key={bing_maps_key}"
                        
                        logger.info(f"Checking Bing Maps API at point {i+1}/{len(sample_points)}: {lat}, {lon}")
                        
                        try:
                            async with session.get(url) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    
                                    if data.get('resourceSets') and data['resourceSets'][0].get('resources'):
                                        resources = data['resourceSets'][0]['resources']
                                        
                                        # Find our domain or business name in results
                                        found = False
                                        for j, resource in enumerate(resources[:15]):  # Limit to top 15
                                            name = resource.get('name', '').lower()
                                            website = resource.get('Website', '').lower()
                                            
                                            if domain in name or domain in website or business_name.lower() in name:
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
            
        # Calculate average rank and format result
        if ranks:
            avg_rank = sum(ranks) / len(ranks)
            if avg_rank <= 2:
                rank_color = "green"
            elif avg_rank <= 3:
                rank_color = "yellow"
            else:
                rank_color = "red"
            
            rank_text = f"rank #{round(avg_rank, 1)}"
        else:
            rank_text = "not found"
            rank_color = "gray"
            
        # Calculate coverage percentage
        coverage_percentage = (found_count / len(sample_points)) * 100 if sample_points else 0
        
        return {
            "rank_text": rank_text,
            "rank_color": rank_color,
            "average_rank": round(sum(ranks) / len(ranks), 1) if ranks else None,
            "coverage_percentage": round(coverage_percentage, 1)
        }
        
    async def _check_bing_maps_scraping(
        self, 
        business_name: str, 
        domain: str,
        geo_points: List[Tuple[float, float]]
    ) -> Dict:
        """
        Fallback method to check Bing Maps using browser scraping with proper error handling.
        
        Args:
            business_name: Business name to search for
            domain: Domain to check in results
            geo_points: List of geo points to check from
            
        Returns:
            Dictionary with ranking results
        """
        browser = None
        page = None
        
        try:
            browser = await self._initialize_browser_pool()
            
            ranks = []
            found_count = 0
            
            # Check a maximum of 3 points to avoid abuse
            sample_points = geo_points[:3]
            
            # Create a new page
            page = await browser.newPage()
            
            # Set user agent from configuration
            await page.setUserAgent(self.user_agent)
            
            # Enable request interception to block unnecessary resources
            await page.setRequestInterception(True)
            
            async def intercept_request(request):
                # Block unnecessary resources
                if request.resourceType in ['image', 'media', 'font', 'stylesheet']:
                    await request.abort()
                else:
                    await request.continue_()
            
            page.on('request', intercept_request)
            
            for i, (lat, lon) in enumerate(sample_points):
                # Prepare search query
                search_query = f"{business_name}"
                
                # Open Bing Maps
                maps_url = f"https://www.bing.com/maps?q={search_query.replace(' ', '+')}&cp={lat}~{lon}"
                
                logger.info(f"Checking Bing Maps at point {i+1}/{len(sample_points)}: {lat}, {lon}")
                
                try:
                    # Navigate to Bing Maps
                    await page.goto(maps_url, {'timeout': 20000})
                    
                    # Wait for results to load
                    await asyncio.sleep(3)
                    await page.waitForSelector('.listViewCard', {'timeout': 10000})
                    
                    # Extract results
                    results = await page.evaluate('''
                    () => {
                        const results = [];
                        const items = document.querySelectorAll('.listViewCard');
                        for (let i = 0; i < Math.min(items.length, 15); i++) {
                            const item = items[i];
                            const title = item.querySelector('.b_dataList h2');
                            if (title) {
                                results.push({
                                    title: title.textContent,
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
                        result_title = result['title'].lower()
                        if domain in result_title or business_name.lower() in result_title:
                            found = True
                            ranks.append(result['position'])
                            break
                            
                    if found:
                        found_count += 1
                        
                except Exception as e:
                    logger.warning(f"Error checking Bing Maps at point {i+1}: {e}")
                    
                # Add delay between requests to avoid detection
                await asyncio.sleep(self.request_delay)
                
        except Exception as e:
            logger.error(f"Error in Bing Maps check: {e}")
        finally:
            # Ensure page is closed
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")
        
        # Calculate average rank and format result
        if ranks:
            avg_rank = sum(ranks) / len(ranks)
            if avg_rank <= 2:
                rank_color = "green"
            elif avg_rank <= 3:
                rank_color = "yellow"
            else:
                rank_color = "red"
            
            rank_text = f"rank #{round(avg_rank, 1)}"
        else:
            rank_text = "not found"
            rank_color = "gray"
            
        # Calculate coverage percentage
        coverage_percentage = (found_count / len(sample_points)) * 100 if sample_points else 0
        
        return {
            "rank_text": rank_text,
            "rank_color": rank_color,
            "average_rank": round(sum(ranks) / len(ranks), 1) if ranks else None,
            "coverage_percentage": round(coverage_percentage, 1)
        }
        
    async def _extract_nap_data(self, url: str) -> Dict:
        """
        Extract NAP (Name, Address, Phone) data from website.
        
        Args:
            url: Website URL
            
        Returns:
            Dictionary with NAP data
        """
        try:
            # Fetch the page
            html, _, _, _ = await self.scraper.fetch_html(url)
            
            soup = BeautifulSoup(html, 'lxml')
            
            nap = {
                "name": await self._extract_business_name(url),
                "address": None,
                "phone": None,
            }
            
            # Try schema.org data first - safe JSON handling with type checking
            schema_data = soup.find('script', {'type': 'application/ld+json'})
            if isinstance(schema_data, Tag) and schema_data.string:
                try:
                    data = json.loads(schema_data.string)
                    if isinstance(data, list):
                        data = data[0]
                    
                    # Check for address
                    if 'address' in data:
                        if isinstance(data['address'], dict):
                            address_parts = []
                            for key in ['streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'addressCountry']:
                                if key in data['address'] and data['address'][key]:
                                    address_parts.append(str(data['address'][key]))
                            if address_parts:
                                nap['address'] = ', '.join(address_parts)
                        elif isinstance(data['address'], str):
                            nap['address'] = data['address']
                    
                    # Check for phone
                    if 'telephone' in data:
                        nap['phone'] = data['telephone']
                        
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    logger.warning(f"Error parsing schema.org data for NAP: {e}")
                    pass
                    
            # If no schema data, try regex patterns
            if not nap['address']:
                # Look for address patterns
                address_candidates = []
                
                # Try to find address in structured elements - safe BeautifulSoup handling with type checking
                for element in soup.find_all(['p', 'div', 'span', 'address']):
                    if isinstance(element, Tag) and element.get_text():
                        text = element.get_text().strip()
                        
                        # Look for address patterns
                        if len(text) > 10 and len(text) < 200:
                            # Look for postal codes
                            postal_match = re.search(r'\b\d{5}(?:[-\s]\d{4})?\b', text)  # US format
                            if postal_match:
                                address_candidates.append((text, 5))
                                continue
                                
                            # Look for common address patterns
                            if re.search(r'\b(calle|carrera|avenida|av|cra|cll|street|st|avenue|ave|road|rd|boulevard|blvd)\b', 
                                        text.lower()):
                                address_candidates.append((text, 4))
                                continue
                                
                            # Look for city, state patterns
                            if re.search(r'\w+,\s*\w{2}', text):  # City, State format
                                address_candidates.append((text, 3))
                                continue
                                
                            # Look for numbers with street
                            if re.search(r'\d+\s+\w+(?:\s+\w+){1,3}', text):
                                address_candidates.append((text, 2))
                                continue
                
                # Use the highest scoring candidate
                address_candidates.sort(key=lambda x: x[1], reverse=True)
                if address_candidates:
                    nap['address'] = address_candidates[0][0]
            
            # Try to find phone if not found yet
            if not nap['phone']:
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
                                nap['phone'] = match.group(0)
                                break
                    if nap['phone']:
                        break
            
            return nap
            
        except Exception as e:
            logger.error(f"Error extracting NAP data: {e}")
            return {
                "name": self._extract_domain_safely(url),
                "address": None,
                "phone": None
            }
            
    async def _check_nap_consistency(
        self, 
        business_name: str, 
        domain: str,
        nap_data: Dict, 
        maps_data: Dict
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
            if maps_name in site_name or site_name in maps_name or domain in maps_name:
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
        
    def _get_default_local_rank_results(self, checked: int = 0) -> Dict:
        """Get default local rank results when checks fail"""
        return {
            "google_maps_rank": "unavailable",
            "bing_maps_rank": "unavailable",
            "apple_maps_rank": "unavailable",
            "nap_consistency": False,
            "sample_locations_checked": checked,
            "geo_coverage_percentage": 0,
            "has_verified_listing": False
        }
        
    async def close(self):
        """Close all resources with proper error handling"""
        try:
            if self.browser_pool:
                for browser in self.browser_pool:
                    try:
                        await browser.close()
                    except Exception as e:
                        logger.warning(f"Error closing browser: {e}")
                self.browser_pool = None
                logger.info("Browser pool closed successfully")
            
            if hasattr(self.scraper, 'close'):
                try:
                    await self.scraper.close()
                    logger.info("Scraper closed successfully")
                except Exception as e:
                    logger.warning(f"Error closing scraper: {e}")
                    
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            logger.info("SEOAnalyzer cleanup completed")