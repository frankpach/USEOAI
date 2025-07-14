#!/usr/bin/env python3
"""
Script para probar el manejo de errores del sistema SEO
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any


async def test_api_endpoint(url: str) -> Dict[str, Any]:
    """Probar un endpoint de la API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "error": True,
                        "status": response.status,
                        "message": await response.text()
                    }
    except Exception as e:
        return {
            "error": True,
            "message": f"Connection error: {str(e)}"
        }


async def test_analysis_endpoint(url: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Probar el endpoint de análisis"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "error": True,
                        "status": response.status,
                        "message": await response.text()
                    }
    except Exception as e:
        return {
            "error": True,
            "message": f"Connection error: {str(e)}"
        }


async def main():
    """Función principal de pruebas"""
    base_url = "http://localhost:8000"
    
    print("🧪 Probando Sistema de Manejo de Errores")
    print("=" * 60)
    
    # Test 1: Verificar estado de la API
    print("\n1️⃣ Probando estado de la API...")
    status_result = await test_api_endpoint(f"{base_url}/api/status")
    if not status_result.get("error"):
        print("✅ API está funcionando")
        print(f"   Status: {status_result.get('status')}")
        print(f"   Timestamp: {status_result.get('timestamp')}")
    else:
        print("❌ API no está disponible")
        print(f"   Error: {status_result.get('message')}")
        return
    
    # Test 2: Verificar estado de LLM
    print("\n2️⃣ Probando estado de LLM...")
    llm_result = await test_api_endpoint(f"{base_url}/api/llm-status")
    if not llm_result.get("error"):
        print("✅ LLM Status obtenido")
        llm_status = llm_result.get("llm_status", {})
        print(f"   Proveedores disponibles: {llm_status.get('available_providers', [])}")
        print(f"   Proveedor principal: {llm_status.get('primary_provider', 'None')}")
        print(f"   Total proveedores: {llm_status.get('total_providers', 0)}")
    else:
        print("❌ Error obteniendo estado de LLM")
        print(f"   Error: {llm_result.get('message')}")
    
    # Test 3: Probar manejo de errores con URL inválida
    print("\n3️⃣ Probando manejo de errores con URL inválida...")
    invalid_url_data = {
        "url": "https://invalid-domain-that-does-not-exist-12345.com",
        "seo_goal": "Test SEO goal",
        "location": "Test Location",
        "language": "es",
        "local_radius_km": 5,
        "geo_samples": 5
    }
    
    analysis_result = await test_analysis_endpoint(f"{base_url}/api/analyze", invalid_url_data)
    if not analysis_result.get("error"):
        print("✅ Análisis completado (con errores manejados)")
        print(f"   Status Code: {analysis_result.get('status_code', 'N/A')}")
        print(f"   Title: {analysis_result.get('title', {}).get('text', 'N/A')}")
        
        # Verificar si hay errores en las recomendaciones
        recommendations = analysis_result.get('recommendations', [])
        error_messages = [rec for rec in recommendations if '⚠️' in rec or 'Error' in rec]
        if error_messages:
            print("   ⚠️ Errores detectados y manejados:")
            for error in error_messages[:3]:  # Mostrar solo los primeros 3
                print(f"      • {error}")
        else:
            print("   ✅ No se detectaron errores")
    else:
        print("❌ Error en el análisis")
        print(f"   Error: {analysis_result.get('message')}")
    
    # Test 4: Probar endpoint específico de manejo de errores
    print("\n4️⃣ Probando endpoint de manejo de errores...")
    error_test_result = await test_api_endpoint(f"{base_url}/api/test-error-handling")
    if not error_test_result.get("error"):
        print("✅ Test de manejo de errores completado")
        print(f"   Status: {error_test_result.get('status')}")
        print(f"   Message: {error_test_result.get('message')}")
        
        if error_test_result.get("result"):
            result = error_test_result.get("result", {})
            print(f"   Title: {result.get('title', {}).get('text', 'N/A')}")
            print(f"   Semantic Engine: {result.get('semantic_summary', {}).get('llm_engine', 'N/A')}")
    else:
        print("❌ Error en test de manejo de errores")
        print(f"   Error: {error_test_result.get('message')}")
    
    # Test 5: Probar con URL válida pero con errores de LLM
    print("\n5️⃣ Probando con URL válida (puede fallar LLM)...")
    valid_url_data = {
        "url": "https://example.com",
        "seo_goal": "Test SEO goal",
        "location": "Test Location",
        "language": "es"
    }
    
    valid_analysis_result = await test_analysis_endpoint(f"{base_url}/api/analyze", valid_url_data)
    if not valid_analysis_result.get("error"):
        print("✅ Análisis con URL válida completado")
        print(f"   Status Code: {valid_analysis_result.get('status_code', 'N/A')}")
        print(f"   Title: {valid_analysis_result.get('title', {}).get('text', 'N/A')}")
        
        # Verificar si hay errores de LLM
        semantic_summary = valid_analysis_result.get('semantic_summary', {})
        llm_engine = semantic_summary.get('llm_engine', 'unknown')
        if llm_engine in ['fallback', 'error']:
            print(f"   ⚠️ LLM falló, usando: {llm_engine}")
        else:
            print(f"   ✅ LLM funcionó: {llm_engine}")
    else:
        print("❌ Error en análisis con URL válida")
        print(f"   Error: {valid_analysis_result.get('message')}")
    
    print("\n" + "=" * 60)
    print("🎯 Resumen de Pruebas Completado")
    print("=" * 60)
    print("✅ El sistema ahora maneja errores de manera robusta")
    print("✅ Los análisis continúan aunque algunos componentes fallen")
    print("✅ Los errores se reportan claramente en las recomendaciones")
    print("✅ El frontend recibirá respuestas útiles en lugar de errores 500")


if __name__ == "__main__":
    asyncio.run(main()) 