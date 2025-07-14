# LLM Configuration Guide

This guide explains how to configure and use the LLM (Large Language Model) providers in the SEO Analyzer application.

## Overview

The application supports multiple LLM providers for semantic analysis:
- **OpenAI** (GPT-4, GPT-3.5-turbo)
- **Anthropic** (Claude)
- **Google Gemini** (Gemini Pro)

The system allows you to:
- Enable/disable specific providers
- Set priority order for provider selection
- Configure fallback behavior
- Customize model parameters

## Quick Start

1. **Copy the example configuration:**
   ```bash
   cp config/llm_config_example.env .env
   ```

2. **Edit the `.env` file** with your API keys and preferences

3. **Restart the application** to apply changes

## Configuration Options

### Provider Enable/Disable

Control which LLM providers are available:

```env
# Enable/disable specific providers
LLM_ENABLE_OPENAI=true
LLM_ENABLE_ANTHROPIC=false
LLM_ENABLE_GEMINI=false
```

### Priority Order

Set the order in which providers are used:

```env
# Priority order (first available will be used)
LLM_PRIORITY_ORDER=openai,anthropic,gemini
```

### API Keys

Configure your API keys:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Google Gemini API Key
GOOGLE_API_KEY=your-google-api-key-here
```

### Model Configuration

Choose specific models for each provider:

```env
# OpenAI Model
OPENAI_MODEL=gpt-4

# Anthropic Model
ANTHROPIC_MODEL=claude-3-opus-20240229

# Google Gemini Model
GEMINI_MODEL=gemini-1.5-pro
```

### Request Parameters

Customize request behavior:

```env
# Temperature (0.0-1.0, higher = more creative)
LLM_TEMPERATURE=0.3

# Maximum response tokens
LLM_MAX_TOKENS=1000

# Request timeout in seconds
LLM_TIMEOUT=30
```

### Fallback Behavior

Configure error handling and retries:

```env
# Enable fallback to other providers
LLM_ENABLE_FALLBACK=true

# Maximum retry attempts per provider
LLM_MAX_RETRIES=3

# Delay between retries in seconds
LLM_RETRY_DELAY=1.0
```

## Usage Examples

### Example 1: OpenAI Only

```env
LLM_ENABLE_OPENAI=true
LLM_ENABLE_ANTHROPIC=false
LLM_ENABLE_GEMINI=false
LLM_PRIORITY_ORDER=openai
OPENAI_API_KEY=sk-your-key-here
```

### Example 2: OpenAI Primary, Anthropic Fallback

```env
LLM_ENABLE_OPENAI=true
LLM_ENABLE_ANTHROPIC=true
LLM_ENABLE_GEMINI=false
LLM_PRIORITY_ORDER=openai,anthropic
LLM_ENABLE_FALLBACK=true
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### Example 3: All Providers with Custom Priority

```env
LLM_ENABLE_OPENAI=true
LLM_ENABLE_ANTHROPIC=true
LLM_ENABLE_GEMINI=true
LLM_PRIORITY_ORDER=anthropic,openai,gemini
LLM_ENABLE_FALLBACK=true
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here
```

### Example 4: Disable All LLMs (Testing Mode)

```env
LLM_ENABLE_OPENAI=false
LLM_ENABLE_ANTHROPIC=false
LLM_ENABLE_GEMINI=false
```

## API Endpoints

### Check LLM Status

```bash
GET /api/llm-status
```

Returns:
```json
{
  "status": "success",
  "timestamp": "2024-01-01T12:00:00",
  "llm_status": {
    "available_providers": ["openai", "anthropic"],
    "total_providers": 2,
    "primary_provider": "openai",
    "configuration": {
      "enable_openai": true,
      "enable_anthropic": true,
      "enable_gemini": false,
      "priority_order": ["openai", "anthropic", "gemini"],
      "enable_fallback": true,
      "max_retries": 3,
      "timeout": 30
    },
    "openai_configured": true,
    "anthropic_configured": true,
    "gemini_configured": false
  }
}
```

### Analyze with Specific Provider

```bash
POST /api/analyze
```

Request body:
```json
{
  "url": "https://example.com",
  "seo_goal": "Rank for web development services",
  "location": "Medellín, Colombia",
  "language": "es",
  "llm_provider": "anthropic"  // Optional: specify preferred provider
}
```

## How It Works

1. **Initialization**: The system checks which providers are enabled and have valid API keys
2. **Priority Sorting**: Available providers are sorted according to `LLM_PRIORITY_ORDER`
3. **Provider Selection**: The first available provider in the priority order is used
4. **Fallback**: If the primary provider fails and fallback is enabled, other providers are tried
5. **Retries**: Each provider is retried up to `LLM_MAX_RETRIES` times before moving to the next

## Error Handling

The system provides robust error handling:

- **API Key Missing**: Provider is disabled with a warning
- **API Errors**: Automatic retry with exponential backoff
- **Timeout**: Provider is skipped and fallback is attempted
- **All Providers Fail**: Returns a standardized error response

## Best Practices

1. **Start with One Provider**: Begin with just OpenAI to test the system
2. **Add Fallbacks**: Enable additional providers for reliability
3. **Monitor Costs**: Different providers have different pricing models
4. **Test Configuration**: Use the `/api/llm-status` endpoint to verify setup
5. **Environment Variables**: Keep API keys secure in `.env` files

## Troubleshooting

### Common Issues

1. **"No LLM providers available"**
   - Check that at least one provider is enabled
   - Verify API keys are correctly set
   - Ensure API keys are valid and have sufficient credits

2. **"Provider failed after X attempts"**
   - Check API key validity
   - Verify network connectivity
   - Review provider-specific error messages

3. **"Timeout errors"**
   - Increase `LLM_TIMEOUT` value
   - Check network latency to provider APIs
   - Consider using a different provider

### Debug Information

Use the `/api/llm-status` endpoint to:
- Verify provider configuration
- Check API key status
- See which providers are available
- Review priority order

## Cost Optimization

- **OpenAI**: Pay per token, GPT-4 is more expensive than GPT-3.5
- **Anthropic**: Pay per token, Claude-3-Opus is more expensive than Claude-3-Sonnet
- **Google Gemini**: Pay per token, generally competitive pricing

Consider using cheaper models for testing and more expensive models for production analysis. 