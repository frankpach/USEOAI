import os
import logging
import json
from typing import Dict, Any, List, Optional
import asyncio
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClientBase(ABC):
    """Base class for LLM clients with standardized interface"""

    def __init__(self, provider_name: str):
        """Initialize base client"""
        self.provider_name = provider_name
        self.api_key = None

    @abstractmethod
    async def analyze_text(
        self,
        content: str,
        seo_goal: str,
        location: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Analyze text content using LLM API.

        Args:
            content: Text content to analyze
            seo_goal: SEO goal for the website
            location: Geographic location
            language: Content language

        Returns:
            Standardized analysis results with keys:
            - coherence_score: float (0-1)
            - detected_intent: str
            - readability_level: str (CEFR level)
            - suggested_improvements: List[str]
        """
        pass

    @abstractmethod
    def _create_analysis_prompt(
        self,
        content: str,
        seo_goal: str,
        location: str,
        language: str
    ) -> str:
        """Create analysis prompt for the specific LLM"""
        pass

    def _get_fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Generate standardized fallback response in case of API error"""
        return {
            "coherence_score": 0.5,
            "detected_intent": "Unable to analyze",
            "readability_level": "Unknown",
            "suggested_improvements": [
                f"ALERTA: Respuesta simulada - {self.provider_name} API error: {error_message}",
                "Verifique que la API key esté correctamente configurada en el entorno.",
                "Asegúrese de que su cuenta tenga acceso a la API correspondiente.",
                "Revise los logs del servidor para más detalles.",
                "Si el problema persiste, contacte al administrador."
            ]
        }

    def _validate_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and standardize LLM response"""
        required_keys = ["coherence_score", "detected_intent", "readability_level", "suggested_improvements"]

        # Ensure all required keys exist
        for key in required_keys:
            if key not in response:
                response[key] = self._get_default_value(key)

        # Validate coherence_score
        if not isinstance(response["coherence_score"], (int, float)):
            response["coherence_score"] = 0.5
        else:
            response["coherence_score"] = max(0.0, min(1.0, float(response["coherence_score"])))

        # Ensure suggested_improvements is a list
        if not isinstance(response["suggested_improvements"], list):
            response["suggested_improvements"] = ["No specific improvements suggested"]

        return response

    def _get_default_value(self, key: str) -> Any:
        """Get default value for missing response keys"""
        defaults = {
            "coherence_score": 0.5,
            "detected_intent": "Unknown",
            "readability_level": "B2",
            "suggested_improvements": ["No specific improvements suggested"]
        }
        return defaults.get(key, "Unknown")


class OpenAIClient(LLMClientBase):
    """Client for OpenAI API (ChatGPT)"""

    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        super().__init__("OpenAI")
        # Import config here to avoid circular imports
        from config.config import SEOAnalyzerConfig
        config = SEOAnalyzerConfig()
        self.api_key = config.OPENAI_API_KEY
        self.model = config.OPENAI_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS
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
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert SEO analyst. Analyze the provided website content and provide a structured JSON response with semantic analysis."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Extract and parse response
            content_str = response.choices[0].message.content
            if content_str is None:
                raise ValueError("OpenAI response content is None")
            result = json.loads(content_str)
            return self._validate_response(result)

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
        """Create analysis prompt for LLM (OpenAI, Anthropic, Gemini)"""
        return f'''
You are an expert SEO consultant and web analyst. You will receive a structured summary of a website, including:

- SEO goal: {seo_goal}
- Industry/sector: (if available)
- Location: {location}
- Main competitors: (if available)
- Metadata (title, meta description)
- HTML structure (H1, H2, H3 counts, etc.)
- Links (internal, external, broken)
- Images (total, without alt text)
- Speed metrics (TTFB, load time, page size)
- Other technical data

Your task: Analyze this data and return a JSON with the following structure:

{{
  "executive_summary": "A clear, concise executive summary of the site's SEO status.",
  "technical_score": 0-100,
  "onpage_score": 0-100,
  "offpage_score": 0-100,
  "overall_score": 0-100,
  "issues": [
    {{
      "title": "Short problem title",
      "description": "Clear, actionable description of the problem.",
      "priority": "high|medium|low"
    }}
    // ...more issues
  ],
  "recommendations": [
    "Short, actionable recommendation 1",
    "Short, actionable recommendation 2"
    // ...more recommendations
  ],
  "checklist": [
    "SMART task 1 (Specific, Measurable, Achievable, Relevant, Time-bound)",
    "SMART task 2"
    // ...more tasks
  ]
}}

Instructions:
- Use the SEO goal, industry, and location to tailor your analysis and recommendations.
- Assign realistic scores (0-100) for each area.
- List the most relevant issues and prioritize them.
- Recommendations must be clear, concise, and focused on real SEO impact.
- The checklist must be actionable, prioritized, and each task should be SMART.
- If any data is missing, note it in the executive summary.
- Respond ONLY with the JSON, no explanations or extra text.
- All output must be in the following language: {language}.

Website data:
{content}
'''


class AnthropicClient(LLMClientBase):
    """Client for Anthropic API (Claude)"""

    def __init__(self):
        """Initialize Anthropic client with API key from environment"""
        super().__init__("Anthropic")
        # Import config here to avoid circular imports
        from config.config import SEOAnalyzerConfig
        config = SEOAnalyzerConfig()
        self.api_key = config.ANTHROPIC_API_KEY
        self.model = config.ANTHROPIC_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS
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
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system="You are an expert SEO analyst. Analyze the provided website content and provide a structured JSON response with semantic analysis.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract JSON from response
            # Anthropic's response.content is a list of blocks; find the first block with 'text' attribute
            result_text = None
            for block in response.content:
                text_val = getattr(block, 'text', None)
                if isinstance(text_val, str):
                    result_text = text_val
                    break
            if result_text is None:
                raise ValueError("No text block found in Anthropic response")
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
            return self._validate_response(result)

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
        """Create analysis prompt for LLM (OpenAI, Anthropic, Gemini)"""
        return f'''
You are an expert SEO consultant and web analyst. You will receive a structured summary of a website, including:

- SEO goal: {seo_goal}
- Industry/sector: (if available)
- Location: {location}
- Main competitors: (if available)
- Metadata (title, meta description)
- HTML structure (H1, H2, H3 counts, etc.)
- Links (internal, external, broken)
- Images (total, without alt text)
- Speed metrics (TTFB, load time, page size)
- Other technical data

Your task: Analyze this data and return a JSON with the following structure:

{{
  "executive_summary": "A clear, concise executive summary of the site's SEO status.",
  "technical_score": 0-100,
  "onpage_score": 0-100,
  "offpage_score": 0-100,
  "overall_score": 0-100,
  "issues": [
    {{
      "title": "Short problem title",
      "description": "Clear, actionable description of the problem.",
      "priority": "high|medium|low"
    }}
    // ...more issues
  ],
  "recommendations": [
    "Short, actionable recommendation 1",
    "Short, actionable recommendation 2"
    // ...more recommendations
  ],
  "checklist": [
    "SMART task 1 (Specific, Measurable, Achievable, Relevant, Time-bound)",
    "SMART task 2"
    // ...more tasks
  ]
}}

Instructions:
- Use the SEO goal, industry, and location to tailor your analysis and recommendations.
- Assign realistic scores (0-100) for each area.
- List the most relevant issues and prioritize them.
- Recommendations must be clear, concise, and focused on real SEO impact.
- The checklist must be actionable, prioritized, and each task should be SMART.
- If any data is missing, note it in the executive summary.
- Respond ONLY with the JSON, no explanations or extra text.
- All output must be in the following language: {language}.

Website data:
{content}
'''


class GeminiClient(LLMClientBase):
    """Client for Google Gemini API"""

    def __init__(self):
        """Initialize Gemini client with API key from environment"""
        super().__init__("Google Gemini")
        # Import config here to avoid circular imports
        from config.config import SEOAnalyzerConfig
        config = SEOAnalyzerConfig()
        self.api_key = config.GOOGLE_API_KEY
        self.model = config.GEMINI_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS
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

            # Google Gemini API usage correction
            # See: https://ai.google.dev/gemini-api/docs/get-started/python
            from google.generativeai.generative_models import GenerativeModel
            prompt = self._create_analysis_prompt(content, seo_goal, location, language)
            model = GenerativeModel(self.model)
            # Gemini expects a list of parts for the prompt
            response = model.generate_content([{"text": prompt}])
            # The response has a 'text' attribute
            result_text = getattr(response, 'text', None)
            if result_text is None:
                raise ValueError("No text found in Gemini response")
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
            return self._validate_response(result)

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
        """Create analysis prompt for LLM (OpenAI, Anthropic, Gemini)"""
        return f'''
You are an expert SEO consultant and web analyst. You will receive a structured summary of a website, including:

- SEO goal: {seo_goal}
- Industry/sector: (if available)
- Location: {location}
- Main competitors: (if available)
- Metadata (title, meta description)
- HTML structure (H1, H2, H3 counts, etc.)
- Links (internal, external, broken)
- Images (total, without alt text)
- Speed metrics (TTFB, load time, page size)
- Other technical data

Your task: Analyze this data and return a JSON with the following structure:

{{
  "executive_summary": "A clear, concise executive summary of the site's SEO status.",
  "technical_score": 0-100,
  "onpage_score": 0-100,
  "offpage_score": 0-100,
  "overall_score": 0-100,
  "issues": [
    {{
      "title": "Short problem title",
      "description": "Clear, actionable description of the problem.",
      "priority": "high|medium|low"
    }}
    // ...more issues
  ],
  "recommendations": [
    "Short, actionable recommendation 1",
    "Short, actionable recommendation 2"
    // ...more recommendations
  ],
  "checklist": [
    "SMART task 1 (Specific, Measurable, Achievable, Relevant, Time-bound)",
    "SMART task 2"
    // ...more tasks
  ]
}}

Instructions:
- Use the SEO goal, industry, and location to tailor your analysis and recommendations.
- Assign realistic scores (0-100) for each area.
- List the most relevant issues and prioritize them.
- Recommendations must be clear, concise, and focused on real SEO impact.
- The checklist must be actionable, prioritized, and each task should be SMART.
- If any data is missing, note it in the executive summary.
- Respond ONLY with the JSON, no explanations or extra text.
- All output must be in the following language: {language}.

Website data:
{content}
'''
