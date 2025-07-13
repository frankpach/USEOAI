import os
import logging
import json
from typing import Dict, Any, List, Optional
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for OpenAI API (ChatGPT)"""
    
    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment")
            
    async def analyze_text(
        self,
        content: str,
        seo_goal: str,
        location: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Analyze text content using OpenAI API.
        
        Args:
            content: Text content to analyze
            seo_goal: SEO goal for the website
            location: Geographic location
            language: Content language
            
        Returns:
            Analysis results
        """
        if not self.api_key:
            return self._get_fallback_response("OpenAI API key not configured")
            
        try:
            # Dynamically import to avoid dependency issues
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(content, seo_goal, location, language)
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert SEO analyst. Analyze the provided website content and provide a structured JSON response with semantic analysis."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1000
            )
            
            # Extract and parse response
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_response(str(e))
    
    def _create_analysis_prompt(
        self,
        content: str,
        seo_goal: str,
        location: str,
        language: str
    ) -> str:
        """Create analysis prompt for OpenAI"""
        return f"""
        Analyze the following website content and provide a semantic analysis focused on SEO effectiveness.
        
        SEO GOAL: {seo_goal}
        TARGET LOCATION: {location}
        CONTENT LANGUAGE: {language}
        
        CONTENT TO ANALYZE:
        {content}
        
        Please provide your analysis in the following JSON format:
        {{
            "coherence_score": (float between 0-1, how coherent the content is with the SEO goal),
            "detected_intent": (string, what appears to be the main intent of the page),
            "readability_level": (string, CEFR level A1-C2),
            "suggested_improvements": [array of specific suggestions to improve SEO for the stated goal]
        }}
        """
    
    def _get_fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Generate fallback response in case of API error"""
        return {
            "coherence_score": 0.5,
            "detected_intent": "Unable to analyze",
            "readability_level": "Unknown",
            "suggested_improvements": [
                f"Error during analysis: {error_message}",
                "Please check API configuration and try again."
            ]
        }


class AnthropicClient:
    """Client for Anthropic API (Claude)"""
    
    def __init__(self):
        """Initialize Anthropic client with API key from environment"""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("Anthropic API key not found in environment")
            
    async def analyze_text(
        self,
        content: str,
        seo_goal: str,
        location: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Analyze text content using Anthropic Claude API.
        
        Args:
            content: Text content to analyze
            seo_goal: SEO goal for the website
            location: Geographic location
            language: Content language
            
        Returns:
            Analysis results
        """
        if not self.api_key:
            return self._get_fallback_response("Anthropic API key not configured")
            
        try:
            # Dynamically import to avoid dependency issues
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(content, seo_goal, location, language)
            
            # Call Claude API
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0.3,
                system="You are an expert SEO analyst. Analyze the provided website content and provide a structured JSON response with semantic analysis.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract JSON from response
            result_text = response.content[0].text
            # Try to parse as JSON
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # Extract JSON from markdown code block
                import re
                json_match = re.search(r'```json\n(.*?)\n```', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not extract JSON from Claude response")
                    
            return result
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._get_fallback_response(str(e))
    
    def _create_analysis_prompt(
        self,
        content: str,
        seo_goal: str,
        location: str,
        language: str
    ) -> str:
        """Create analysis prompt for Claude"""
        return f"""
        Analyze the following website content and provide a semantic analysis focused on SEO effectiveness.
        
        SEO GOAL: {seo_goal}
        TARGET LOCATION: {location}
        CONTENT LANGUAGE: {language}
        
        CONTENT TO ANALYZE:
        {content}
        
        Respond with only a JSON object in this exact format:
        ```json
        {{
            "coherence_score": (float between 0-1, how coherent the content is with the SEO goal),
            "detected_intent": (string, what appears to be the main intent of the page),
            "readability_level": (string, CEFR level A1-C2),
            "suggested_improvements": [array of specific suggestions to improve SEO for the stated goal]
        }}
        ```
        
        Do not include any text outside the JSON code block.
        """
    
    def _get_fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Generate fallback response in case of API error"""
        return {
            "coherence_score": 0.5,
            "detected_intent": "Unable to analyze",
            "readability_level": "Unknown",
            "suggested_improvements": [
                f"Error during analysis: {error_message}",
                "Please check API configuration and try again."
            ]
        }


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini client with API key from environment"""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("Google Gemini API key not found in environment")
            
    async def analyze_text(
        self,
        content: str,
        seo_goal: str,
        location: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Analyze text content using Google Gemini API.
        
        Args:
            content: Text content to analyze
            seo_goal: SEO goal for the website
            location: Geographic location
            language: Content language
            
        Returns:
            Analysis results
        """
        if not self.api_key:
            return self._get_fallback_response("Google Gemini API key not configured")
            
        try:
            # Dynamically import to avoid dependency issues
            import google.generativeai as genai
            
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(content, seo_goal, location, language)
            
            # Call Gemini API
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            
            # Extract JSON from response
            result_text = response.text
            
            # Try to parse as JSON
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # Extract JSON from markdown code block
                import re
                json_match = re.search(r'```json\n(.*?)\n```', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not extract JSON from Gemini response")
                    
            return result
            
        except Exception as e:
            logger.error(f"Google Gemini API error: {e}")
            return self._get_fallback_response(str(e))
    
    def _create_analysis_prompt(
        self,
        content: str,
        seo_goal: str,
        location: str,
        language: str
    ) -> str:
        """Create analysis prompt for Gemini"""
        return f"""
        You are an expert SEO analyst. Analyze the following website content and provide a semantic analysis focused on SEO effectiveness.
        
        SEO GOAL: {seo_goal}
        TARGET LOCATION: {location}
        CONTENT LANGUAGE: {language}
        
        CONTENT TO ANALYZE:
        {content}
        
        Respond with only a JSON object in this exact format:
        ```json
        {{
            "coherence_score": (float between 0-1, how coherent the content is with the SEO goal),
            "detected_intent": (string, what appears to be the main intent of the page),
            "readability_level": (string, CEFR level A1-C2),
            "suggested_improvements": [array of specific suggestions to improve SEO for the stated goal]
        }}
        ```
        
        Do not include any text outside the JSON code block.
        """
    
    def _get_fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Generate fallback response in case of API error"""
        return {
            "coherence_score": 0.5,
            "detected_intent": "Unable to analyze",
            "readability_level": "Unknown",
            "suggested_improvements": [
                f"Error during analysis: {error_message}",
                "Please check API configuration and try again."
            ]
        }