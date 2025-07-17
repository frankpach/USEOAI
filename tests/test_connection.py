#!/usr/bin/env python3
"""
Script de prueba para verificar la comunicación entre frontend y backend
"""

import requests
import json

def test_backend_health():
    """Prueba el endpoint de health del backend"""
    try:
        response = requests.get('http://localhost:8000/')
        print(f"✅ Backend Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Backend Health Check Failed: {e}")
        return False

def test_analyze_endpoint():
    """Prueba el endpoint de análisis con datos de ejemplo"""
    test_data = {
        "url": "https://example.com",
        "seo_goal": "Rank for web development services",
        "location": "Madrid, España",
        "language": "es",
        "local_radius_km": 10,
        "geo_samples": 5
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/analyze',
            json=test_data,
            timeout=30
        )
        print(f"✅ Analyze Endpoint: {response.status_code}")
        if response.status_code == 200:
            print("   Analysis completed successfully!")
        else:
            print(f"   Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Analyze Endpoint Failed: {e}")
        return False

def test_geo_analysis_endpoint():
    """Prueba el endpoint de análisis geográfico"""
    test_data = {
        "company_name": "Test Company",
        "keywords": ["restaurante madrid"],
        "location": "Madrid, España",
        "local_radius_km": 10,
        "geo_samples": 5
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/geo-rank-analysis',
            json=test_data,
            timeout=30
        )
        print(f"✅ Geo Analysis Endpoint: {response.status_code}")
        if response.status_code == 200:
            print("   Geo analysis completed successfully!")
        else:
            print(f"   Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Geo Analysis Endpoint Failed: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("🔍 Testing USEOAI Backend Connection...")
    print("=" * 50)
    
    # Prueba 1: Health Check
    health_ok = test_backend_health()
    
    if not health_ok:
        print("\n❌ Backend is not running. Please start the backend first:")
        print("   python main.py")
        return
    
    print("\n" + "=" * 50)
    
    # Prueba 2: Analyze Endpoint
    analyze_ok = test_analyze_endpoint()
    
    print("\n" + "=" * 50)
    
    # Prueba 3: Geo Analysis Endpoint
    geo_ok = test_geo_analysis_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Analyze Endpoint: {'✅ PASS' if analyze_ok else '❌ FAIL'}")
    print(f"   Geo Analysis Endpoint: {'✅ PASS' if geo_ok else '❌ FAIL'}")
    
    if health_ok and analyze_ok and geo_ok:
        print("\n🎉 All tests passed! Backend is working correctly.")
        print("   Frontend should be able to connect successfully.")
    else:
        print("\n⚠️  Some tests failed. Check the backend configuration.")

if __name__ == "__main__":
    main() 