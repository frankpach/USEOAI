from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, HttpUrl, Field, validator


class AnalysisRequest(BaseModel):
    """Input model for SEO analysis request"""
    url: str
    seo_goal: str
    location: str
    language: str = "es"
    local_radius_km: Optional[int] = 5
    geo_samples: Optional[int] = 10
    llm_provider: Optional[str] = "chatgpt"  # Options: chatgpt, claude, gemini
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class TitleAnalysis(BaseModel):
    """Analysis of page title"""
    text: str
    length: int
    has_keywords: bool


class MetaDescription(BaseModel):
    """Analysis of meta description"""
    text: str
    length: int


class HeadingTags(BaseModel):
    """Analysis of heading tags"""
    h1: List[Dict[str, str]]
    h2: List[Dict[str, str]]
    h3: List[Dict[str, str]]
    h4: List[Dict[str, str]]
    h5: List[Dict[str, str]]
    h6: List[Dict[str, str]]


class Paragraph(BaseModel):
    """Paragraph content and length"""
    text: str
    length: int


class SemanticSummary(BaseModel):
    """LLM-based semantic analysis"""
    llm_engine: str
    coherence_score: float
    detected_intent: str
    readability_level: str
    suggested_improvements: List[str]


class ImageWithoutAlt(BaseModel):
    """Image missing alt attribute"""
    src: str


class Links(BaseModel):
    """Analysis of links"""
    internal: List[str]
    external: List[str]
    broken: List[str]


class SpeedMetrics(BaseModel):
    """Performance metrics"""
    ttfb_ms: int
    resource_count: int
    gzip_enabled: bool
    lazy_loaded_images: bool


class LocalRankCheck(BaseModel):
    """Local SEO metrics"""
    google_maps: str
    bing_maps: str
    nap_consistency: bool


class AnalysisResponse(BaseModel):
    """Complete SEO analysis response"""
    status_code: int
    redirections: List[str]
    title: TitleAnalysis
    meta_description: MetaDescription
    meta_robots: str
    canonical_url: str
    h_tags: HeadingTags
    paragraphs: List[Paragraph]
    semantic_summary: SemanticSummary
    images_without_alt: List[ImageWithoutAlt]
    links: Links
    semantic_structure: List[str]
    structured_data: List[str]
    speed_metrics: SpeedMetrics
    local_rank_check: LocalRankCheck
    recommendations: List[str]