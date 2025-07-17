from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.sql import func
from config.database import Base
from datetime import datetime


class Analysis(Base):
    """Modelo para almacenar análisis SEO completos"""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False, index=True)
    seo_goal = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    language = Column(String(10), default="es")

    # Configuración geográfica
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    local_radius_km = Column(Integer, default=10)
    geo_samples = Column(Integer, default=10)

    # Tipo de reporte
    report_type = Column(String(50), default="Web SEO", nullable=False)

    # Estado del análisis
    status = Column(String(20), default="completed")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Puntuaciones
    technical_score = Column(Float, nullable=True)
    onpage_score = Column(Float, nullable=True)
    offpage_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)

    # Datos del análisis (JSON)
    analysis_data = Column(Text, nullable=True)  # JSON serializado con todos los resultados

    # Errores
    error_message = Column(Text, nullable=True)

    keywords = Column(Text, nullable=True)


class GeoAnalysis(Base):
    """Modelo para almacenar análisis geográficos específicos"""
    __tablename__ = "geo_analyses"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, nullable=True)  # Referencia al análisis principal

    # Datos de la empresa
    company_name = Column(String(200), nullable=False)
    keywords = Column(Text, nullable=False)  # JSON array de keywords

    # Configuración geográfica
    location = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    local_radius_km = Column(Integer, nullable=False)
    geo_samples = Column(Integer, nullable=False)

    # Estado
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Resultados
    geo_analysis_data = Column(Text, nullable=True)  # JSON con resultados geográficos

    # Errores
    error_message = Column(Text, nullable=True)


class MapImage(Base):
    """Modelo para almacenar imágenes de mapas generadas"""
    __tablename__ = "map_images"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, nullable=True)
    geo_analysis_id = Column(Integer, nullable=True)

    keyword = Column(String(200), nullable=False)
    image_data = Column(Text, nullable=False)  # Base64 de la imagen
    image_format = Column(String(10), default="png")

    created_at = Column(DateTime, default=func.now())
    file_size = Column(Integer, nullable=True)  # Tamaño en bytes
