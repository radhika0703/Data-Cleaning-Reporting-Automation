import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_messy_dataset(output_path: str, num_rows: int = 200) -> pd.DataFrame:
    """
    Generates a realistic, highly inconsistent, and 'messy' e-commerce sales dataset
    for testing data cleaning and reporting workflows.
    """
    np.random.seed(42)
    random.seed(42)

    categories = ['Electronics', 'Home & Kitchen', 'Office Supplies', 'Clothing', 'Books']
    names = ['Liam Neeson', 'Olivia Rodrigo', 'Noah Centineo', 'Emma Watson', 'Oliver Twist', 
             'Ava Max', 'Elijah Wood', 'Charlotte Bronte', 'James Bond', 'Amelia Earhart']
    
    data = []
    
    # Generate base transaction IDs (with some duplicates)
    txn_ids = [f"TXN-{1000 + i}" for i in range(int(num_rows * 0.9))]
    # Pad to reach target rows with duplicates
    while len(txn_ids) < num_rows:
        txn_ids.append(random.choice(txn_ids[:50]))
    
    random.shuffle(txn_ids)
    
    for i in range(num_rows):
        row = {}
        row['Transaction_ID'] = txn_ids[i]
        
        # 1. Date - Mixed formats and missing values
        date_rand = random.random()
        base_date = datetime(2026, 1, 1) + timedelta(days=random.randint(0, 120))
        if date_rand < 0.08:
            row['Date'] = np.nan # Missing
        elif date_rand < 0.15:
            row['Date'] = "" # Empty string
        elif date_rand < 0.30:
            row['Date'] = base_date.strftime("%d/%m/%Y") # DD/MM/YYYY
        elif date_rand < 0.45:
            row['Date'] = base_date.strftime("%Y.%m.%d") # Dot notation
        elif date_rand < 0.60:
            row['Date'] = base_date.strftime("%B %d, %Y") # Month name format
        elif date_rand < 0.70:
            row['Date'] = base_date.strftime("%d-%b-%y") # DD-Mon-YY
        else:
            row['Date'] = base_date.strftime("%Y-%m-%d") # Standard ISO
            
        # 2. Customer Name - Inconsistent spacing, mixed casing, missing values
        name_rand = random.random()
        if name_rand < 0.06:
            row['Customer_Name'] = np.nan
        elif name_rand < 0.12:
            row['Customer_Name'] = "   " # Spaces only
        else:
            name = random.choice(names)
            if name_rand < 0.30:
                row['Customer_Name'] = f"  {name}  " # Leading/trailing spaces
            elif name_rand < 0.45:
                row['Customer_Name'] = name.lower() # All lower
            elif name_rand < 0.60:
                row['Customer_Name'] = name.upper() # All upper
            else:
                row['Customer_Name'] = name # Standard
                
        # 3. Product Category - Inconsistent naming, typos, casing
        cat_rand = random.random()
        if cat_rand < 0.05:
            row['Product_Category'] = np.nan
        elif cat_rand < 0.10:
            row['Product_Category'] = "unknown"
        else:
            cat = random.choice(categories)
            if cat == 'Electronics' and cat_rand < 0.30:
                row['Product_Category'] = 'elec' # Inconsistent abbreviation
            elif cat == 'Home & Kitchen' and cat_rand < 0.45:
                row['Product_Category'] = 'Home and Kitchen' # Spelling variation
            elif cat == 'Office Supplies' and cat_rand < 0.60:
                row['Product_Category'] = 'OFFICE SUPPLIES  ' # Casing/spaces
            else:
                row['Product_Category'] = cat
                
        # 4. Price - Currencies, commas, missing, corrupted strings
        price_rand = random.random()
        base_price = round(random.uniform(10.0, 1500.0), 2)
        if price_rand < 0.08:
            row['Price'] = np.nan
        elif price_rand < 0.15:
            row['Price'] = "null"
        elif price_rand < 0.25:
            row['Price'] = "-"
        elif price_rand < 0.40:
            row['Price'] = f"${base_price:,.2f}" # Currency dollar with commas
        elif price_rand < 0.55:
            row['Price'] = f"€{base_price * 0.9:,.2f}" # Euro currency
        elif price_rand < 0.70:
            row['Price'] = f" {base_price} " # Floating strings with spaces
        else:
            row['Price'] = base_price # Float
            
        # 5. Quantity - Missing, negatives, floats as ints, outliers
        qty_rand = random.random()
        if qty_rand < 0.08:
            row['Quantity'] = np.nan
        elif qty_rand < 0.15:
            row['Quantity'] = -random.randint(1, 5) # Inconsistent negative
        elif qty_rand < 0.25:
            row['Quantity'] = f"{random.randint(1, 10)}.0" # Decimal string
        elif qty_rand < 0.30:
            row['Quantity'] = 150 # High quantity outlier
        elif qty_rand < 0.35:
            row['Quantity'] = "three" # Word representations
        else:
            row['Quantity'] = random.randint(1, 10)
            
        # 6. Discount - Mixed formatting, percentages, out of range values
        disc_rand = random.random()
        if disc_rand < 0.10:
            row['Discount'] = np.nan
        elif disc_rand < 0.25:
            row['Discount'] = f"{random.randint(5, 30)}%" # Percentage string
        elif disc_rand < 0.40:
            row['Discount'] = round(random.uniform(0.05, 0.40), 2) # Proper decimal float
        elif disc_rand < 0.50:
            row['Discount'] = random.randint(5, 40) # Integer percentage
        elif disc_rand < 0.55:
            row['Discount'] = 9.99 # Large outlier discount (>100% or absolute value error)
        else:
            row['Discount'] = 0.0 # No discount
            
        # 7. Rating - Numbers, missing, outlier
        rating_rand = random.random()
        if rating_rand < 0.15:
            row['Rating'] = np.nan
        elif rating_rand < 0.20:
            row['Rating'] = 99.0 # Extreme outlier rating
        elif rating_rand < 0.25:
            row['Rating'] = 0.0 # Boundary low
        else:
            row['Rating'] = round(random.uniform(1.0, 5.0), 1)
            
        data.append(row)
        
    df = pd.DataFrame(data)
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Messy dataset generated successfully with {num_rows} rows at: {output_path}")
    return df

if __name__ == "__main__":
    # Generate default dataset for development
    raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw"))
    generate_messy_dataset(os.path.join(raw_dir, "sample_sales.csv"))
