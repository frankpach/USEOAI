"""
LLM Manager for handling multiple LLM providers with configuration-based selection
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from config.config import SEOAnalyzerConfig
from utils.llm_clients import OpenAIClient, AnthropicClient, GeminiClient, LLMClientBase

logger = logging.getLogger(__name__)


class LLMManager:
    """Manages LLM providers based on configuration and priority order"""
    
    def __init__(self):
        """Initialize LLM manager with configuration"""
        self.config = SEOAnalyzerConfig()
        self.clients: Dict[str, LLMClientBase] = {}
        self.available_providers: List[str] = []
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize available LLM clients based on configuration"""
        # Create clients for enabled providers
        if self.config.ENABLE_OPENAI:
            self.clients["openai"] = OpenAIClient()
            if self.clients["openai"].api_key:
                self.available_providers.append("openai")
                logger.info("OpenAI client initialized and available")
            else:
                logger.warning("OpenAI enabled but API key not configured")
        
        if self.config.ENABLE_ANTHROPIC:
            self.clients["anthropic"] = AnthropicClient()
            if self.clients["anthropic"].api_key:
                self.available_providers.append("anthropic")
                logger.info("Anthropic client initialized and available")
            else:
                logger.warning("Anthropic enabled but API key not configured")
        
        if self.config.ENABLE_GEMINI:
            self.clients["gemini"] = GeminiClient()
            if self.clients["gemini"].api_key:
                self.available_providers.append("gemini")
                logger.info("Google Gemini client initialized and available")
            else:
                logger.warning("Google Gemini enabled but API key not configured")
        
        # Sort available providers by priority order
        self._sort_providers_by_priority()
        
        if not self.available_providers:
            logger.error("No LLM providers are available. Please check your configuration and API keys.")
    
    def _sort_providers_by_priority(self):
        """Sort available providers according to priority order in config"""
        priority_order = [p.strip().lower() for p in self.config.LLM_PRIORITY_ORDER]
        
        # Sort available providers by priority order
        sorted_providers = []
        for provider in priority_order:
            if provider in self.available_providers:
                sorted_providers.append(provider)
        
        # Add any remaining providers not in priority order
        for provider in self.available_providers:
            if provider not in sorted_providers:
                sorted_providers.append(provider)
        
        self.available_providers = sorted_providers
        logger.info(f"LLM providers priority order: {self.available_providers}")
    
    def get_primary_provider(self) -> Optional[str]:
        """Get the primary (first available) LLM provider"""
        return self.available_providers[0] if self.available_providers else None
    
    def get_client(self, provider: str) -> Optional[LLMClientBase]:
        """Get LLM client for specific provider"""
        return self.clients.get(provider)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers in priority order"""
        return self.available_providers.copy()
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a specific provider is available"""
        return provider in self.available_providers
    
    async def analyze_text(
        self,
        content: str,
        seo_goal: str,
        location: str,
        language: str,
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze text using the best available LLM provider
        
        Args:
            content: Text content to analyze
            seo_goal: SEO goal for the website
            location: Geographic location
            language: Content language
            preferred_provider: Optional preferred provider (if available)
            
        Returns:
            Analysis results from the selected provider
        """
        if not self.available_providers:
            return self._get_error_response("No LLM providers available")
        
        # Determine which provider to use
        provider_to_use = None
        
        if preferred_provider and preferred_provider in self.available_providers:
            provider_to_use = preferred_provider
            logger.info(f"Using preferred provider: {provider_to_use}")
        else:
            provider_to_use = self.available_providers[0]
            logger.info(f"Using primary provider: {provider_to_use}")
        
        client = self.clients[provider_to_use]
        
        # Try the selected provider
        for attempt in range(self.config.LLM_MAX_RETRIES):
            try:
                logger.info(f"Attempting analysis with {provider_to_use} (attempt {attempt + 1})")
                
                result = await asyncio.wait_for(
                    client.analyze_text(content, seo_goal, location, language),
                    timeout=self.config.LLM_TIMEOUT
                )
                
                # Add provider info to result
                result["provider_used"] = provider_to_use
                result["attempt_number"] = attempt + 1
                
                logger.info(f"Successfully analyzed with {provider_to_use}")
                return result
                
            except asyncio.TimeoutError:
                logger.warning(f"Timeout with {provider_to_use} (attempt {attempt + 1})")
                if attempt < self.config.LLM_MAX_RETRIES - 1:
                    await asyncio.sleep(self.config.LLM_RETRY_DELAY)
                    
            except Exception as e:
                logger.error(f"Error with {provider_to_use} (attempt {attempt + 1}): {e}")
                if attempt < self.config.LLM_MAX_RETRIES - 1:
                    await asyncio.sleep(self.config.LLM_RETRY_DELAY)
        
        # If primary provider failed and fallback is enabled, try other providers
        if self.config.LLM_ENABLE_FALLBACK and len(self.available_providers) > 1:
            logger.info("Primary provider failed, trying fallback providers")
            
            for fallback_provider in self.available_providers[1:]:
                try:
                    logger.info(f"Trying fallback provider: {fallback_provider}")
                    
                    fallback_client = self.clients[fallback_provider]
                    result = await asyncio.wait_for(
                        fallback_client.analyze_text(content, seo_goal, location, language),
                        timeout=self.config.LLM_TIMEOUT
                    )
                    
                    # Add provider info to result
                    result["provider_used"] = fallback_provider
                    result["attempt_number"] = 1
                    result["fallback_used"] = True
                    
                    logger.info(f"Successfully analyzed with fallback provider: {fallback_provider}")
                    return result
                    
                except Exception as e:
                    logger.error(f"Fallback provider {fallback_provider} also failed: {e}")
                    continue
        
        # All providers failed
        logger.error("All LLM providers failed")
        return self._get_error_response(f"All providers failed after {self.config.LLM_MAX_RETRIES} attempts")
    
    def _get_error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate standardized error response"""
        return {
            "coherence_score": 0.0,
            "detected_intent": "Error occurred",
            "readability_level": "Unknown",
            "suggested_improvements": [
                f"ERROR: {error_message}",
                "Verifique la configuración de los proveedores LLM",
                "Asegúrese de que las API keys estén correctamente configuradas",
                "Revise los logs del servidor para más detalles"
            ],
            "provider_used": "none",
            "error": True,
            "error_message": error_message
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get status information about LLM providers"""
        status = {
            "available_providers": self.available_providers,
            "total_providers": len(self.available_providers),
            "primary_provider": self.get_primary_provider(),
            "configuration": {
                "enable_openai": self.config.ENABLE_OPENAI,
                "enable_anthropic": self.config.ENABLE_ANTHROPIC,
                "enable_gemini": self.config.ENABLE_GEMINI,
                "priority_order": self.config.LLM_PRIORITY_ORDER,
                "enable_fallback": self.config.LLM_ENABLE_FALLBACK,
                "max_retries": self.config.LLM_MAX_RETRIES,
                "timeout": self.config.LLM_TIMEOUT
            }
        }
        
        # Add API key status (without exposing keys)
        for provider in ["openai", "anthropic", "gemini"]:
            client = self.clients.get(provider)
            if client:
                status[f"{provider}_configured"] = bool(client.api_key)
            else:
                status[f"{provider}_configured"] = False
        
        return status


# Global LLM manager instance
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get global LLM manager instance (singleton)"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager


def reset_llm_manager():
    """Reset global LLM manager instance (useful for testing)"""
    global _llm_manager
    _llm_manager = None 