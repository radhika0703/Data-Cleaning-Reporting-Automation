import os
import logging
import matplotlib
matplotlib.use('Agg') # Headless matplotlib backend for server usage
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from fpdf import FPDF
from typing import List, Dict, Any

logger = logging.getLogger("Reporter")

class ProfessionalPDF(FPDF):
    def __init__(self, primary_color=(30, 27, 75), secondary_color=(15, 118, 110), text_color=(30, 41, 59)):
        super().__init__()
        self.custom_primary = primary_color      # Indigo (#1E1B4B)
        self.custom_secondary = secondary_color  # Teal (#0F766E)
        self.custom_text = text_color            # Slate-800 (#1E293B)
        self.custom_accent_light = (248, 250, 252)     # Slate-50 (#F8FAFC)
        self.custom_border_color = (226, 232, 240)     # Slate-200 (#E2E8F0)
        self.set_char_widths = {}
        
    def header(self):
        if self.page_no() > 1:
            # Running Header
            self.set_font('helvetica', 'B', 8)
            self.set_text_color(*self.custom_secondary)
            self.cell(0, 8, "DATA CLEANING & REPORTING AUTOMATION SYSTEM", 0, 0, 'L')
            self.set_font('helvetica', '', 8)
            self.set_text_color(148, 163, 184) # Light gray
            self.cell(0, 8, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1, 'R')
            
            # Colored thin bar beneath header
            self.set_fill_color(*self.custom_secondary)
            self.rect(10, 18, 190, 0.7, 'F')
            self.ln(5)

    def footer(self):
        # Running Footer
        self.set_y(-15)
        # Colored thin bar above footer
        self.set_fill_color(*self.custom_border_color)
        self.rect(10, 280, 190, 0.5, 'F')
        self.ln(2)
        
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(100, 116, 139) # slate-500
        self.cell(0, 10, "Confidential - Automated Audit & Analytics Report", 0, 0, 'L')
        self.cell(0, 10, f"Page {self.page_no()} of {{nb}}", 0, 0, 'R')

    def draw_cover_page(self, title: str, subtitle: str, metadata: Dict[str, str]):
        self.add_page()
        
        # Draw background shapes for premium look
        self.set_fill_color(*self.custom_primary)
        self.rect(0, 0, 210, 95, 'F') # Top block
        
        self.set_fill_color(*self.custom_secondary)
        self.rect(0, 95, 210, 6, 'F') # Teal accent strip
        
        # Cover Title
        self.set_y(35)
        self.set_font('helvetica', 'B', 28)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, title.upper(), 0, 1, 'C')
        
        # Cover Subtitle
        self.ln(4)
        self.set_font('helvetica', 'I', 14)
        self.set_text_color(204, 251, 241) # Light teal
        self.cell(0, 8, subtitle, 0, 1, 'C')
        
        # Cover Metadata Panel
        self.set_y(140)
        self.set_fill_color(*self.custom_accent_light)
        self.set_draw_color(*self.custom_border_color)
        self.rect(20, 130, 170, 90, 'DF')
        
        self.set_y(138)
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(*self.custom_primary)
        self.cell(0, 10, "     REPORT METADATA & DOCUMENT CONTROLS", 0, 1, 'L')
        
        # Divider Line
        self.set_draw_color(*self.custom_secondary)
        self.line(30, 150, 180, 150)
        self.ln(8)
        
        self.set_font('helvetica', '', 11)
        self.set_text_color(*self.custom_text)
        
        for key, val in metadata.items():
            self.cell(25) # Margin
            self.set_font('helvetica', 'B', 11)
            self.cell(50, 8, f"{key}:", 0, 0, 'L')
            self.set_font('helvetica', '', 11)
            self.cell(100, 8, str(val), 0, 1, 'L')
            
        # Bottom Branding
        self.set_y(250)
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*self.custom_primary)
        self.cell(0, 5, "POWERED BY ANTIGRAVITY ENGINE", 0, 1, 'C')
        self.set_font('helvetica', '', 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, "Automated Professional Data Preprocessing Framework", 0, 1, 'C')

    def print_section_heading(self, label: str):
        self.ln(8)
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(*self.custom_primary)
        self.cell(0, 10, label, 0, 1, 'L')
        
        # Solid Accent line
        self.set_fill_color(*self.custom_secondary)
        self.rect(self.get_x(), self.get_y() - 1, 190, 1.5, 'F')
        self.ln(6)

    def print_table(self, headers: List[str], data: List[List[str]], col_widths: List[float]):
        # Table Header
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(*self.custom_primary)
        self.set_draw_color(*self.custom_border_color)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, str(header), 1, 0, 'C', True)
        self.ln()
        
        # Table Rows
        self.set_font('helvetica', '', 9)
        self.set_text_color(*self.custom_text)
        
        for row_idx, row in enumerate(data):
            # Alternating rows
            fill = row_idx % 2 == 1
            self.set_fill_color(*self.custom_accent_light) if fill else self.set_fill_color(255, 255, 255)
            
            # Calculate height needed for the row (multiline support)
            max_lines = 1
            for col_idx, cell_value in enumerate(row):
                val_str = str(cell_value)
                # Quick estimate of line wrapping
                char_limit = int(col_widths[col_idx] / 1.8)
                lines = (len(val_str) // char_limit) + 1
                if lines > max_lines:
                    max_lines = lines
            
            row_height = max(7, max_lines * 4)
            
            x_start = self.get_x()
            for col_idx, cell_value in enumerate(row):
                x_pos = self.get_x()
                y_pos = self.get_y()
                val_str = str(cell_value)
                
                # Use MultiCell if text is long, else Cell
                if len(val_str) > int(col_widths[col_idx] / 1.8):
                    self.multi_cell(col_widths[col_idx], row_height / max_lines, val_str, 1, 'L', fill)
                    self.set_xy(x_pos + col_widths[col_idx], y_pos)
                else:
                    self.cell(col_widths[col_idx], row_height, val_str, 1, 0, 'L', fill)
            self.ln(row_height)

def create_pdf_report(
    raw_profile: Dict[str, Any],
    clean_profile: Dict[str, Any],
    audit_log: List[Dict[str, Any]],
    cleaned_df: pd.DataFrame,
    output_pdf_path: str
):
    """
    Assembles a gorgeous, multi-page, executive PDF report containing audit trail,
    comparative health stats, and data visual dashboards.
    """
    pdf = ProfessionalPDF()
    pdf.alias_nb_pages()
    
    # 1. Cover Page
    metadata = {
        "Analysis Date": datetime.now().strftime("%Y-%m-%d"),
        "System Host": "Antigravity Analytics Platform",
        "Framework Version": "v1.4.2",
        "Records Preprocessed": f"{raw_profile['total_rows']} -> {clean_profile['total_rows']}",
        "Data Health Index": f"{raw_profile['health_score']}% -> {clean_profile['health_score']}%",
        "Status": "Approved & Standardized"
    }
    pdf.draw_cover_page("Automated Data Profiling & Audit Report", "Executive Summary, Quality Metrics & Standardized Diagnostics", metadata)
    
    # 2. Page 2: Executive Summary & Performance Indicators
    pdf.add_page()
    pdf.print_section_heading("1. Executive Summary")
    
    summary_text = (
        f"This automated analysis represents a complete pipeline run of the Antigravity Data Cleaning & Standardizing "
        f"Engine. The input dataset consisted of {raw_profile['total_rows']} raw records across {raw_profile['total_columns']} columns. "
        f"Following the automated validation rules, duplicates were pruned, datetimes standardized, numerical symbols stripped, "
        f"and missing values imputed. The final cleansed dataset contains {clean_profile['total_rows']} records. "
        f"Crucially, the dataset quality score has improved from {raw_profile['health_score']}% to {clean_profile['health_score']}%."
    )
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(*pdf.custom_text)
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(5)
    
    # Summary comparative Table
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 8, "Dataset Health Progression Metrics", 0, 1, 'L')
    pdf.ln(2)
    
    headers = ["Metric Flag", "Raw Dataset Status", "Cleansed Dataset Status", "Operational Delta"]
    
    rows = [
        ["Total Rows", str(raw_profile["total_rows"]), str(clean_profile["total_rows"]), f"{clean_profile['total_rows'] - raw_profile['total_rows']} rows"],
        ["Total Columns", str(raw_profile["total_columns"]), str(clean_profile["total_columns"]), "0 (Locked schema)"],
        ["Duplicate Row Counts", str(raw_profile["duplicate_count"]), str(clean_profile["duplicate_count"]), f"-{raw_profile['duplicate_count']}"],
        ["Global Missing Cells", str(sum(raw_profile["missing_counts"].values())), str(sum(clean_profile["missing_counts"].values())), f"-{sum(raw_profile['missing_counts'].values()) - sum(clean_profile['missing_counts'].values())}"],
        ["System Outliers Found", str(sum(raw_profile["outlier_counts"].values())), str(sum(clean_profile["outlier_counts"].values())), f"-{sum(raw_profile['outlier_counts'].values()) - sum(clean_profile['outlier_counts'].values())}"],
        ["Overall Quality Score", f"{raw_profile['health_score']}%", f"{clean_profile['health_score']}%", f"+{round(clean_profile['health_score'] - raw_profile['health_score'], 1)}%"]
    ]
    
    col_widths = [55, 45, 45, 45]
    pdf.print_table(headers, rows, col_widths)
    
    # 3. Health Audit Trail
    pdf.ln(6)
    pdf.print_section_heading("2. Core Cleaning Audit Logs")
    
    pdf.set_font('helvetica', '', 9.5)
    pdf.multi_cell(0, 5, "The table below lists each cleaning filter applied to the dataset in sequential order, details the operational logic utilized, and provides absolute numbers of affected rows.")
    pdf.ln(4)
    
    audit_headers = ["Step", "Filter Operation", "Filter Context & Parameters", "Rows Impacted"]
    audit_rows = []
    for log in audit_log:
        audit_rows.append([
            str(log["step"]),
            str(log["operation"]),
            str(log["details"]),
            str(log["rows_affected"])
        ])
        
    if not audit_rows:
        audit_rows = [["-", "No Filters Applied", "The dataset is in pristine shape.", "0"]]
        
    audit_widths = [15, 45, 105, 25]
    pdf.print_table(audit_headers, audit_rows, audit_widths)
    
    # 4. Diagnostics Visual Dashboards
    pdf.add_page()
    pdf.print_section_heading("3. Diagnostic Analytics & Distributions")
    
    # Generate static Matplotlib plots and embed them
    tmp_img_dir = os.path.dirname(output_pdf_path)
    os.makedirs(tmp_img_dir, exist_ok=True)
    
    # Plot 1: Missing values by Column
    img1_path = os.path.join(tmp_img_dir, "temp_missing_bar.png")
    cols = list(raw_profile["missing_percentages"].keys())
    pcts = list(raw_profile["missing_percentages"].values())
    
    plt.figure(figsize=(7, 2.5))
    plt.bar(cols, pcts, color='#0F766E', alpha=0.85, edgecolor='#1E1B4B', width=0.5)
    plt.title("Missing Value Distribution (%)", fontsize=10, fontweight='bold', color='#1E1B4B')
    plt.ylabel("Missing Percentage (%)", fontsize=8)
    plt.xticks(rotation=15, ha='right', fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(img1_path, dpi=200)
    plt.close()
    
    # Plot 2: Category volume breakdown (Cleaned)
    img2_path = os.path.join(tmp_img_dir, "temp_cat_bar.png")
    plt.figure(figsize=(7, 2.5))
    
    # Find a column that looks categorical
    cat_col = None
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == object and cleaned_df[col].nunique() < 10:
            cat_col = col
            break
            
    if cat_col:
        vc = cleaned_df[cat_col].value_counts()
        plt.barh(vc.index.astype(str), vc.values, color='#1E1B4B', alpha=0.85, height=0.5)
        plt.title(f"Standardized Record Counts by {cat_col}", fontsize=10, fontweight='bold', color='#1E1B4B')
        plt.xlabel("Number of Rows", fontsize=8)
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
        plt.grid(axis='x', linestyle='--', alpha=0.3)
    else:
        plt.text(0.5, 0.5, "No Cleaned Categorical Column Identified", ha='center', va='center')
        
    plt.tight_layout()
    plt.savefig(img2_path, dpi=200)
    plt.close()
    
    # Embed images in PDF
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 8, "Missing Values Profile (Raw Dataset)", 0, 1, 'L')
    pdf.image(img1_path, x=15, w=180, h=55)
    pdf.ln(60)
    
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(0, 8, "Structural Distribution Breakdown (Cleansed)", 0, 1, 'L')
    pdf.image(img2_path, x=15, w=180, h=55)
    
    # Clean up temporary plots
    try:
        if os.path.exists(img1_path):
            os.remove(img1_path)
        if os.path.exists(img2_path):
            os.remove(img2_path)
    except Exception as e:
        logger.warning(f"Error removing temporary plot images: {e}")
        
    # Save the PDF
    pdf.output(output_pdf_path)
    logger.info(f"Professional PDF Report generated and saved to: {output_pdf_path}")
