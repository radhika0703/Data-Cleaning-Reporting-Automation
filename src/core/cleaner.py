import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Tuple, Optional

# Setup logger
logger = logging.getLogger("DataCleaner")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DataCleaner:
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def log_step(self, step_name: str, details: str, rows_affected: int = 0, columns_affected: int = 0):
        """Records a cleaning step for reporting and visual compliance logs."""
        log_entry = {
            "step": len(self.audit_log) + 1,
            "operation": step_name,
            "details": details,
            "rows_affected": rows_affected,
            "columns_affected": columns_affected
        }
        self.audit_log.append(log_entry)
        logger.info(f"[{step_name}] {details} (Rows affected: {rows_affected}, Cols affected: {columns_affected})")

    def profile_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Profiles the dataset and calculates detailed health diagnostics.
        """
        total_rows = len(df)
        total_cols = len(df.columns)
        
        # Missing values profile
        missing_counts = df.isnull().sum().to_dict()
        missing_pct = {k: round((v / total_rows) * 100, 2) if total_rows > 0 else 0.0 for k, v in missing_counts.items()}
        
        # Duplicate profile
        duplicate_count = int(df.duplicated().sum())
        
        # Data types and unique value count
        types = {col: str(dtype) for col, dtype in df.dtypes.items()}
        unique_counts = {col: int(df[col].nunique(dropna=True)) for col in df.columns}
        
        # Outliers profile
        outlier_counts = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                col_clean = df[col].dropna()
                if len(col_clean) > 0:
                    q1 = col_clean.quantile(0.25)
                    q3 = col_clean.quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    outliers = col_clean[(col_clean < lower_bound) | (col_clean > upper_bound)]
                    outlier_counts[col] = len(outliers)
                else:
                    outlier_counts[col] = 0
            else:
                outlier_counts[col] = 0
                
        # Calculate overall health score (0-100 scale)
        # Based on missing values, duplicate percentage, and outliers relative to dataset size
        if total_rows > 0 and total_cols > 0:
            total_elements = total_rows * total_cols
            total_missing = sum(missing_counts.values())
            total_outliers = sum(outlier_counts.values())
            
            missing_factor = (total_missing / total_elements) * 40 # Up to 40% deduction
            duplicate_factor = (duplicate_count / total_rows) * 30 # Up to 30% deduction
            outlier_factor = (total_outliers / total_elements) * 30 # Up to 30% deduction
            
            health_score = max(0, round(100 - (missing_factor + duplicate_factor + outlier_factor), 1))
        else:
            health_score = 0.0

        return {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "missing_counts": missing_counts,
            "missing_percentages": missing_pct,
            "duplicate_count": duplicate_count,
            "column_types": types,
            "unique_counts": unique_counts,
            "outlier_counts": outlier_counts,
            "health_score": health_score
        }

    def remove_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None, keep: str = 'first') -> pd.DataFrame:
        """
        Removes duplicate rows based on all or a subset of columns.
        """
        initial_rows = len(df)
        df_cleaned = df.drop_duplicates(subset=subset, keep=keep)
        rows_dropped = initial_rows - len(df_cleaned)
        
        details = f"Removed duplicate rows based on {'all columns' if subset is None else str(subset)}. Kept: '{keep}'."
        self.log_step("Remove Duplicates", details, rows_affected=rows_dropped)
        return df_cleaned

    def parse_numeric(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Cleans and normalizes columns into proper numeric floats/ints.
        Handles currency symbols, commas, percent signs, and spaces.
        """
        df_cleaned = df.copy()
        
        for col in columns:
            if col not in df_cleaned.columns:
                continue
            
            initial_nulls = df_cleaned[col].isnull().sum()
            
            # Convert series to string representation to do string replacement operations
            raw_series = df_cleaned[col].astype(str)
            
            # Standardize common symbols
            cleaned_series = (
                raw_series.str.replace(r'[$\u20ac\u00a3\s,]', '', regex=True) # remove $, €, £, spaces, commas
                .str.replace('%', '', regex=False) # remove %
                .replace(['nan', 'None', 'null', '?', '-', 'unknown'], np.nan)
            )
            
            # Parse to numeric (coerce unparseable to NaN)
            converted = pd.to_numeric(cleaned_series, errors='coerce')
            
            # For percentages, scale down by 100 if the raw value contained a percentage sign
            pct_mask = raw_series.str.contains('%', na=False)
            converted.loc[pct_mask] = converted.loc[pct_mask] / 100.0
            
            df_cleaned[col] = converted
            final_nulls = df_cleaned[col].isnull().sum()
            coerced_count = final_nulls - initial_nulls
            
            details = f"Normalized and parsed column '{col}' to numeric. Coerced {coerced_count} invalid entries to NaN."
            self.log_step("Numeric Parsing", details, rows_affected=coerced_count)
            
        return df_cleaned

    def parse_datetimes(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Intelligently parses mixed date formats, converting them to standard ISO YYYY-MM-DD.
        """
        df_cleaned = df.copy()
        
        for col in columns:
            if col not in df_cleaned.columns:
                continue
                
            initial_nulls = df_cleaned[col].isnull().sum()
            
            # Safe parsing utilizing pd.to_datetime with format='mixed' if pandas version supports it
            # Otherwise fall back to regular coerced parsing
            try:
                converted = pd.to_datetime(df_cleaned[col], format='mixed', errors='coerce')
            except Exception:
                converted = pd.to_datetime(df_cleaned[col], errors='coerce')
                
            df_cleaned[col] = converted.dt.date # Keep ISO date format (YYYY-MM-DD)
            final_nulls = df_cleaned[col].isnull().sum()
            coerced_count = final_nulls - initial_nulls
            
            details = f"Parsed mixed date format in column '{col}' to ISO YYYY-MM-DD. Coerced {coerced_count} unparseable entries to NaT."
            self.log_step("Datetime Standardization", details, rows_affected=coerced_count)
            
        return df_cleaned

    def standardize_text(self, df: pd.DataFrame, columns: List[str], casing: str = 'title', strip: bool = True) -> pd.DataFrame:
        """
        Normalizes text fields (strips trailing spaces, handles mixed casing).
        """
        df_cleaned = df.copy()
        
        for col in columns:
            if col not in df_cleaned.columns:
                continue
                
            initial_series = df_cleaned[col].copy()
            
            # Only perform string operations on non-null values
            non_null_mask = df_cleaned[col].notnull()
            series_str = df_cleaned[col].astype(str)
            
            if strip:
                series_str = series_str.str.strip()
                
            if casing == 'lower':
                series_str = series_str.str.lower()
            elif casing == 'upper':
                series_str = series_str.str.upper()
            elif casing == 'title':
                series_str = series_str.str.title()
                
            # Replace empty space cells with NaN
            series_str = series_str.replace(['', 'Nan', 'None', 'Null', 'N/A'], np.nan)
            
            df_cleaned.loc[non_null_mask, col] = series_str.loc[non_null_mask]
            
            # Count changes
            changed_mask = initial_series != df_cleaned[col]
            rows_changed = int(changed_mask.sum())
            
            details = f"Standardized text column '{col}' to {casing} casing (trimmed whitespace: {strip})."
            self.log_step("Text Standardization", details, rows_affected=rows_changed)
            
        return df_cleaned

    def impute_missing(self, df: pd.DataFrame, columns: List[str], strategy: str = 'median', fill_value: Any = None) -> pd.DataFrame:
        """
        Imputes missing values in specified columns using diverse statistical techniques.
        """
        df_cleaned = df.copy()
        
        for col in columns:
            if col not in df_cleaned.columns:
                continue
                
            null_mask = df_cleaned[col].isnull()
            null_count = int(null_mask.sum())
            
            if null_count == 0:
                continue
                
            if strategy == 'mean':
                val = df_cleaned[col].mean()
                df_cleaned.loc[null_mask, col] = val
            elif strategy == 'median':
                val = df_cleaned[col].median()
                df_cleaned.loc[null_mask, col] = val
            elif strategy == 'mode':
                val = df_cleaned[col].mode().iloc[0] if not df_cleaned[col].mode().empty else "Unknown"
                df_cleaned.loc[null_mask, col] = val
            elif strategy == 'constant':
                val = fill_value if fill_value is not None else ("Unknown" if df_cleaned[col].dtype == object else 0)
                df_cleaned.loc[null_mask, col] = val
            elif strategy == 'ffill':
                df_cleaned[col] = df_cleaned[col].ffill()
                val = "Forward Fill"
            elif strategy == 'bfill':
                df_cleaned[col] = df_cleaned[col].bfill()
                val = "Backward Fill"
            elif strategy == 'drop':
                df_cleaned = df_cleaned.dropna(subset=[col])
                val = "Dropped Rows"
                
            details = f"Imputed {null_count} missing values in '{col}' using strategy: '{strategy}' (value: {val})."
            self.log_step("Missing Value Imputation", details, rows_affected=null_count if strategy != 'drop' else null_count)
            
        return df_cleaned

    def handle_outliers(self, df: pd.DataFrame, columns: List[str], method: str = 'iqr', action: str = 'clip', threshold: float = 1.5) -> pd.DataFrame:
        """
        Detects and resolves numeric outliers using standard statistical rules (IQR or Z-Score).
        """
        df_cleaned = df.copy()
        
        for col in columns:
            if col not in df_cleaned.columns or not pd.api.types.is_numeric_dtype(df_cleaned[col]):
                continue
                
            col_series = df_cleaned[col].dropna()
            if len(col_series) == 0:
                continue
                
            if method == 'iqr':
                q1 = col_series.quantile(0.25)
                q3 = col_series.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
            else: # z-score
                mean = col_series.mean()
                std = col_series.std()
                lower = mean - threshold * std
                upper = mean + threshold * std
                
            outlier_mask = (df_cleaned[col] < lower) | (df_cleaned[col] > upper)
            outlier_count = int(outlier_mask.sum())
            
            if outlier_count == 0:
                continue
                
            if action == 'clip':
                df_cleaned[col] = df_cleaned[col].clip(lower, upper)
                details = f"Clipped {outlier_count} outliers in '{col}' to range [{lower:.2f}, {upper:.2f}] using {method.upper()}."
            elif action == 'drop':
                df_cleaned = df_cleaned[~outlier_mask]
                details = f"Dropped {outlier_count} outlier rows in '{col}' using {method.upper()}."
            elif action == 'replace_median':
                median_val = col_series.median()
                df_cleaned.loc[outlier_mask, col] = median_val
                details = f"Replaced {outlier_count} outliers in '{col}' with median ({median_val:.2f}) using {method.upper()}."
                
            self.log_step("Outlier Handling", details, rows_affected=outlier_count)
            
        return df_cleaned

    def standardize_categories(self, df: pd.DataFrame, column: str, mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Maps inconsistent category tags to unified standard values.
        E.g. {'elec': 'Electronics', 'Home and Kitchen': 'Home & Kitchen'}
        """
        df_cleaned = df.copy()
        if column not in df_cleaned.columns:
            return df_cleaned
            
        initial_series = df_cleaned[column].copy()
        
        # Apply exact mapping case-insensitively
        def map_val(val):
            if pd.isnull(val):
                return val
            val_str = str(val).strip()
            # Try matching exactly
            if val_str in mapping:
                return mapping[val_str]
            # Try matching case-insensitively
            for k, v in mapping.items():
                if val_str.lower() == k.lower():
                    return v
            return val_str
            
        df_cleaned[column] = df_cleaned[column].apply(map_val)
        
        changed_mask = initial_series != df_cleaned[column]
        rows_changed = int(changed_mask.sum())
        
        details = f"Standardized values in category column '{column}' using dictionary mapping."
        self.log_step("Category Standardization", details, rows_affected=rows_changed)
        return df_cleaned
