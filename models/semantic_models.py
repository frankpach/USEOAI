from typing import List, Dict, Optional
from pydantic import BaseModel


class SemanticAnalysisRequest(BaseModel):
    """Input model for semantic analysis"""
    texts: List[str]
    page_title: str
    meta_description: str
    headings: Dict[str, List[Dict[str, str]]]
    seo_goal: str
    location: str
    language: str


class SemanticAnalysisResponse(BaseModel):
    """Output model for semantic analysis"""
    llm_engine: str
    coherence_score: float
    detected_intent: str
    readability_level: str
    suggested_improvements: List[str]
    # Nuevos campos estructurados del LLM
    executive_summary: Optional[str] = None
    technical_score: Optional[float] = None
    onpage_score: Optional[float] = None
    offpage_score: Optional[float] = None
    overall_score: Optional[float] = None
    issues: Optional[List[Dict[str, str]]] = None
    recommendations: Optional[List[str]] = None
    checklist: Optional[List[str]] = None


class LLMProviderConfig(BaseModel):
    """Configuration for LLM providers"""
    name: str
    api_key: str
    model: str
    timeout: int = 30
