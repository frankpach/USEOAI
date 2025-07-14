# 🚀 Guía de Instalación - USEOAI

Esta guía te ayudará a configurar y ejecutar el proyecto USEOAI (SEO Analyzer con IA) en tu entorno local.

## 📋 Requisitos Previos

### Software Necesario
- **Python 3.8+** (recomendado 3.11+)
- **Git** (para clonar el repositorio)
- **Navegador web** (Chrome/Chromium para scraping)

### Sistema Operativo
- ✅ **Windows 10/11**
- ✅ **macOS 10.15+**
- ✅ **Linux** (Ubuntu 18.04+, CentOS 7+)

## 🔧 Instalación Paso a Paso

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd USEOAI_App
```

### 2. Crear Entorno Virtual (Recomendado)

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

#### Opción A: Crear archivo .env
Crea un archivo `.env` en la raíz del proyecto:

```env
# API Keys (Obligatorio para funcionalidad completa)
GOOGLE_API_KEY=tu_api_key_de_gemini
OPENAI_API_KEY=tu_api_key_de_openai
ANTHROPIC_API_KEY=tu_api_key_de_anthropic

# Opcional: Bing Maps API Key
BING_MAPS_API_KEY=tu_bing_maps_api_key

# Configuración del Analizador SEO
SEO_DEFAULT_TIMEOUT=20
SEO_MAX_CONCURRENT_REQUESTS=5
SEO_MAX_LINKS_CHECK=20
SEO_MAX_GEO_POINTS=5
SEO_REQUEST_DELAY=2.0
SEO_BROWSER_POOL_SIZE=3
SEO_TTFB_THRESHOLD_MS=500
SEO_TITLE_MIN_LENGTH=30
SEO_TITLE_MAX_LENGTH=70
SEO_META_DESC_MIN_LENGTH=100
SEO_META_DESC_MAX_LENGTH=160
SEO_RANK_GREEN_THRESHOLD=2.0
SEO_RANK_YELLOW_THRESHOLD=3.0
SEO_HTTP_TIMEOUT=10
SEO_BROWSER_TIMEOUT=20000
SEO_SELECTOR_TIMEOUT=10000
SEO_THREAD_POOL_MAX_WORKERS=10
SEO_MAX_RETRIES=3
SEO_RETRY_DELAY=1.0

# Flags de Funcionalidad
SEO_ENABLE_HTML_CACHE=true
SEO_ENABLE_BROKEN_LINKS_CHECK=true
SEO_ENABLE_PERFORMANCE_CHECK=true
SEO_ENABLE_GOOGLE_MAPS_CHECK=true
SEO_ENABLE_BING_MAPS_CHECK=true

# Configuración de Logging
SEO_LOG_LEVEL=INFO

# User Agents
SEO_ANALYZER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
SEO_GEOCODING_USER_AGENT=SEO Analyzer Geocoding Client
```

#### Opción B: Variables de entorno del sistema
```bash
# Windows
set GOOGLE_API_KEY=AIzaSyAUjV6Bw9RaLD8bAQ9P5T7nBi3c6r7mxvQ

# macOS/Linux
export GOOGLE_API_KEY=AIzaSyAUjV6Bw9RaLD8bAQ9P5T7nBi3c6r7mxvQ
```

### 5. Instalar Chromium (Para Scraping)

El proyecto usa `pyppeteer` que requiere Chromium. La primera vez puede fallar la descarga automática:

```bash
# Instalar Chromium manualmente
playwright install
```

#### Solución de Problemas con Chromium

**Windows:**
```bash
# Si hay problemas de permisos, ejecutar como administrador
# O usar una versión específica
set PYPPETEER_CHROMIUM_REVISION=1095492
playwright install
```

**macOS:**
```bash
# Instalar con Homebrew si hay problemas
brew install chromium
export PYPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
```

**Linux (Ubuntu/Debian):**
```bash
# Instalar dependencias del navegador
sudo apt-get update
sudo apt-get install -y \
    gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 \
    libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 \
    libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 \
    libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 \
    libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation \
    libappindicator1 libnss3 lsb-release xdg-utils wget
```

## 🧪 Verificar la Instalación

### 1. Ejecutar Tests
```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio

# Ejecutar tests
python -m pytest tests/ -v
```

### 2. Probar el Analizador
```bash
# Ejecutar script de prueba
python test_seo_analyzer.py
```

### 3. Iniciar el Servidor
```bash
# Ejecutar la aplicación
python main.py
```

El servidor estará disponible en: `http://localhost:8000`

## 🔑 Configuración de API Keys

### Google Gemini (Incluida)
- ✅ **Ya configurada**: `AIzaSyAUjV6Bw9RaLD8bAQ9P5T7nBi3c6r7mxvQ`

### OpenAI (Opcional)
1. Ve a [OpenAI API](https://platform.openai.com/api-keys)
2. Crea una nueva API key
3. Añádela a tu archivo `.env`:
   ```env
   OPENAI_API_KEY=sk-...
   ```

### Anthropic Claude (Opcional)
1. Ve a [Anthropic Console](https://console.anthropic.com/)
2. Crea una nueva API key
3. Añádela a tu archivo `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### Bing Maps (Opcional)
1. Ve a [Bing Maps Dev Center](https://www.bingmapsportal.com/)
2. Crea una nueva API key
3. Añádela a tu archivo `.env`:
   ```env
   BING_MAPS_API_KEY=...
   ```

## 🚀 Uso Rápido

### 1. Análisis Básico
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
        language="es"
    )
    result = await analyzer.analyze_site(request)
    print(f"Título: {result.title.text}")
    print(f"Recomendaciones: {result.recommendations}")

asyncio.run(analizar_sitio())
```

### 2. API REST
```bash
# Analizar un sitio web
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://ejemplo.com",
    "seo_goal": "Rankear para servicios web",
    "location": "Medellín, Colombia",
    "language": "es"
  }'
```

## 🛠️ Solución de Problemas

### Error: "ModuleNotFoundError"
```bash
# Asegúrate de estar en el directorio correcto
cd USEOAI_App

# Verifica que el entorno virtual esté activado
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

### Error: "Chromium not found"
```bash
# Reinstalar Chromium
playwright install --force

# O usar una versión específica
set PYPPETEER_CHROMIUM_REVISION=1095492
playwright install
```

### Error: "API key not found"
```bash
# Verifica que el archivo .env esté en la raíz del proyecto
# Y que contenga las variables correctas
cat .env
```

### Error: "Permission denied" (Linux/macOS)
```bash
# Dar permisos de ejecución
chmod +x main.py
chmod +x test_seo_analyzer.py
```

### Error: "Port already in use"
```bash
# Cambiar puerto en main.py
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
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
├── requirements.txt       # Dependencias
├── .env                   # Variables de entorno
└── README.md              # Documentación
```

## 🔍 Verificación Final

Después de la instalación, deberías poder:

1. ✅ Ejecutar `python test_seo_analyzer.py` sin errores
2. ✅ Ejecutar `python -m pytest tests/` con tests pasando
3. ✅ Ejecutar `python main.py` e iniciar el servidor
4. ✅ Acceder a `http://localhost:8000` y ver la documentación de la API

## 📞 Soporte

Si encuentras problemas:

1. Verifica que todas las dependencias estén instaladas
2. Asegúrate de que las API keys estén configuradas
3. Revisa los logs para errores específicos
4. Ejecuta los tests para identificar problemas

---

¡Listo! 🎉 Tu proyecto USEOAI está configurado y listo para usar. 