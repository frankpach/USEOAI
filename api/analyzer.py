from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Body
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from models.seo_models import AnalysisRequest, AnalysisResponse, GeoRankRequest, GeoRankResponse, KeywordUsageResponse, KeywordUsageResult
from services.seo_analyzer import SEOAnalyzer
from services.database_service import DatabaseService
from config.database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api",
    tags=["SEO Analysis"],
    responses={404: {"description": "Not found"}}
)

# Initialize SEO analyzer
seo_analyzer = SEOAnalyzer()


@router.post("/analyze")
async def analyze_site(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyze a website for SEO factors based on provided URL and parameters.

    This endpoint performs:
    - Technical SEO analysis
    - HTML structure analysis
    - Link analysis
    - Semantic content analysis using LLMs
    - Speed metrics calculation
    - Local SEO ranking check

    Parameters:
    - url: Website URL to analyze
    - seo_goal: SEO objective (e.g., "Rank for web development services")
    - location: Location string (e.g., "Medellín, Colombia")
    - latitude: Optional exact latitude coordinate (for precise location targeting)
    - longitude: Optional exact longitude coordinate (for precise location targeting)
    - language: Content language (default: "es")
    - local_radius_km: Radius in km for local SEO analysis (default: 5)
    - geo_samples: Number of geographic sample points (default: 10)
    - llm_provider: LLM provider to use (chatgpt, claude, gemini, default: "chatgpt")

    Returns a comprehensive analysis with recommendations and database ID.
    """
    try:
        logger.info(f"Analysis request for URL: {request.url}")
        result = await seo_analyzer.analyze_site(request)

        # Guardar en base de datos
        db_service = DatabaseService(db)
        db_analysis = db_service.create_analysis(request, result.dict(), report_type=getattr(request, 'report_type', None))
        logger.info(f"Analysis saved to database with ID: {db_analysis.id}")

        # Return result with database ID
        response_data = result.dict()
        response_data["id"] = db_analysis.id

        return response_data
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during analysis: {str(e)}"
        )


@router.post("/geo-rank-analysis")
async def analyze_geo_ranking(request: GeoRankRequest, db: Session = Depends(get_db)):
    """
    Perform standalone geolocation-based ranking analysis.

    This endpoint analyzes how well a business ranks in local search results
    across multiple geographic sample points for specified keywords.

    Required Parameters:
    - company_name: Name of the business to analyze
    - keywords: Single keyword string or array of keywords to analyze
    - local_radius_km: Radius in km for local SEO analysis (1-50)
    - geo_samples: Number of geographic sample points (1-20)

    Location Parameters (either location OR both latitude/longitude):
    - location: Location string (e.g., "Medellín, Colombia")
    - latitude: Exact latitude coordinate (for precise location targeting)
    - longitude: Exact longitude coordinate (for precise location targeting)

    Returns detailed ranking analysis with coverage metrics and NAP consistency checks.
    """
    try:
        logger.info(f"Geo-ranking analysis request for company: {request.company_name}")
        result = await seo_analyzer.analyze_geo_ranking(request)

        # Guardar en base de datos
        db_service = DatabaseService(db)
        db_geo_analysis = db_service.create_geo_analysis(request, result.dict())
        logger.info(f"Geo analysis saved to database with ID: {db_geo_analysis.id}")

        # Return result with database ID
        response_data = result.dict()
        response_data["id"] = db_geo_analysis.id

        return response_data
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Geo-ranking analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during geo-ranking analysis: {str(e)}"
        )


@router.post("/analyses/html")
async def analyze_html_file(
    html_file: UploadFile = File(...),
    url: str = Form(...),
    seo_goal: str = Form(...),
    language: str = Form("es"),
    sector: str = Form("Otro"),
    location: str = Form(""),
    keywords: str = Form(""),
    latitude: float = Form(None),
    longitude: float = Form(None),
    local_radius_km: int = Form(5),
    geo_samples: int = Form(10),
    llm_provider: str = Form("chatgpt"),
    force_playwright: bool = Form(False)
):
    """
    Analiza un archivo HTML local usando la misma lógica que el análisis normal, pero sin hacer scraping en línea ni guardar en la base de datos.
    """
    try:
        html_content = (await html_file.read()).decode("utf-8", errors="replace")
        # Construir un AnalysisRequest simulado para compatibilidad
        analysis_request = AnalysisRequest(
            url=url,
            seo_goal=seo_goal,
            language=language,
            location=location,
            keywords=keywords,
            latitude=latitude,
            longitude=longitude,
            local_radius_km=local_radius_km,
            geo_samples=geo_samples,
            llm_provider=llm_provider,
            force_playwright=force_playwright
        )
        # Usar el método parse_html directamente
        parsed_data = seo_analyzer.scraper.parse_html(html_content, url)
        # Simular el resto del análisis (sin scraping ni performance real)
        # Puedes ajustar aquí si quieres análisis semántico, etc.
        # Devolver los datos principales relevantes para la comparación
        return parsed_data
    except Exception as e:
        logger.error(f"Error analizando HTML local: {e}")
        raise HTTPException(status_code=500, detail=f"Error analizando HTML local: {e}")


@router.get("/analyses")
async def get_analyses(db: Session = Depends(get_db), limit: int = 20):
    """
    Get recent analyses from database
    """
    try:
        db_service = DatabaseService(db)
        analyses = db_service.get_recent_analyses(limit)

        return {
            "analyses": [
                {
                    "id": analysis.id,
                    "url": analysis.url,
                    "seo_goal": analysis.seo_goal,
                    "location": analysis.location,
                    "status": analysis.status,
                    "created_at": analysis.created_at.isoformat(),
                    "technical_score": analysis.technical_score,
                    "onpage_score": analysis.onpage_score,
                    "offpage_score": analysis.offpage_score,
                    "overall_score": analysis.overall_score
                }
                for analysis in analyses
            ]
        }
    except Exception as e:
        logger.error(f"Error getting analyses: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analyses")


@router.get("/analyses/{analysis_id}")
async def get_analysis_by_id(analysis_id: int, db: Session = Depends(get_db)):
    """
    Get analysis by ID from database
    """
    try:
        db_service = DatabaseService(db)
        analysis = db_service.get_analysis_by_id(analysis_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Parse analysis data
        analysis_data = {}
        if analysis.analysis_data and analysis.analysis_data != "":
            import json
            analysis_data = json.loads(analysis.analysis_data)

        # Create response with analysis data merged at root level
        response = {
            "id": analysis.id,
            "url": analysis.url,
            "seo_goal": analysis.seo_goal,
            "location": analysis.location,
            "language": analysis.language,
            "status": analysis.status,
            "created_at": analysis.created_at.isoformat(),
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at is not None else None,
            "technical_score": analysis.technical_score,
            "onpage_score": analysis.onpage_score,
            "offpage_score": analysis.offpage_score,
            "overall_score": analysis.overall_score,
            "error_message": analysis.error_message
        }

        # Merge analysis_data fields into the main response
        if analysis_data:
            response.update(analysis_data)

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analysis")


@router.delete("/analyses/{analysis_id}")
async def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Delete analysis by ID
    """
    try:
        db_service = DatabaseService(db)
        success = db_service.delete_analysis(analysis_id)

        if not success:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return {"message": "Analysis deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting analysis")


@router.get("/reports")
async def get_reports(db: Session = Depends(get_db)):
    """
    Get all reports with grouping by URL
    """
    try:
        db_service = DatabaseService(db)
        analyses = db_service.get_all_analyses()

        return [
            {
                "id": analysis.id,
                "url": analysis.url,
                "report_type": analysis.report_type,
                "seo_goal": analysis.seo_goal,
                "keywords": analysis.keywords,
                "location": analysis.location,
                "language": analysis.language,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat(),
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at is not None else None,
                "technical_score": analysis.technical_score,
                "onpage_score": analysis.onpage_score,
                "offpage_score": analysis.offpage_score,
                "overall_score": analysis.overall_score
            }
            for analysis in analyses
        ]
    except Exception as e:
        logger.error(f"Error getting reports: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving reports")


@router.get("/reports/{report_id}")
async def get_report_by_id(report_id: int, db: Session = Depends(get_db)):
    """
    Get report by ID
    """
    try:
        db_service = DatabaseService(db)
        analysis = db_service.get_analysis_by_id(report_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Report not found")

        # Parse analysis data
        analysis_data = {}
        if analysis.analysis_data and analysis.analysis_data != "":
            import json
            analysis_data = json.loads(analysis.analysis_data)

        # Create response with analysis data merged at root level
        response = {
            "id": analysis.id,
            "url": analysis.url,
            "report_type": analysis.report_type,
            "seo_goal": analysis.seo_goal,
            "keywords": analysis.keywords,
            "location": analysis.location,
            "language": analysis.language,
            "status": analysis.status,
            "created_at": analysis.created_at.isoformat(),
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at is not None else None,
            "technical_score": analysis.technical_score,
            "onpage_score": analysis.onpage_score,
            "offpage_score": analysis.offpage_score,
            "overall_score": analysis.overall_score,
            "error_message": analysis.error_message
        }

        # Merge analysis_data fields into the main response
        if analysis_data:
            response.update(analysis_data)

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving report")


@router.delete("/reports/{report_id}")
async def delete_report(report_id: int, db: Session = Depends(get_db)):
    """
    Delete report by ID
    """
    try:
        db_service = DatabaseService(db)
        success = db_service.delete_analysis(report_id)

        if not success:
            raise HTTPException(status_code=404, detail="Report not found")

        return {"message": "Report deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting report")


@router.get("/reports/search")
async def search_reports(
    db: Session = Depends(get_db),
    q: str = None,
    type: str = None,
    date_range: str = None
):
    """
    Search reports with filters
    """
    try:
        db_service = DatabaseService(db)
        analyses = db_service.search_analyses(q or "", type or "", date_range or "")

        return [
            {
                "id": analysis.id,
                "url": analysis.url,
                "report_type": analysis.report_type,
                "seo_goal": analysis.seo_goal,
                "keywords": analysis.keywords,
                "location": analysis.location,
                "language": analysis.language,
                "status": analysis.status,
                "created_at": analysis.created_at.isoformat(),
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at is not None else None,
                "technical_score": analysis.technical_score,
                "onpage_score": analysis.onpage_score,
                "offpage_score": analysis.offpage_score,
                "overall_score": analysis.overall_score
            }
            for analysis in analyses
        ]
    except Exception as e:
        logger.error(f"Error searching reports: {e}")
        raise HTTPException(status_code=500, detail="Error searching reports")


@router.get("/reports/{report_id}/export")
async def export_report(report_id: int, db: Session = Depends(get_db)):
    """
    Export report as PDF
    """
    try:
        db_service = DatabaseService(db)
        analysis = db_service.get_analysis_by_id(report_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Report not found")

        # Parse analysis data
        analysis_data = {}
        if analysis.analysis_data and analysis.analysis_data != "":
            import json
            analysis_data = json.loads(analysis.analysis_data)

        # Generate PDF report
        from services.report_generator import ReportGenerator
        report_generator = ReportGenerator()
        pdf_content = await report_generator.generate_pdf_report(analysis, analysis_data)

        from fastapi.responses import Response
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report-{report_id}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error exporting report")


@router.get("/reports/export-all")
async def export_all_reports(db: Session = Depends(get_db)):
    """
    Export all reports as ZIP
    """
    try:
        db_service = DatabaseService(db)
        analyses = db_service.get_all_analyses()

        # Generate ZIP with all reports
        from services.report_generator import ReportGenerator
        report_generator = ReportGenerator()
        zip_content = await report_generator.generate_zip_reports(analyses)

        from fastapi.responses import Response
        return Response(
            content=zip_content,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=all-reports-{datetime.now().strftime('%Y-%m-%d')}.zip"}
        )
    except Exception as e:
        logger.error(f"Error exporting all reports: {e}")
        raise HTTPException(status_code=500, detail="Error exporting all reports")


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get analysis statistics
    """
    try:
        db_service = DatabaseService(db)
        stats = db_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")


@router.get("/status")
async def api_status():
    """
    Check API status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/llm-status")
async def llm_status():
    """Get LLM providers status and configuration"""
    from utils.llm_manager import get_llm_manager

    try:
        llm_manager = get_llm_manager()
        status = llm_manager.get_status()

        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "llm_status": status
        }
    except Exception as e:
        logger.error(f"Error getting LLM status: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "llm_status": {
                "available_providers": [],
                "total_providers": 0,
                "primary_provider": None,
                "error": True
            }
        }


@router.get("/test-error-handling")
async def test_error_handling():
    """Test endpoint to verify error handling works correctly"""
    from services.seo_analyzer import SEOAnalyzer
    from models.seo_models import AnalysisRequest

    try:
        # Create a test request that will trigger various errors
        test_request = AnalysisRequest(
            url="https://invalid-domain-that-does-not-exist-12345.com",
            seo_goal="Test SEO goal",
            location="Test Location",
            language="es",
            local_radius_km=5,
            geo_samples=5
        )

        seo_analyzer = SEOAnalyzer()
        result = await seo_analyzer.analyze_site(test_request)

        return {
            "status": "success",
            "message": "Error handling test completed",
            "result": result.dict(),
            "note": "This test should show how errors are handled gracefully"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Test failed: {str(e)}",
            "note": "This indicates the error handling is not working as expected"
        }


@router.get("/reports/grouped")
async def get_grouped_reports(
    db: Session = Depends(get_db),
    search: str = None,
    report_type: str = None,
    date_range: str = None,
    offset: int = 0,
    limit: int = 10
):
    """
    Obtener reportes agrupados por URL, con paginación tipo infinite scroll y filtros.
    """
    try:
        db_service = DatabaseService(db)
        result = db_service.get_grouped_reports(search, report_type, date_range, offset, limit)
        return result
    except Exception as e:
        logger.error(f"Error getting grouped reports: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving grouped reports")

@router.get("/reports/by-url")
async def get_reports_by_url(
    url: str,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 20
):
    """
    Obtener reportes individuales de una URL, paginados (paginación tradicional)
    """
    try:
        db_service = DatabaseService(db)
        result = db_service.get_reports_by_url(url, page, per_page)
        return result
    except Exception as e:
        logger.error(f"Error getting reports by url: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving reports by url")


@router.post("/keyword-usage", response_model=KeywordUsageResponse)
async def keyword_usage(
    url: str = Body(...),
    keywords: list = Body(...),
    match: str = Body("exact")
):
    """
    Analiza el uso de palabras clave en headers y párrafos de una página web.
    """
    try:
        results_dict = seo_analyzer.run_web_keywords_test(url, keywords, match)
        # Convertir a modelos Pydantic
        results = [KeywordUsageResult(**r) for r in results_dict["results"]]
        return KeywordUsageResponse(
            results=results,
            checklist=results_dict.get("checklist", []),
            url=results_dict.get("url", url),
            keywords=results_dict.get("keywords", keywords),
            match=results_dict.get("match", match)
        )
    except Exception as e:
        logger.error(f"Error en keyword-usage: {e}")
        raise HTTPException(status_code=500, detail=f"Error en keyword-usage: {e}")
