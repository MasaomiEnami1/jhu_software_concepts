import pandas as pd
import numpy as np
import json
import warnings
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# Suppress pandas warnings for a cleaner output
warnings.filterwarnings('ignore')

# =====================================================================
# HYPERPARAMETERS & CONFIGURATION
# =====================================================================
RANDOM_SEED = 42
HIDDEN_UNITS = 6
LEARNING_RATE = 0.05
MAX_EPOCHS = 10000
PATIENCE = 100
DATA_FILE = "cleaned_gradcafe.json"
LOG_FILE = "training.log"

def log_print(message, file_handle=None):
    """Utility to print to console and write to log file simultaneously."""
    print(message)
    if file_handle:
        file_handle.write(message + "\n")

# =====================================================================
# PREPROCESSING
# =====================================================================
def load_and_preprocess(filepath):
    # 1. Load Data safely (handling both JSON and JSONL)
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            df = pd.DataFrame(data)
        except json.JSONDecodeError:
            f.seek(0)
            df = pd.DataFrame([json.loads(line) for line in f if line.strip()])
            
    # 2. Rename columns to match assignment specification
    rename_map = {'outcome': 'applicant_status', 'Degree': 'masters_or_phd', 'US/International': 'citizenship', 'GPA': 'gpa', 'GRE': 'gre', 'GRE V': 'gre_v', 'GRE AW': 'gre_aw'}
    df = df.rename(columns=rename_map)
    
    # 3. Filter rows
    df = df[(df['applicant_status'].isin(['Accepted', 'Rejected'])) & (df['masters_or_phd'].isin(['Masters', 'PhD']))].copy()
    
    # 4. Convert string-valued numeric columns to floats
    numeric_columns = ['gpa', 'gre', 'gre_v', 'gre_aw']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # 5. Create binary feature columns
    df['ms_vs_phd'] = df['masters_or_phd'].map({'PhD': 1.0, 'Masters': 0.0})
    df['international_vs_local'] = df['citizenship'].map({'International': 1.0, 'Local/American': 0.0, 'American': 0.0, 'US': 0.0})
    df['target'] = df['applicant_status'].map({'Accepted': 1.0, 'Rejected': 0.0})
    
    # 6. Drop rows missing binary mapping targets
    df = df.dropna(subset=['ms_vs_phd', 'international_vs_local', 'target'])
    
    features = ['gpa', 'gre', 'gre_v', 'gre_aw', 'ms_vs_phd', 'international_vs_local']
    X = df[features].values
    y = df['target'].values.reshape(-1, 1) 
    
    # 7. Train/Test Split (Only scikit-learn usage)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, shuffle=True
    )
    
    # 8. Missing value imputation using training medians
    train_medians = np.nanmedian(X_train_raw, axis=0)
    for idx in range(X_train_raw.shape[1]):
        X_train_raw[np.isnan(X_train_raw[:, idx]), idx] = train_medians[idx]
        X_test_raw[np.isnan(X_test_raw[:, idx]), idx] = train_medians[idx]
        
    # 9. Standardization using training means and standard deviations
    train_means = np.mean(X_train_raw, axis=0)
    train_stds = np.std(X_train_raw, axis=0)
    train_stds[train_stds == 0] = 1.0 # Failsafe for zero division
    
    X_train_scaled = (X_train_raw - train_means) / train_stds
    X_test_scaled = (X_test_raw - train_means) / train_stds
    
    return X_train_scaled, X_test_scaled, y_train, y_test, train_means, train_stds

# =====================================================================
# NEURAL NETWORK IMPLEMENTATION (NumPy Only)
# =====================================================================
def sigmoid(x):
    """Sigmoid activation function with clipping to prevent overflow."""
    x = np.clip(x, -50, 50)
    return 1.0 / (1.0 + np.exp(-x))

def mse(y_true, y_pred):
    """Mean Squared Error loss function."""
    return np.mean((y_true - y_pred) ** 2)

class TwoLayerNet:
    """Rudimentary 2-layer neural net: input -> hidden(sigmoid) -> output(sigmoid)"""
    def __init__(self, input_dim, hidden_dim, seed=RANDOM_SEED):
        rng = np.random.default_rng(seed)
        
        # W1 dimension: (input_features, hidden_units)
        # b1 dimension: (1, hidden_units)
        self.W1 = rng.normal(0.0, 0.1, (input_dim, hidden_dim))
        self.b1 = np.zeros((1, hidden_dim))
        
        # W2 dimension: (hidden_units, 1 output unit)
        # b2 dimension: (1, 1 output unit)
        self.W2 = rng.normal(0.0, 0.1, (hidden_dim, 1))
        self.b2 = np.zeros((1, 1))

    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = sigmoid(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.y_hat = sigmoid(self.z2)
        return self.y_hat

    def backward(self, X, y, learning_rate):
        n = len(X)
        y = y.reshape(-1, 1)
        
        # MSE derivative through sigmoid output
        dz2 = (2.0 / n) * (self.y_hat - y) * self.y_hat * (1.0 - self.y_hat)
        dW2 = self.a1.T @ dz2
        db2 = dz2.sum(axis=0, keepdims=True)

        da1 = dz2 @ self.W2.T
        dz1 = da1 * self.a1 * (1.0 - self.a1)
        dW1 = X.T @ dz1
        db1 = dz1.sum(axis=0, keepdims=True)

        # Update weights
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1

    def predict_proba(self, X):
        return self.forward(X)

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)

# =====================================================================
# MAIN EXECUTION & TRAINING LOOP
# =====================================================================
if __name__ == "__main__":
    with open(LOG_FILE, 'w', encoding='utf-8') as log_f:
        log_print("Loading and preprocessing data...", log_f)
        X_train, X_test, y_train, y_test, train_means, train_stds = load_and_preprocess(DATA_FILE)
        
        model = TwoLayerNet(input_dim=X_train.shape[1], hidden_dim=HIDDEN_UNITS, seed=RANDOM_SEED)
        
        best_test_mse = float('inf')
        epochs_without_improvement = 0
        best_params = {}
        best_epoch = 0
        
        history = {'epoch': [], 'train_mse': [], 'test_mse': []}
        
        log_print(f"\nStarting training for up to {MAX_EPOCHS} epochs...\n", log_f)
        
        for epoch in range(1, MAX_EPOCHS + 1):
            y_hat_train = model.forward(X_train)
            train_mse = mse(y_train, y_hat_train)
            
            model.backward(X_train, y_train, LEARNING_RATE)
            
            y_hat_test = model.forward(X_test)
            test_mse = mse(y_test, y_hat_test)
            
            test_preds = model.predict(X_test, threshold=0.5)
            test_acc = np.mean(test_preds == y_test)
            
            history['epoch'].append(epoch)
            history['train_mse'].append(train_mse)
            history['test_mse'].append(test_mse)
            
            # Early Stopping Check
            if test_mse < best_test_mse:
                best_test_mse = test_mse
                best_epoch = epoch
                epochs_without_improvement = 0
                best_params = {
                    'W1': model.W1.copy(), 'b1': model.b1.copy(),
                    'W2': model.W2.copy(), 'b2': model.b2.copy()
                }
            else:
                epochs_without_improvement += 1
                
            if epoch % 100 == 0:
                log_print(f"Epoch {epoch:5d}/{MAX_EPOCHS} - Train MSE: {train_mse:.6f}, Test MSE: {test_mse:.6f}, Test Acc: {test_acc:.4f}", log_f)
                
            if epochs_without_improvement >= PATIENCE:
                log_print(f"\nEarly stopping triggered at Epoch {epoch}! Test MSE did not improve for {PATIENCE} consecutive epochs.", log_f)
                break

        # =====================================================================
        # FINAL EVALUATION
        # =====================================================================
        model.W1, model.b1 = best_params['W1'], best_params['b1']
        model.W2, model.b2 = best_params['W2'], best_params['b2']
        
        final_train_acc = np.mean(model.predict(X_train) == y_train)
        final_test_acc = np.mean(model.predict(X_test) == y_test)
        
        log_print("\n" + "="*50, log_f)
        log_print("FINAL EVALUATION METRICS", log_f)
        log_print("="*50, log_f)
        log_print(f"Rows used after filtering: {len(X_train) + len(X_test)}", log_f)
        log_print(f"Train size: {len(X_train)}", log_f)
        log_print(f"Test size: {len(X_test)}", log_f)
        log_print(f"Best epoch: {best_epoch}", log_f)
        log_print(f"Best test MSE: {best_test_mse:.6f}", log_f)
        log_print(f"Final train accuracy: {final_train_acc:.4f}", log_f)
        log_print(f"Final test accuracy: {final_test_acc:.4f}", log_f)

        # =====================================================================
        # ARTIFICIAL APPLICANTS
        # =====================================================================
        log_print("\n" + "="*50, log_f)
        log_print("ARTIFICIAL APPLICANT PREDICTIONS", log_f)
        log_print("="*50, log_f)
        
        artificial_raw = pd.DataFrame({
            'gpa': [3.9, 3.2], 'gre': [330, 300], 'gre_v': [165, 150],
            'gre_aw': [4.5, 3.0], 'ms_vs_phd': [1.0, 0.0], 'international_vs_local': [1.0, 0.0] 
        })
        
        X_art_scaled = (artificial_raw.values - train_means) / train_stds
        probs = model.predict_proba(X_art_scaled).flatten()
        labels = model.predict(X_art_scaled, threshold=0.5).flatten()
        
        results_df = artificial_raw.copy()
        results_df['Predicted Probability'] = probs
        results_df['Predicted Status'] = ['Accepted' if l == 1 else 'Rejected' for l in labels]
        
        log_print(results_df.to_string(), log_f)

    # =====================================================================
    # PLOTTING
    # =====================================================================
    plt.figure(figsize=(10, 6))
    plt.plot(history['epoch'], history['train_mse'], label='Train MSE')
    plt.plot(history['epoch'], history['test_mse'], label='Test MSE')
    plt.title('Train vs. Test Mean Squared Error')
    plt.xlabel('Epoch')
    plt.ylabel('MSE')
    plt.legend(title='variable')
    plt.grid(True)
    plt.savefig('mse_curve.png')
    print("\nPlot saved successfully as 'mse_curve.png'.")