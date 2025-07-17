import asyncio
import io
import zipfile
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import json


class ReportGenerator:
    """Servicio para generar reportes en PDF y ZIP"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        # Párrafos normales
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        ))
        
        # Información de metadatos
        self.styles.add(ParagraphStyle(
            name='CustomMeta',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            textColor=colors.grey
        ))
    
    async def generate_pdf_report(self, analysis, analysis_data: Dict[str, Any]) -> bytes:
        """Generar reporte PDF para un análisis individual"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        story = []
        
        # Título
        story.append(Paragraph("Reporte de Análisis SEO", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Información del análisis
        story.append(Paragraph("Información del Análisis", self.styles['CustomHeading2']))
        
        meta_data = [
            ["URL Analizada:", analysis.url],
            ["Objetivo SEO:", analysis.seo_goal or "No especificado"],
            ["Ubicación:", analysis.location or "No especificada"],
            ["Idioma:", analysis.language or "es"],
            ["Fecha de Análisis:", analysis.created_at.strftime("%d/%m/%Y %H:%M")],
            ["Estado:", "Completado" if analysis.status == "completed" else "En proceso"]
        ]
        
        if analysis.latitude and analysis.longitude:
            meta_data.append(["Coordenadas:", f"{analysis.latitude}, {analysis.longitude}"])
        
        if analysis.local_radius_km:
            meta_data.append(["Radio Local:", f"{analysis.local_radius_km} km"])
        
        meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(meta_table)
        story.append(Spacer(1, 20))
        
        # Puntuaciones
        if analysis.technical_score is not None or analysis.onpage_score is not None or analysis.offpage_score is not None:
            story.append(Paragraph("Puntuaciones SEO", self.styles['CustomHeading2']))
            
            scores_data = []
            if analysis.technical_score is not None:
                scores_data.append(["Puntuación Técnica:", f"{analysis.technical_score}/100"])
            if analysis.onpage_score is not None:
                scores_data.append(["Puntuación On-Page:", f"{analysis.onpage_score}/100"])
            if analysis.offpage_score is not None:
                scores_data.append(["Puntuación Off-Page:", f"{analysis.offpage_score}/100"])
            if analysis.overall_score is not None:
                scores_data.append(["Puntuación General:", f"{analysis.overall_score}/100"])
            
            scores_table = Table(scores_data, colWidths=[2*inch, 1*inch])
            scores_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(scores_table)
            story.append(Spacer(1, 20))
        
        # Datos del análisis
        if analysis_data:
            story.append(Paragraph("Resultados Detallados", self.styles['CustomHeading2']))
            
            # Análisis técnico
            if 'technical_analysis' in analysis_data:
                story.append(Paragraph("Análisis Técnico", self.styles['CustomHeading2']))
                tech_data = analysis_data['technical_analysis']
                
                if 'http_status' in tech_data:
                    story.append(Paragraph(f"Estado HTTP: {tech_data['http_status']}", self.styles['CustomBody']))
                
                if 'load_time' in tech_data:
                    story.append(Paragraph(f"Tiempo de Carga: {tech_data['load_time']}s", self.styles['CustomBody']))
                
                if 'page_size' in tech_data:
                    story.append(Paragraph(f"Tamaño de Página: {tech_data['page_size']}", self.styles['CustomBody']))
                
                story.append(Spacer(1, 12))
            
            # Análisis de contenido
            if 'content_analysis' in analysis_data:
                story.append(Paragraph("Análisis de Contenido", self.styles['CustomHeading2']))
                content_data = analysis_data['content_analysis']
                
                if 'title' in content_data:
                    story.append(Paragraph(f"Título: {content_data['title']}", self.styles['CustomBody']))
                
                if 'meta_description' in content_data:
                    story.append(Paragraph(f"Meta Descripción: {content_data['meta_description']}", self.styles['CustomBody']))
                
                if 'word_count' in content_data:
                    story.append(Paragraph(f"Palabras: {content_data['word_count']}", self.styles['CustomBody']))
                
                story.append(Spacer(1, 12))
            
            # Recomendaciones
            if 'recommendations' in analysis_data:
                story.append(Paragraph("Recomendaciones", self.styles['CustomHeading2']))
                recommendations = analysis_data['recommendations']
                
                if isinstance(recommendations, list):
                    for i, rec in enumerate(recommendations, 1):
                        story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
                elif isinstance(recommendations, str):
                    story.append(Paragraph(recommendations, self.styles['CustomBody']))
                
                story.append(Spacer(1, 12))
        
        # Pie de página
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} por USEOAI",
            self.styles['CustomMeta']
        ))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    async def generate_zip_reports(self, analyses: List) -> bytes:
        """Generar ZIP con todos los reportes"""
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for analysis in analyses:
                try:
                    # Parse analysis data
                    analysis_data = {}
                    if analysis.analysis_data and analysis.analysis_data != "":
                        analysis_data = json.loads(analysis.analysis_data)
                    
                    # Generate PDF for this analysis
                    pdf_content = await self.generate_pdf_report(analysis, analysis_data)
                    
                    # Add to ZIP
                    filename = f"report-{analysis.id}-{analysis.url.replace('://', '_').replace('/', '_').replace('.', '_')}.pdf"
                    zip_file.writestr(filename, pdf_content)
                    
                except Exception as e:
                    # If PDF generation fails, create a simple text report
                    text_content = f"""
Reporte de Análisis SEO
=======================

URL: {analysis.url}
Fecha: {analysis.created_at.strftime('%d/%m/%Y %H:%M')}
Estado: {analysis.status}

Error al generar PDF: {str(e)}
                    """
                    filename = f"report-{analysis.id}-error.txt"
                    zip_file.writestr(filename, text_content)
        
        buffer.seek(0)
        return buffer.getvalue() 