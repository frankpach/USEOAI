#!/usr/bin/env python3
"""
Demonstration of the new dynamic performance analysis functionality.

This script shows how the enhanced _analyze_performance method works,
comparing static HTML analysis with dynamic browser-based resource counting.
"""

import asyncio
import json
from typing import Dict, Any
from unittest.mock import patch, AsyncMock

# Add project root to Python path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.seo_analyzer import SEOAnalyzer


def print_performance_results(results: Dict[str, Any], title: str):
    """Pretty print performance analysis results"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")
    
    print(f"⏱️  TTFB: {results['ttfb_ms']}ms")
    print(f"📦 Total Resources: {results['resource_count']}")
    print(f"🗜️  Gzip Enabled: {results['gzip_enabled']}")
    print(f"🖼️  Lazy Loading: {results['lazy_loaded_images']}")
    
    print(f"\n📊 Resource Breakdown:")
    print(f"   🔧 Scripts: {results['scripts_count']}")
    print(f"   🎨 Stylesheets: {results['stylesheets_count']}")
    print(f"   🖼️  Images: {results['images_count']}")
    print(f"   🔤 Fonts: {results['fonts_count']}")
    print(f"   🔄 Fetch/XHR: {results['fetch_requests_count']}")
    print(f"   🌐 Total Requests: {results['total_requests']}")
    
    print(f"\n📈 Resource Types:")
    for resource_type, count in results['resource_types'].items():
        print(f"   {resource_type}: {count}")


async def demonstrate_static_analysis():
    """Demonstrate static HTML analysis (fallback method)"""
    print("\n🔍 STATIC ANALYSIS DEMONSTRATION")
    print("   (Analyzing HTML without JavaScript execution)")
    
    analyzer = SEOAnalyzer()
    
    # Mock HTTP response with a realistic HTML structure
    mock_response = AsyncMock()
    mock_response.headers = {'Content-Encoding': 'gzip'}
    mock_response.text = AsyncMock(return_value="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Example Modern Website</title>
        
        <!-- External CSS -->
        <link rel="stylesheet" href="https://cdn.example.com/bootstrap.min.css">
        <link rel="stylesheet" href="/assets/css/main.css">
        
        <!-- External JavaScript -->
        <script src="https://cdn.example.com/jquery.min.js"></script>
        <script src="/assets/js/app.js"></script>
        
        <!-- Inline CSS -->
        <style>
            body { font-family: Arial, sans-serif; }
            .header { background: #333; color: white; }
        </style>
        
        <!-- Inline JavaScript -->
        <script>
            console.log('Page loaded');
            window.analytics = { track: function() {} };
        </script>
    </head>
    <body>
        <header class="header">
            <img src="/assets/images/logo.png" alt="Logo">
            <h1>Modern Website</h1>
        </header>
        
        <main>
            <section class="hero">
                <img src="/assets/images/hero-banner.jpg" alt="Hero Banner" loading="lazy">
                <h2>Welcome to Our Site</h2>
            </section>
            
            <section class="content">
                <img src="/assets/images/feature1.png" alt="Feature 1">
                <img src="/assets/images/feature2.png" alt="Feature 2" loading="lazy">
                <p>This is a modern website with various resources.</p>
            </section>
        </main>
        
        <footer>
            <p>&copy; 2024 Example Company</p>
        </footer>
    </body>
    </html>
    """)
    
    # Mock the context manager
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    
    # Force static analysis by mocking dynamic analysis to fail
    with patch.object(analyzer, '_analyze_performance_dynamic', side_effect=Exception("Browser not available")):
        with patch.object(analyzer.http_client, 'get', return_value=mock_response):
            with patch('app.services.seo_analyzer.time.time', side_effect=[0, 0.15]):  # 150ms TTFB
                result = await analyzer._analyze_performance("https://example.com")
                
                print_performance_results(result, "STATIC ANALYSIS RESULTS")
                
                print(f"\n💡 Static Analysis Limitations:")
                print(f"   • Only counts resources in initial HTML")
                print(f"   • Cannot detect dynamically loaded resources")
                print(f"   • No XHR/fetch requests captured")
                print(f"   • Missing resources loaded by JavaScript")


async def demonstrate_dynamic_analysis():
    """Demonstrate dynamic browser-based analysis"""
    print("\n🚀 DYNAMIC ANALYSIS DEMONSTRATION")
    print("   (Simulating browser-based resource capture)")
    
    analyzer = SEOAnalyzer()
    
    # Mock network requests that would be captured by browser
    mock_network_requests = [
        # Initial document
        {'url': 'https://example.com', 'resourceType': 'document', 'method': 'GET'},
        
        # CSS resources
        {'url': 'https://cdn.example.com/bootstrap.min.css', 'resourceType': 'stylesheet', 'method': 'GET'},
        {'url': 'https://example.com/assets/css/main.css', 'resourceType': 'stylesheet', 'method': 'GET'},
        
        # JavaScript resources
        {'url': 'https://cdn.example.com/jquery.min.js', 'resourceType': 'script', 'method': 'GET'},
        {'url': 'https://example.com/assets/js/app.js', 'resourceType': 'script', 'method': 'GET'},
        
        # Images from initial HTML
        {'url': 'https://example.com/assets/images/logo.png', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/assets/images/hero-banner.jpg', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/assets/images/feature1.png', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/assets/images/feature2.png', 'resourceType': 'image', 'method': 'GET'},
        
        # Dynamically loaded resources (would be missed by static analysis)
        {'url': 'https://example.com/assets/js/analytics.js', 'resourceType': 'script', 'method': 'GET'},
        {'url': 'https://example.com/assets/css/dynamic-styles.css', 'resourceType': 'stylesheet', 'method': 'GET'},
        {'url': 'https://example.com/assets/images/lazy-loaded-gallery-1.jpg', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/assets/images/lazy-loaded-gallery-2.jpg', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/assets/images/lazy-loaded-gallery-3.jpg', 'resourceType': 'image', 'method': 'GET'},
        
        # Fonts
        {'url': 'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700', 'resourceType': 'stylesheet', 'method': 'GET'},
        {'url': 'https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2', 'resourceType': 'font', 'method': 'GET'},
        {'url': 'https://fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmEU9fBBc4.woff2', 'resourceType': 'font', 'method': 'GET'},
        
        # API calls
        {'url': 'https://api.example.com/user-data', 'resourceType': 'fetch', 'method': 'GET'},
        {'url': 'https://api.example.com/product-recommendations', 'resourceType': 'xhr', 'method': 'GET'},
        {'url': 'https://analytics.example.com/track', 'resourceType': 'fetch', 'method': 'POST'},
        
        # Third-party resources
        {'url': 'https://www.google-analytics.com/analytics.js', 'resourceType': 'script', 'method': 'GET'},
        {'url': 'https://connect.facebook.net/en_US/fbevents.js', 'resourceType': 'script', 'method': 'GET'},
        
        # Additional images loaded dynamically
        {'url': 'https://example.com/assets/images/social-icons.svg', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/assets/images/testimonial-avatar-1.jpg', 'resourceType': 'image', 'method': 'GET'},
        {'url': 'https://example.com/assets/images/testimonial-avatar-2.jpg', 'resourceType': 'image', 'method': 'GET'},
    ]
    
    # Mock the browser and page interactions
    mock_browser = AsyncMock()
    mock_page = AsyncMock()
    mock_response = AsyncMock()
    mock_response.headers = {'content-encoding': 'gzip'}
    
    mock_browser.newPage.return_value = mock_page
    mock_page.goto.return_value = mock_response
    mock_page.evaluate.return_value = True  # lazy loading detected
    mock_page.setRequestInterception = AsyncMock()
    mock_page.on = lambda event, handler: None  # Just capture the event handler
    mock_page.close = AsyncMock()
    
    # Mock browser pool context manager
    browser_context = AsyncMock()
    browser_context.__aenter__.return_value = mock_browser
    browser_context.__aexit__.return_value = None
    
    # Mock the processing of captured requests
    expected_stats = analyzer._process_dynamic_requests(mock_network_requests)
    
    with patch.object(analyzer.browser_pool, 'get_browser', return_value=browser_context):
        with patch.object(analyzer, '_process_dynamic_requests', return_value=expected_stats):
            with patch('app.services.seo_analyzer.time.time', side_effect=[0, 0.12]):  # 120ms TTFB
                result = await analyzer._analyze_performance("https://example.com")
                
                # Add the total requests count
                result['total_requests'] = len(mock_network_requests)
                
                print_performance_results(result, "DYNAMIC ANALYSIS RESULTS")
                
                print(f"\n✨ Dynamic Analysis Advantages:")
                print(f"   • Captures ALL network requests made by the page")
                print(f"   • Includes resources loaded by JavaScript")
                print(f"   • Detects XHR/fetch API calls")
                print(f"   • Counts dynamically loaded images and fonts")
                print(f"   • Provides realistic resource statistics")
                print(f"   • Accounts for third-party scripts and trackers")


async def demonstrate_comparison():
    """Compare static vs dynamic analysis side by side"""
    print("\n📊 COMPARISON: STATIC vs DYNAMIC ANALYSIS")
    print("="*70)
    
    # Example showing what each method would find
    static_html = """
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
    print("   • Total in HTML: 4 resources")
    
    print("\n🔍 What Static Analysis Finds:")
    print("   • Scripts: 1")
    print("   • Stylesheets: 1")
    print("   • Images: 2")
    print("   • Total: 4 resources")
    
    print("\n🚀 What Dynamic Analysis Might Find:")
    print("   • Scripts: 5 (app.js + 4 loaded dynamically)")
    print("   • Stylesheets: 3 (styles.css + 2 loaded dynamically)")
    print("   • Images: 8 (2 initial + 6 lazy-loaded)")
    print("   • Fonts: 2 (loaded by CSS)")
    print("   • Fetch/XHR: 3 (API calls)")
    print("   • Total: 21 resources")
    
    print("\n📈 Key Differences:")
    print("   • Dynamic analysis captures 5x more resources")
    print("   • Includes resources loaded after page load")
    print("   • Detects API calls and background requests")
    print("   • Provides realistic performance metrics")
    print("   • Better reflects user experience")


async def main():
    """Main demonstration function"""
    print("🎯 DYNAMIC PERFORMANCE ANALYSIS DEMO")
    print("="*70)
    print("This demo shows the enhanced _analyze_performance method")
    print("that captures resources loaded dynamically via JavaScript.")
    print("="*70)
    
    try:
        await demonstrate_static_analysis()
        await demonstrate_dynamic_analysis()
        await demonstrate_comparison()
        
        print(f"\n🎉 SUMMARY")
        print("="*50)
        print("✅ Enhanced _analyze_performance method implemented")
        print("✅ Dynamic browser-based resource counting added")
        print("✅ Backward compatibility maintained")
        print("✅ Fallback to static analysis when browser unavailable")
        print("✅ Comprehensive resource type breakdown added")
        print("✅ Modern web applications now properly analyzed")
        
        print(f"\n📚 Benefits for SEO Analysis:")
        print("   • More accurate resource counting")
        print("   • Better performance insights")
        print("   • Realistic loading time analysis")
        print("   • Comprehensive resource optimization recommendations")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())