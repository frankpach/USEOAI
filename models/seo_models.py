from typing import List, Dict, Optional, Any, Union, Tuple
from pydantic import BaseModel, HttpUrl, Field, field_validator


class AnalysisRequest(BaseModel):
    """Input model for SEO analysis request"""
    url: str
    seo_goal: str
    location: str
    language: str = "es"
    # Keywords opcionales para análisis local específico
    keywords: Optional[Union[str, List[str]]] = None
    # Coordenadas exactas (opcionales, para mayor precisión)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    local_radius_km: Optional[int] = 5
    geo_samples: Optional[int] = 10
    llm_provider: Optional[str] = "chatgpt"  # Options: chatgpt, claude, gemini
    # Nuevo campo para forzar Playwright desde el frontend (si está habilitado en config)
    force_playwright: Optional[bool] = False
    # Tipo de reporte
    report_type: Optional[str] = "Web SEO"  # Valores: 'Web SEO', 'Local Ranking', 'Web SEO and Local Ranking'

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            if not v.strip():
                return None
            return [v.strip()]
        elif isinstance(v, list):
            if not v:
                return None
            # Filter out empty strings and strip whitespace
            cleaned_keywords = [kw.strip() for kw in v if kw and kw.strip()]
            return cleaned_keywords if cleaned_keywords else None
        else:
            raise ValueError('Keywords must be a string or list of strings')

    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v

    @field_validator('local_radius_km')
    @classmethod
    def validate_radius(cls, v):
        if v is not None and (v < 1 or v > 50):
            raise ValueError('Local radius must be between 1 and 50 km')
        return v

    @field_validator('geo_samples')
    @classmethod
    def validate_geo_samples(cls, v):
        if v is not None and (v < 1 or v > 20):
            raise ValueError('Geo samples must be between 1 and 20')
        return v


class GeoRankRequest(BaseModel):
    """Input model for standalone geolocation ranking analysis"""
    location: Optional[str] = None  # Optional if latitude and longitude are provided
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    local_radius_km: int = Field(..., ge=1, le=50)
    geo_samples: int = Field(..., ge=1, le=20)
    company_name: str = Field(..., min_length=1, description="Nombre de la empresa")
    keywords: Union[str, List[str]] = Field(..., description="Palabras clave obligatorias para análisis local")

    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        if isinstance(v, str):
            if not v.strip():
                raise ValueError('Keywords cannot be empty')
            return [v.strip()]
        elif isinstance(v, list):
            if not v:
                raise ValueError('Keywords list cannot be empty')
            # Filter out empty strings and strip whitespace
            cleaned_keywords = [kw.strip() for kw in v if kw and kw.strip()]
            if not cleaned_keywords:
                raise ValueError('Keywords list cannot contain only empty values')
            return cleaned_keywords
        else:
            raise ValueError('Keywords must be a string or list of strings')

    @field_validator('location')
    @classmethod
    def validate_location_or_coordinates(cls, v, info):
        """Ensure either location or both latitude/longitude are provided"""
        latitude = info.data.get('latitude') if info.data else None
        longitude = info.data.get('longitude') if info.data else None

        if not v and (latitude is None or longitude is None):
            raise ValueError('Either location or both latitude and longitude must be provided')

        return v


class KeywordRankResult(BaseModel):
    """Individual keyword ranking result"""
    keyword: str
    average_rank: Optional[float] = None
    coverage_percentage: float
    total_samples: int
    found_in_samples: int
    google_maps_rank: Optional[str] = None
    bing_maps_rank: Optional[str] = None
    nap_inconsistencies: List[str] = []
    visibility_score: float  # 0-100 scale


class GeoRankResponse(BaseModel):
    """Response model for geolocation ranking analysis"""
    company_name: str
    location_used: str
    coordinates: Optional[Tuple[float, float]] = None
    radius_km: int
    total_samples: int
    keywords_analyzed: int
    keyword_results: List[KeywordRankResult]
    overall_visibility_score: float
    nap_consistency: bool
    has_verified_listing: bool
    analysis_timestamp: str


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
    h1: List[Dict[str, Any]]
    h2: List[Dict[str, Any]]
    h3: List[Dict[str, Any]]
    h4: List[Dict[str, Any]]
    h5: List[Dict[str, Any]]
    h6: List[Dict[str, Any]]


class Paragraph(BaseModel):
    """Paragraph content and length"""
    text: str
    length: int
    word_count: Optional[int] = None


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
    width: Optional[str] = None
    height: Optional[str] = None


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


class KeywordUsageResult(BaseModel):
    keyword: str
    h1_h6: bool
    p: bool
    freq: int
    obs: str
    color: str
    freq_headers: int
    freq_paragraphs: int
    positions_headers: list
    positions_paragraphs: list

class KeywordUsageResponse(BaseModel):
    results: List[KeywordUsageResult]
    checklist: List[str]
    url: str
    keywords: List[str]
    match: str


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
    # Nuevos campos estructurados del LLM
    executive_summary: Optional[str] = None
    technical_score: Optional[float] = None
    onpage_score: Optional[float] = None
    offpage_score: Optional[float] = None
    overall_score: Optional[float] = None
    issues: Optional[List[Dict[str, str]]] = None
    llm_recommendations: Optional[List[str]] = None
    checklist: Optional[List[str]] = None
    # --- Agregados para comparación avanzada ---
    images_count: Optional[int] = None
    page_metrics: Optional[Dict[str, Any]] = None
    # --- Keyword usage analysis ---
    keyword_usage: Optional[KeywordUsageResponse] = None
