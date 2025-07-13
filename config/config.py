"""
Configuration settings for SEO Analyzer
"""
import os
from typing import List


class SEOAnalyzerConfig:
    """Configuration constants for SEO Analyzer"""
    
    # Basic configuration
    DEFAULT_TIMEOUT: int = int(os.getenv("SEO_DEFAULT_TIMEOUT", "20"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("SEO_MAX_CONCURRENT_REQUESTS", "5"))
    MAX_LINKS_TO_CHECK: int = int(os.getenv("SEO_MAX_LINKS_CHECK", "20"))
    MAX_GEO_POINTS: int = int(os.getenv("SEO_MAX_GEO_POINTS", "5"))
    REQUEST_DELAY: float = float(os.getenv("SEO_REQUEST_DELAY", "2.0"))
    BROWSER_POOL_SIZE: int = int(os.getenv("SEO_BROWSER_POOL_SIZE", "3"))
    
    # Performance thresholds
    TTFB_THRESHOLD_MS: int = int(os.getenv("SEO_TTFB_THRESHOLD_MS", "500"))
    
    # Content length thresholds
    TITLE_MIN_LENGTH: int = int(os.getenv("SEO_TITLE_MIN_LENGTH", "30"))
    TITLE_MAX_LENGTH: int = int(os.getenv("SEO_TITLE_MAX_LENGTH", "70"))
    META_DESC_MIN_LENGTH: int = int(os.getenv("SEO_META_DESC_MIN_LENGTH", "100"))
    META_DESC_MAX_LENGTH: int = int(os.getenv("SEO_META_DESC_MAX_LENGTH", "160"))
    
    # Ranking thresholds
    RANK_GREEN_THRESHOLD: float = float(os.getenv("SEO_RANK_GREEN_THRESHOLD", "2.0"))
    RANK_YELLOW_THRESHOLD: float = float(os.getenv("SEO_RANK_YELLOW_THRESHOLD", "3.0"))
    
    # User Agent
    DEFAULT_USER_AGENT: str = os.getenv(
        "SEO_ANALYZER_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    
    # Browser configuration
    BROWSER_LAUNCH_ARGS: List[str] = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-field-trial-config',
        '--disable-ipc-flooding-protection',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-background-networking',
        '--disable-default-apps',
        '--disable-sync',
        '--disable-translate',
        '--disable-logging',
        '--disable-permissions-api',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-features=TranslateUI',
        '--disable-features=BlinkGenPropertyTrees',
        '--disable-component-update',
        '--disable-domain-reliability',
        '--disable-dev-shm-usage',
        '--disable-features=AutofillServerCommunication',
        '--disable-features=CertificateTransparencyComponentUpdater',
        '--disable-features=OptimizationHints',
        '--disable-features=Translate',
        '--disable-hang-monitor',
        '--disable-popup-blocking',
        '--disable-prompt-on-repost',
        '--disable-client-side-phishing-detection',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-features=ScriptStreaming',
        '--disable-features=V8VmFuture',
        '--disable-features=VizDisplayCompositor',
    ]
    
    # HTTP configuration
    HTTP_TIMEOUT: int = int(os.getenv("SEO_HTTP_TIMEOUT", "10"))
    
    # Browser specific timeouts
    BROWSER_TIMEOUT: int = int(os.getenv("SEO_BROWSER_TIMEOUT", "20000"))
    SELECTOR_TIMEOUT: int = int(os.getenv("SEO_SELECTOR_TIMEOUT", "10000"))
    
    # External APIs
    BING_MAPS_API_KEY: str = os.getenv("BING_MAPS_API_KEY", "")
    
    # Geocoding configuration
    GEOCODING_USER_AGENT: str = os.getenv(
        "SEO_GEOCODING_USER_AGENT",
        "SEO Analyzer Geocoding Client"
    )
    
    # Threading configuration
    THREAD_POOL_MAX_WORKERS: int = int(os.getenv("SEO_THREAD_POOL_MAX_WORKERS", "10"))
    
    # Feature flags
    ENABLE_HTML_CACHE: bool = os.getenv("SEO_ENABLE_HTML_CACHE", "true").lower() == "true"
    ENABLE_BROKEN_LINKS_CHECK: bool = os.getenv("SEO_ENABLE_BROKEN_LINKS_CHECK", "true").lower() == "true"
    ENABLE_PERFORMANCE_CHECK: bool = os.getenv("SEO_ENABLE_PERFORMANCE_CHECK", "true").lower() == "true"
    ENABLE_GOOGLE_MAPS_CHECK: bool = os.getenv("SEO_ENABLE_GOOGLE_MAPS_CHECK", "true").lower() == "true"
    ENABLE_BING_MAPS_CHECK: bool = os.getenv("SEO_ENABLE_BING_MAPS_CHECK", "true").lower() == "true"
    
    # Log level
    LOG_LEVEL: str = os.getenv("SEO_LOG_LEVEL", "INFO")
    
    # Resource blocking for performance
    BLOCK_RESOURCE_TYPES: List[str] = ['image', 'media', 'font', 'stylesheet']
    
    # Dangerous networks (for SSRF protection)
    DANGEROUS_NETWORKS: List[str] = [
        "127.0.0.0/8",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "169.254.0.0/16",
        "0.0.0.0/8"
    ]
    
    # Business schema types
    BUSINESS_SCHEMA_TYPES: List[str] = [
        "LocalBusiness",
        "Organization",
        "Corporation",
        "EducationalOrganization",
        "GovernmentOrganization",
        "NGO",
        "Restaurant",
        "Store",
        "AutoDealer",
        "Hospital",
        "Hotel",
        "TouristAttraction",
        "Museum",
        "Library",
        "School",
        "University",
        "CollegeOrUniversity",
        "HighSchool",
        "MiddleSchool",
        "ElementarySchool",
        "Preschool",
        "Dentist",
        "Physician",
        "MedicalOrganization",
        "Pharmacy",
        "VeterinaryCare",
        "AnimalShelter",
        "AutomotiveBusiness",
        "FoodEstablishment",
        "FastFoodRestaurant",
        "IceCreamShop",
        "Winery",
        "Brewery",
        "Distillery",
        "EntertainmentBusiness",
        "MovieTheater",
        "ComedyClub",
        "DanceGroup",
        "MusicGroup",
        "TheaterGroup",
        "PerformingGroup",
        "SportsOrganization",
        "SportsTeam",
        "HealthAndBeautyBusiness",
        "BeautySalon",
        "DaySpa",
        "HairSalon",
        "HealthClub",
        "NailSalon",
        "TattooParlor",
        "HomeAndConstructionBusiness",
        "Electrician",
        "GeneralContractor",
        "HVACBusiness",
        "Locksmith",
        "MovingCompany",
        "Plumber",
        "RoofingContractor",
        "ProfessionalService",
        "AccountingService",
        "Attorney",
        "Notary",
        "RealEstateAgent",
        "TaxService",
        "FinancialService",
        "BankOrCreditUnion",
        "InsuranceAgency",
        "LodgingBusiness",
        "BedAndBreakfast",
        "Campground",
        "Hostel",
        "Motel",
        "Resort",
        "SelfStorage",
        "TravelAgency",
        "EmergencyService",
        "FireStation",
        "Hospital",
        "PoliceStation",
        "RadioStation",
        "TelevisionStation",
        "GovernmentOffice",
        "PostOffice",
        "CivicStructure",
        "Airport",
        "Aquarium",
        "Beach",
        "BusStation",
        "BusStop",
        "Campground",
        "Cemetery",
        "Crematorium",
        "EventVenue",
        "FireStation",
        "GovernmentBuilding",
        "Hospital",
        "MovieTheater",
        "Museum",
        "MusicVenue",
        "Park",
        "ParkingFacility",
        "PerformingArtsTheater",
        "PlaceOfWorship",
        "Playground",
        "PoliceStation",
        "PublicSwimmingPool",
        "RVPark",
        "StadiumOrArena",
        "SubwayStation",
        "TaxiStand",
        "TrainStation",
        "Zoo"
    ]
    
    # Google Maps selectors
    GOOGLE_MAPS_SELECTORS: dict = {
        'feed': 'div[role="feed"]',
        'result_item': 'div[role="feed"] > div',
        'result_link': 'a[href*="maps/place"]',
        'result_title': 'div[class*="fontHeadlineSmall"]',
        'page_title': 'h1[data-attrid="title"]',
        'verified_badge': 'img[src*="verified"]',
        'address': 'button[data-item-id="address"]',
        'phone': 'button[data-item-id="phone"]'
    }
    
    # Bing Maps selectors
    BING_MAPS_SELECTORS: dict = {
        'results': '.listViewCard',
        'result_title': '.b_dataList h2',
        'result_link': '.listViewCard a'
    }
    
    # Address extraction configuration
    MIN_ADDRESS_LENGTH: int = 20
    MAX_ADDRESS_LENGTH: int = 300
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance of config"""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
    
    # Geocoding configuration
    GEOCODING_USER_AGENT: str = os.getenv("SEO_GEOCODING_USER_AGENT", "seo-analyzer")
    
    # Thread pool configuration
    THREAD_POOL_MAX_WORKERS: int = int(os.getenv("SEO_THREAD_POOL_MAX_WORKERS", "4"))
    
    # Cache configuration
    ENABLE_HTML_CACHE: bool = os.getenv("SEO_ENABLE_HTML_CACHE", "true").lower() == "true"
    MAX_CACHE_SIZE: int = int(os.getenv("SEO_MAX_CACHE_SIZE", "100"))
    
    # Network timeouts
    HTTP_TIMEOUT: int = int(os.getenv("SEO_HTTP_TIMEOUT", "10"))
    BROWSER_TIMEOUT: int = int(os.getenv("SEO_BROWSER_TIMEOUT", "20000"))
    SELECTOR_TIMEOUT: int = int(os.getenv("SEO_SELECTOR_TIMEOUT", "10000"))
    
    # Safety configuration
    DANGEROUS_NETWORKS: List[str] = [
        '169.254.169.254/32',  # AWS/GCP/Azure metadata service
        '127.0.0.0/8',         # Loopback
        '10.0.0.0/8',          # Private class A
        '172.16.0.0/12',       # Private class B
        '192.168.0.0/16',      # Private class C
        '169.254.0.0/16',      # Link-local
        '::1/128',             # IPv6 loopback
        'fc00::/7',            # IPv6 private
        'fe80::/10',           # IPv6 link-local
    ]
    
    # API Keys (optional)
    BING_MAPS_API_KEY: str = os.getenv("BING_MAPS_API_KEY", "")
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("SEO_LOG_LEVEL", "INFO")
    
    # Performance optimization
    BLOCK_RESOURCE_TYPES: List[str] = ['image', 'media', 'font', 'stylesheet']
    
    # Address extraction patterns
    ADDRESS_PATTERNS: List[str] = [
        r'\b(calle|carrera|avenida|av|cra|cll|street|st|avenue|ave|road|rd|boulevard|blvd)\b',
        r'\b\d{5}(?:[-\s]\d{4})?\b',  # Postal codes
        r'\w+,\s*\w{2,}',  # City, state patterns
        r'\d+\s+\w+(?:\s+\w+){1,3}',  # Number with street
    ]
    
    # Phone number patterns
    PHONE_PATTERNS: List[str] = [
        r'\+\d{1,3}\s?[\d\s-]{7,15}',  # International format
        r'\(\d{3}\)\s?\d{3}-\d{4}',     # US format (123) 456-7890
        r'\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4}',  # 123-456-7890
        r'\d{2}[-\.\s]?\d{2}[-\.\s]?\d{2}[-\.\s]?\d{2}[-\.\s]?\d{2}'  # European formats
    ]
    
    # Address normalization replacements
    ADDRESS_REPLACEMENTS: List[tuple] = [
        ('street', 'st'), ('avenue', 'ave'), ('boulevard', 'blvd'),
        ('road', 'rd'), ('drive', 'dr'), ('lane', 'ln'),
        ('suite', 'ste'), ('apartment', 'apt'), ('building', 'bldg'),
        ('calle', 'c'), ('avenida', 'av'), ('carrera', 'cra'),
    ]
    
    # Schema.org business types
    BUSINESS_SCHEMA_TYPES: List[str] = [
        'LocalBusiness', 'Organization', 'Restaurant', 'Store',
        'Corporation', 'EducationalOrganization', 'GovernmentOrganization',
        'NGO', 'SportsOrganization'
    ]
    
    # CSS selectors for maps
    GOOGLE_MAPS_SELECTORS: dict = {
        'feed': 'div[role="feed"]',
        'results': 'div[role="feed"] a[href*="maps/place"]',
        'title': 'div[class*="fontHeadlineSmall"]',
        'page_title': 'h1[data-attrid="title"]',
        'verified': 'img[src*="verified"]',
        'address': 'button[data-item-id="address"]',
        'phone': 'button[data-item-id="phone"]',
    }
    
    BING_MAPS_SELECTORS: dict = {
        'results': '.listViewCard',
        'title': '.b_dataList h2',
        'link': 'a',
    }
    
    # Validation settings
    MIN_BUSINESS_NAME_LENGTH: int = 1
    MAX_BUSINESS_NAME_LENGTH: int = 200
    MIN_ADDRESS_LENGTH: int = 10
    MAX_ADDRESS_LENGTH: int = 200
    MIN_PHONE_LENGTH: int = 7
    MAX_PHONE_LENGTH: int = 20
    
    # Retry settings
    MAX_RETRIES: int = int(os.getenv("SEO_MAX_RETRIES", "3"))
    RETRY_DELAY: float = float(os.getenv("SEO_RETRY_DELAY", "1.0"))
    
    # Feature flags
    ENABLE_GOOGLE_MAPS_CHECK: bool = os.getenv("SEO_ENABLE_GOOGLE_MAPS", "true").lower() == "true"
    ENABLE_BING_MAPS_CHECK: bool = os.getenv("SEO_ENABLE_BING_MAPS", "true").lower() == "true"
    ENABLE_PERFORMANCE_CHECK: bool = os.getenv("SEO_ENABLE_PERFORMANCE", "true").lower() == "true"
    ENABLE_BROKEN_LINKS_CHECK: bool = os.getenv("SEO_ENABLE_BROKEN_LINKS", "true").lower() == "true"
    
    @classmethod
    def get_instance(cls) -> 'SEOAnalyzerConfig':
        """Get singleton instance of configuration"""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance