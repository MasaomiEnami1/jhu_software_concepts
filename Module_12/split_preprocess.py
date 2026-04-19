import pandas as pd
import numpy as np
import json
import warnings
from sklearn.model_selection import train_test_split

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# =====================================================================
# STEP 1: DATA PREPARATION (Carried over to make script runnable)
# =====================================================================
def load_and_prepare_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            df = pd.DataFrame(data)
        except json.JSONDecodeError:
            f.seek(0)
            df = pd.DataFrame([json.loads(line) for line in f if line.strip()])
            
    rename_map = {'outcome': 'applicant_status', 'Degree': 'masters_or_phd', 'US/International': 'citizenship', 'GPA': 'gpa', 'GRE': 'gre', 'GRE V': 'gre_v', 'GRE AW': 'gre_aw'}
    df = df.rename(columns=rename_map)

    df = df[(df['applicant_status'].isin(['Accepted', 'Rejected'])) & (df['masters_or_phd'].isin(['Masters', 'PhD']))].copy()
    
    numeric_columns = ['gpa', 'gre', 'gre_v', 'gre_aw']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # We will NOT drop NaNs here as the assignment specifically asks us to fill them with medians later.
    
    df['ms_vs_phd'] = df['masters_or_phd'].map({'PhD': 1.0, 'Masters': 0.0})
    df['international_vs_local'] = df['citizenship'].map({'International': 1.0, 'Local/American': 0.0, 'American': 0.0, 'US': 0.0})
    df['target'] = df['applicant_status'].map({'Accepted': 1.0, 'Rejected': 0.0})
    
    # Only drop rows where the binary mapping failed or target is missing
    df = df.dropna(subset=['ms_vs_phd', 'international_vs_local', 'target'])
    
    return df

# =====================================================================
# STEP 2: SPLIT AND PREPROCESS (Assignment implementation)
# =====================================================================
if __name__ == "__main__":
    filepath = "cleaned_gradcafe.json"
    df = load_and_prepare_data(filepath)
    
    features = ['gpa', 'gre', 'gre_v', 'gre_aw', 'ms_vs_phd', 'international_vs_local']
    
    # Convert to NumPy arrays for mathematical operations
    X = df[features].values
    y = df['target'].values
    
    # 1. Split the data
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=42, 
        shuffle=True
    )
    
    # 2. Compute the median of each feature using the training set only
    # np.nanmedian calculates the median while ignoring any existing NaNs
    train_medians = np.nanmedian(X_train_raw, axis=0)
    
    # 3. Fill missing values in both sets using training medians
    # Find indices where values are NaN
    train_nan_indices = np.where(np.isnan(X_train_raw))
    test_nan_indices = np.where(np.isnan(X_test_raw))
    
    # Replace NaNs with the corresponding feature's median
    X_train_raw[train_nan_indices] = np.take(train_medians, train_nan_indices[1])
    X_test_raw[test_nan_indices] = np.take(train_medians, test_nan_indices[1])
    
    # 4. Compute the mean and standard deviation using the training set only
    train_means = np.mean(X_train_raw, axis=0)
    train_stds = np.std(X_train_raw, axis=0)
    
    # 5. Failsafe: Replace standard deviation of 0 with 1
    train_stds[train_stds == 0] = 1.0
    
    # 6. Standardize both sets
    X_train_scaled = (X_train_raw - train_means) / train_stds
    X_test_scaled = (X_test_raw - train_means) / train_stds
    
    # =====================================================================
    # REQUIRED ASSIGNMENT OUTPUT
    # =====================================================================
    print("\n" + "="*50)
    print("DATA SPLIT AND PREPROCESSING RESULTS")
    print("="*50)
    print(f"Training set size: {X_train_scaled.shape[0]} rows")
    print(f"Test set size: {X_test_scaled.shape[0]} rows")
    print("-" * 50)
    
    print("Training-set medians (used for imputation):")
    for name, median in zip(features, train_medians):
        print(f"  {name}: {median}")
        
    print("-" * 50)
    print("Training-set means (used for scaling):")
    for name, mean in zip(features, train_means):
        print(f"  {name}: {mean:.4f}")
        
    print("-" * 50)
    print("Training-set standard deviations (used for scaling):")
    for name, std in zip(features, train_stds):
        print(f"  {name}: {std:.4f}")
    print("="*50 + "\n")