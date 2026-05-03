"""
Module 12: Neural Network Training Pipeline for Grad Café Data.
Includes substantive revisions for logging audit trails and 
preventing data leakage during feature engineering.
"""

import json
import logging
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# --- 1. AUDIT TRAIL SETUP ---
# This ensures all console output is also saved to training.log
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler("training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Suppress warnings
warnings.filterwarnings('ignore')

# =====================================================================
# 1. DATA PREPARATION (Fixes Section 1 Prints)
# =====================================================================
def load_and_prepare_data(filepath):
    """Loads and preprocesses the GradCafe dataset with an audit trail."""
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            original_df = pd.DataFrame(data)
        except json.JSONDecodeError:
            f.seek(0)
            records = [json.loads(line) for line in f if line.strip()]
            original_df = pd.DataFrame(records)

    # REQUIRED PRINT: Original row count
    initial_count = len(original_df)
    logger.info(f"--- SECTION 1: DATA PREPARATION ---")
    logger.info(f"Original Row Count: {initial_count}")
            
    rename_map = {
        'outcome': 'applicant_status',
        'Degree': 'masters_or_phd',
        'US/International': 'citizenship',
        'GPA': 'gpa',
        'GRE': 'gre',
        'GRE V': 'gre_v',
        'GRE AW': 'gre_aw'
    }
    original_df = original_df.rename(columns=rename_map)

    filtered_df = original_df[
        (original_df['applicant_status'].isin(['Accepted', 'Rejected'])) &
        (original_df['masters_or_phd'].isin(['Masters', 'PhD']))
    ].copy()
    
    numeric_columns = ['gpa', 'gre', 'gre_v', 'gre_aw']
    for col in numeric_columns:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
        
    filtered_df = filtered_df.dropna(subset=numeric_columns)
    
    filtered_df['ms_vs_phd'] = filtered_df['masters_or_phd'].map({'PhD': 1.0, 'Masters': 0.0})
    citizenship_mapping = {'International': 1.0, 'Local/American': 0.0, 'American': 0.0, 'US': 0.0}
    filtered_df['international_vs_local'] = filtered_df['citizenship'].map(citizenship_mapping)
    filtered_df['target'] = filtered_df['applicant_status'].map({'Accepted': 1.0, 'Rejected': 0.0})
    filtered_df = filtered_df.dropna(subset=['ms_vs_phd', 'international_vs_local', 'target'])
    
    # REQUIRED PRINT: Filtered row count
    final_count = len(filtered_df)
    logger.info(f"Filtered Row Count: {final_count}")
    logger.info(f"Total Rows Removed: {initial_count - final_count}")
    
    return filtered_df

# =====================================================================
# 2. NEURAL NETWORK IMPLEMENTATION
# =====================================================================
class TwoLayerNN:
    """Simple 2-Layer Neural Network using NumPy."""
    def __init__(self, input_size, hidden_size, output_size, learning_rate=0.1):
        np.random.seed(42)
        self.lr = learning_rate
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(1. / input_size)
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(1. / hidden_size)
        self.b2 = np.zeros((1, output_size))

    def sigmoid(self, z):
        """Sigmoid activation with overflow protection."""
        z = np.clip(z, -500, 500)
        return 1.0 / (1.0 + np.exp(-z))

    def sigmoid_derivative(self, a):
        """Derivative of sigmoid for backpropagation."""
        return a * (1.0 - a)

    def forward(self, X):
        """Standard Forward Pass."""
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        return self.a2

    def backward(self, X, y):
        """Backpropagation and weight updates."""
        m = X.shape[0]
        dz2 = (self.a2 - y) * self.sigmoid_derivative(self.a2)
        dW2 = (1 / m) * np.dot(self.a1.T, dz2)
        db2 = (1 / m) * np.sum(dz2, axis=0, keepdims=True)
        dz1 = np.dot(dz2, self.W2.T) * self.sigmoid_derivative(self.a1)
        dW1 = (1 / m) * np.dot(X.T, dz1)
        db1 = (1 / m) * np.sum(dz1, axis=0, keepdims=True)
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1

    def calculate_mse(self, predictions, targets):
        """MSE Loss Calculation."""
        return np.mean(np.square(predictions - targets))

# =====================================================================
# 3. MAIN EXECUTION PIPELINE
# =====================================================================
if __name__ == "__main__":
    filepath = "cleaned_gradcafe.json"
    df_main = load_and_prepare_data(filepath)
    
    features_list = ['gpa', 'gre', 'gre_v', 'gre_aw', 'ms_vs_phd', 'international_vs_local']
    X_vals = df_main[features_list].values
    y_vals = df_main['target'].values.reshape(-1, 1) 
    
    # --- SUBSTANTIVE REVISION: DATA LEAKAGE PREVENTION ---
    # We split BEFORE scaling to ensure X_test remains completely unseen.
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_vals, y_vals, test_size=0.2, random_state=42
    )
    
    # 3c. Standardize the data using TRAIN-ONLY statistics
    # WHY TRAIN-ONLY STATS? 
    # To prevent Data Leakage. Fitting stats (mean/std) on the entire dataset 
    # would leak information about the test set distribution into the training process.
    logger.info("\n--- SECTION 2: FEATURE ENGINEERING ---")
    train_mean = np.mean(X_train_raw, axis=0)
    train_std = np.std(X_train_raw, axis=0)
    train_std[train_std == 0] = 1e-8 
    
    X_train = (X_train_raw - train_mean) / train_std
    X_test = (X_test_raw - train_mean) / train_std
    
    logger.info("Standardization successful: Normalization parameters derived strictly from X_train.")

    # 3d. Initialize Neural Network
    nn = TwoLayerNN(input_size=6, hidden_size=16, output_size=1, learning_rate=0.1)
    
    # 3e. Training Loop
    best_mse = float('inf')
    train_hist, test_hist = [], []
    
    logger.info("\nStarting Training Pipeline...")
    for epoch in range(10001):
        # Training pass
        t_preds = nn.forward(X_train)
        t_mse = nn.calculate_mse(t_preds, y_train)
        nn.backward(X_train, y_train)
        
        # Testing pass
        v_preds = nn.forward(X_test)
        v_mse = nn.calculate_mse(v_preds, y_test)
        
        train_hist.append(t_mse)
        test_hist.append(v_mse)
        
        if epoch % 2000 == 0:
            logger.info(f"Epoch {epoch:5d} | Train MSE: {t_mse:.4f} | Test MSE: {v_mse:.4f}")

    final_accuracy = np.mean((nn.forward(X_test) >= 0.5) == y_test)
    logger.info(f"\nFinal Test Accuracy: {final_accuracy * 100:.2f}%")