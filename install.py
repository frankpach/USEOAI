#!/usr/bin/env python3
"""
Script de instalación automatizada para USEOAI
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def print_step(message):
    """Imprimir un paso de instalación"""
    print(f"\n🔧 {message}")
    print("=" * 50)

def run_command(command, check=True):
    """Ejecutar un comando del sistema"""
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_python_version():
    """Verificar versión de Python"""
    print_step("Verificando versión de Python")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("   Se requiere Python 3.8+")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def create_venv():
    """Crear entorno virtual"""
    print_step("Creando entorno virtual")
    
    if os.path.exists("venv"):
        print("✅ Entorno virtual ya existe")
        return True
    
    success, stdout, stderr = run_command("python -m venv venv")
    if success:
        print("✅ Entorno virtual creado")
        return True
    else:
        print(f"❌ Error creando entorno virtual: {stderr}")
        return False

def activate_venv():
    """Activar entorno virtual"""
    print_step("Activando entorno virtual")
    
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "venv/bin/activate"
    
    if os.path.exists(activate_script):
        print("✅ Entorno virtual activado")
        return True
    else:
        print("❌ No se pudo activar el entorno virtual")
        return False

def install_dependencies():
    """Instalar dependencias"""
    print_step("Instalando dependencias")
    
    # Actualizar pip
    success, stdout, stderr = run_command("python -m pip install --upgrade pip")
    if not success:
        print(f"⚠️  Error actualizando pip: {stderr}")
    
    # Instalar dependencias
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    if success:
        print("✅ Dependencias instaladas")
        return True
    else:
        print(f"❌ Error instalando dependencias: {stderr}")
        return False

def create_env_file():
    """Crear archivo .env"""
    print_step("Creando archivo .env")
    
    if os.path.exists(".env"):
        print("✅ Archivo .env ya existe")
        return True
    
    env_content = """# API Keys (Obligatorio para funcionalidad completa)
GOOGLE_API_KEY=AIzaSyAUjV6Bw9RaLD8bAQ9P5T7nBi3c6r7mxvQ
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
"""
    
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ Archivo .env creado")
        return True
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")
        return False

def install_chromium():
    """Instalar Chromium"""
    print_step("Instalando Chromium")
    
    success, stdout, stderr = run_command("playwright install")
    if success:
        print("✅ Chromium instalado")
        return True
    else:
        print(f"⚠️  Error instalando Chromium: {stderr}")
        print("   Puedes intentar manualmente: playwright install")
        return False

def run_tests():
    """Ejecutar tests básicos"""
    print_step("Ejecutando tests básicos")
    
    success, stdout, stderr = run_command("python -m pytest tests/test_services.py::TestScraper::test_init -v")
    if success:
        print("✅ Tests básicos pasaron")
        return True
    else:
        print(f"⚠️  Tests básicos fallaron: {stderr}")
        return False

def main():
    """Función principal de instalación"""
    print("🚀 Instalador Automatizado - USEOAI")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("requirements.txt"):
        print("❌ No se encontró requirements.txt")
        print("   Asegúrate de estar en el directorio raíz del proyecto")
        return False
    
    steps = [
        ("Verificando versión de Python", check_python_version),
        ("Creando entorno virtual", create_venv),
        ("Activando entorno virtual", activate_venv),
        ("Instalando dependencias", install_dependencies),
        ("Creando archivo .env", create_env_file),
        ("Instalando Chromium", install_chromium),
        ("Ejecutando tests básicos", run_tests),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE INSTALACIÓN")
    print("=" * 60)
    
    if not failed_steps:
        print("🎉 ¡Instalación completada exitosamente!")
        print("\n📝 Próximos pasos:")
        print("1. Edita el archivo .env con tus API keys")
        print("2. Ejecuta: pytest -v tests/")
        print("3. Ejecuta: python main.py")
        print("4. Abre: http://localhost:8000")
        return True
    else:
        print("❌ Instalación incompleta")
        print("\n⚠️  Pasos que fallaron:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\n🔧 Soluciones:")
        print("1. Revisa los errores arriba")
        print("2. Consulta INSTALLATION_GUIDE.md")
        print("3. Ejecuta manualmente los pasos que fallaron")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 