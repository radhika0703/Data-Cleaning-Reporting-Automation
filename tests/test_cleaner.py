import unittest
import pandas as pd
import numpy as np
from src.core.cleaner import DataCleaner

class TestDataCleaner(unittest.TestCase):
    def setUp(self):
        self.cleaner = DataCleaner()
        # Mock dataset with various messy artifacts
        self.raw_data = pd.DataFrame({
            "ID": ["TXN01", "TXN02", "TXN02", "TXN03", "TXN04"], # Duplicates present
            "Date": ["2026-05-01", "15/05/2026", "2026-05-02", "InvalidDate", "2026.05.04"], # Mixed and corrupted dates
            "Category": ["elec", "Electronics", "elec", " Clothing ", np.nan], # Whitespaces, inconsistent categories
            "Price": ["$120.00", "€45.50", " $ 120.00 ", "unknown", "$2,000.99"], # Comma, currency symbols, unknown values
            "Quantity": [1.0, -2.0, 1.0, 150.0, np.nan], # Negatives, floats as integers, massive outlier, missing values
            "Discount": ["10%", "0.15", "10%", "NaN", "500%"] # Percentages, decimals, outliers
        })

    def test_remove_duplicates(self):
        df = self.raw_data.copy()
        df_cleaned = self.cleaner.remove_duplicates(df, subset=None, keep='first')
        
        # Expected: Index 2 is an exact duplicate of Index 0 except for Date format representing another date, but wait, 
        # let's see which rows are exact duplicates. Rows 0 and 2 have ID=TXN01/TXN02...
        # Wait, TXN02 at Row 1 and Row 2 have Date "02/05/2026" and "2026-05-02" which represent the same date,
        # but let's test if subset matches:
        df_cleaned_subset = self.cleaner.remove_duplicates(df, subset=["ID"], keep='first')
        self.assertEqual(len(df_cleaned_subset), 4) # Should drop 1 duplicate ID
        self.assertEqual(self.cleaner.audit_log[-1]["rows_affected"], 1)

    def test_parse_numeric(self):
        df = self.raw_data.copy()
        df_cleaned = self.cleaner.parse_numeric(df, ["Price", "Quantity", "Discount"])
        
        # Dollar currency, space currency, Euro check
        self.assertAlmostEqual(df_cleaned.loc[0, "Price"], 120.0)
        self.assertAlmostEqual(df_cleaned.loc[1, "Price"], 45.5) # Euro converted
        self.assertTrue(pd.isna(df_cleaned.loc[3, "Price"])) # unknown coerced to NaN
        self.assertAlmostEqual(df_cleaned.loc[4, "Price"], 2000.99) # commas stripped
        
        # Percentages check
        self.assertAlmostEqual(df_cleaned.loc[0, "Discount"], 0.1) # '10%' -> 0.1
        self.assertAlmostEqual(df_cleaned.loc[1, "Discount"], 0.15) # '0.15' -> 0.15
        self.assertAlmostEqual(df_cleaned.loc[4, "Discount"], 5.0) # '500%' -> 5.0

    def test_parse_datetimes(self):
        df = self.raw_data.copy()
        df_cleaned = self.cleaner.parse_datetimes(df, ["Date"])
        
        # Verify valid dates are structured as dates
        self.assertEqual(str(df_cleaned.loc[0, "Date"]), "2026-05-01")
        # mixed parsing checks 15/05/2026 -> 2026-05-15
        self.assertEqual(str(df_cleaned.loc[1, "Date"]), "2026-05-15")
        # invalid coerced
        self.assertTrue(pd.isna(df_cleaned.loc[3, "Date"]))

    def test_standardize_text(self):
        df = self.raw_data.copy()
        df_cleaned = self.cleaner.standardize_text(df, ["Category"], casing="title", strip=True)
        
        self.assertEqual(df_cleaned.loc[3, "Category"], "Clothing") # Spaces stripped
        self.assertEqual(df_cleaned.loc[0, "Category"], "Elec") # casing check

    def test_impute_missing(self):
        df = self.raw_data.copy()
        # Pre-parse numeric to populate np.nan correctly
        df = self.cleaner.parse_numeric(df, ["Quantity"])
        
        # Median imputation
        # Quantity parsed: [1.0, -2.0, 1.0, 150.0, NaN] -> Med = 1.0
        df_imputed = self.cleaner.impute_missing(df, ["Quantity"], strategy="median")
        self.assertEqual(df_imputed.loc[4, "Quantity"], 1.0)
        
        # Drop strategy
        df_dropped = self.cleaner.impute_missing(df, ["Quantity"], strategy="drop")
        self.assertEqual(len(df_dropped), 4)

    def test_handle_outliers(self):
        df = self.raw_data.copy()
        df = self.cleaner.parse_numeric(df, ["Quantity"])
        # Quantity: [1.0, -2.0, 1.0, 150.0, NaN]
        # IQR limits for [1.0, -2.0, 1.0, 150.0]:
        # Q1 = 0.25, Q3 = 38.25, IQR = 38.0. Upper = 38.25 + 1.5*38 = 95.25. Lower = 0.25 - 57 = -56.75
        # 150 is outlier.
        
        df_clipped = self.cleaner.handle_outliers(df, ["Quantity"], method="iqr", action="clip", threshold=1.5)
        # Verify 150 got clipped to upper bound
        self.assertLess(df_clipped.loc[3, "Quantity"], 150.0)
        self.assertGreater(df_clipped.loc[3, "Quantity"], 38.0)

if __name__ == "__main__":
    unittest.main()
