"""
Universal AI Web Scraper - Exporter Module
Exports scraped data into CSV, Excel, JSON, and PDF formats.
Uses Pandas for spreadsheet/json formats and ReportLab for custom designed PDF reports.
"""

import os
import json
import logging
import pandas as pd
from typing import List, Dict, Any, Optional

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = logging.getLogger(__name__)

class DataExporter:
    """
    Handles exporting list-of-dictionary structures to multiple formats.
    Ensures directories are created and processes formatting.
    """

    @staticmethod
    def export_data(
        data: List[Dict[str, Any]], 
        format_type: str, 
        base_filename: str, 
        output_dir: str,
        meta_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Main entry point for exports.
        :param data: The list of row dicts.
        :param format_type: 'csv', 'xlsx', 'json', or 'pdf'.
        :param base_filename: Filename without extension.
        :param output_dir: Destination folder path.
        :param meta_info: Metadata dictionary for headers/summaries (especially in PDF).
        :return: Absolute file path to the exported file.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        format_type = format_type.lower().strip()
        filename = f"{base_filename}.{format_type}"
        filepath = os.path.join(output_dir, filename)

        if not data:
            logger.warning("Attempted to export an empty data set.")
            # Create a simple placeholder dataframe if empty to prevent empty files crashing viewers
            df = pd.DataFrame([{"Message": "No data extracted"}])
        else:
            df = pd.DataFrame(data)

        logger.info(f"Initiating export of {len(data)} rows to format: {format_type.upper()}")

        if format_type == "csv":
            df.to_csv(filepath, index=False, encoding="utf-8")
        elif format_type == "xlsx":
            # Pandas uses openpyxl as default engine for .xlsx
            df.to_excel(filepath, index=False, engine="openpyxl")
        elif format_type == "json":
            df.to_json(filepath, orient="records", indent=4, force_ascii=False)
        elif format_type == "pdf":
            DataExporter._export_to_pdf(data, filepath, meta_info or {})
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

        logger.info(f"Successfully exported data to: {filepath}")
        return filepath

    @staticmethod
    def _export_to_pdf(data: List[Dict[str, Any]], filepath: str, meta_info: Dict[str, Any]):
        """
        Custom PDF report generation using ReportLab.
        Utilizes page orientation landscape to fit more data.
        """
        # Calculate dynamic columns
        headers = list(data[0].keys()) if data else ["Message"]
        if not data:
            data = [{"Message": "No data extracted"}]

        # Setup document in Landscape mode
        doc = SimpleDocTemplate(
            filepath,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()
        
        # Color Palette - Professional Deep Blue / Dark Slate
        PRIMARY_COLOR = colors.HexColor("#1A365D")   # Deep Blue
        SECONDARY_COLOR = colors.HexColor("#2B6CB0") # Medium Blue
        TEXT_COLOR = colors.HexColor("#2D3748")      # Dark Grey
        LIGHT_BG = colors.HexColor("#EDF2F7")        # Light Grey
        
        # Custom styles
        title_style = ParagraphStyle(
            name='PdfTitleStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=PRIMARY_COLOR,
            spaceAfter=15
        )
        
        meta_label_style = ParagraphStyle(
            name='PdfMetaLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=PRIMARY_COLOR
        )
        
        meta_val_style = ParagraphStyle(
            name='PdfMetaVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=TEXT_COLOR
        )

        cell_header_style = ParagraphStyle(
            name='PdfCellHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=colors.white
        )

        cell_text_style = ParagraphStyle(
            name='PdfCellText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=TEXT_COLOR
        )

        story = []

        # Document Header
        story.append(Paragraph("UNIVERSAL AI WEB SCRAPER", title_style))
        story.append(Paragraph("Extraction Report & Audit Log", ParagraphStyle(
            name='SubTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=SECONDARY_COLOR,
            spaceAfter=10
        )))
        story.append(Spacer(1, 10))

        # Metadata Table (URL, Prompt, Time)
        meta_data = [
            [
                Paragraph("Target URL:", meta_label_style),
                Paragraph(meta_info.get("url", "N/A"), meta_val_style),
                Paragraph("Timestamp:", meta_label_style),
                Paragraph(meta_info.get("timestamp", "N/A"), meta_val_style),
            ],
            [
                Paragraph("NL Prompt:", meta_label_style),
                Paragraph(meta_info.get("prompt", "N/A"), meta_val_style),
                Paragraph("Total Extracted:", meta_label_style),
                Paragraph(f"{len(data)} items", meta_val_style),
            ]
        ]
        
        meta_table = Table(meta_data, colWidths=[80, 280, 80, 260])
        meta_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,-1), (-1,-1), 1, SECONDARY_COLOR),
        ]))
        
        story.append(meta_table)
        story.append(Spacer(1, 20))

        # Build Data Table
        # Maximum available width is page height (Landscape Letter) - margins: 792 - 60 = 732
        avail_width = 732
        col_count = len(headers)
        col_width = avail_width / max(col_count, 1)
        col_widths = [col_width] * col_count

        table_data = []
        
        # Headers Row
        headers_row = [Paragraph(str(h).upper(), cell_header_style) for h in headers]
        table_data.append(headers_row)

        # Values Rows
        for row_dict in data:
            row_cells = []
            for h in headers:
                val = str(row_dict.get(h, ""))
                row_cells.append(Paragraph(val, cell_text_style))
            table_data.append(row_cells)

        results_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Table Styling
        t_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ])

        # Add alternating row backgrounds
        for idx in range(1, len(table_data)):
            if idx % 2 == 0:
                t_style.add('BACKGROUND', (0, idx), (-1, idx), LIGHT_BG)

        results_table.setStyle(t_style)
        story.append(results_table)

        # Build PDF
        doc.build(story)
