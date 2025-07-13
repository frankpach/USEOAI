import logging
import os
from typing import Dict, List, Optional, Any
import json
import asyncio

from utils.llm_clients import OpenAIClient, AnthropicClient, GeminiClient
from models.semantic_models import (
    SemanticAnalysisRequest,
    SemanticAnalysisResponse
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticAnalyzer:
    """
    Service for analyzing website content semantically using LLMs.
    """
    
    def __init__(self):
        """Initialize the semantic analyzer with LLM clients"""
        self.openai_client = OpenAIClient()
        self.anthropic_client = AnthropicClient()
        self.gemini_client = GeminiClient()
    
    async def analyze_semantics(
        self,
        texts: List[str],
        page_title: str,
        meta_description: str,
        headings: Dict[str, List[Dict[str, str]]],
        seo_goal: str,
        location: str,
        language: str,
        provider: str = "chatgpt"
    ) -> Dict[str, Any]:
        """
        Analyze website content semantically using selected LLM.
        
        Args:
            texts: List of text content from the page
            page_title: Page title
            meta_description: Meta description
            headings: Dictionary of heading tags
            seo_goal: SEO goal for the website
            location: Geographic location
            language: Content language
            provider: LLM provider to use (chatgpt, claude, gemini)
            
        Returns:
            Semantic analysis results
        """
        logger.info(f"Starting semantic analysis with {provider}")
        
        # Prepare combined content for analysis
        combined_content = self._prepare_content_for_analysis(
            texts, page_title, meta_description, headings
        )
        
        # Select the appropriate LLM client
        if provider.lower() == "claude":
            result = await self.anthropic_client.analyze_text(
                combined_content, seo_goal, location, language
            )
        elif provider.lower() == "gemini":
            result = await self.gemini_client.analyze_text(
                combined_content, seo_goal, location, language
            )
        else:  # default to OpenAI/ChatGPT
            result = await self.openai_client.analyze_text(
                combined_content, seo_goal, location, language
            )
            
        # Parse the result
        try:
            if isinstance(result, str):
                # If the result is a string, try to parse it as JSON
                parsed_result = self._parse_llm_response(result)
            else:
                # If the result is already structured, use it directly
                parsed_result = result
                
            # Ensure we have all required fields
            semantic_response = SemanticAnalysisResponse(
                llm_engine=provider,
                coherence_score=parsed_result.get("coherence_score", 0.5),
                detected_intent=parsed_result.get("detected_intent", "Unknown"),
                readability_level=parsed_result.get("readability_level", "B2"),
                suggested_improvements=parsed_result.get("suggested_improvements", [])
            )
            
            return semantic_response.dict()
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Return fallback values in case of error
            return {
                "llm_engine": provider,
                "coherence_score": 0.5,
                "detected_intent": "Error in analysis",
                "readability_level": "Unknown",
                "suggested_improvements": [
                    "Error during semantic analysis. Please try again."
                ]
            }
    
    def _prepare_content_for_analysis(
        self,
        texts: List[str],
        page_title: str,
        meta_description: str,
        headings: Dict[str, List[Dict[str, str]]]
    ) -> str:
        """
        Prepare content for semantic analysis.
        
        Args:
            texts: List of text content
            page_title: Page title
            meta_description: Meta description
            headings: Dictionary of heading tags
            
        Returns:
            Formatted content string for LLM analysis
        """
        # Start with title and meta description
        content = f"Title: {page_title}\n\n"
        content += f"Meta Description: {meta_description}\n\n"
        
        # Add headings by level
        content += "Headings structure:\n"
        for level in range(1, 7):
            h_key = f"h{level}"
            if headings.get(h_key):
                for h in headings[h_key]:
                    content += f"H{level}: {h['text']}\n"
        content += "\n"
        
        # Add main content (limited to avoid token limits)
        content += "Main content:\n"
        total_chars = 0
        max_chars = 10000  # Limit to avoid exceeding token limits
        
        for text in texts:
            if total_chars + len(text) > max_chars:
                # Add a partial text if we're about to exceed the limit
                remaining = max_chars - total_chars
                if remaining > 100:  # Only add if we can include a meaningful chunk
                    content += text[:remaining] + "...\n"
                content += "[Content truncated due to length]\n"
                break
                
            content += text + "\n\n"
            total_chars += len(text)
            
        return content
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM.
        
        Args:
            response: JSON string from LLM
            
        Returns:
            Dictionary with parsed values
        """
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Look for JSON without code blocks
                json_str = response
                
            # Parse the JSON
            return json.loads(json_str)
            
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Error parsing LLM JSON: {e}")
            
            # Fallback: try to extract key information manually
            coherence_score = self._extract_float(response, r'coherence_score["\s:]+([0-9.]+)')
            detected_intent = self._extract_string(response, r'detected_intent["\s:]+([^",\n]+)')
            readability_level = self._extract_string(response, r'readability_level["\s:]+([^",\n]+)')
            
            # Extract improvements as list
            improvements = []
            improvements_match = re.search(r'suggested_improvements["\s:]+\[(.*?)\]', response, re.DOTALL)
            if improvements_match:
                items = improvements_match.group(1).split(',')
                improvements = [item.strip(' "\'') for item in items if item.strip()]
                
            return {
                "coherence_score": coherence_score or 0.5,
                "detected_intent": detected_intent or "Unknown",
                "readability_level": readability_level or "B2",
                "suggested_improvements": improvements or ["No specific suggestions available"]
            }
    
    def _extract_float(self, text: str, pattern: str) -> Optional[float]:
        """Extract float value using regex"""
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
    
    def _extract_string(self, text: str, pattern: str) -> Optional[str]:
        """Extract string value using regex"""
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None