#!/usr/bin/env python3
"""
Script simple para probar el sistema de manejo de errores
"""

import requests
import json
from datetime import datetime

def test_endpoint(url):
    """Probar un endpoint"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": True, "status": response.status_code, "message": response.text}
    except Exception as e:
        return {"error": True, "message": str(e)}

def test_analysis(url, data):
    """Probar el endpoint de análisis"""
    try:
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": True, "status": response.status_code, "message": response.text}
    except Exception as e:
        return {"error": True, "message": str(e)}

def main():
    base_url = "http://localhost:8000"
    
    print("🧪 Probando Sistema de Manejo de Errores")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    
    # Test 1: Estado de la API
    print("\n1️⃣ Probando estado de la API...")
    status = test_endpoint(f"{base_url}/api/status")
    if not status.get("error"):
        print("✅ API funcionando")
        print(f"   Status: {status.get('status')}")
    else:
        print("❌ API no disponible")
        print(f"   Error: {status.get('message')}")
        return
    
    # Test 2: Estado de LLM
    print("\n2️⃣ Probando estado de LLM...")
    llm_status = test_endpoint(f"{base_url}/api/llm-status")
    if not llm_status.get("error"):
        print("✅ LLM Status obtenido")
        llm_data = llm_status.get("llm_status", {})
        print(f"   Proveedores: {llm_data.get('available_providers', [])}")
        print(f"   Principal: {llm_data.get('primary_provider', 'None')}")
    else:
        print("❌ Error LLM Status")
        print(f"   Error: {llm_status.get('message')}")
    
    # Test 3: Análisis con URL inválida
    print("\n3️⃣ Probando análisis con URL inválida...")
    invalid_data = {
        "url": "https://invalid-domain-that-does-not-exist-12345.com",
        "seo_goal": "Test SEO goal",
        "location": "Test Location",
        "language": "es"
    }
    
    result = test_analysis(f"{base_url}/api/analyze", invalid_data)
    if not result.get("error"):
        print("✅ Análisis completado (con errores manejados)")
        print(f"   Status Code: {result.get('status_code', 'N/A')}")
        print(f"   Title: {result.get('title', {}).get('text', 'N/A')}")
        
        # Verificar errores en recomendaciones
        recommendations = result.get('recommendations', [])
        error_msgs = [r for r in recommendations if '⚠️' in r or 'Error' in r]
        if error_msgs:
            print("   ⚠️ Errores manejados:")
            for error in error_msgs[:2]:
                print(f"      • {error}")
    else:
        print("❌ Error en análisis")
        print(f"   Error: {result.get('message')}")
    
    # Test 4: Test específico de manejo de errores
    print("\n4️⃣ Probando endpoint de manejo de errores...")
    error_test = test_endpoint(f"{base_url}/api/test-error-handling")
    if not error_test.get("error"):
        print("✅ Test de errores completado")
        print(f"   Status: {error_test.get('status')}")
        print(f"   Message: {error_test.get('message')}")
    else:
        print("❌ Error en test")
        print(f"   Error: {error_test.get('message')}")
    
    print("\n" + "=" * 60)
    print("🎯 Pruebas Completadas")
    print("=" * 60)

if __name__ == "__main__":
    main() 