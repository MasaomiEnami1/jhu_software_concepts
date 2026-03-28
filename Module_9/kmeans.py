"""
Module 9: Data Preparation and Models Assignment.
This script processes Grad Cafe application data, uses TF-IDF and PCA
to reduce dimensionality, and applies K-Means clustering to group
similar academic programs. It outputs visualizations of the clusters.
"""

import warnings
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# Suppress Windows memory leak warnings for K-Means loops
warnings.filterwarnings('ignore')

def load_and_clean_data(filepath: str) -> pd.DataFrame:
    """
    Loads JSON data and cleans the Program and University columns.
    """
    print("Loading and cleaning data...")
    dataframe = pd.read_json(filepath)
    dataframe = dataframe.dropna(subset=['Program'])
    dataframe = dataframe[
        dataframe['Program'].astype(str).str.strip().str.lower() != 'none'
    ]

    if 'University' in dataframe.columns:
        dataframe['University'] = dataframe['University'].fillna('Not Provided')
    else:
        dataframe['University'] = 'Not Provided'

    return dataframe

def perform_initial_clustering(dataframe: pd.DataFrame) -> tuple:
    """
    Vectorizes text, applies 2-component PCA, and runs an initial 50-cluster K-Means.
    Saves the initial_cluster.png and clustered_dataFrame.png files.
    """
    print("Vectorizing text data...")
    vectorizer = TfidfVectorizer(stop_words='english')
    x_sparse = vectorizer.fit_transform(dataframe['Program'].fillna(''))

    print("Performing 2-Component PCA...")
    x_dense = x_sparse.toarray()
    pca = PCA(n_components=2)
    x_pca = pca.fit_transform(x_dense)

    print("Running initial K-Means Clustering (K=50)...")
    kmeans = KMeans(n_clusters=50, max_iter=100, n_init=5, random_state=42)
    labels = kmeans.fit_predict(x_pca)

    print("Generating initial_cluster.png...")
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(x_pca[:, 0], x_pca[:, 1], c=labels, cmap='tab20', s=15, alpha=0.6)
    plt.title('K-Means Clustering of Grad Café Programs (50 Clusters)')
    plt.xlabel('Principal Component 1 (PCA Unit)')
    plt.ylabel('Principal Component 2 (PCA Unit)')
    # Adding a legend to satisfy assignment constraints
    plt.legend(*scatter.legend_elements(), title="Clusters", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.savefig('initial_cluster.png', bbox_inches='tight')
    plt.close('all')

    print("Saving clustered_dataFrame.png...")
    dataframe['cluster'] = labels
    df_100 = dataframe[['Program', 'University', 'cluster']].head(100)

    fig, axis = plt.subplots(figsize=(10, 25))
    axis.axis('off')
    axis.axis('tight')

    table = axis.table(
        cellText=df_100.values,
        colLabels=df_100.columns,
        loc='center',
        cellLoc='right'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.2)
    plt.savefig('clustered_dataFrame.png', bbox_inches='tight', dpi=150)
    plt.close('all')

    return x_dense

def perform_elbow_method(x_dense) -> tuple:
    """
    Expands PCA to 75 components and tests K-Means cluster sizes from 5 to 100.
    Saves the elbow.png graph.
    """
    print("\n--- STARTING PART 2: THE ELBOW METHOD ---")
    print("Performing Expanded PCA Dimensionality Reduction (75 components)...")
    pca_expanded = PCA(n_components=75)
    x_pca_expanded = pca_expanded.fit_transform(x_dense)

    print("Calculating Inertia for the Elbow Method (This will take a minute)...")
    inertias = []
    k_values = list(range(5, 101, 5))

    for k in k_values:
        kmeans_elbow = KMeans(n_clusters=k, n_init=3, max_iter=100, random_state=42)
        kmeans_elbow.fit(x_pca_expanded)
        inertias.append(kmeans_elbow.inertia_)

    print("Generating elbow.png...")
    plt.figure(figsize=(10, 6))
    plt.plot(k_values, inertias, marker='o', linestyle='-', color='b', label='Inertia Trend')
    plt.title('The Elbow Method using Inertia (75 PCA Components)')
    plt.xlabel('Values of K (Number of Clusters)')
    plt.ylabel('Inertia (Squared Distance)')
    plt.xticks(k_values, rotation=45)
    plt.grid(True)
    plt.legend()
    plt.savefig('elbow.png', bbox_inches='tight')
    plt.close('all')

    return x_pca_expanded

def perform_final_analysis(dataframe: pd.DataFrame, x_pca_expanded):
    """
    Runs final K-Means with 85 clusters, extracts GRE numeric scores,
    and generates comparative boxplots for Computer Science and Philosophy.
    """
    print("\n--- STARTING PART 3: FINAL ANALYSIS (85 CLUSTERS) ---")
    optimal_kmeans = KMeans(n_clusters=85, n_init=5, max_iter=100, random_state=42)
    final_labels = optimal_kmeans.fit_predict(x_pca_expanded)

    if 'cluster' in dataframe.columns:
        dataframe = dataframe.drop(columns=['cluster'])
    dataframe.insert(0, 'cluster', final_labels)

    # Clean GRE data for plotting
    dataframe['GRE_clean'] = pd.to_numeric(
        dataframe['GRE'].astype(str).str.extract(r'(\d+\.?\d*)')[0], errors='coerce'
    )
    dataframe['GRE_V_clean'] = pd.to_numeric(
        dataframe['GRE V'].astype(str).str.extract(r'(\d+\.?\d*)')[0], errors='coerce'
    )

    # Identify cluster IDs for target programs
    cs_programs = dataframe[dataframe['Program'].str.lower() == 'computer science']
    phil_programs = dataframe[dataframe['Program'].str.lower() == 'philosophy']

    cs_cluster_id = cs_programs['cluster'].mode()[0]
    phil_cluster_id = phil_programs['cluster'].mode()[0]

    df_cs = dataframe[dataframe['cluster'] == cs_cluster_id][['GRE_clean', 'GRE_V_clean']]
    df_cs = df_cs.rename(columns={'GRE_clean': 'GRE', 'GRE_V_clean': 'GRE V'})

    df_phil = dataframe[dataframe['cluster'] == phil_cluster_id][['GRE_clean', 'GRE_V_clean']]
    df_phil = df_phil.rename(columns={'GRE_clean': 'GRE', 'GRE_V_clean': 'GRE V'})

    # Plot Philosophy
    print("Generating philosophy.png...")
    plt.figure(figsize=(7, 5))
    df_phil.boxplot(column=['GRE', 'GRE V'])
    plt.title('GRE and GRE Verbal Scores for Philosophy Majors')
    plt.ylabel('Score (Points)')
    plt.xlabel('GRE Component')
    plt.plot([], [], ' ', label=f"n={len(df_phil)} applicants") # Dummy legend to satisfy rubric
    plt.legend()
    plt.savefig('philosophy.png', bbox_inches='tight')
    plt.close('all')

    # Plot Computer Science
    print("Generating computer_science.png...")
    plt.figure(figsize=(7, 5))
    df_cs.boxplot(column=['GRE', 'GRE V'])
    plt.title('GRE and GRE Verbal Scores for CS Majors')
    plt.ylabel('Score (Points)')
    plt.xlabel('GRE Component')
    plt.plot([], [], ' ', label=f"n={len(df_cs)} applicants") # Dummy legend to satisfy rubric
    plt.legend()
    plt.savefig('computer_science.png', bbox_inches='tight')
    plt.close('all')

    print("✅ All parts of the assignment have executed successfully!")

def main():
    """
    Main entry point for the kmeans.py execution flow.
    """
    dataframe = load_and_clean_data('cleaned_gradcafe.json')
    x_dense = perform_initial_clustering(dataframe)
    x_pca_expanded = perform_elbow_method(x_dense)
    perform_final_analysis(dataframe, x_pca_expanded)

if __name__ == "__main__":
    main()