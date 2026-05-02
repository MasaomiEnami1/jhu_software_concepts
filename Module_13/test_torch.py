import torch

# Check if PyTorch is installed
print(f"PyTorch Version: {torch.__version__}")

# Check if a GPU is available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Create a simple tensor
x = torch.rand(5, 3)
print(x)