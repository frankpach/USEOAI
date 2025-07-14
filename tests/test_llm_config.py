#!/usr/bin/env python3
"""
Test script for LLM Configuration System

This script demonstrates how to use the new LLM configuration system
to enable/disable providers and set priority order.
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.llm_manager import get_llm_manager, reset_llm_manager
from config.config import SEOAnalyzerConfig


async def test_llm_configuration():
    """Test the LLM configuration system"""
    
    print("🔧 LLM Configuration Test")
    print("=" * 50)
    
    # Get the LLM manager
    llm_manager = get_llm_manager()
    
    # Display current configuration
    print("\n📋 Current Configuration:")
    print("-" * 30)
    
    config = SEOAnalyzerConfig()
    print(f"OpenAI Enabled: {config.ENABLE_OPENAI}")
    print(f"Anthropic Enabled: {config.ENABLE_ANTHROPIC}")
    print(f"Gemini Enabled: {config.ENABLE_GEMINI}")
    print(f"Priority Order: {config.LLM_PRIORITY_ORDER}")
    print(f"Fallback Enabled: {config.LLM_ENABLE_FALLBACK}")
    print(f"Max Retries: {config.LLM_MAX_RETRIES}")
    print(f"Timeout: {config.LLM_TIMEOUT}s")
    
    # Display API key status
    print(f"\n🔑 API Key Status:")
    print("-" * 30)
    print(f"OpenAI API Key: {'✅ Configured' if config.OPENAI_API_KEY else '❌ Not configured'}")
    print(f"Anthropic API Key: {'✅ Configured' if config.ANTHROPIC_API_KEY else '❌ Not configured'}")
    print(f"Google API Key: {'✅ Configured' if config.GOOGLE_API_KEY else '❌ Not configured'}")
    
    # Get LLM status
    print(f"\n📊 LLM Status:")
    print("-" * 30)
    
    status = llm_manager.get_status()
    print(f"Available Providers: {status['available_providers']}")
    print(f"Total Providers: {status['total_providers']}")
    print(f"Primary Provider: {status['primary_provider']}")
    
    if status['total_providers'] == 0:
        print("\n⚠️  No LLM providers are available!")
        print("Please check your configuration and API keys.")
        return
    
    # Test analysis with sample content
    print(f"\n🧪 Testing Analysis:")
    print("-" * 30)
    
    sample_content = """
    Welcome to our web development company. We specialize in creating 
    modern, responsive websites and web applications. Our team of 
    experienced developers uses the latest technologies to deliver 
    high-quality solutions for businesses of all sizes.
    
    We offer services including:
    - Frontend development with React and Vue.js
    - Backend development with Python and Node.js
    - E-commerce solutions
    - SEO optimization
    - Mobile app development
    
    Contact us today to discuss your project requirements.
    """
    
    try:
        print("Testing semantic analysis...")
        result = await llm_manager.analyze_text(
            content=sample_content,
            seo_goal="Rank for web development services in Medellín",
            location="Medellín, Colombia",
            language="es"
        )
        
        print(f"✅ Analysis completed successfully!")
        print(f"Provider used: {result.get('provider_used', 'unknown')}")
        print(f"Coherence score: {result.get('coherence_score', 0.0):.2f}")
        print(f"Detected intent: {result.get('detected_intent', 'Unknown')}")
        print(f"Readability level: {result.get('readability_level', 'Unknown')}")
        
        improvements = result.get('suggested_improvements', [])
        if improvements:
            print(f"Suggested improvements ({len(improvements)}):")
            for i, improvement in enumerate(improvements[:3], 1):  # Show first 3
                print(f"  {i}. {improvement}")
            if len(improvements) > 3:
                print(f"  ... and {len(improvements) - 3} more")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
    
    print(f"\n🎯 Configuration Examples:")
    print("-" * 30)
    print("To use only OpenAI:")
    print("  LLM_ENABLE_OPENAI=true")
    print("  LLM_ENABLE_ANTHROPIC=false")
    print("  LLM_ENABLE_GEMINI=false")
    print("  LLM_PRIORITY_ORDER=openai")
    print()
    print("To use OpenAI as primary with Anthropic fallback:")
    print("  LLM_ENABLE_OPENAI=true")
    print("  LLM_ENABLE_ANTHROPIC=true")
    print("  LLM_ENABLE_GEMINI=false")
    print("  LLM_PRIORITY_ORDER=openai,anthropic")
    print("  LLM_ENABLE_FALLBACK=true")
    print()
    print("To disable all LLMs (testing mode):")
    print("  LLM_ENABLE_OPENAI=false")
    print("  LLM_ENABLE_ANTHROPIC=false")
    print("  LLM_ENABLE_GEMINI=false")


def show_environment_setup():
    """Show how to set up environment variables"""
    
    print("\n🔧 Environment Setup:")
    print("=" * 50)
    
    print("1. Copy the example configuration:")
    print("   cp config/llm_config_example.env .env")
    print()
    print("2. Edit the .env file with your API keys:")
    print("   OPENAI_API_KEY=sk-your-openai-api-key-here")
    print("   ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here")
    print("   GOOGLE_API_KEY=your-google-api-key-here")
    print()
    print("3. Configure which providers to enable:")
    print("   LLM_ENABLE_OPENAI=true")
    print("   LLM_ENABLE_ANTHROPIC=false")
    print("   LLM_ENABLE_GEMINI=false")
    print()
    print("4. Set priority order:")
    print("   LLM_PRIORITY_ORDER=openai,anthropic,gemini")
    print()
    print("5. Restart the application to apply changes")


async def main():
    """Main function"""
    
    print("🚀 LLM Configuration System Demo")
    print("=" * 60)
    
    # Show environment setup
    show_environment_setup()
    
    # Test the configuration
    await test_llm_configuration()
    
    print("\n✅ Demo completed!")
    print("\nFor more information, see: docs/LLM_CONFIGURATION.md")


if __name__ == "__main__":
    # Run the test
    asyncio.run(main()) 