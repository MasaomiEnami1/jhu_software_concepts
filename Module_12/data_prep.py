import pandas as pd
import json
import warnings

# Suppress standard pandas warnings for a cleaner terminal output
warnings.filterwarnings('ignore')

def load_and_prepare_data(filepath):
    """
    Loads JSON data, maps the real column names to the assignment's expected names, 
    applies filtering, converts data types, and prepares features.
    """
    # 1. Load the JSON objects into a Pandas DataFrame
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            original_df = pd.DataFrame(data)
        except json.JSONDecodeError:
            f.seek(0)
            records = [json.loads(line) for line in f if line.strip()]
            original_df = pd.DataFrame(records)
            
    num_original_rows = len(original_df)
    
    # --- FIX THE COLUMN NAMES ---
    # Map the actual column names in your file to the names the assignment expects
    rename_map = {
        'outcome': 'applicant_status',
        'Degree': 'masters_or_phd',
        'US/International': 'citizenship',
        'GPA': 'gpa',
        'GRE': 'gre',
        'GRE V': 'gre_v',
        'GRE AW': 'gre_aw'
    }
    # Safely rename them
    original_df = original_df.rename(columns=rename_map)

    # 2. Filter the dataframe based on target status and program type
    # The assignment strictly requires keeping 'Accepted'/'Rejected' and 'Masters'/'PhD'
    filtered_df = original_df[
        (original_df['applicant_status'].isin(['Accepted', 'Rejected'])) &
        (original_df['masters_or_phd'].isin(['Masters', 'PhD']))
    ].copy()
    
    # 3. Convert string-valued numeric columns into floats
    numeric_columns = ['gpa', 'gre', 'gre_v', 'gre_aw']
    for col in numeric_columns:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
        
    # Drop rows that resulted in NaN during float conversion
    filtered_df = filtered_df.dropna(subset=numeric_columns)
    
    # 4. Create binary feature columns
    # ms_vs_phd: encode PhD = 1, Masters = 0
    filtered_df['ms_vs_phd'] = filtered_df['masters_or_phd'].map({'PhD': 1.0, 'Masters': 0.0})
    
    # international_vs_local: encode International = 1, Local/American = 0
    # Note: Adding 'American' and 'US' to the mapping just in case the raw data uses those instead of 'Local/American'
    citizenship_mapping = {
        'International': 1.0, 
        'Local/American': 0.0, 
        'American': 0.0, 
        'US': 0.0
    }
    filtered_df['international_vs_local'] = filtered_df['citizenship'].map(citizenship_mapping)
    
    # 5. Create the target variable
    # target: encode Accepted = 1, Rejected = 0
    filtered_df['target'] = filtered_df['applicant_status'].map({'Accepted': 1.0, 'Rejected': 0.0})
    
    # Drop any remaining NaNs in our mapped columns (in case of weird data artifacts)
    filtered_df = filtered_df.dropna(subset=['ms_vs_phd', 'international_vs_local', 'target'])
    
    # 6. Define exactly the 6 required model input features
    features = ['gpa', 'gre', 'gre_v', 'gre_aw', 'ms_vs_phd', 'international_vs_local']
    
    # Calculate required final output statistics
    num_filtered_rows = len(filtered_df)
    num_accepted = len(filtered_df[filtered_df['target'] == 1.0])
    num_rejected = len(filtered_df[filtered_df['target'] == 0.0])
    
    # 7. Print Required Output for Assignment Section 1
    print("\n" + "="*50)
    print("DATA PREPROCESSING RESULTS")
    print("="*50)
    print(f"Number of rows in the original dataset: {num_original_rows}")
    print(f"Number of rows remaining after filtering: {num_filtered_rows}")
    print(f"Number of Accepted rows: {num_accepted}")
    print(f"Number of Rejected rows: {num_rejected}")
    print("-" * 50)
    
    print("The names of the six final input features:")
    for feature in features:
        print(f"  - {feature}")
        
    print("-" * 50)
    print("First few rows of the cleaned dataframe:")
    
    # Reorder to show just the relevant inputs and the target
    final_columns_to_display = features + ['target']
    print(filtered_df[final_columns_to_display].head())
    print("="*50 + "\n")
    
    return filtered_df

if __name__ == "__main__":
    filepath = "cleaned_gradcafe.json"
    clean_data = load_and_prepare_data(filepath)