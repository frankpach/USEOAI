# Dynamic Performance Analysis Enhancement

## Overview

The `_analyze_performance` method in the SEO Analyzer has been enhanced to support dynamic resource counting using browser-based analysis. This improvement allows for more accurate resource counting on modern websites that load content dynamically via JavaScript.

## Key Features

### 1. Dynamic Resource Counting
- **Browser-based analysis**: Uses the existing browser pool to navigate pages and capture real network requests
- **Comprehensive resource detection**: Captures resources loaded dynamically via JavaScript, including:
  - Scripts loaded asynchronously
  - Images loaded via lazy loading
  - Fonts loaded by CSS
  - API calls (fetch/XHR)
  - Third-party resources and trackers

### 2. Fallback Mechanism
- **Graceful degradation**: Automatically falls back to static HTML analysis when browser is unavailable
- **Error handling**: Robust error handling ensures analysis continues even if browser fails
- **Logging**: Proper logging for debugging and monitoring

### 3. Backward Compatibility
- **API consistency**: All existing return fields are preserved
- **Extended metrics**: New fields are added without breaking existing functionality
- **Default values**: Safe defaults provided for all new fields

## Technical Implementation

### Method Structure

```python
async def _analyze_performance(self, url: str) -> Dict[str, Union[int, bool]]:
    """
    Main method that tries dynamic analysis first, falls back to static analysis
    """
    try:
        return await self._analyze_performance_dynamic(url)
    except Exception as e:
        logger.warning(f"Dynamic analysis failed: {e}, falling back to static analysis")
        return await self._analyze_performance_static(url)
```

### Dynamic Analysis Process

1. **Browser Navigation**: Uses existing browser pool to navigate to the URL
2. **Request Interception**: Sets up network request interception to capture all requests
3. **Resource Categorization**: Processes captured requests and categorizes by type
4. **Performance Metrics**: Calculates TTFB, checks compression, detects lazy loading

### Static Analysis Fallback

- **HTML Parsing**: Parses static HTML to count resources
- **BeautifulSoup**: Uses existing BeautifulSoup parsing for consistency
- **Enhanced Counting**: Improved resource counting logic

## Return Format

### Original Fields (Preserved)
```python
{
    "ttfb_ms": int,           # Time to First Byte in milliseconds
    "resource_count": int,    # Total number of resources
    "gzip_enabled": bool,     # Whether gzip compression is enabled
    "lazy_loaded_images": bool # Whether lazy loading is detected
}
```

### New Fields (Added)
```python
{
    "resource_types": dict,       # Breakdown by resource type
    "scripts_count": int,         # Number of JavaScript files
    "images_count": int,          # Number of images
    "stylesheets_count": int,     # Number of CSS files
    "fonts_count": int,           # Number of font files
    "fetch_requests_count": int,  # Number of fetch/XHR requests
    "total_requests": int         # Total network requests made
}
```

## Usage Examples

### Basic Usage
```python
analyzer = SEOAnalyzer()
result = await analyzer._analyze_performance("https://example.com")

print(f"Total resources: {result['resource_count']}")
print(f"Scripts: {result['scripts_count']}")
print(f"Images: {result['images_count']}")
print(f"API calls: {result['fetch_requests_count']}")
```

### Resource Type Breakdown
```python
for resource_type, count in result['resource_types'].items():
    print(f"{resource_type}: {count}")
```

## Benefits

### For Modern Websites
- **Accurate counting**: Captures resources loaded after initial page load
- **JavaScript-heavy sites**: Properly analyzes SPAs and dynamic content
- **Third-party resources**: Detects external scripts, fonts, and trackers
- **API monitoring**: Tracks background API calls and data fetching

### For SEO Analysis
- **Performance insights**: More accurate resource counting for performance recommendations
- **Optimization guidance**: Better understanding of resource usage patterns
- **Loading analysis**: Realistic assessment of page loading behavior
- **User experience**: Better reflection of actual user experience

## Testing

### Unit Tests
- `test_process_dynamic_requests`: Tests request processing logic
- `test_analyze_performance_static_fallback`: Tests static analysis fallback
- `test_analyze_performance_dynamic_success`: Tests successful dynamic analysis
- `test_analyze_performance_fallback_to_static`: Tests fallback mechanism
- `test_get_default_performance_metrics`: Tests default metrics structure

### Integration Tests
- Comprehensive integration testing with mock browser interactions
- Backward compatibility testing with existing API
- Error handling and fallback testing

## Configuration

The dynamic analysis uses existing configuration from `SEOAnalyzerConfig`:

```python
# Browser configuration
BROWSER_POOL_SIZE: int = 3
BROWSER_TIMEOUT: int = 20000
BROWSER_LAUNCH_ARGS: List[str] = [...]

# Performance optimization
BLOCK_RESOURCE_TYPES: List[str] = ['image', 'media', 'font', 'stylesheet']
```

## Performance Considerations

### Resource Usage
- **Browser pool**: Reuses existing browser pool infrastructure
- **Request interception**: Minimal overhead for request capture
- **Fallback efficiency**: Fast fallback to static analysis when needed

### Memory Management
- **Cleanup**: Proper cleanup of browser pages and resources
- **Error handling**: Graceful handling of browser failures
- **Resource limits**: Respects existing browser pool limits

## Error Handling

### Common Scenarios
- **Browser unavailable**: Falls back to static analysis
- **Network timeouts**: Handled gracefully with retries
- **Page errors**: Continues analysis with available data
- **Resource limits**: Respects browser pool constraints

### Logging
- **Debug information**: Detailed logging for troubleshooting
- **Performance metrics**: Timing information for analysis
- **Error tracking**: Comprehensive error logging

## Future Enhancements

### Potential Improvements
- **Metric caching**: Cache results for repeated analysis
- **Performance profiling**: Add more detailed performance metrics
- **Resource optimization**: Suggest specific resource optimizations
- **Comparative analysis**: Compare before/after optimization

### Browser Alternatives
- **Playwright support**: Add support for modern Playwright library
- **Headless Chrome**: Direct Chrome DevTools Protocol integration
- **Performance APIs**: Use browser Performance APIs for more metrics

## Migration Guide

### For Existing Code
No changes required - all existing code will continue to work as before.

### For New Features
To use the new metrics:

```python
# Old way (still works)
result = await analyzer._analyze_performance(url)
print(f"Resources: {result['resource_count']}")

# New way (additional information)
result = await analyzer._analyze_performance(url)
print(f"Scripts: {result['scripts_count']}")
print(f"Images: {result['images_count']}")
print(f"API calls: {result['fetch_requests_count']}")
```

## Troubleshooting

### Common Issues
1. **Browser fails to start**: Check browser pool configuration
2. **Timeouts**: Adjust `BROWSER_TIMEOUT` setting
3. **Memory issues**: Reduce `BROWSER_POOL_SIZE`
4. **Network issues**: Ensure proper network configuration

### Debug Mode
Enable debug logging for detailed analysis information:

```python
import logging
logging.getLogger('app.services.seo_analyzer').setLevel(logging.DEBUG)
```