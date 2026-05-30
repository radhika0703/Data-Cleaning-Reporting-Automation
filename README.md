# ⚡ Antigravity Data Cleaning & Reporting Automation Suite

An enterprise-grade, professional Python framework designed to automate the ingestion, profiling, cleaning, visual analysis, and reporting of datasets. 

Designed for both data scientists and corporate business users, this system features a **dual-interface architecture**:
1. **Interactive Web Dashboard (Streamlit & Plotly)**: Drag-and-drop workspace to interactively profile, filter, clean, and visualize datasets with side-by-side comparative health scores.
2. **Scheduled CLI Pipeline Engine (`run_cli.py`)**: Headless JSON configuration-driven runner suitable for cron tasks, Windows Task Scheduler, or CI/CD data workflows.

---

## 🌟 Key Features

- **📊 Comprehensive Data Profiling**: Instantly computes dataset metadata, memory usage, duplicate rows, missing cell percentages, schema types, outlier indices, and aggregates them into a **Data Health Score (0-100%)**.
- **⚙️ Advanced Preprocessing Suite**:
  - **Missing Values**: Flexible imputation strategies (mean, median, mode, constant values, forward fill, backward fill, or row drop).
  - **Duplicate Records**: Prunes redundant items with custom column subsets and indexing controls.
  - **Mixed Datetime Standardization**: Intelligently parses scattered date representations into standardized ISO `YYYY-MM-DD` stamps.
  - **Numeric Scrubbing**: Automatically strips currency symbols (`$`, `€`, `£`), thousands commas, whitespaces, and converts formatted percent symbols into clean decimal scales.
  - **Outlier Engine**: Detects extreme values using standard statistical methods (IQR or Z-Score) and provides clipping, dropping, or median substitution actions.
  - **Text & Category Normalization**: Regulates whitespace padding, standardizes text casing (title, upper, lower), and maps arbitrary abbreviations or typos using configuration dictionaries.
- **📄 Audit Log & PDF Generator**: Keeps a detailed compliance log of all cleaning adjustments (exact counts of affected rows per column) and compiles it into a premium, multi-page **Executive PDF Quality Report** containing graphical data distribution dashboards.

---

## 📁 Repository Directory Structure

```
P4/
├── data/
│   ├── raw/                     # Messy CSV/Excel inputs
│   └── processed/               # Standardized data and PDF reports
├── config/
│   └── default_config.json      # Default cleaning configuration profile
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── cleaner.py           # Core Pandas profiling and cleaning logic
│   │   ├── reporter.py          # ReportLab-like PDF compilation engine (FPDF2)
│   │   ├── pipeline.py          # Orchestrates multi-step configurations
│   │   └── generator.py         # Messy synthetic data creator
│   ├── app/
│   │   ├── __init__.py
│   │   ├── dashboard.py         # Gorgeous Streamlit Web Interface
│   │   └── styles.py            # Glassmorphism CSS overrides
│   └── cli.py                   # Command-line entry points
├── tests/
│   ├── __init__.py
│   └── test_cleaner.py          # Unit test suites
├── requirements.txt             # Python dependencies
├── run_app.py                   # One-click dashboard execution wrapper
└── run_cli.py                   # Headless script automation wrapper
```

---

## 🚀 Installation & Quick Start

### 1. Requirements Setup
Requires Python 3.10 or higher. Install all library dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run Automated Unit Tests
To verify all operations (datetime standardizers, currency cleaners, outlier clippers, mode imputers) work correctly on your OS:
```bash
python -m unittest discover tests
```

### 3. Headless CLI Pipeline Run (Scheduled Automation)
You can generate a sample messy e-commerce dataset for testing:
```bash
python run_cli.py --generate-sample
```
This generates `data/raw/sample_sales.csv`. 

To clean it automatically using `config/default_config.json`:
```bash
python run_cli.py --input data/raw/sample_sales.csv
```
This outputs:
- **Cleaned Data File**: `data/processed/sample_sales_cleaned.csv`
- **Executive Audit Report**: `data/processed/sample_sales_audit_report.pdf` (with missing value bars, volume distributions, and health summaries).

You can pass a custom output path, custom PDF path, and customized JSON configuration profiles:
```bash
python run_cli.py --input raw.csv --output clean.xlsx --report report.pdf --config my_custom_rules.json
```

### 4. Interactive Web Dashboard (Streamlit GUI)
To launch the interactive dashboard workspace in your default browser:
```bash
python run_app.py
```
This opens the workspace at `http://localhost:8501/`, showing:
- **Data Ingestion Tab**: Quick drag-and-drop csv/xlsx uploads. Shows quality indexes and missing heatmaps immediately.
- **Auto-Cleaning Workspace**: Simple toggles and dropdown inputs to configure and live-preview cleaning filters.
- **Interactive Analytics Tab**: Instantly builds custom plotly lines, bars, outlier box plots, histograms, and correlations.
- **Export Center**: Downloads your standardized CSV/Excel spreadsheets and compiles PDF audit files on the fly.
