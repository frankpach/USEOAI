#!/usr/bin/env python3
"""
Script para inicializar la base de datos SQLite de USEOAI
"""

import os
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

def init_database():
    """Inicializa la base de datos y crea las tablas"""
    try:
        from config.database import engine, Base
        from models.database_models import Analysis, GeoAnalysis, MapImage
        
        print("🗄️  Inicializando base de datos USEOAI...")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        print("✅ Base de datos inicializada correctamente")
        print("📁 Archivo: useoai.db")
        
        # Verificar que las tablas se crearon
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📊 Tablas creadas: {', '.join(tables)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de tener SQLAlchemy instalado:")
        print("   pip install sqlalchemy")
        return False
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        return False


def check_database():
    """Verifica el estado de la base de datos"""
    try:
        from config.database import engine
        from models.database_models import Analysis, GeoAnalysis, MapImage
        
        print("🔍 Verificando estado de la base de datos...")
        
        # Verificar conexión
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            
            print(f"📋 Tablas encontradas: {', '.join(tables)}")
            
            # Contar registros en cada tabla
            for table in tables:
                if table != 'sqlite_sequence':  # Tabla del sistema
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"   {table}: {count} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar la base de datos: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Inicializar base de datos USEOAI")
    parser.add_argument("--check", action="store_true", help="Solo verificar estado de la DB")
    
    args = parser.parse_args()
    
    if args.check:
        check_database()
    else:
        init_database()
        print("\n" + "="*50)
        check_database() 