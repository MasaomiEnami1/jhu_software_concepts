"""
MLOps pipeline for GradCafe clustering using KMeans and MLflow.

This module performs text vectorization, PCA dimensionality reduction,
and KMeans clustering while tracking results to a local MLflow server.
"""

import warnings
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import mlflow
import mlflow.sklearn

# Suppress memory leak warnings
warnings.filterwarnings('ignore')

def main():
    """
    Main function to execute the clustering and MLOps tracking pipeline.
    """
    # --- 1. MLOPS SETUP ---
    mlflow.set_tracking_uri("http://localhost:8080")
    mlflow.set_experiment("GradCafe_KMeans_Assignment")

    # --- 2. DATA PREPARATION ---
    print("Loading and cleaning data...")
    try:
        df_raw = pd.read_json('cleaned_gradcafe.json')
    except FileNotFoundError:
        print("Error: 'cleaned_gradcafe.json' not found in the Module_11 folder.")
        return

    df_clean = df_raw.dropna(subset=['Program'])
    df_clean = df_clean[df_clean['Program'].astype(str).str.strip().str.lower() != 'none']

    # --- 3. VECTORIZATION & PCA ---
    print("Vectorizing and reducing dimensionality...")
    vectorizer = TfidfVectorizer(stop_words='english')
    # Renamed variables to snake_case for Pylint compliance
    sparse_features = vectorizer.fit_transform(df_clean['Program'].fillna(''))
    dense_features = sparse_features.toarray()

    # Using 75 components as determined in the elbow method section
    pca = PCA(n_components=75)
    pca_features = pca.fit_transform(dense_features)

    # --- 4. THE TRACKED RUN ---
    params = {
        "max_iter": 500,
        "n_clusters": 25,
        "n_init": 5,
        "random_state": 42,
    }

    with mlflow.start_run(run_name="KMeans_Assigned_Params"):
        print("Running K-Means with specified parameters...")

        # 1. Log the entire parameter dictionary
        mlflow.log_params(params)

        # 2. Initialize and fit the model
        model = KMeans(**params)
        model.fit(pca_features)

        # 3. Log the performance metric: inertia_
        mlflow.log_metric("inertia", model.inertia_)

        # 4. Log the model artifact
        mlflow.sklearn.log_model(model, artifact_path="kmeans-model")

        print("-" * 30)
        # Removed 'f' prefix from strings without interpolation to fix W1309
        print("✅ Run Successful!")
        print(f"Logged Parameters: {params}")
        print(f"Logged Inertia: {model.inertia_:.2f}")
        print("-" * 30)

    print("\nRefresh your browser at http://localhost:8080 to see the new run.")

if __name__ == "__main__":
    main()
