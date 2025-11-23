"""
Professional PDF Report Generator for MCC-Level Coaching Analysis
Uses ReportLab for corporate-quality PDF generation with Arabic support
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import arabic_reshaper
from bidi.algorithm import get_display
import os
from io import BytesIO

class PDFRenderer:
    def __init__(self, language="English"):
        self.language = language
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_fonts()
        self._setup_custom_styles()
    
    def _setup_fonts(self):
        """Attempt to load Arabic-compatible fonts with graceful fallback"""
        try:
            # Try to load the Amiri font if available
            if os.path.exists("Amiri-Regular.ttf"):
                pdfmetrics.registerFont(TTFont('AmiriFont', 'Amiri-Regular.ttf'))
                self.arabic_font = 'AmiriFont'
            else:
                print("WARNING: Amiri font not found. Arabic text may not render correctly.")
                self.arabic_font = 'Helvetica'
        except Exception as e:
            print(f"WARNING: Font loading failed: {e}. Using default font.")
            self.arabic_font = 'Helvetica'
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=self.arabic_font if self.language == "العربية" else 'Helvetica-Bold'
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            fontName=self.arabic_font if self.language == "العربية" else 'Helvetica-Bold'
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_RIGHT if self.language == "العربية" else TA_LEFT,
            fontName=self.arabic_font if self.language == "العربية" else 'Helvetica'
        ))
    
    def _process_arabic_text(self, text):
        """Process Arabic text for proper RTL rendering"""
        if self.language == "العربية":
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        return str(text)
    
    def create_session_report(self, session_report):
        """
        Generate PDF report for Level 3 Full Coaching Session
        """
        doc = SimpleDocTemplate(self.buffer, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        
        # PAGE 1: SESSION SUMMARY
        story.extend(self._create_session_summary(session_report))
        story.append(PageBreak())
        
        # PAGE 2: DETAILED ANALYSIS
        story.extend(self._create_session_details(session_report))
        
        # Build PDF
        doc.build(story)
        self.buffer.seek(0)
        return self.buffer
    
    def _create_session_summary(self, report):
        """Create session summary page"""
        elements = []
        
        # Title
        title_text = "Full Coaching Session Report" if self.language == "English" else "تقرير جلسة التدريب الكاملة"
        title = Paragraph(self._process_arabic_text(title_text), self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Metrics
        header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['CustomBody'],
            fontSize=11,
            textColor=colors.whitesmoke,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        data_style = ParagraphStyle(
            'TableData',
            parent=self.styles['CustomBody'],
            fontSize=13,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        metrics_data = [
            [
                Paragraph(self._process_arabic_text("Overall Score" if self.language == "English" else "النتيجة الإجمالية"), header_style),
                Paragraph(self._process_arabic_text("Duration" if self.language == "English" else "المدة"), header_style),
                Paragraph(self._process_arabic_text("Exchanges" if self.language == "English" else "التبادلات"), header_style),
                Paragraph(self._process_arabic_text("Talk Ratio" if self.language == "English" else "نسبة الحديث"), header_style)
            ],
            [
                Paragraph(f"{report.get('overall_score', 0)}/10", data_style),
                Paragraph(report.get('session_duration', 'N/A'), data_style),
                Paragraph(str(report.get('total_exchanges', 0)), data_style),
                Paragraph(report.get('talk_ratio', 'N/A'), data_style)
            ]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[1.5*inch]*4)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Session Flow
        header_text = "Session Flow Quality" if self.language == "English" else "جودة تدفق الجلسة"
        header = Paragraph(self._process_arabic_text(header_text), self.styles['CustomHeader'])
        elements.append(header)
        elements.append(Spacer(1, 0.2*inch))
        
        flow = report.get('session_flow', {})
        flow_data = [
            [
                Paragraph(self._process_arabic_text("Phase" if self.language == "English" else "المرحلة"), header_style),
                Paragraph(self._process_arabic_text("Assessment" if self.language == "English" else "التقييم"), header_style)
            ]
        ]
        
        for phase_name, phase_label in [
            ('opening', 'Opening / الافتتاح'),
            ('exploration', 'Exploration / الاستكشاف'),
            ('deepening', 'Deepening / التعمق'),
            ('closing', 'Closing / الإغلاق')
        ]:
            phase_assessment = flow.get(phase_name, 'N/A')
            flow_data.append([
                Paragraph(self._process_arabic_text(phase_label), self.styles['CustomBody']),
                Paragraph(self._process_arabic_text(phase_assessment), self.styles['CustomBody'])
            ])
        
        flow_table = Table(flow_data, colWidths=[2*inch, 4.4*inch])
        flow_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37474f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        elements.append(flow_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Talk Ratio Assessment
        header_text = "Talk Ratio Assessment" if self.language == "English" else "تقييم نسبة الحديث"
        header = Paragraph(self._process_arabic_text(header_text), self.styles['CustomHeader'])
        elements.append(header)
        talk_ratio_assessment = report.get('talk_ratio_assessment', 'N/A')
        talk_para = Paragraph(self._process_arabic_text(talk_ratio_assessment), self.styles['CustomBody'])
        elements.append(talk_para)
        
        return elements
    
    def _create_session_details(self, report):
        """Create detailed analysis pages"""
        elements = []
        
        # Strengths
        header_text = "Strengths" if self.language == "English" else "نقاط القوة"
        header = Paragraph(self._process_arabic_text(header_text), self.styles['CustomHeader'])
        elements.append(header)
        elements.append(Spacer(1, 0.2*inch))
        
        strengths = report.get('strengths', [])
        for i, strength in enumerate(strengths, 1):
            strength_para = Paragraph(
                self._process_arabic_text(f"{i}. {strength}"), 
                self.styles['CustomBody']
            )
            elements.append(strength_para)
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Areas for Improvement
        header_text = "Areas for Improvement" if self.language == "English" else "مجالات التحسين"
        header = Paragraph(self._process_arabic_text(header_text), self.styles['CustomHeader'])
        elements.append(header)
        elements.append(Spacer(1, 0.2*inch))
        
        improvements = report.get('areas_for_improvement', [])
        for i, improvement in enumerate(improvements, 1):
            improvement_para = Paragraph(
                self._process_arabic_text(f"{i}. {improvement}"),
                self.styles['CustomBody']
            )
            elements.append(improvement_para)
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Key Moments
        header_text = "Key Moments" if self.language == "English" else "اللحظات الرئيسية"
        header = Paragraph(self._process_arabic_text(header_text), self.styles['CustomHeader'])
        elements.append(header)
        elements.append(Spacer(1, 0.2*inch))
        
        key_moments = report.get('key_moments', [])
        for moment in key_moments:
            timestamp = moment.get('timestamp', '')
            what_happened = moment.get('what_happened', '')
            significance = moment.get('significance', '')
            
            moment_text = f"<b>{timestamp}</b>: {what_happened}<br/><i>Significance:</i> {significance}"
            moment_para = Paragraph(
                self._process_arabic_text(moment_text),
                self.styles['CustomBody']
            )
            elements.append(moment_para)
            elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        header_text = "Actionable Recommendations" if self.language == "English" else "التوصيات العملية"
        header = Paragraph(self._process_arabic_text(header_text), self.styles['CustomHeader'])
        elements.append(header)
        elements.append(Spacer(1, 0.2*inch))
        
        recommendations = report.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            rec_para = Paragraph(
                self._process_arabic_text(f"{i}. {rec}"),
                self.styles['CustomBody']
            )
            elements.append(rec_para)
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def create_report(self, analysis_result, radar_chart_path=None):
        """
        Generate a professional MCC-level coaching analysis report
        
        Args:
            analysis_result: Dictionary containing analysis data
            radar_chart_path: Path to the radar chart image (optional)
        
        Returns:
            BytesIO buffer containing the PDF
        """
        doc = SimpleDocTemplate(self.buffer, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        
        # PAGE 1: EXECUTIVE SUMMARY
        story.extend(self._create_executive_summary(analysis_result, radar_chart_path))
        story.append(PageBreak())
        
        # PAGE 2+: DETAILED ANALYSIS
        story.extend(self._create_detailed_analysis(analysis_result))
        story.append(PageBreak())
        
        # FINAL PAGE: DEVELOPMENT RECOMMENDATIONS
        story.extend(self._create_recommendations(analysis_result))
        
        # Build PDF
        doc.build(story)
        self.buffer.seek(0)
        return self.buffer
    
    def _create_executive_summary(self, result, radar_chart_path):
        """Create the executive summary page"""
        elements = []
        
        # Title
        title_text = "MCC Session Audit Report" if self.language == "English" else "تقرير تدقيق جلسة MCC"
        title = Paragraph(self._process_arabic_text(title_text), self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Metrics Table - using Paragraphs for all cells
        header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['CustomBody'],
            fontSize=11,
            textColor=colors.whitesmoke,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        data_style = ParagraphStyle(
            'TableData',
            parent=self.styles['CustomBody'],
            fontSize=13,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        metrics_data = [
            [
                Paragraph(self._process_arabic_text("Overall Score" if self.language == "English" else "النتيجة الإجمالية"), header_style),
                Paragraph(self._process_arabic_text("Talk Ratio" if self.language == "English" else "نسبة التحدث"), header_style),
                Paragraph(self._process_arabic_text("Silence Moments" if self.language == "English" else "لحظات الصمت"), header_style),
                Paragraph(self._process_arabic_text("Ethics" if self.language == "English" else "الأخلاقيات"), header_style)
            ],
            [
                Paragraph(f"{result.get('overall_score', 6.0):.1f}/10", data_style),
                Paragraph(result.get('talk_ratio', 'N/A'), data_style),
                Paragraph(str(result.get('silence_count', 0)), data_style),
                Paragraph(result.get('ethics_status', 'PASS'), data_style)
            ]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Radar Chart
        if radar_chart_path and os.path.exists(radar_chart_path):
            try:
                img = Image(radar_chart_path, width=5*inch, height=4*inch)
                elements.append(img)
            except Exception as e:
                print(f"WARNING: Could not embed radar chart: {e}")
        
        return elements
    
    def _create_detailed_analysis(self, result):
        """Create detailed competency analysis with evidence tables"""
        elements = []
        
        # Section title
        header_text = "Detailed Competency Analysis" if self.language == "English" else "التحليل التفصيلي للجدارات"
        header = Paragraph(self._process_arabic_text(header_text), self.styles['CustomHeader'])
        elements.append(header)
        elements.append(Spacer(1, 0.2*inch))
        
        competencies = result.get('competencies', {})
        
        for comp_id, comp_data in competencies.items():
            comp_name = comp_data.get('name', comp_id)
            comp_score = comp_data.get('score', 0)
            
            # Competency header
            comp_header = f"{comp_id}: {comp_name} - Score: {comp_score}/10"
            comp_para = Paragraph(self._process_arabic_text(comp_header), self.styles['CustomHeader'])
            elements.append(comp_para)
            elements.append(Spacer(1, 0.1*inch))
            
            # Markers table - using Paragraphs for proper text wrapping
            table_data = [[
                Paragraph(self._process_arabic_text("Marker" if self.language == "English" else "المؤشر"), self.styles['CustomBody']),
                Paragraph(self._process_arabic_text("Evidence & Time" if self.language == "English" else "الدليل والوقت"), self.styles['CustomBody']),
                Paragraph(self._process_arabic_text("Auditor Critique" if self.language == "English" else "ملاحظة المدقق"), self.styles['CustomBody'])
            ]]
            
            for marker in comp_data.get('markers', []):
                status = marker.get('status', 'Fail')
                marker_id = marker.get('id', '')
                evidence = marker.get('evidence', 'N/A')
                auditor_note = marker.get('auditor_note', '')
                
                # Create Paragraphs for each cell to allow proper wrapping
                marker_cell = Paragraph(
                    self._process_arabic_text(f"{marker_id}<br/>[{status}]"),
                    self.styles['CustomBody']
                )
                
                evidence_cell = Paragraph(
                    self._process_arabic_text(evidence),
                    self.styles['CustomBody']
                )
                
                auditor_cell = Paragraph(
                    self._process_arabic_text(auditor_note),
                    self.styles['CustomBody']
                )
                
                table_data.append([marker_cell, evidence_cell, auditor_cell])
            
            markers_table = Table(table_data, colWidths=[0.8*inch, 2.8*inch, 2.8*inch])
            
            # Apply styling
            style_commands = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37474f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]
            
            # Color code rows based on Pass/Fail
            for i, marker in enumerate(comp_data.get('markers', []), start=1):
                if marker.get('status') == 'Pass':
                    style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#e8f5e9')))
                else:
                    style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#ffebee')))
            
            markers_table.setStyle(TableStyle(style_commands))
            
            elements.append(markers_table)
            elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_recommendations(self, result):
        """Create development recommendations page with professional formatting"""
        elements = []
        
        # Section title
        header_text = "Development Recommendations" if self.language == "English" else "توصيات التطوير"
        header = Paragraph(self._process_arabic_text(header_text), self.styles['CustomTitle'])
        elements.append(header)
        elements.append(Spacer(1, 0.3*inch))
        
        # Introduction
        intro_text = "Based on the MCC-level audit, the following competencies require focused development:" if self.language == "English" else "بناءً على تدقيق مستوى MCC، تحتاج الجدارات التالية إلى تطوير مركز:"
        intro_style = ParagraphStyle(
            'IntroStyle',
            parent=self.styles['CustomBody'],
            fontSize=12,
            spaceAfter=20,
            fontName='Helvetica-Bold' if self.language == "English" else self.arabic_font
        )
        intro = Paragraph(self._process_arabic_text(intro_text), intro_style)
        elements.append(intro)
        elements.append(Spacer(1, 0.2*inch))
        
        competencies = result.get('competencies', {})
        
        # Collect failed markers by competency
        recommendations = []
        for comp_id, comp_data in competencies.items():
            failed_markers = [m for m in comp_data.get('markers', []) if m.get('status') == 'Fail']
            
            if failed_markers:
                comp_name = comp_data.get('name', comp_id)
                recommendations.append({
                    'id': comp_id,
                    'name': comp_name,
                    'markers': failed_markers
                })
        
        if not recommendations:
            # No recommendations needed
            no_rec_text = "Excellent work! All competencies demonstrated at MCC level." if self.language == "English" else "عمل ممتاز! جميع الجدارات ظهرت بمستوى MCC."
            no_rec = Paragraph(self._process_arabic_text(no_rec_text), self.styles['CustomBody'])
            elements.append(no_rec)
        else:
            # Create recommendations table
            for rec in recommendations:
                # Competency header with background
                comp_header_style = ParagraphStyle(
                    'CompHeader',
                    parent=self.styles['CustomBody'],
                    fontSize=13,
                    textColor=colors.HexColor('#1a237e'),
                    fontName='Helvetica-Bold' if self.language == "English" else self.arabic_font,
                    spaceAfter=5
                )
                
                comp_header_text = f"{rec['id']}: {rec['name']}"
                comp_header = Paragraph(self._process_arabic_text(comp_header_text), comp_header_style)
                elements.append(comp_header)
                
                # Create table for markers
                marker_data = [[
                    Paragraph(self._process_arabic_text("Marker" if self.language == "English" else "المؤشر"), self.styles['CustomBody']),
                    Paragraph(self._process_arabic_text("Development Action" if self.language == "English" else "إجراء التطوير"), self.styles['CustomBody'])
                ]]
                
                for marker in rec['markers']:
                    marker_id = marker.get('id', '')
                    auditor_note = marker.get('auditor_note', 'Review this marker in ICF guidelines.')
                    
                    marker_cell = Paragraph(
                        self._process_arabic_text(f"<b>{marker_id}</b>"),
                        self.styles['CustomBody']
                    )
                    
                    action_cell = Paragraph(
                        self._process_arabic_text(auditor_note),
                        self.styles['CustomBody']
                    )
                    
                    marker_data.append([marker_cell, action_cell])
                
                marker_table = Table(marker_data, colWidths=[1*inch, 5.4*inch])
                marker_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff9e6')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                
                elements.append(marker_table)
                elements.append(Spacer(1, 0.2*inch))
        
        return elements


def generate_mcc_pdf(analysis_result, language="English", radar_chart_path=None):
    """
    Convenience function to generate MCC-level PDF report
    
    Args:
        analysis_result: Analysis data dictionary
        language: "English" or "العربية"
        radar_chart_path: Path to radar chart image
    
    Returns:
        Bytes of the generated PDF
    """
    renderer = PDFRenderer(language=language)
    pdf_buffer = renderer.create_report(analysis_result, radar_chart_path)
    return pdf_buffer.getvalue()


def generate_session_pdf(session_report, language="English"):
    """
    Convenience function to generate Full Coaching Session PDF report
    
    Args:
        session_report: Session analysis data dictionary
        language: "English" or "العربية"
    
    Returns:
        Bytes of the generated PDF
    """
    renderer = PDFRenderer(language=language)
    pdf_buffer = renderer.create_session_report(session_report)
    return pdf_buffer.getvalue()
