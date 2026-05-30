import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Add project root directory to system path for clean relative/absolute package imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.cleaner import DataCleaner
from src.core.reporter import create_pdf_report
from src.core.generator import generate_messy_dataset
from src.app.styles import inject_premium_styles

# Set page config for a widescreen layout and a dark themed default
st.set_page_config(
    page_title="Data Cleaning & Reporting Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject modern, sleek CSS styling
inject_premium_styles()

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLE_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "sample_sales.csv")

# Initialize session state variables
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None
if 'raw_profile' not in st.session_state:
    st.session_state.raw_profile = None
if 'clean_profile' not in st.session_state:
    st.session_state.clean_profile = None
if 'cleaner' not in st.session_state:
    st.session_state.cleaner = DataCleaner()
if 'filename' not in st.session_state:
    st.session_state.filename = ""

def load_data(file):
    try:
        st.session_state.filename = file.name

        if file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)

        else:
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file, encoding='latin1')
                except UnicodeDecodeError:
                    file.seek(0)
                    df = pd.read_csv(file, encoding='cp1252')

        st.session_state.raw_df = df
        st.session_state.cleaned_df = df.copy()
        st.session_state.cleaner = DataCleaner()
        st.session_state.raw_profile = st.session_state.cleaner.profile_data(df)
        st.session_state.clean_profile = st.session_state.raw_profile.copy()

        st.success(f"Successfully imported dataset '{file.name}' containing {len(df)} rows!")

    except Exception as e:
        st.error(f"Error reading file: {e}")

# Sidebar Brand Banner & Navigation
st.sidebar.markdown(
    """
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #1E1B4B 0%, #0F766E 100%); border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.15);'>
        <h2 style='color: white; margin: 0; font-size: 1.5rem;'>DATA ANALYTICS HUB</h2>
        <p style='color: #CCFBF1; margin: 0.2rem 0 0 0; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px;'>Advanced Analytics Platform</p>
    </div>
    """,
    unsafe_allow_html=True
)
  
navigation = st.sidebar.radio(
    "WORKSPACE MODULES",
    [
        "📊 Data Profile & Import",
        "⚙️ Auto-Cleaning Suite",
        "📈 Interactive Analytics",
        "📥 Report & Export Center"
    ]
)

# Fast demonstration trigger in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🚀 Quick Sandbox Demo")
if st.sidebar.button("Load Raw Sample Dataset"):
    if not os.path.exists(SAMPLE_DATA_PATH):
        generate_messy_dataset(SAMPLE_DATA_PATH)
    st.session_state.filename = "sample_sales.csv"
    df = pd.read_csv(SAMPLE_DATA_PATH)
    st.session_state.raw_df = df
    st.session_state.cleaned_df = df.copy()
    st.session_state.cleaner = DataCleaner()
    st.session_state.raw_profile = st.session_state.cleaner.profile_data(df)
    st.session_state.clean_profile = st.session_state.raw_profile.copy()
    st.sidebar.success("Messy sales dataset loaded into workspace!")

# Main Title Area
st.markdown(
    """
    <div class="title-banner">
        <h1>DATA CLEANING & REPORTING AUTOMATION</h1>
        <p>A Professional-Grade Preprocessing, Standardizing & Visual Analytics Framework</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# ----------------------------------------------------
# MODULE 1: DATA PROFILE & IMPORT
# ----------------------------------------------------
if navigation == "📊 Data Profile & Import":
    st.header("📊 Dataset Ingestion & Profiling Workspace")
    
    col_uploader, col_instructions = st.columns([2, 1])
    
    with col_uploader:
        uploaded_file = st.file_uploader(
            "Upload raw data file (supports CSV, XLS, XLSX)", 
            type=["csv", "xlsx", "xls"],
            key="dashboard_uploader"
        )
        if uploaded_file is not None:
            load_data(uploaded_file)
            
    with col_instructions:
        st.markdown(
            """
            <div class="glass-card" style="padding: 1.25rem;">
                <h4 style="margin-top:0; color:#1E1B4B;">In Ingestion Stage:</h4>
                <ul style="padding-left:1.2rem; font-size:0.9rem; color:#475569; margin-bottom:0;">
                    <li>Drop your spreadsheet in the upload box.</li>
                    <li>System automatically processes schema, shapes, missing rows, and flags anomalies.</li>
                    <li>If you don't have a dataset, click <b>"Load Raw Sample Dataset"</b> in the sidebar for a demo.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.session_state.raw_df is not None:
        prof = st.session_state.raw_profile
        
        # High level metric displays
        st.markdown("<h3 style='color:#1E1B4B;'>Quality Profiling Dashboard</h3>", unsafe_allow_html=True)
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        
        with m_col1:
            st.markdown(f"""
            <div class="custom-metric">
                <div class="custom-metric-lbl">Total Records</div>
                <div class="custom-metric-val">{prof['total_rows']:,}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col2:
            st.markdown(f"""
            <div class="custom-metric" style="border-left-color: #0F766E;">
                <div class="custom-metric-lbl">Total Columns</div>
                <div class="custom-metric-val">{prof['total_columns']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col3:
            st.markdown(f"""
            <div class="custom-metric" style="border-left-color: #F59E0B;">
                <div class="custom-metric-lbl">Duplicate Rows</div>
                <div class="custom-metric-val">{prof['duplicate_count']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col4:
            null_sum = sum(prof['missing_counts'].values())
            st.markdown(f"""
            <div class="custom-metric" style="border-left-color: #EF4444;">
                <div class="custom-metric-lbl">Missing Cells</div>
                <div class="custom-metric-val">{null_sum:,}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col5:
            st.markdown(f"""
            <div class="custom-metric" style="border-left-color: {'#10B981' if prof['health_score'] >= 80 else '#F59E0B' if prof['health_score'] >= 50 else '#EF4444'};">
                <div class="custom-metric-lbl">Data Health Score</div>
                <div class="custom-metric-val">{prof['health_score']}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Details & Missing heatmap tabs
        tab_preview, tab_missing, tab_types = st.tabs(["📋 Data Snapshot", "🔍 Missing Value Matrix", "🔤 Schema & Types"])
        
        with tab_preview:
            st.dataframe(st.session_state.raw_df.head(15), use_container_width=True)
            
        with tab_missing:
            # Bar chart of missing percentage
            cols = list(prof["missing_percentages"].keys())
            pcts = list(prof["missing_percentages"].values())
            
            fig = px.bar(
                x=cols, 
                y=pcts,
                labels={"x": "Columns", "y": "Missing Percentage (%)"},
                title="Missing Value Densities per Column",
                color=pcts,
                color_continuous_scale="Tealgrn"
            )
            fig.update_layout(yaxis_range=[0, 100], plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
        with tab_types:
            type_data = []
            for col in st.session_state.raw_df.columns:
                type_data.append({
                    "Column Name": col,
                    "Inferred Pandas Type": prof["column_types"][col],
                    "Distinct Values": prof["unique_counts"][col],
                    "Missing Percent": f"{prof['missing_percentages'][col]}%",
                    "Identified Outliers": prof["outlier_counts"][col]
                })
            st.table(pd.DataFrame(type_data))

    else:
        st.info("Ingest a dataset via the uploader or load the demo sandbox dataset in the sidebar to get started.")

# ----------------------------------------------------
# MODULE 2: AUTO-CLEANING SUITE
# ----------------------------------------------------
elif navigation == "⚙️ Auto-Cleaning Suite":
    st.header("⚙️ Intelligent Cleaning & Transformation Suite")
    
    if st.session_state.raw_df is None:
        st.info("No data available in workspace. Please ingest data in the Ingestion stage first.")
    else:
        df = st.session_state.raw_df
        cleaner = st.session_state.cleaner
        
        # Display side-by-side configurators
        st.subheader("Configure Preprocessing Steps")
        
        c_col1, c_col2 = st.columns([1, 1])
        
        with c_col1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#0F766E;'>1. Structural Controls</h4>", unsafe_allow_html=True)
            
            # Duplicates
            clean_dups = st.checkbox("Remove Duplicate Records", value=True)
            dup_cols = st.multiselect("Select columns to base duplicates on (leave empty to check all)", df.columns)
            dup_keep = st.selectbox("Record to keep", ["first", "last", "none"], index=0)
            
            st.markdown("---")
            
            # Datetime Casting
            st.markdown("<h4 style='color:#0F766E;'>2. Parse Datetimes</h4>", unsafe_allow_html=True)
            date_cols = st.multiselect("Select columns representing dates", df.columns, 
                                      default=[c for c in df.columns if 'date' in c.lower()])
            
            st.markdown("---")
            
            # Numeric Parsing
            st.markdown("<h4 style='color:#0F766E;'>3. Clean & Parse Numeric Values</h4>", unsafe_allow_html=True)
            st.caption("Auto-scrubs currency symbols, percentage characters, commas, and trims whitespaces.")
            numeric_cols = st.multiselect("Select numeric fields to clean", df.columns,
                                         default=[c for c in df.columns if c.lower() in ['price', 'quantity', 'discount', 'rating', 'sales', 'revenue']])
            st.markdown("</div>", unsafe_allow_html=True)

        with c_col2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#0F766E;'>4. Missing Value Imputations</h4>", unsafe_allow_html=True)
            
            # Advanced Missing Value configuration
            impute_entries = []
            cols_to_impute = st.multiselect("Select columns to impute", df.columns)
            
            for col in cols_to_impute:
                imp_col1, imp_col2 = st.columns(2)
                with imp_col1:
                    strategy = st.selectbox(f"Impute {col} via:", ["median", "mean", "mode", "constant", "ffill", "bfill", "drop"], key=f"strat_{col}")
                with imp_col2:
                    val = None
                    if strategy == "constant":
                        val = st.text_input("Impute custom constant:", value="0", key=f"val_{col}")
                impute_entries.append({"column": col, "strategy": strategy, "fill_value": val})
                
            st.markdown("---")
            
            # Outliers
            st.markdown("<h4 style='color:#0F766E;'>5. Numeric Outlier Handling</h4>", unsafe_allow_html=True)
            outlier_cols = st.multiselect("Select columns for outlier cleaning", 
                                          [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) or c in numeric_cols])
            
            if outlier_cols:
                out_col1, out_col2, out_col3 = st.columns(3)
                with out_col1:
                    out_method = st.selectbox("Outlier Detection Method", ["iqr", "z-score"])
                with out_col2:
                    out_action = st.selectbox("Outlier Handling Action", ["clip", "drop", "replace_median"])
                with out_col3:
                    out_thresh = st.number_input("Threshold multiplier", value=1.5, step=0.1)
            
            st.markdown("---")
            
            # Text normalization
            st.markdown("<h4 style='color:#0F766E;'>6. Text Normalization</h4>", unsafe_allow_html=True)
            text_cols = st.multiselect("Select text columns to clean casing/spaces", 
                                       [c for c in df.columns if df[c].dtype == object and c not in date_cols and c not in numeric_cols])
            text_casing = st.selectbox("Casing standard", ["title", "lower", "upper", "none"], index=0)
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Trigger Cleaning
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Execute Pipeline Filters"):
            with st.spinner("Processing dataset through cleaning layers..."):
                cleaned_df = df.copy()
                
                # Reset clean history
                st.session_state.cleaner = DataCleaner()
                cleaner = st.session_state.cleaner
                
                # 1. Duplicates
                if clean_dups:
                    cleaned_df = cleaner.remove_duplicates(cleaned_df, subset=dup_cols if dup_cols else None, keep=dup_keep)
                    
                # 2. Date formats
                if date_cols:
                    cleaned_df = cleaner.parse_datetimes(cleaned_df, date_cols)
                    
                # 3. Numeric symbols
                if numeric_cols:
                    cleaned_df = cleaner.parse_numeric(cleaned_df, numeric_cols)
                    
                # 4. Custom text
                if text_cols and text_casing != "none":
                    for t_col in text_cols:
                        cleaned_df = cleaner.standardize_text(cleaned_df, [t_col], casing=text_casing)
                        
                # 5. Missing value imputations
                for imp_cfg in impute_entries:
                    # Cast custom fill value appropriately if constant
                    f_val = imp_cfg["fill_value"]
                    if f_val is not None:
                        try:
                            # Try to make float, else keep string
                            f_val = float(f_val)
                            if f_val.is_integer():
                                f_val = int(f_val)
                        except ValueError:
                            pass
                    cleaned_df = cleaner.impute_missing(cleaned_df, [imp_cfg["column"]], strategy=imp_cfg["strategy"], fill_value=f_val)
                    
                # 6. Outlier processing
                if outlier_cols:
                    cleaned_df = cleaner.handle_outliers(cleaned_df, outlier_cols, method=out_method, action=out_action, threshold=out_thresh)
                    
                # Store
                st.session_state.cleaned_df = cleaned_df
                st.session_state.clean_profile = cleaner.profile_data(cleaned_df)
                
                st.balloons()
                st.success("Cleaning pipeline executed completely!")

        # Comparative View
        if st.session_state.cleaned_df is not None and len(cleaner.audit_log) > 0:
            st.markdown("<br>---", unsafe_allow_html=True)
            st.subheader("Cleaning Diagnostic Summary & Comparative Matrix")
            
            # Show Audit Log
            st.markdown("<h4 style='color:#1E1B4B;'>Cleaning Filter Audit Trail</h4>", unsafe_allow_html=True)
            st.table(pd.DataFrame(cleaner.audit_log))
            
            # Comparative Score Display
            prof_raw = st.session_state.raw_profile
            prof_clean = st.session_state.clean_profile
            
            c_col_r, c_col_c, c_col_d = st.columns(3)
            with c_col_r:
                st.metric("Raw Health Score", f"{prof_raw['health_score']}%")
            with c_col_c:
                delta_score = round(prof_clean['health_score'] - prof_raw['health_score'], 1)
                st.metric("Cleaned Health Score", f"{prof_clean['health_score']}%", delta=f"+{delta_score}%" if delta_score > 0 else f"{delta_score}%")
            with c_col_d:
                dropped_rows = prof_raw["total_rows"] - prof_clean["total_rows"]
                st.metric("Records Pruned", f"{dropped_rows} rows", delta=f"-{dropped_rows}" if dropped_rows > 0 else "0")
                
            # Comparative Preview tabs
            pv1, pv2 = st.tabs(["📈 Processed Dataset Preview", "📋 Raw Dataset Preview"])
            with pv1:
                st.dataframe(st.session_state.cleaned_df.head(15), use_container_width=True)
            with pv2:
                st.dataframe(st.session_state.raw_df.head(15), use_container_width=True)

# ----------------------------------------------------
# MODULE 3: INTERACTIVE ANALYTICS
# ----------------------------------------------------
elif navigation == "📈 Interactive Analytics":
    st.header("📈 Interactive Visual Analytics Builder")
    
    # Use cleaned data if available, otherwise raw
    active_df = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else st.session_state.raw_df
    
    if active_df is None:
        st.info("No data in workspace. Please import data to unlock analytics.")
    else:
        st.caption(f"Currently plotting: **{'Cleaned Dataset' if st.session_state.cleaned_df is not None else 'Raw Ingested Dataset'}**")
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        plot_type = st.selectbox(
            "Select Chart Layout Template", 
            ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram / Frequency Distribution", "Outlier Box Plot", "Correlation Matrix Heatmap"]
        )
        
        num_cols = [c for c in active_df.columns if pd.api.types.is_numeric_dtype(active_df[c])]
        cat_cols = [c for c in active_df.columns if not pd.api.types.is_numeric_dtype(active_df[c])]
        
        if plot_type == "Bar Chart":
            a_col1, a_col2, a_col3 = st.columns(3)
            with a_col1:
                x_col = st.selectbox("X-Axis (Categories)", cat_cols + num_cols)
            with a_col2:
                y_col = st.selectbox("Y-Axis (Metrics)", num_cols)
            with a_col3:
                color_col = st.selectbox("Color Legend Grouping (Optional)", [None] + cat_cols)
                
            fig = px.bar(active_df, x=x_col, y=y_col, color=color_col, color_discrete_sequence=px.colors.qualitative.Prism, barmode="group")
            
        elif plot_type == "Line Chart":
            a_col1, a_col2, a_col3 = st.columns(3)
            with a_col1:
                x_col = st.selectbox("X-Axis (Time/Continuous)", active_df.columns)
            with a_col2:
                y_col = st.selectbox("Y-Axis (Metric value)", num_cols)
            with a_col3:
                color_col = st.selectbox("Color Grouping (Optional)", [None] + cat_cols)
                
            fig = px.line(active_df, x=x_col, y=y_col, color=color_col, color_discrete_sequence=px.colors.qualitative.Prism)
            
        elif plot_type == "Scatter Plot":
            a_col1, a_col2, a_col3 = st.columns(3)
            with a_col1:
                x_col = st.selectbox("X-Axis (Numeric)", num_cols)
            with a_col2:
                y_col = st.selectbox("Y-Axis (Numeric)", num_cols)
            with a_col3:
                color_col = st.selectbox("Color Grouping (Optional)", [None] + cat_cols)
                
            fig = px.scatter(active_df, x=x_col, y=y_col, color=color_col, color_discrete_sequence=px.colors.qualitative.Prism, size_max=15)
            
        elif plot_type == "Histogram / Frequency Distribution":
            a_col1, a_col2, a_col3 = st.columns(3)
            with a_col1:
                x_col = st.selectbox("Target Metric Variable", num_cols)
            with a_col2:
                bins = st.slider("Bin Details Count", min_value=5, max_value=100, value=20)
            with a_col3:
                color_col = st.selectbox("Color Breakdown (Optional)", [None] + cat_cols)
                
            fig = px.histogram(active_df, x=x_col, nbins=bins, color=color_col, color_discrete_sequence=px.colors.qualitative.Prism)
            
        elif plot_type == "Outlier Box Plot":
            a_col1, a_col2 = st.columns(2)
            with a_col1:
                y_col = st.selectbox("Numeric Spread Metric", num_cols)
            with a_col2:
                x_col = st.selectbox("Categorical Groups (Optional)", [None] + cat_cols)
                
            fig = px.box(active_df, x=x_col, y=y_col, color=x_col, color_discrete_sequence=px.colors.qualitative.Prism)
            
        elif plot_type == "Correlation Matrix Heatmap":
            if len(num_cols) < 2:
                st.warning("Heatmap requires at least 2 numerical columns.")
                fig = None
            else:
                corr = active_df[num_cols].corr()
                fig = go.Figure(data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.columns,
                    colorscale="Viridis",
                    zmin=-1, zmax=1
                ))
                fig.update_layout(title="Correlation Coefficient Matrix", width=700, height=500)
                
        if fig is not None:
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=40, r=40, t=40, b=40)
            )
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(226, 232, 240, 0.4)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(226, 232, 240, 0.4)')
            st.plotly_chart(fig, use_container_width=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# MODULE 4: REPORT & EXPORT CENTER
# ----------------------------------------------------
elif navigation == "📥 Report & Export Center":
    st.header("📥 Report Generation & Clean Dataset Export")
    
    if st.session_state.cleaned_df is None:
        st.info("No cleaned dataset is ready. Ingest a dataset and apply clean filters to compile audit reports.")
    else:
        st.caption(f"File active: **{st.session_state.filename}**")
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#1E1B4B;'>Generate Executive Data Health Report</h4>", unsafe_allow_html=True)
        st.markdown(
            """
            Clicking the button below compiles a publication-ready multi-page **PDF Executive Report**. 
            It contains a summary health index progression grid, a structured step-by-step cleaning audit log, 
            and complete frequency breakdown/missing value graphics.
            """
        )
        
        pdf_filename = f"{os.path.splitext(st.session_state.filename)[0]}_health_report.pdf"
        pdf_output_path = os.path.join(BASE_DIR, "data", "processed", pdf_filename)
        
        if st.button("📄 Compile Executive PDF Report"):
            with st.spinner("Compiling pages, formatting metrics, and drawing visual charts..."):
                try:
                    # Run create_pdf_report on the cached profile states
                    create_pdf_report(
                        raw_profile=st.session_state.raw_profile,
                        clean_profile=st.session_state.clean_profile,
                        audit_log=st.session_state.cleaner.audit_log,
                        cleaned_df=st.session_state.cleaned_df,
                        output_pdf_path=pdf_output_path
                    )
                    st.success(f"Report compiled successfully and saved to: `{pdf_output_path}`!")
                    
                    # Provide immediate browser download
                    with open(pdf_output_path, "rb") as f:
                        pdf_data = f.read()
                        
                    st.download_button(
                        label="📥 Download Compiled PDF Report",
                        data=pdf_data,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error compiling report: {e}")
                    
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Data Export grid
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#1E1B4B;'>Export Standardized Data Files</h4>", unsafe_allow_html=True)
        
        ex_col1, ex_col2 = st.columns(2)
        
        # CSV Export
        with ex_col1:
            st.markdown("##### CSV (Comma Separated Values)")
            st.caption("Best suited for direct import into python pipelines, cloud databases, and text editors.")
            
            csv_buffer = BytesIO()
            st.session_state.cleaned_df.to_csv(csv_buffer, index=False)
            
            st.download_button(
                label="📥 Export Cleaned CSV",
                data=csv_buffer.getvalue(),
                file_name=f"{os.path.splitext(st.session_state.filename)[0]}_cleaned.csv",
                mime="text/csv"
            )
            
        # Excel Export
        with ex_col2:
            st.markdown("##### Microsoft Excel Spreadsheet")
            st.caption("Pre-formatted columns, ready for instant corporate distributions and manual analysis.")
            
            excel_buffer = BytesIO()
            # Suppress openpyxl warnings
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                st.session_state.cleaned_df.to_excel(writer, index=False, sheet_name="Cleaned Data")
                
            st.download_button(
                label="📥 Export Cleaned Excel (.xlsx)",
                data=excel_buffer.getvalue(),
                file_name=f"{os.path.splitext(st.session_state.filename)[0]}_cleaned.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        st.markdown("</div>", unsafe_allow_html=True)
