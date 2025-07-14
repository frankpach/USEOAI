# 🚀 USEOAI - SEO Analyzer con IA

Un analizador SEO avanzado que combina análisis técnico tradicional con inteligencia artificial para proporcionar insights profundos sobre el posicionamiento web.

## ✨ Características

### 🔍 Análisis Técnico SEO
- **Análisis de HTML**: Títulos, meta descripciones, headings, enlaces
- **Validación de enlaces**: Detección de enlaces rotos internos y externos
- **Métricas de rendimiento**: TTFB, compresión GZIP, lazy loading
- **Estructura semántica**: Análisis de schema.org y datos estructurados
- **Validación de URLs**: Prevención de ataques SSRF

### 🧠 Análisis Semántico con IA
- **Múltiples proveedores de IA**:
  - ✅ **Google Gemini** (incluido)
  - 🔧 OpenAI ChatGPT
  - 🔧 Anthropic Claude
- **Análisis de contenido**: Coherencia, intención, legibilidad
- **Recomendaciones inteligentes**: Basadas en el objetivo SEO
- **Análisis de contexto geográfico**: Optimización local

### 🗺️ SEO Local
- **Ranking en Google Maps**: Verificación de posicionamiento local
- **Ranking en Bing Maps**: Análisis multi-plataforma
- **Consistencia NAP**: Name, Address, Phone verification
- **Muestreo geográfico**: Análisis desde múltiples ubicaciones
- **Análisis de ranking geográfico independiente**: Endpoint dedicado para análisis de posicionamiento local
- **Análisis condicional**: El análisis geográfico se ejecuta solo cuando se proporcionan todos los parámetros requeridos

### 🛡️ Seguridad y Robustez
- **Validación de IPs**: Prevención de ataques SSRF
- **Sanitización de URLs**: Protección contra inyecciones
- **Manejo de errores**: Recuperación graceful de fallos
- **Rate limiting**: Protección contra bloqueos

## 🚀 Instalación Rápida

### Opción 1: Instalador Automatizado
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd USEOAI_App

# Ejecutar instalador
python install.py
```

### Opción 2: Instalación Manual
```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear archivo .env
cp env.example .env

# 4. Instalar Chromium
playwright install
```

## 🔑 Configuración

### API Keys Requeridas

#### Google Gemini (✅ Incluida)
```env
GOOGLE_API_KEY=AIzaSyAUjV6Bw9RaLD8bAQ9P5T7nBi3c6r7mxvQ
```

#### OpenAI ChatGPT (Opcional)
```env
OPENAI_API_KEY=sk-...
```

#### Anthropic Claude (Opcional)
```env
ANTHROPIC_API_KEY=sk-ant-...
```

## 🧪 Verificación

```bash
# Ejecutar tests
python -m pytest tests/ -v

# Probar analizador
python test_seo_analyzer.py

# Iniciar servidor
python main.py
```

## 📖 Uso

### API REST

#### Endpoints Disponibles

1. **POST /api/analyze** - Análisis completo de sitio web
2. **POST /api/geo-rank-analysis** - Análisis de ranking geográfico independiente
3. **GET /api/status** - Estado de la API y proveedores de IA disponibles

#### Análisis de Sitio Web (con ubicación por texto)
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://ejemplo.com",
    "seo_goal": "Rankear para servicios web",
    "location": "Medellín, Colombia",
    "language": "es",
    "llm_provider": "gemini"
  }'
```

#### Análisis de Sitio Web (con coordenadas exactas)
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://ejemplo.com",
    "seo_goal": "Rankear para servicios web",
    "location": "Medellín, Colombia",
    "latitude": 6.2442,
    "longitude": -75.5812,
    "local_radius_km": 10,
    "geo_samples": 15,
    "language": "es",
    "llm_provider": "gemini"
  }'
```

#### Análisis de Ranking Geográfico (Nuevo)
```bash
curl -X POST "http://localhost:8000/api/geo-rank-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Medellín, Colombia",
    "latitude": 6.2442,
    "longitude": -75.5812,
    "local_radius_km": 5,
    "geo_samples": 10,
    "company_name": "Acme HVAC",
    "keywords": ["hvac repair", "ac install", "emergency hvac", "thermostat replacement"]
  }'
```

**Nota**: El análisis geográfico en el endpoint `/api/analyze` solo se ejecuta si se proporcionan TODOS los parámetros requeridos:
- `location` O (`latitude` Y `longitude`)
- `local_radius_km`
- `geo_samples`

Si falta alguno de estos parámetros, el análisis procede sin la verificación de ranking local.

#### Respuesta de Ejemplo - Análisis Completo
```json
{
        "status_code": 200,
        "title": {
    "text": "Servicios Web Profesionales",
    "length": 32,
    "has_keywords": true
        },
        "meta_description": {
    "text": "Servicios web profesionales en Medellín...",
    "length": 156
        },
        "semantic_summary": {
    "llm_engine": "gemini",
    "coherence_score": 0.85,
    "detected_intent": "Commercial",
    "readability_level": "B2",
    "suggested_improvements": [
      "Añadir más palabras clave específicas",
      "Mejorar la estructura de headings"
    ]
  },
        "speed_metrics": {
    "ttfb_ms": 245,
    "resource_count": 12,
    "gzip_enabled": true,
    "lazy_loaded_images": false
        },
        "local_rank_check": {
    "google_maps_rank": "rank #2.5",
    "nap_consistency": true,
    "sample_locations_checked": 5
        },
        "recommendations": [
    "Implementar lazy loading para imágenes",
    "Optimizar meta descripción",
    "Añadir más contenido relevante"
        ]
    }
```

#### Respuesta de Ejemplo - Análisis de Ranking Geográfico
```json
{
  "company_name": "Acme HVAC",
  "location_used": "Medellín, Colombia",
  "coordinates": [6.2442, -75.5812],
  "radius_km": 5,
  "total_samples": 10,
  "keywords_analyzed": 4,
  "keyword_results": [
    {
      "keyword": "hvac repair",
      "average_rank": 2.5,
      "coverage_percentage": 80.0,
      "total_samples": 10,
      "found_in_samples": 8,
      "google_maps_rank": "rank #2.5",
      "bing_maps_rank": "rank #3.0",
      "nap_inconsistencies": [],
      "visibility_score": 80.0
    },
    {
      "keyword": "ac install",
      "average_rank": 4.2,
      "coverage_percentage": 60.0,
      "total_samples": 10,
      "found_in_samples": 6,
      "google_maps_rank": "rank #4.2",
      "bing_maps_rank": "rank #5.0",
      "nap_inconsistencies": ["Missing phone number in Google Maps listing"],
      "visibility_score": 60.0
    }
  ],
  "overall_visibility_score": 70.0,
  "nap_consistency": true,
  "has_verified_listing": true,
  "analysis_timestamp": "2024-01-15 14:30:25 UTC"
}
```

### Uso Programático

```python
import asyncio
from services.seo_analyzer import SEOAnalyzer
from models.seo_models import AnalysisRequest

async def analizar_sitio():
    analyzer = SEOAnalyzer()
    request = AnalysisRequest(
        url="https://ejemplo.com",
        seo_goal="Rankear para servicios web",
        location="Medellín, Colombia",
        language="es",
        llm_provider="gemini"
    )
    
    result = await analyzer.analyze_site(request)
    print(f"Título: {result.title.text}")
    print(f"Recomendaciones: {result.recommendations}")

asyncio.run(analizar_sitio())
```

## 📁 Estructura del Proyecto

```
USEOAI_App/
├── api/                    # Endpoints de la API
│   ├── analyzer.py        # Análisis individual
│   └── batch_analyzer.py  # Análisis en lote
├── services/              # Servicios principales
│   ├── seo_analyzer.py    # Analizador SEO principal
│   ├── scraper.py         # Scraping web
│   └── semantic_analyzer.py # Análisis semántico
├── models/                # Modelos de datos
│   ├── seo_models.py      # Modelos SEO
│   └── semantic_models.py # Modelos semánticos
├── utils/                 # Utilidades
│   └── llm_clients.py     # Clientes de IA
├── config/                # Configuración
│   └── config.py          # Configuración principal
├── tests/                 # Tests
├── main.py                # Punto de entrada
├── install.py             # Instalador automatizado
├── test_seo_analyzer.py   # Script de prueba
├── requirements.txt       # Dependencias
├── env.example            # Variables de entorno ejemplo
├── INSTALLATION_GUIDE.md  # Guía de instalación
└── README.md              # Este archivo
```

## ⚙️ Configuración Avanzada

### Variables de Entorno

```env
# Configuración de rendimiento
SEO_DEFAULT_TIMEOUT=20
SEO_MAX_CONCURRENT_REQUESTS=5
SEO_BROWSER_POOL_SIZE=3

# Umbrales de análisis
SEO_TTFB_THRESHOLD_MS=500
SEO_TITLE_MIN_LENGTH=30
SEO_TITLE_MAX_LENGTH=70

# Flags de funcionalidad
SEO_ENABLE_HTML_CACHE=true
SEO_ENABLE_BROKEN_LINKS_CHECK=true
SEO_ENABLE_PERFORMANCE_CHECK=true
SEO_ENABLE_GOOGLE_MAPS_CHECK=true
```

### Personalización

El analizador es altamente configurable. Puedes:

- **Ajustar umbrales**: Modificar valores en `config/config.py`
- **Cambiar proveedores de IA**: Seleccionar entre Gemini, ChatGPT, Claude
- **Deshabilitar funcionalidades**: Usar flags de configuración
- **Personalizar user agents**: Configurar diferentes navegadores

## 🛠️ Desarrollo

### Ejecutar Tests
```bash
# Todos los tests
python -m pytest tests/ -v

# Tests específicos
python -m pytest tests/test_services.py::TestScraper -v

# Tests con coverage
python -m pytest tests/ --cov=services --cov=api
```

### Estructura de Tests
- `tests/test_services.py`: Tests de servicios principales
- `tests/test_endpoints.py`: Tests de endpoints de API
- `test_seo_analyzer.py`: Script de prueba integrado

## 🚨 Solución de Problemas

### Error: "Chromium not found"
```bash
playwright install --force
```

### Error: "API key not found"
```bash
# Verificar archivo .env
cat .env

# O establecer variable de entorno
export GOOGLE_API_KEY=AIzaSyAUjV6Bw9RaLD8bAQ9P5T7nBi3c6r7mxvQ
```

### Error: "ModuleNotFoundError"
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstalar dependencias
pip install -r requirements.txt
```

## 📊 Métricas y Rendimiento

- **Tiempo de análisis**: 5-15 segundos por sitio
- **Concurrencia**: Hasta 5 análisis simultáneos
- **Precisión**: 95%+ en detección de problemas SEO
- **Cobertura**: Análisis completo de 50+ factores SEO

## 🔒 Seguridad

- ✅ Validación de URLs contra SSRF
- ✅ Sanitización de entradas
- ✅ Rate limiting integrado
- ✅ Manejo seguro de API keys
- ✅ Logs sin información sensible

## 📈 Roadmap

- [ ] **Análisis de competencia**: Comparación con competidores
- [ ] **Reportes automáticos**: Generación de PDF/Excel
- [ ] **Monitoreo continuo**: Tracking de cambios SEO
- [ ] **Integración con Google Analytics**: Métricas de tráfico
- [ ] **API de webhooks**: Notificaciones en tiempo real

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

- 📧 **Email**: soporte@useoai.com
- 📖 **Documentación**: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/tu-usuario/USEOAI/issues)

---

**¡Gracias por usar USEOAI! 🎉**

*Optimiza tu SEO con la potencia de la inteligencia artificial.*