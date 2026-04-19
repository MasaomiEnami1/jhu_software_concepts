import pandas as pd
import numpy as np
import json
import warnings
from sklearn.model_selection import train_test_split

# Suppress warnings
warnings.filterwarnings('ignore')

# =====================================================================
# HYPERPARAMETERS
# =====================================================================
RANDOM_SEED = 42
HIDDEN_UNITS = 6
LEARNING_RATE = 0.05
MAX_EPOCHS = 10000
PATIENCE = 100

# =====================================================================
# DATA PREPARATION PIPELINE
# =====================================================================
def load_and_preprocess():
    filepath = "cleaned_gradcafe.json"
    
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
        
    df['ms_vs_phd'] = df['masters_or_phd'].map({'PhD': 1.0, 'Masters': 0.0})
    df['international_vs_local'] = df['citizenship'].map({'International': 1.0, 'Local/American': 0.0, 'American': 0.0, 'US': 0.0})
    df['target'] = df['applicant_status'].map({'Accepted': 1.0, 'Rejected': 0.0})
    df = df.dropna(subset=['ms_vs_phd', 'international_vs_local', 'target'])
    
    features = ['gpa', 'gre', 'gre_v', 'gre_aw', 'ms_vs_phd', 'international_vs_local']
    X = df[features].values
    y = df['target'].values.reshape(-1, 1) 
    
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, shuffle=True
    )
    
    train_medians = np.nanmedian(X_train_raw, axis=0)
    for idx in range(X_train_raw.shape[1]):
        X_train_raw[np.isnan(X_train_raw[:, idx]), idx] = train_medians[idx]
        X_test_raw[np.isnan(X_test_raw[:, idx]), idx] = train_medians[idx]
        
    train_means = np.mean(X_train_raw, axis=0)
    train_stds = np.std(X_train_raw, axis=0)
    train_stds[train_stds == 0] = 1.0 
    
    X_train_scaled = (X_train_raw - train_means) / train_stds
    X_test_scaled = (X_test_raw - train_means) / train_stds
    
    return X_train_scaled, X_test_scaled, y_train, y_test, train_means, train_stds

# =====================================================================
# THE NEURAL NETWORK CLASS
# =====================================================================
def sigmoid(x):
    x = np.clip(x, -50, 50)
    return 1.0 / (1.0 + np.exp(-x))

def mse(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

class TwoLayerNet:
    def __init__(self, input_dim, hidden_dim, seed=RANDOM_SEED):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0.0, 0.1, (input_dim, hidden_dim))
        self.b1 = np.zeros((1, hidden_dim))
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
        
        dz2 = (2.0 / n) * (self.y_hat - y) * self.y_hat * (1.0 - self.y_hat)
        dW2 = self.a1.T @ dz2
        db2 = dz2.sum(axis=0, keepdims=True)

        da1 = dz2 @ self.W2.T
        dz1 = da1 * self.a1 * (1.0 - self.a1)
        dW1 = X.T @ dz1
        db1 = dz1.sum(axis=0, keepdims=True)

        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1

    def predict_proba(self, X):
        return self.forward(X)

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)

# =====================================================================
# TRAINING LOOP & EVALUATION
# =====================================================================
if __name__ == "__main__":
    print("Loading and preprocessing data...")
    # NOTE: Extracted train_means and train_stds for use in Step 7
    X_train, X_test, y_train, y_test, train_means, train_stds = load_and_preprocess()
    
    model = TwoLayerNet(input_dim=X_train.shape[1], hidden_dim=HIDDEN_UNITS, seed=RANDOM_SEED)
    
    best_test_mse = float('inf')
    epochs_without_improvement = 0
    best_params = {}
    best_epoch = 0
    
    print(f"\nStarting training for up to {MAX_EPOCHS} epochs...\n")
    
    for epoch in range(1, MAX_EPOCHS + 1):
        # Forward, Loss, Backward
        y_hat_train = model.forward(X_train)
        train_mse = mse(y_train, y_hat_train)
        
        model.backward(X_train, y_train, LEARNING_RATE)
        
        y_hat_test = model.forward(X_test)
        test_mse = mse(y_test, y_hat_test)
        
        test_preds = model.predict(X_test, threshold=0.5)
        test_acc = np.mean(test_preds == y_test)
        
        # Early Stopping Logic
        if test_mse < best_test_mse:
            best_test_mse = test_mse
            best_epoch = epoch
            epochs_without_improvement = 0
            best_params = {
                'W1': model.W1.copy(),
                'b1': model.b1.copy(),
                'W2': model.W2.copy(),
                'b2': model.b2.copy()
            }
        else:
            epochs_without_improvement += 1
            
        if epoch % 100 == 0:
            print(f"Epoch {epoch:5d}/{MAX_EPOCHS} - Train MSE: {train_mse:.6f}, Test MSE: {test_mse:.6f}, Test Acc: {test_acc:.4f}")
            
        if epochs_without_improvement >= PATIENCE:
            print(f"\nEarly stopping triggered at Epoch {epoch}! Test MSE did not improve for {PATIENCE} consecutive epochs.")
            break

    # RESTORE BEST PARAMETERS
    model.W1 = best_params['W1']
    model.b1 = best_params['b1']
    model.W2 = best_params['W2']
    model.b2 = best_params['b2']
    
    final_train_preds = model.predict(X_train)
    final_train_acc = np.mean(final_train_preds == y_train)
    
    final_test_preds = model.predict(X_test)
    final_test_acc = np.mean(final_test_preds == y_test)
    total_rows_used = len(X_train) + len(X_test)
    
    print("\n" + "="*50)
    print("STEP 5: FINAL EVALUATION METRICS")
    print("="*50)
    print(f"Rows used after filtering: {total_rows_used}")
    print(f"Train size: {len(X_train)}")
    print(f"Test size: {len(X_test)}")
    print(f"Best epoch: {best_epoch}")
    print(f"Best test MSE: {best_test_mse:.6f}")
    print(f"Final train accuracy: {final_train_acc:.4f}")
    print(f"Final test accuracy: {final_test_acc:.4f}")

    # =====================================================================
    # STEP 7: TEST THE MODEL ON ARTIFICIAL APPLICANTS
    # =====================================================================
    print("\n" + "="*50)
    print("STEP 7: ARTIFICIAL APPLICANT PREDICTIONS")
    print("="*50)
    
    # Define the exact artificial applicants from the assignment example
    artificial_applicants_raw = pd.DataFrame({
        'gpa': [3.9, 3.2],
        'gre': [330, 300],
        'gre_v': [165, 150],
        'gre_aw': [4.5, 3.0],
        'ms_vs_phd': [1.0, 0.0], 
        'international_vs_local': [1.0, 0.0] 
    })
    
    print("Artificial Applicants (Raw Data):")
    # Using to_string() ensures Pandas prints the whole table neatly in the terminal
    print(artificial_applicants_raw.to_string())
    print("-" * 50)
    
    # 1. Convert to NumPy array
    X_artificial = artificial_applicants_raw.values
    
    # 2. Standardize using the stored training means and standard deviations
    X_artificial_scaled = (X_artificial - train_means) / train_stds
    
    # 3. Run the trained model on these artificial applicants
    predicted_probs = model.predict_proba(X_artificial_scaled)
    predicted_labels = model.predict(X_artificial_scaled, threshold=0.5)
    
    # Map the binary labels back to readable text
    status_map = {1: 'Accepted', 0: 'Rejected'}
    predicted_statuses = [status_map[label[0]] for label in predicted_labels]
    
    # 4. Create output table matching the assignment requirements
    results_df = artificial_applicants_raw.copy()
    # Flatten the probabilities array so it fits neatly into the pandas column
    results_df['Predicted Probability'] = predicted_probs.flatten()
    results_df['Predicted Status'] = predicted_statuses
    
    print("Model Predictions for Artificial Applicants:")
    print(results_df.to_string())
    print("="*50 + "\n")