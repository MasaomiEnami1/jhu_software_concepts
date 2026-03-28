import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def main():
    # --- 1. DATA PREPARATION ---
    print("Loading and cleaning data...")
    df = pd.read_json('cleaned_gradcafe.json')
    df = df.dropna(subset=['Program'])
    df = df[df['Program'].astype(str).str.strip().str.lower() != 'none']
    
    split_cols = df['Program'].astype(str).str.split(',', n=1, expand=True)
    df['Program'] = split_cols[0].str.strip()
    if split_cols.shape[1] > 1:
        df['University'] = split_cols[1].str.strip()
    else:
        df['University'] = None

    # --- 2. VECTORIZATION ---
    print("Vectorizing text data...")
    vectorizer = TfidfVectorizer(stop_words='english')
    X_sparse = vectorizer.fit_transform(df['Program'].fillna(''))

    # --- 3. PRINCIPAL COMPONENT ANALYSIS ---
    print("\nPerforming PCA Dimensionality Reduction...")
    # Scikit-Learn's PCA requires a "dense" matrix, so we convert our sparse one first
    X_dense = X_sparse.toarray()
    
    # Initialize PCA to reduce our thousands of word-columns down to just 2 columns
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_dense)
    
    # Print the output to match your assignment requirements
    print(X_pca.shape)
    print(pca)

    # --- 4. K-MEANS CLUSTERING ---
    print("\nRunning K-Means Clustering...")
    # Setup K-Means with the exact parameters from your assignment
    kmeans = KMeans(n_clusters=50, max_iter=100, n_init=5, random_state=42)
    
    # Train the model on our 2D PCA data and predict which cluster each row belongs to
    labels = kmeans.fit_predict(X_pca)

    # --- 5. VISUALIZATION ---
    print("Generating cluster plot...")
    plt.figure(figsize=(12, 8))
    
    # Scatter plot: 
    # X-axis is the first PCA column (X_pca[:, 0])
    # Y-axis is the second PCA column (X_pca[:, 1])
    # c=labels colors the dots based on their assigned cluster (0 to 49)
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='tab20', s=15, alpha=0.6)
    
    plt.title('K-Means Clustering of Grad Café Programs (50 Clusters)')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    
    # Save the image to your folder and then display it
    plt.savefig('kmeans_50_clusters.png', bbox_inches='tight')
    plt.show()

    

if __name__ == "__main__":
    main()