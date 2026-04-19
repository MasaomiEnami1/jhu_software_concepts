import numpy as np

# Set the required hyperparameters as constants at the top
RANDOM_SEED = 42
HIDDEN_UNITS = 6
LEARNING_RATE = 0.05
MAX_EPOCHS = 10000
PATIENCE = 100

def sigmoid(x):
    x = np.clip(x, -50, 50)
    return 1.0 / (1.0 + np.exp(-x))

def mse(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

class TwoLayerNet:
    """
    Rudimentary 2-layer neural net:
    input -> hidden(sigmoid) -> output(sigmoid)
    """

    def __init__(self, input_dim, hidden_dim, seed=42):
        # Initialize the random number generator with the required seed
        rng = np.random.default_rng(seed)
        
        # Initialize weights with normal distribution (mean=0, std=0.1)
        self.W1 = rng.normal(0.0, 0.1, (input_dim, hidden_dim))
        # Initialize biases to 0
        self.b1 = np.zeros((1, hidden_dim))
        
        # Output layer has 1 unit for binary classification
        self.W2 = rng.normal(0.0, 0.1, (hidden_dim, 1))
        self.b2 = np.zeros((1, 1))

    def forward(self, X):
        # Layer 1 computation: Z = X * W + b
        self.z1 = X @ self.W1 + self.b1
        self.a1 = sigmoid(self.z1)
        
        # Layer 2 computation
        self.z2 = self.a1 @ self.W2 + self.b2
        self.y_hat = sigmoid(self.z2)
        
        return self.y_hat

    def backward(self, X, y, learning_rate):
        n = len(X)
        
        # Ensure y is a column vector to match y_hat's shape (n, 1)
        y = y.reshape(-1, 1)
        
        # MSE derivative through sigmoid output
        # The derivative of MSE w.r.t y_hat is: 2/n * (y_hat - y)
        # The derivative of sigmoid w.r.t z2 is: y_hat * (1 - y_hat)
        # We multiply them together for the chain rule:
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

# Quick validation check to ensure it instantiates properly
if __name__ == "__main__":
    # 6 Input features, 6 Hidden Units
    model = TwoLayerNet(input_dim=6, hidden_dim=HIDDEN_UNITS, seed=RANDOM_SEED)
    print("TwoLayerNet successfully initialized!")
    print(f"W1 shape: {model.W1.shape}")
    print(f"W2 shape: {model.W2.shape}")