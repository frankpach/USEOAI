#!/usr/bin/env python3
"""
Script para verificar y validar la configuración del archivo env
"""

import os
import sys
from typing import Dict, List, Any
from dotenv import load_dotenv

def load_env_file(file_path: str) -> Dict[str, str]:
    """Cargar variables de entorno desde un archivo"""
    env_vars = {}
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Ignorar líneas vacías y comentarios
                if not line or line.startswith('#'):
                    continue
                
                # Procesar variables de entorno
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remover comillas si las hay
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
    
    return env_vars

def validate_llm_config(env_vars: Dict[str, str]) -> List[str]:
    """Validar configuración de LLM"""
    issues = []
    
    # Verificar variables requeridas
    required_vars = [
        'LLM_ENABLE_OPENAI',
        'LLM_ENABLE_ANTHROPIC', 
        'LLM_ENABLE_GEMINI',
        'LLM_PRIORITY_ORDER'
    ]
    
    for var in required_vars:
        if var not in env_vars:
            issues.append(f"❌ Variable faltante: {var}")
    
    # Verificar valores booleanos
    boolean_vars = [
        'LLM_ENABLE_OPENAI',
        'LLM_ENABLE_ANTHROPIC',
        'LLM_ENABLE_GEMINI',
        'LLM_ENABLE_FALLBACK'
    ]
    
    for var in boolean_vars:
        if var in env_vars:
            value = env_vars[var].lower()
            if value not in ['true', 'false']:
                issues.append(f"❌ Valor inválido para {var}: {value} (debe ser 'true' o 'false')")
    
    # Verificar API keys
    api_key_mapping = {
        'LLM_ENABLE_OPENAI': 'OPENAI_API_KEY',
        'LLM_ENABLE_ANTHROPIC': 'ANTHROPIC_API_KEY', 
        'LLM_ENABLE_GEMINI': 'GOOGLE_API_KEY'
    }
    
    for enable_var, api_key_var in api_key_mapping.items():
        if enable_var in env_vars and env_vars[enable_var].lower() == 'true':
            if api_key_var not in env_vars or not env_vars[api_key_var] or env_vars[api_key_var] == 'your-api-key-here':
                issues.append(f"❌ {enable_var} está habilitado pero {api_key_var} no está configurado")
    
    # Verificar orden de prioridad
    if 'LLM_PRIORITY_ORDER' in env_vars:
        priority_order = env_vars['LLM_PRIORITY_ORDER'].split(',')
        valid_providers = ['openai', 'anthropic', 'gemini']
        
        for provider in priority_order:
            provider = provider.strip().lower()
            if provider not in valid_providers:
                issues.append(f"❌ Proveedor inválido en LLM_PRIORITY_ORDER: {provider}")
    
    return issues

def validate_seo_config(env_vars: Dict[str, str]) -> List[str]:
    """Validar configuración de SEO"""
    issues = []
    
    # Verificar variables numéricas
    numeric_vars = [
        'SEO_DEFAULT_TIMEOUT',
        'SEO_MAX_CONCURRENT_REQUESTS',
        'SEO_MAX_LINKS_CHECK',
        'SEO_MAX_GEO_POINTS',
        'SEO_REQUEST_DELAY',
        'SEO_BROWSER_POOL_SIZE',
        'SEO_TTFB_THRESHOLD_MS',
        'SEO_TITLE_MIN_LENGTH',
        'SEO_TITLE_MAX_LENGTH',
        'SEO_META_DESC_MIN_LENGTH',
        'SEO_META_DESC_MAX_LENGTH',
        'SEO_RANK_GREEN_THRESHOLD',
        'SEO_RANK_YELLOW_THRESHOLD',
        'SEO_HTTP_TIMEOUT',
        'SEO_BROWSER_TIMEOUT',
        'SEO_SELECTOR_TIMEOUT',
        'SEO_THREAD_POOL_MAX_WORKERS',
        'SEO_MAX_RETRIES',
        'SEO_RETRY_DELAY'
    ]
    
    for var in numeric_vars:
        if var in env_vars:
            try:
                float(env_vars[var])
            except ValueError:
                issues.append(f"❌ Valor no numérico para {var}: {env_vars[var]}")
    
    return issues

def check_duplicates(env_vars: Dict[str, str]) -> List[str]:
    """Verificar variables duplicadas"""
    issues = []
    seen_keys = set()
    
    for key in env_vars.keys():
        if key in seen_keys:
            issues.append(f"❌ Variable duplicada: {key}")
        seen_keys.add(key)
    
    return issues

def generate_corrected_env(env_vars: Dict[str, str]) -> str:
    """Generar contenido corregido para el archivo .env"""
    
    template = """# =============================================================================
# LLM CONFIGURATION
# =============================================================================

# Enable/disable specific LLM providers (true/false)
LLM_ENABLE_OPENAI={openai_enabled}
LLM_ENABLE_ANTHROPIC={anthropic_enabled}
LLM_ENABLE_GEMINI={gemini_enabled}

# Priority order for LLM providers (comma-separated)
# First available provider in this order will be used
# Options: "openai", "anthropic", "gemini"
LLM_PRIORITY_ORDER={priority_order}

# =============================================================================
# LLM API KEYS
# =============================================================================

# OpenAI API Key (required if LLM_ENABLE_OPENAI=true)
OPENAI_API_KEY={openai_key}

# Anthropic API Key (required if LLM_ENABLE_ANTHROPIC=true)
ANTHROPIC_API_KEY={anthropic_key}

# Google Gemini API Key (required if LLM_ENABLE_GEMINI=true)
# ⚠️  WARNING: Replace with your actual API key
GOOGLE_API_KEY={google_key}

# =============================================================================
# LLM MODEL CONFIGURATION
# =============================================================================

# OpenAI Model (default: gpt-4)
OPENAI_MODEL={openai_model}

# Anthropic Model (default: claude-3-opus-20240229)
ANTHROPIC_MODEL={anthropic_model}

# Google Gemini Model (default: gemini-1.5-pro)
GEMINI_MODEL={gemini_model}

# =============================================================================
# LLM REQUEST PARAMETERS
# =============================================================================

# Temperature for all LLM requests (0.0-1.0, default: 0.3)
LLM_TEMPERATURE={temperature}

# Maximum tokens for responses (default: 1000)
LLM_MAX_TOKENS={max_tokens}

# Request timeout in seconds (default: 30)
LLM_TIMEOUT={timeout}

# =============================================================================
# LLM FALLBACK BEHAVIOR
# =============================================================================

# Enable fallback to other providers if primary fails (true/false, default: true)
LLM_ENABLE_FALLBACK={fallback}

# Maximum retry attempts per provider (default: 3)
LLM_MAX_RETRIES={max_retries}

# Delay between retries in seconds (default: 1.0)
LLM_RETRY_DELAY={retry_delay}

# =============================================================================
# SEO ANALYZER CONFIGURATION
# =============================================================================

# Basic configuration
SEO_DEFAULT_TIMEOUT={seo_timeout}
SEO_MAX_CONCURRENT_REQUESTS={seo_concurrent}
SEO_MAX_LINKS_CHECK={seo_links}
SEO_MAX_GEO_POINTS={seo_geo}
SEO_REQUEST_DELAY={seo_delay}
SEO_BROWSER_POOL_SIZE={seo_pool}

# Performance thresholds
SEO_TTFB_THRESHOLD_MS={seo_ttfb}

# Content length thresholds
SEO_TITLE_MIN_LENGTH={seo_title_min}
SEO_TITLE_MAX_LENGTH={seo_title_max}
SEO_META_DESC_MIN_LENGTH={seo_desc_min}
SEO_META_DESC_MAX_LENGTH={seo_desc_max}

# Ranking thresholds
SEO_RANK_GREEN_THRESHOLD={seo_green}
SEO_RANK_YELLOW_THRESHOLD={seo_yellow}

# Timeout configuration
SEO_HTTP_TIMEOUT={seo_http_timeout}
SEO_BROWSER_TIMEOUT={seo_browser_timeout}
SEO_SELECTOR_TIMEOUT={seo_selector_timeout}

# Threading configuration
SEO_THREAD_POOL_MAX_WORKERS={seo_workers}

# Retry settings
SEO_MAX_RETRIES={seo_retries}
SEO_RETRY_DELAY={seo_retry_delay}

# =============================================================================
# FEATURE FLAGS
# =============================================================================

SEO_ENABLE_HTML_CACHE={seo_cache}
SEO_ENABLE_BROKEN_LINKS_CHECK={seo_broken}
SEO_ENABLE_PERFORMANCE_CHECK={seo_performance}
SEO_ENABLE_GOOGLE_MAPS_CHECK={seo_google_maps}
SEO_ENABLE_BING_MAPS_CHECK={seo_bing_maps}

# =============================================================================
# LOGGING
# =============================================================================

SEO_LOG_LEVEL={seo_log}

# =============================================================================
# USER AGENTS
# =============================================================================

SEO_ANALYZER_USER_AGENT={seo_user_agent}
SEO_GEOCODING_USER_AGENT={seo_geocoding_agent}

# =============================================================================
# EXTERNAL API KEYS
# =============================================================================

# Bing Maps API Key (for enhanced local SEO)
BING_MAPS_API_KEY={bing_maps_key}
"""
    
    # Valores por defecto
    defaults = {
        'openai_enabled': env_vars.get('LLM_ENABLE_OPENAI', 'false'),
        'anthropic_enabled': env_vars.get('LLM_ENABLE_ANTHROPIC', 'false'),
        'gemini_enabled': env_vars.get('LLM_ENABLE_GEMINI', 'true'),
        'priority_order': env_vars.get('LLM_PRIORITY_ORDER', 'gemini,openai,anthropic'),
        'openai_key': env_vars.get('OPENAI_API_KEY', 'your-openai-api-key-here'),
        'anthropic_key': env_vars.get('ANTHROPIC_API_KEY', 'your-anthropic-api-key-here'),
        'google_key': env_vars.get('GOOGLE_API_KEY', 'your-google-api-key-here'),
        'openai_model': env_vars.get('OPENAI_MODEL', 'gpt-4'),
        'anthropic_model': env_vars.get('ANTHROPIC_MODEL', 'claude-3-opus-20240229'),
        'gemini_model': env_vars.get('GEMINI_MODEL', 'gemini-1.5-pro'),
        'temperature': env_vars.get('LLM_TEMPERATURE', '0.3'),
        'max_tokens': env_vars.get('LLM_MAX_TOKENS', '1000'),
        'timeout': env_vars.get('LLM_TIMEOUT', '30'),
        'fallback': env_vars.get('LLM_ENABLE_FALLBACK', 'true'),
        'max_retries': env_vars.get('LLM_MAX_RETRIES', '3'),
        'retry_delay': env_vars.get('LLM_RETRY_DELAY', '1.0'),
        'seo_timeout': env_vars.get('SEO_DEFAULT_TIMEOUT', '20'),
        'seo_concurrent': env_vars.get('SEO_MAX_CONCURRENT_REQUESTS', '5'),
        'seo_links': env_vars.get('SEO_MAX_LINKS_CHECK', '20'),
        'seo_geo': env_vars.get('SEO_MAX_GEO_POINTS', '5'),
        'seo_delay': env_vars.get('SEO_REQUEST_DELAY', '2.0'),
        'seo_pool': env_vars.get('SEO_BROWSER_POOL_SIZE', '3'),
        'seo_ttfb': env_vars.get('SEO_TTFB_THRESHOLD_MS', '500'),
        'seo_title_min': env_vars.get('SEO_TITLE_MIN_LENGTH', '30'),
        'seo_title_max': env_vars.get('SEO_TITLE_MAX_LENGTH', '70'),
        'seo_desc_min': env_vars.get('SEO_META_DESC_MIN_LENGTH', '100'),
        'seo_desc_max': env_vars.get('SEO_META_DESC_MAX_LENGTH', '160'),
        'seo_green': env_vars.get('SEO_RANK_GREEN_THRESHOLD', '2.0'),
        'seo_yellow': env_vars.get('SEO_RANK_YELLOW_THRESHOLD', '3.0'),
        'seo_http_timeout': env_vars.get('SEO_HTTP_TIMEOUT', '10'),
        'seo_browser_timeout': env_vars.get('SEO_BROWSER_TIMEOUT', '20000'),
        'seo_selector_timeout': env_vars.get('SEO_SELECTOR_TIMEOUT', '10000'),
        'seo_workers': env_vars.get('SEO_THREAD_POOL_MAX_WORKERS', '10'),
        'seo_retries': env_vars.get('SEO_MAX_RETRIES', '3'),
        'seo_retry_delay': env_vars.get('SEO_RETRY_DELAY', '1.0'),
        'seo_cache': env_vars.get('SEO_ENABLE_HTML_CACHE', 'true'),
        'seo_broken': env_vars.get('SEO_ENABLE_BROKEN_LINKS_CHECK', 'true'),
        'seo_performance': env_vars.get('SEO_ENABLE_PERFORMANCE_CHECK', 'true'),
        'seo_google_maps': env_vars.get('SEO_ENABLE_GOOGLE_MAPS_CHECK', 'true'),
        'seo_bing_maps': env_vars.get('SEO_ENABLE_BING_MAPS_CHECK', 'true'),
        'seo_log': env_vars.get('SEO_LOG_LEVEL', 'INFO'),
        'seo_user_agent': env_vars.get('SEO_ANALYZER_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
        'seo_geocoding_agent': env_vars.get('SEO_GEOCODING_USER_AGENT', 'SEO Analyzer Geocoding Client'),
        'bing_maps_key': env_vars.get('BING_MAPS_API_KEY', 'your_bing_maps_api_key_here')
    }
    
    return template.format(**defaults)

def main():
    """Función principal"""
    print("🔍 Verificando configuración del archivo env")
    print("=" * 60)
    
    # Cargar variables de entorno
    env_file = "env"
    env_vars = load_env_file(env_file)
    
    if not env_vars:
        print(f"❌ No se encontraron variables en el archivo {env_file}")
        return
    
    print(f"📋 Variables encontradas: {len(env_vars)}")
    print()
    
    # Validar configuración
    all_issues = []
    
    # Verificar duplicados
    duplicate_issues = check_duplicates(env_vars)
    if duplicate_issues:
        print("🚨 Variables duplicadas:")
        for issue in duplicate_issues:
            print(f"  {issue}")
        all_issues.extend(duplicate_issues)
        print()
    
    # Validar configuración LLM
    llm_issues = validate_llm_config(env_vars)
    if llm_issues:
        print("🚨 Problemas en configuración LLM:")
        for issue in llm_issues:
            print(f"  {issue}")
        all_issues.extend(llm_issues)
        print()
    
    # Validar configuración SEO
    seo_issues = validate_seo_config(env_vars)
    if seo_issues:
        print("🚨 Problemas en configuración SEO:")
        for issue in seo_issues:
            print(f"  {issue}")
        all_issues.extend(seo_issues)
        print()
    
    # Mostrar resumen
    if not all_issues:
        print("✅ Configuración válida!")
    else:
        print(f"❌ Se encontraron {len(all_issues)} problemas")
        print()
        
        # Generar archivo corregido
        corrected_content = generate_corrected_env(env_vars)
        
        print("📝 Archivo corregido generado:")
        print("=" * 60)
        print(corrected_content)
        
        # Guardar en archivo temporal
        with open('env_corrected.txt', 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        
        print()
        print("💡 Para aplicar las correcciones:")
        print("1. Copia el contenido de arriba")
        print("2. Reemplaza el contenido de tu archivo .env")
        print("3. O usa el archivo temporal: env_corrected.txt")
    
    # Mostrar configuración actual
    print()
    print("📊 Configuración actual:")
    print("-" * 30)
    print(f"OpenAI habilitado: {env_vars.get('LLM_ENABLE_OPENAI', 'No configurado')}")
    print(f"Anthropic habilitado: {env_vars.get('LLM_ENABLE_ANTHROPIC', 'No configurado')}")
    print(f"Gemini habilitado: {env_vars.get('LLM_ENABLE_GEMINI', 'No configurado')}")
    print(f"Orden de prioridad: {env_vars.get('LLM_PRIORITY_ORDER', 'No configurado')}")
    
    # Verificar API keys
    print()
    print("🔑 Estado de API Keys:")
    print("-" * 30)
    openai_key = env_vars.get('OPENAI_API_KEY', '')
    anthropic_key = env_vars.get('ANTHROPIC_API_KEY', '')
    google_key = env_vars.get('GOOGLE_API_KEY', '')
    
    print(f"OpenAI API Key: {'✅ Configurado' if openai_key and openai_key != 'your-openai-api-key-here' else '❌ No configurado'}")
    print(f"Anthropic API Key: {'✅ Configurado' if anthropic_key and anthropic_key != 'your-anthropic-api-key-here' else '❌ No configurado'}")
    print(f"Google API Key: {'✅ Configurado' if google_key and google_key != 'your-google-api-key-here' else '❌ No configurado'}")

if __name__ == "__main__":
    main() 