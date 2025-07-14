from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_
from models.database_models import Analysis, GeoAnalysis, MapImage
from models.seo_models import AnalysisRequest, GeoRankRequest
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any


class DatabaseService:
    """Servicio para manejar operaciones de base de datos"""

    def __init__(self, db: Session):
        self.db = db

    # Métodos para Analysis
    def create_analysis(self, request: AnalysisRequest, analysis_result: Dict[str, Any], report_type: str = None) -> Analysis:
        """Crear un nuevo análisis en la base de datos"""
        # Procesar keywords: puede ser None, str o list
        keywords_value = ""
        if request.keywords:
            if isinstance(request.keywords, list):
                keywords_value = ", ".join([k.strip() for k in request.keywords if k and k.strip()])
            elif isinstance(request.keywords, str):
                keywords_value = request.keywords.strip()
        # Determinar el tipo de reporte
        _report_type = report_type or getattr(request, 'report_type', None) or "Web SEO"
        if _report_type is None:
            _report_type = "Web SEO"
        analysis = Analysis(
            url=request.url,
            seo_goal=request.seo_goal,
            location=request.location,
            language=request.language,
            latitude=request.latitude,
            longitude=request.longitude,
            local_radius_km=request.local_radius_km,
            geo_samples=request.geo_samples,
            status="completed",
            completed_at=datetime.utcnow(),
            technical_score=analysis_result.get("technical_score"),
            onpage_score=analysis_result.get("onpage_score"),
            offpage_score=analysis_result.get("offpage_score"),
            overall_score=analysis_result.get("overall_score"),
            analysis_data=json.dumps(analysis_result, ensure_ascii=False, indent=2),
            report_type=_report_type
        )

        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_analysis_by_id(self, analysis_id: int) -> Optional[Analysis]:
        """Obtener análisis por ID"""
        return self.db.query(Analysis).filter(Analysis.id == analysis_id).first()

    def get_all_analyses(self) -> List[Analysis]:
        """Obtener todos los análisis"""
        return self.db.query(Analysis).order_by(desc(Analysis.created_at)).all()

    def get_analyses_by_url(self, url: str, limit: int = 10) -> List[Analysis]:
        """Obtener análisis por URL"""
        return self.db.query(Analysis).filter(
            Analysis.url == url
        ).order_by(desc(Analysis.created_at)).limit(limit).all()

    def get_recent_analyses(self, limit: int = 20) -> List[Analysis]:
        """Obtener análisis recientes"""
        return self.db.query(Analysis).order_by(
            desc(Analysis.created_at)
        ).limit(limit).all()

    def search_analyses(self, query: str, analysis_type: str, date_range: str) -> List[Analysis]:
        """Buscar análisis con filtros"""
        filters = []

        # Filtro por búsqueda
        if query:
            filters.append(
                or_(
                    Analysis.url.contains(query),
                    Analysis.seo_goal.contains(query)
                )
            )

        # Filtro por tipo (comentado porque no existe el campo analysis_type)
        # if analysis_type:
        #     filters.append(Analysis.analysis_type == analysis_type)

        # Filtro por rango de fechas
        if date_range:
            now = datetime.utcnow()
            if date_range == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                filters.append(Analysis.created_at >= start_date)
            elif date_range == "week":
                start_date = now - timedelta(days=7)
                filters.append(Analysis.created_at >= start_date)
            elif date_range == "month":
                start_date = now - timedelta(days=30)
                filters.append(Analysis.created_at >= start_date)
            elif date_range == "quarter":
                start_date = now - timedelta(days=90)
                filters.append(Analysis.created_at >= start_date)

        query_obj = self.db.query(Analysis)
        if filters:
            query_obj = query_obj.filter(and_(*filters))

        return query_obj.order_by(desc(Analysis.created_at)).all()

    def update_analysis_status(self, analysis_id: int, status: str, error_message: str = None):
        """Actualizar estado de un análisis"""
        analysis = self.get_analysis_by_id(analysis_id)
        if analysis:
            analysis.status = status
            if status == "completed":
                analysis.completed_at = datetime.utcnow()
            if error_message:
                analysis.error_message = error_message
            self.db.commit()

    def delete_analysis(self, analysis_id: int) -> bool:
        """Eliminar un análisis"""
        analysis = self.get_analysis_by_id(analysis_id)
        if analysis:
            self.db.delete(analysis)
            self.db.commit()
            return True
        return False

    # Métodos para GeoAnalysis
    def create_geo_analysis(self, request: GeoRankRequest, geo_result: Dict[str, Any],
                          analysis_id: Optional[int] = None) -> GeoAnalysis:
        """Crear un nuevo análisis geográfico"""
        geo_analysis = GeoAnalysis(
            analysis_id=analysis_id,
            company_name=request.company_name,
            keywords=json.dumps(request.keywords, ensure_ascii=False),
            location=request.location,
            latitude=request.latitude,
            longitude=request.longitude,
            local_radius_km=request.local_radius_km,
            geo_samples=request.geo_samples,
            status="completed",
            completed_at=datetime.utcnow(),
            geo_analysis_data=json.dumps(geo_result, ensure_ascii=False, indent=2)
        )

        self.db.add(geo_analysis)
        self.db.commit()
        self.db.refresh(geo_analysis)
        return geo_analysis

    def get_geo_analysis_by_id(self, geo_analysis_id: int) -> Optional[GeoAnalysis]:
        """Obtener análisis geográfico por ID"""
        return self.db.query(GeoAnalysis).filter(GeoAnalysis.id == geo_analysis_id).first()

    def get_geo_analyses_by_company(self, company_name: str, limit: int = 10) -> List[GeoAnalysis]:
        """Obtener análisis geográficos por empresa"""
        return self.db.query(GeoAnalysis).filter(
            GeoAnalysis.company_name == company_name
        ).order_by(desc(GeoAnalysis.created_at)).limit(limit).all()

    # Métodos para MapImage
    def save_map_image(self, image_data: str, keyword: str, analysis_id: Optional[int] = None,
                      geo_analysis_id: Optional[int] = None) -> MapImage:
        """Guardar imagen de mapa"""
        map_image = MapImage(
            analysis_id=analysis_id,
            geo_analysis_id=geo_analysis_id,
            keyword=keyword,
            image_data=image_data,
            image_format="png",
            file_size=len(image_data)
        )

        self.db.add(map_image)
        self.db.commit()
        self.db.refresh(map_image)
        return map_image

    def get_map_images_by_analysis(self, analysis_id: int) -> List[MapImage]:
        """Obtener imágenes de mapa por análisis"""
        return self.db.query(MapImage).filter(
            MapImage.analysis_id == analysis_id
        ).order_by(MapImage.created_at).all()

    def get_map_images_by_geo_analysis(self, geo_analysis_id: int) -> List[MapImage]:
        """Obtener imágenes de mapa por análisis geográfico"""
        return self.db.query(MapImage).filter(
            MapImage.geo_analysis_id == geo_analysis_id
        ).order_by(MapImage.created_at).all()

    # Métodos de estadísticas
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de análisis"""
        total_analyses = self.db.query(Analysis).count()
        completed_analyses = self.db.query(Analysis).filter(Analysis.status == "completed").count()
        failed_analyses = self.db.query(Analysis).filter(Analysis.status == "failed").count()

        total_geo_analyses = self.db.query(GeoAnalysis).count()
        completed_geo_analyses = self.db.query(GeoAnalysis).filter(GeoAnalysis.status == "completed").count()

        total_map_images = self.db.query(MapImage).count()

        return {
            "total_analyses": total_analyses,
            "completed_analyses": completed_analyses,
            "failed_analyses": failed_analyses,
            "total_geo_analyses": total_geo_analyses,
            "completed_geo_analyses": completed_geo_analyses,
            "total_map_images": total_map_images
        }

    def get_analysis_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de análisis (alias para compatibilidad)"""
        return self.get_stats()

    def get_analysis_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Analysis]:
        """Obtener análisis por rango de fechas"""
        return self.db.query(Analysis).filter(
            Analysis.created_at >= start_date,
            Analysis.created_at <= end_date
        ).order_by(desc(Analysis.created_at)).all()

    def get_grouped_reports(self, search: str = None, report_type: str = None, date_range: str = None, offset: int = 0, limit: int = 10):
        """Obtener reportes agrupados por URL, con paginación por grupo (infinite scroll)"""
        query = self.db.query(Analysis)
        if search:
            query = query.filter(Analysis.url.contains(search))
        if report_type:
            query = query.filter(Analysis.report_type == report_type)
        if date_range:
            now = datetime.utcnow()
            if date_range == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(Analysis.created_at >= start_date)
            elif date_range == "week":
                start_date = now - timedelta(days=7)
                query = query.filter(Analysis.created_at >= start_date)
            elif date_range == "month":
                start_date = now - timedelta(days=30)
                query = query.filter(Analysis.created_at >= start_date)
            elif date_range == "quarter":
                start_date = now - timedelta(days=90)
                query = query.filter(Analysis.created_at >= start_date)
        # Agrupar por URL
        from sqlalchemy import func
        grouped = query.with_entities(
            Analysis.url,
            func.count(Analysis.id).label('total_reports'),
            func.max(Analysis.created_at).label('last_report_date'),
            func.max(Analysis.report_type).label('last_report_type')
        ).group_by(Analysis.url)
        total_groups = grouped.count()
        groups = grouped.order_by(func.max(Analysis.created_at).desc()).offset(offset).limit(limit).all()
        return {
            "total_groups": total_groups,
            "groups": [
                {
                    "url": g.url,
                    "total_reports": g.total_reports,
                    "last_report_date": g.last_report_date.isoformat() if g.last_report_date else None,
                    "last_report_type": g.last_report_type
                } for g in groups
            ]
        }

    def get_reports_by_url(self, url: str, page: int = 1, per_page: int = 20):
        """Obtener reportes individuales de una URL, paginados (paginación tradicional)"""
        query = self.db.query(Analysis).filter(Analysis.url == url).order_by(desc(Analysis.created_at))
        total = query.count()
        reports = query.offset((page - 1) * per_page).limit(per_page).all()
        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "reports": [
                {
                    "id": r.id,
                    "report_type": r.report_type,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "status": r.status,
                    "seo_goal": r.seo_goal,
                    "location": r.location,
                    "overall_score": r.overall_score
                } for r in reports
            ]
        }
