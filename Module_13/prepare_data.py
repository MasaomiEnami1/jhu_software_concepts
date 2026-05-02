import pandas as pd
import numpy as np
import os

def load_and_clean_admissions_data(file_path):
    """
    Loads JSON admissions data and prepares it for a multimodal 
    binary classification task using exact keys from the dataset.
    """
    # 1. Load the dataset
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None

    try:
        df = pd.read_json(file_path)
    except ValueError:
        df = pd.read_json(file_path, lines=True)
        
    original_row_count = len(df)

    # --- 2. EXACT COLUMN MAPPING (Matching your JSON example) ---
    # We must use the exact casing and spaces found in your JSON
    STATUS_COL = 'status'            # e.g., "Rejected"
    
    # Required: At least two text-based fields
    TEXT_COLS = ['Program', 'comments'] 
    
    # Required: At least three non-text fields
    # We will use GPA, GRE, and GRE V (numeric) and Degree (categorical)
    NUMERIC_COLS = ['GPA', 'GRE', 'GRE V'] 
    CAT_COLS = ['Degree', 'US/International']

    # --- 3. FILTER STATUS ---
    # Ensure the status column exists and filter for Accepted/Rejected
    if STATUS_COL not in df.columns:
        print(f"Error: Column '{STATUS_COL}' not found. Check JSON keys.")
        return None

    # Handle missing status and filter
    df = df.dropna(subset=[STATUS_COL])
    
    # Mapping status to binary labels
    # We use case-insensitive matching just in case
    is_accepted = df[STATUS_COL].str.contains('Accepted', case=False, na=False)
    is_rejected = df[STATUS_COL].str.contains('Rejected', case=False, na=False)
    
    # Create the label: 1 for Accepted, 0 for Rejected
    df.loc[is_accepted, 'label'] = 1
    df.loc[is_rejected, 'label'] = 0
    
    # Drop rows that aren't clearly Accepted or Rejected
    df = df[df['label'].notna()].copy()
    df['label'] = df['label'].astype(int)

    # --- 4. DEDUPLICATE ---
    # Using URL as the unique identifier as per assignment instructions
    if 'url' in df.columns:
        df = df.drop_duplicates(subset=['url'])
    else:
        df = df.drop_duplicates()

    # --- 5. PREPROCESS TEXT FIELDS ---
    for col in TEXT_COLS:
        if col in df.columns:
            # fillna("None") prevents the tokenizer from crashing later
            df[col] = df[col].fillna("None").astype(str).str.strip()
        else:
            print(f"Warning: Text column '{col}' not found in JSON.")
            df[col] = "None"

    # --- 6. PREPROCESS NUMERIC FIELDS ---
    for col in NUMERIC_COLS:
        if col in df.columns:
            # Convert to numeric, non-numeric becomes NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Fill NaNs with the median of the column
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val if not np.isnan(median_val) else 0.0)
        else:
            print(f"Warning: Numeric column '{col}' not found in JSON.")
            df[col] = 0.0

    # --- 7. PREPROCESS CATEGORICAL FIELDS ---
    for col in CAT_COLS:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()
        else:
            print(f"Warning: Categorical column '{col}' not found in JSON.")
            df[col] = "Unknown"

    # Final count after cleaning
    final_count = len(df)
    
    # --- REQUIRED OUTPUT FOR ASSIGNMENT ---
    print("="*60)
    print("SECTION 1: DATA PREPARATION SUMMARY")
    print("="*60)
    print(f"Number of rows in original dataset:      {original_row_count}")
    print(f"Number of rows remaining after filtering: {final_count}")
    print(f"Number of Accepted rows (Label 1):       {len(df[df['label']==1])}")
    print(f"Number of Rejected rows (Label 0):       {len(df[df['label']==0])}")
    print("-" * 60)
    print("Fields used for modeling:")
    print(f"Text Fields:       {TEXT_COLS}")
    print(f"Non-text Fields:   {NUMERIC_COLS + CAT_COLS}")
    print("-" * 60)
    print("Preview of cleaned dataframe:")
    # Displaying the required fields in the preview
    display_cols = TEXT_COLS + NUMERIC_COLS + ['label']
    print(df[display_cols].head())
    print("="*60)
    
    return df

if __name__ == "__main__":
    # Ensure this matches your file name in Module_13
    INPUT_FILE = "cleaned_gradcafe.json"
    
    cleaned_df = load_and_clean_admissions_data(INPUT_FILE)
    
    if cleaned_df is not None and len(cleaned_df) > 0:
        # Save as CSV for easier loading into PyTorch/HuggingFace later
        cleaned_df.to_csv("processed_admissions.csv", index=False)
        print("\nSuccess: Processed data saved to 'processed_admissions.csv'")
    else:
        print("\nError: No data was processed. Check column names and status values.")