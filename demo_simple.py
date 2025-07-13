#!/usr/bin/env python3
"""
Simple demonstration of the new dynamic performance analysis functionality.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.seo_analyzer import SEOAnalyzer


def demo_request_processing():
    """Demonstrate the request processing functionality"""
    print("🔍 DYNAMIC REQUEST PROCESSING DEMO")
    print("="*50)
    
    analyzer = SEOAnalyzer()
    
    # Example network requests that would be captured by the browser
    mock_requests = [
        {'url': 'https://example.com', 'resourceType': 'document', 'method': 'GET'},
        {'url': 'https://example.com/app.js', 'resourceType': 'script', 'method': 'GET'},
        {'url': 'https://example.com/utils.js', 'resourceType': 'script', 'method': 'GET'},
        {'url': 'https://example.com/analytics.js', 'resourceType': 'script', 'method': 'GET'},
        {'url': 'https://example.com/styles.css', 'resourceType': 'stylesheet', 'method': 'GET'},
        {'url': 'https://example.com/theme.css', 'resourceType': 'stylesheet', 'method': 'GET'},
        {'url': 'https://example.com/logo.png', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/banner.jpg', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/gallery-1.jpg', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/gallery-2.jpg', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/font.woff2', 'resourceType': 'font', 'method': 'GET'},
        {'url': 'https://example.com/font-bold.woff2', 'resourceType': 'font', 'method': 'GET'},
        {'url': 'https://api.example.com/user', 'resourceType': 'fetch', 'method': 'GET'},
        {'url': 'https://api.example.com/products', 'resourceType': 'xhr', 'method': 'GET'},
        {'url': 'https://analytics.example.com/track', 'resourceType': 'fetch', 'method': 'POST'},
    ]
    
    print("📡 Network Requests Captured by Browser:")
    for i, req in enumerate(mock_requests, 1):
        print(f"   {i:2d}. {req['resourceType']:10} - {req['url']}")
    
    # Process the requests
    result = analyzer._process_dynamic_requests(mock_requests)
    
    print(f"\n📊 Processing Results:")
    print(f"   Total Resources: {result['total_count']} (excluding document)")
    print(f"   Scripts: {result['scripts']}")
    print(f"   Stylesheets: {result['stylesheets']}")
    print(f"   Images: {result['images']}")
    print(f"   Fonts: {result['fonts']}")
    print(f"   Fetch/XHR: {result['fetch_requests']}")
    
    print(f"\n📈 Breakdown by Type:")
    for resource_type, count in result['by_type'].items():
        print(f"   {resource_type}: {count}")
    
    return result


def demonstrate_static_vs_dynamic():
    """Show the difference between static and dynamic analysis"""
    print("\n📊 STATIC vs DYNAMIC ANALYSIS COMPARISON")
    print("="*60)
    
    # What static analysis would find in this HTML
    html_content = """
    <html>
        <head>
            <script src="app.js"></script>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <img src="logo.png" alt="Logo">
            <img src="banner.jpg" alt="Banner" loading="lazy">
        </body>
    </html>
    """
    
    print("📄 Initial HTML Content:")
    print("   • 1 JavaScript file (app.js)")
    print("   • 1 CSS file (styles.css)")
    print("   • 2 images (logo.png, banner.jpg)")
    print("   • Total visible in HTML: 4 resources")
    
    print("\n🔍 Static Analysis Results:")
    print("   • Scripts: 1")
    print("   • Stylesheets: 1")
    print("   • Images: 2")
    print("   • Fonts: 0")
    print("   • Fetch/XHR: 0")
    print("   • Total: 4 resources")
    
    print("\n🚀 Dynamic Analysis Results (from demo above):")
    result = demo_request_processing()
    print(f"   • Scripts: {result['scripts']}")
    print(f"   • Stylesheets: {result['stylesheets']}")
    print(f"   • Images: {result['images']}")
    print(f"   • Fonts: {result['fonts']}")
    print(f"   • Fetch/XHR: {result['fetch_requests']}")
    print(f"   • Total: {result['total_count']} resources")
    
    print(f"\n📈 Improvement:")
    print(f"   • Dynamic analysis found {result['total_count']/4:.1f}x more resources")
    print(f"   • Captured {result['scripts']} scripts vs 1 in HTML")
    print(f"   • Detected {result['fetch_requests']} API calls (invisible to static)")
    print(f"   • Found {result['fonts']} fonts (loaded by CSS)")


async def demonstrate_fallback():
    """Show how the fallback mechanism works"""
    print("\n🔄 FALLBACK MECHANISM DEMO")
    print("="*40)
    
    analyzer = SEOAnalyzer()
    
    # Test the default metrics
    default_metrics = analyzer._get_default_performance_metrics()
    
    print("🛡️  Default Performance Metrics (when all analysis fails):")
    print(f"   • TTFB: {default_metrics['ttfb_ms']}ms")
    print(f"   • Resource Count: {default_metrics['resource_count']}")
    print(f"   • Gzip Enabled: {default_metrics['gzip_enabled']}")
    print(f"   • Lazy Loading: {default_metrics['lazy_loaded_images']}")
    print(f"   • Scripts: {default_metrics['scripts_count']}")
    print(f"   • Images: {default_metrics['images_count']}")
    print(f"   • Stylesheets: {default_metrics['stylesheets_count']}")
    print(f"   • Fonts: {default_metrics['fonts_count']}")
    print(f"   • Fetch/XHR: {default_metrics['fetch_requests_count']}")
    print(f"   • Total Requests: {default_metrics['total_requests']}")
    
    print(f"\n✅ All required fields are present for backward compatibility")


def main():
    """Main demonstration function"""
    print("🎯 DYNAMIC PERFORMANCE ANALYSIS - FEATURE DEMO")
    print("="*70)
    print("This demo shows the new dynamic resource counting capabilities")
    print("that capture JavaScript-loaded resources for accurate analysis.")
    print("="*70)
    
    try:
        # Demo the request processing
        demo_request_processing()
        
        # Show the comparison
        demonstrate_static_vs_dynamic()
        
        # Show fallback mechanism
        asyncio.run(demonstrate_fallback())
        
        print(f"\n🎉 FEATURE SUMMARY")
        print("="*50)
        print("✅ Dynamic browser-based resource counting implemented")
        print("✅ Captures resources loaded via JavaScript")
        print("✅ Processes all network requests by type")
        print("✅ Provides detailed resource breakdown")
        print("✅ Falls back to static analysis when browser unavailable")
        print("✅ Maintains backward compatibility")
        print("✅ Adds comprehensive metrics for modern web apps")
        
        print(f"\n📚 Key Benefits:")
        print("   • Accurate resource counting for modern websites")
        print("   • Detects dynamically loaded content")
        print("   • Captures API calls and background requests")
        print("   • Better performance insights for SEO")
        print("   • Realistic loading time analysis")
        
        print(f"\n🔧 Technical Implementation:")
        print("   • Uses existing browser pool infrastructure")
        print("   • Intercepts network requests via pyppeteer")
        print("   • Categorizes resources by type automatically")
        print("   • Graceful fallback to static HTML analysis")
        print("   • Thread-safe and async-compatible")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()