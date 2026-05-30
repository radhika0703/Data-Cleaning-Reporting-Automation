import os
import json
import pandas as pd
from typing import Dict, Any, Optional
from src.core.cleaner import DataCleaner
from src.core.reporter import create_pdf_report

class DataPipeline:
    def __init__(self, config_path: Optional[str] = None):
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = json.load(f)
        self.cleaner = DataCleaner()

    def run(self, input_path: str, output_data_path: str, output_report_path: str) -> Dict[str, Any]:
        """
        Executes the entire cleaning and reporting workflow from end-to-end.
        """
        # Load raw data
        if input_path.endswith('.xlsx') or input_path.endswith('.xls'):
            df = pd.read_excel(input_path)
        else:
            df = pd.read_csv(input_path)

        # Profile raw data
        raw_profile = self.cleaner.profile_data(df)
        
        df_clean = df.copy()

        # Step 1: Remove Duplicates
        dup_config = self.config.get("remove_duplicates", {})
        if dup_config.get("enabled", True):
            df_clean = self.cleaner.remove_duplicates(
                df_clean, 
                subset=dup_config.get("subset"), 
                keep=dup_config.get("keep", "first")
            )

        # Step 2: Parse Datetime Columns
        date_cols = self.config.get("datetime_columns", [])
        if date_cols:
            df_clean = self.cleaner.parse_datetimes(df_clean, date_cols)

        # Step 3: Parse Numeric Columns (Currencies, percentage scrubbing)
        numeric_cols = self.config.get("numeric_columns", [])
        if numeric_cols:
            df_clean = self.cleaner.parse_numeric(df_clean, numeric_cols)

        # Step 4: Text Standardization
        text_cols = self.config.get("text_columns", [])
        for t_cfg in text_cols:
            df_clean = self.cleaner.standardize_text(
                df_clean, 
                columns=[t_cfg["column"]], 
                casing=t_cfg.get("casing", "title"), 
                strip=t_cfg.get("strip", True)
            )

        # Step 5: Categorical Standardizations
        cat_mappings = self.config.get("categorical_mappings", [])
        for c_cfg in cat_mappings:
            df_clean = self.cleaner.standardize_categories(
                df_clean,
                column=c_cfg["column"],
                mapping=c_cfg["mapping"]
            )

        # Step 6: Missing Value Imputation
        imputations = self.config.get("imputations", [])
        for imp in imputations:
            df_clean = self.cleaner.impute_missing(
                df_clean,
                columns=[imp["column"]],
                strategy=imp.get("strategy", "median"),
                fill_value=imp.get("fill_value")
            )

        # Step 7: Outlier Trimming / Clipping
        outliers = self.config.get("outliers", [])
        for out in outliers:
            df_clean = self.cleaner.handle_outliers(
                df_clean,
                columns=[out["column"]],
                method=out.get("method", "iqr"),
                action=out.get("action", "clip"),
                threshold=out.get("threshold", 1.5)
            )

        # Profile clean data
        clean_profile = self.cleaner.profile_data(df_clean)

        # Save Cleaned Dataset
        os.makedirs(os.path.dirname(output_data_path), exist_ok=True)
        if output_data_path.endswith('.xlsx'):
            df_clean.to_excel(output_data_path, index=False)
        else:
            df_clean.to_csv(output_data_path, index=False)

        # Generate Automated PDF Report
        os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
        create_pdf_report(
            raw_profile=raw_profile,
            clean_profile=clean_profile,
            audit_log=self.cleaner.audit_log,
            cleaned_df=df_clean,
            output_pdf_path=output_report_path
        )

        return {
            "raw_profile": raw_profile,
            "clean_profile": clean_profile,
            "audit_log": self.cleaner.audit_log,
            "cleaned_rows": len(df_clean),
            "rows_dropped": raw_profile["total_rows"] - len(df_clean)
        }
