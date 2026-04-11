import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import mlflow
import mlflow.sklearn
import warnings

# Suppress memory leak warnings
warnings.filterwarnings('ignore')

def main():
    # --- 1. MLOPS SETUP ---
    # Replace 'localhost' with your specific IP if you are running on a remote machine
    mlflow.set_tracking_uri("http://localhost:8080")
    mlflow.set_experiment("GradCafe_KMeans_Assignment")

    # --- 2. DATA PREPARATION ---
    print("Loading and cleaning data...")
    try:
        df = pd.read_json('cleaned_gradcafe.json')
    except FileNotFoundError:
        print("Error: 'cleaned_gradcafe.json' not found. Please ensure it is in your Module_11 folder.")
        return

    df = df.dropna(subset=['Program'])
    df = df[df['Program'].astype(str).str.strip().str.lower() != 'none']
    
    # --- 3. VECTORIZATION & PCA ---
    print("Vectorizing and reducing dimensionality...")
    vectorizer = TfidfVectorizer(stop_words='english')
    X_sparse = vectorizer.fit_transform(df['Program'].fillna(''))
    X_dense = X_sparse.toarray()
    
    # Using 75 components as determined in the elbow method section
    pca = PCA(n_components=75)
    X_pca = pca.fit_transform(X_dense)

    # --- 4. THE TRACKED RUN ---
    # Define parameters exactly as shown in your image
    params = {
        "max_iter": 500,
        "n_clusters": 25,
        "n_init": 5,
        "random_state": 42,
    }

    with mlflow.start_run(run_name="KMeans_Assigned_Params"):
        print("Running K-Means with specified parameters...")
        
        # 1. Log the entire parameter dictionary at once
        mlflow.log_params(params)
        
        # 2. Initialize and fit the model using the dictionary
        # The ** syntax 'unpacks' the dictionary into the function arguments
        model = KMeans(**params)
        model.fit(X_pca)

        # 3. Log the performance metric: inertia_
        # In MLflow, we use log_metric for values that represent performance
        mlflow.log_metric("inertia", model.inertia_)
        
        # 4. Log the model artifact
        mlflow.sklearn.log_model(model, artifact_path="kmeans-model")

        print("-" * 30)
        print(f"✅ Run Successful!")
        print(f"Logged Parameters: {params}")
        print(f"Logged Inertia: {model.inertia_:.2f}")
        print("-" * 30)

    print("\nRefresh your browser at http://localhost:8080 to see the new run.")

if __name__ == "__main__":
    main()