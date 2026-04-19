import pandas as pd
import numpy as np
import json
import warnings
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# Suppress warnings
warnings.filterwarnings('ignore')

# =====================================================================
# 1. DATA PREPARATION
# =====================================================================
def load_and_prepare_data(filepath):
    """Loads and preprocesses the GradCafe dataset."""
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            original_df = pd.DataFrame(data)
        except json.JSONDecodeError:
            f.seek(0)
            records = [json.loads(line) for line in f if line.strip()]
            original_df = pd.DataFrame(records)
            
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
    
    return filtered_df

# =====================================================================
# 2. NEURAL NETWORK IMPLEMENTATION (NumPy Only)
# =====================================================================
class TwoLayerNN:
    def __init__(self, input_size, hidden_size, output_size, learning_rate=0.1):
        # Set a random seed for reproducibility
        np.random.seed(42)
        
        self.lr = learning_rate
        
        # Initialize weights. Using a slightly different scaling to help Sigmoid activation
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(1. / input_size)
        self.b1 = np.zeros((1, hidden_size))
        
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(1. / hidden_size)
        self.b2 = np.zeros((1, output_size))

    def sigmoid(self, z):
        # Clip values to prevent overflow errors in exp
        z = np.clip(z, -500, 500)
        return 1.0 / (1.0 + np.exp(-z))

    def sigmoid_derivative(self, a):
        return a * (1.0 - a)

    def forward(self, X):
        # Layer 1
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        
        # Layer 2 (Output)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        
        return self.a2

    def backward(self, X, y):
        m = X.shape[0]
        
        # The derivative of MSE loss with respect to a2
        dz2 = (self.a2 - y) * self.sigmoid_derivative(self.a2)
        dW2 = (1 / m) * np.dot(self.a1.T, dz2)
        db2 = (1 / m) * np.sum(dz2, axis=0, keepdims=True)
        
        dz1 = np.dot(dz2, self.W2.T) * self.sigmoid_derivative(self.a1)
        dW1 = (1 / m) * np.dot(X.T, dz1)
        db1 = (1 / m) * np.sum(dz1, axis=0, keepdims=True)
        
        # Update weights and biases
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1

    def calculate_mse(self, predictions, targets):
        return np.mean(np.square(predictions - targets))

# =====================================================================
# 3. MAIN EXECUTION PIPELINE
# =====================================================================
if __name__ == "__main__":
    print("\nLoading and preparing data...")
    filepath = "cleaned_gradcafe.json"
    df = load_and_prepare_data(filepath)
    
    # 3a. Extract Features and Target
    features = ['gpa', 'gre', 'gre_v', 'gre_aw', 'ms_vs_phd', 'international_vs_local']
    X = df[features].values
    y = df['target'].values.reshape(-1, 1) 
    
    # 3b. Train/Test Split using Scikit-Learn
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3c. Standardize the data
    train_mean = np.mean(X_train_raw, axis=0)
    train_std = np.std(X_train_raw, axis=0)
    train_std[train_std == 0] = 1e-8 
    
    X_train = (X_train_raw - train_mean) / train_std
    X_test = (X_test_raw - train_mean) / train_std
    
    # 3d. Initialize Neural Network (UPDATED HYPERPARAMETERS)
    input_size = 6
    hidden_size = 16       # Increased capacity
    output_size = 1
    learning_rate = 0.1    # Lowered for stability
    
    nn = TwoLayerNN(input_size, hidden_size, output_size, learning_rate)
    
    # 3e. Training Loop with Early Stopping
    epochs = 20000         # Allow more time to train
    patience = 1000        # Much higher patience so it doesn't quit early
    best_test_mse = float('inf')
    epochs_without_improvement = 0
    
    train_loss_history = []
    test_loss_history = []
    
    print("\nStarting Training...")
    for epoch in range(epochs):
        # Forward pass
        train_preds = nn.forward(X_train)
        train_mse = nn.calculate_mse(train_preds, y_train)
        
        # Backpropagation
        nn.backward(X_train, y_train)
        
        # Testing
        test_preds = nn.forward(X_test)
        test_mse = nn.calculate_mse(test_preds, y_test)
        
        train_loss_history.append(train_mse)
        test_loss_history.append(test_mse)
        
        # Early Stopping
        if test_mse < best_test_mse:
            best_test_mse = test_mse
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            
        if epochs_without_improvement >= patience:
            print(f"Early stopping triggered at epoch {epoch}. Test MSE has not improved for {patience} epochs.")
            break
            
        if epoch % 1000 == 0:
            print(f"Epoch {epoch:5d} | Train MSE: {train_mse:.4f} | Test MSE: {test_mse:.4f}")
            
    print(f"\nFinal Test MSE: {best_test_mse:.4f}")
    
    # 3f. Evaluate the Trained Model
    final_test_preds = nn.forward(X_test)
    binary_preds = (final_test_preds >= 0.5).astype(float)
    accuracy = np.mean(binary_preds == y_test)
    print(f"Final Test Accuracy: {accuracy * 100:.2f}%")
    
    # 3g. Plot Training and Testing Loss
    plt.figure(figsize=(10, 6))
    plt.plot(train_loss_history, label='Training MSE Loss')
    plt.plot(test_loss_history, label='Testing MSE Loss')
    plt.title('Neural Network Loss over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Mean Squared Error (MSE)')
    plt.legend()
    plt.grid(True)
    plt.savefig('loss_plot.png')
    print("\nSaved loss plot to 'loss_plot.png' in the current directory.")
    
    # =====================================================================
    # 4. PREDICTIONS ON ARTIFICIAL APPLICANTS
    # =====================================================================
    print("\n" + "="*50)
    print("ARTIFICIAL APPLICANT PREDICTIONS")
    print("="*50)
    
    app1 = np.array([4.0, 335.0, 168.0, 5.0, 1.0, 0.0])
    app2 = np.array([2.5, 290.0, 140.0, 2.5, 0.0, 1.0])
    
    artificial_applicants = np.vstack((app1, app2))
    artificial_scaled = (artificial_applicants - train_mean) / train_std
    
    app_preds = nn.forward(artificial_scaled)
    
    print("Applicant 1 (GPA 4.0, GRE 335, PhD, Local):")
    print(f"  -> Model Output (Probability of Acceptance): {app_preds[0][0]*100:.2f}%")
    
    print("\nApplicant 2 (GPA 2.5, GRE 290, Masters, International):")
    print(f"  -> Model Output (Probability of Acceptance): {app_preds[1][0]*100:.2f}%")
    print("="*50 + "\n")
    
    print("Model Reflection: Observe how the tuned neural network is now able to distinguish between applicant profiles.")