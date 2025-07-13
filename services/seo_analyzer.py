import logging
import time
import re
import asyncio
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup

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
    
    def __init__(self):
        """Initialize the SEO analyzer"""
        self.scraper = Scraper(timeout=20)
        self.semantic_analyzer = SemanticAnalyzer()
    
    async def analyze_site(self, analysis_request: AnalysisRequest) -> AnalysisResponse:
        """
        Main method to analyze a website.
        
        Args:
            analysis_request: AnalysisRequest object containing URL and parameters
            
        Returns:
            AnalysisResponse object with complete SEO analysis
        """
        url = analysis_request.url
        logger.info(f"Starting analysis for {url}")
        
        # Fetch HTML content
        html, headers, status_code, redirections = self.scraper.fetch_html(url)
        
        # Parse HTML
        parsed_data = self.scraper.parse_html(html)
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
        links_data["broken"] = self._find_broken_links(links_data["internal"] + links_data["external"])
        
        # Perform speed and performance analysis
        speed_metrics = await self._analyze_performance(url)
        
        # Check local ranking
        local_rank = self._check_local_ranking(
            url, 
            analysis_request.location, 
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
            provider=analysis_request.llm_provider
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
    
    def _find_broken_links(self, links: List[str]) -> List[str]:
        """Check for broken links"""
        broken_links = []
        
        for link in links[:10]:  # Limit to first 10 to avoid too many requests
            try:
                # Only check http/https links
                if not link.startswith(('http://', 'https://')):
                    continue
                    
                response = requests.head(
                    link, 
                    timeout=5, 
                    allow_redirects=True
                )
                
                if response.status_code >= 400:
                    broken_links.append(link)
                    
            except requests.RequestException:
                broken_links.append(link)
                
        return broken_links
    
    async def _analyze_performance(self, url: str) -> Dict:
        """Analyze page performance metrics"""
        # Start timing for TTFB
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=10)
            ttfb_ms = int((time.time() - start_time) * 1000)
            
            # Check if gzip is enabled
            gzip_enabled = 'gzip' in response.headers.get('Content-Encoding', '').lower()
            
            # Count resources (simulated)
            soup = BeautifulSoup(response.text, 'lxml')
            scripts = len(soup.find_all('script'))
            styles = len(soup.find_all('link', rel='stylesheet'))
            images = len(soup.find_all('img'))
            resource_count = scripts + styles + images
            
            # Check for lazy loading
            lazy_loaded_images = any(img.get('loading') == 'lazy' for img in soup.find_all('img'))
            
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
    
    def _check_local_ranking(self, url: str, location: str, radius_km: int, samples: int) -> Dict:
        """Check local ranking (simulated for MVP)"""
        # Note: In a real implementation, this would call the Google Maps API, etc.
        # For MVP, we'll simulate the results
        
        # Simulate Google Maps check
        google_maps = "no listing found"
        if "example" in url:
            google_maps = "rank #3"
            
        # Simulate Bing Maps check
        bing_maps = "no listing found"
        if "example" in url:
            bing_maps = "rank #8"
            
        # Simulate NAP consistency check
        nap_consistency = False
        if "example" in url:
            nap_consistency = True
            
        return {
            "google_maps": google_maps,
            "bing_maps": bing_maps,
            "nap_consistency": nap_consistency
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