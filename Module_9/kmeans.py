import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import warnings

# Suppress memory leak warnings that Windows sometimes throws during K-Means loops
warnings.filterwarnings('ignore')

def main():
    # --- 1. DATA PREPARATION ---
    print("Loading and cleaning data...")
    df = pd.read_json('cleaned_gradcafe.json')
    
    # Drop missing or "None" programs
    df = df.dropna(subset=['Program'])
    df = df[df['Program'].astype(str).str.strip().str.lower() != 'none']
    
    # Fill any genuinely missing universities with a placeholder so it looks clean in the table
    if 'University' in df.columns:
        df['University'] = df['University'].fillna('Not Provided')
    else:
        df['University'] = 'Not Provided'
        
    # --- 2. VECTORIZATION ---
    print("Vectorizing text data...")
    vectorizer = TfidfVectorizer(stop_words='english')
    X_sparse = vectorizer.fit_transform(df['Program'].fillna(''))

    # --- 3. PRINCIPAL COMPONENT ANALYSIS (2 Components) ---
    print("\nPerforming PCA Dimensionality Reduction...")
    # Scikit-Learn's PCA requires a "dense" matrix, so we convert our sparse one first
    X_dense = X_sparse.toarray()
    
    # Initialize PCA to reduce our thousands of word-columns down to just 2 columns
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_dense)
    
    # Print the output to match your assignment requirements
    print(X_pca.shape)
    print(pca)

    # --- 4. K-MEANS CLUSTERING (50 Clusters) ---
    print("\nRunning K-Means Clustering...")
    # Setup K-Means with the exact parameters from your assignment
    kmeans = KMeans(n_clusters=50, max_iter=100, n_init=5, random_state=42)
    
    # Train the model on our 2D PCA data and predict which cluster each row belongs to
    labels = kmeans.fit_predict(X_pca)

    # --- 5. VISUALIZATION (SCATTER PLOT) ---
    print("Generating cluster plot...")
    plt.figure(figsize=(12, 8))
    
    # Scatter plot
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='tab20', s=15, alpha=0.6)
    
    plt.title('K-Means Clustering of Grad Café Programs (50 Clusters)')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    
    # Save the image (NOTE: plt.show() has been removed to prevent freezing!)
    plt.savefig('initial_cluster.png', bbox_inches='tight')
    print("Saved initial_cluster.png successfully.")

    # --- 6. ATTACH CLUSTERS TO DATAFRAME ---
    print("\nMapping clusters back to the dataset...")
    # Add the predicted labels as a new column named 'cluster'
    df['cluster'] = labels

    # --- 7. CREATE THE 100-ROW VIEW ---
    # Select only the three requested columns and grab the first 100 rows
    df_100 = df[['Program', 'University', 'cluster']].head(100)

    # Force the terminal to print all 100 rows so you can verify it visually
    pd.set_option('display.max_rows', 100)
    print("\n--- First 100 Rows of Clustered Data ---")
    print(df_100)

    # --- 8. SAVE DATAFRAME AS PNG ---
    print("\nSaving DataFrame image as clustered_dataFrame.png...")
    
    # Create a tall, blank matplotlib canvas to hold 100 rows of text
    fig, ax = plt.subplots(figsize=(10, 25)) 
    ax.axis('off')   # Hide the graph axes (we only want the table)
    ax.axis('tight') # Remove extra whitespace

    # Draw the table using the dataframe's values and columns
    table = ax.table(cellText=df_100.values, 
                     colLabels=df_100.columns, 
                     loc='center',
                     cellLoc='right') # Aligns text to the right, matching your image

    # Formatting to make it readable
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.2) # Stretches the cells slightly for better spacing

    # Save the final table image
    plt.savefig('clustered_dataFrame.png', bbox_inches='tight', dpi=150)
    print("✅ Done! clustered_dataFrame.png has been saved to your folder.")
    
    # Close previous plots to free up memory before doing the new assignment
    plt.close('all')

    # =========================================================================
    # --- ASSIGNMENT PART 2 CODE STARTS HERE: ELBOW METHOD ---
    # =========================================================================

    # --- 9. EXPANDED PCA ---
    print("\n--- STARTING PART 2: THE ELBOW METHOD ---")
    print("Performing Expanded PCA Dimensionality Reduction (75 components)...")
    # We reuse X_dense from Step 3, but this time keep 75 components instead of 2
    pca_expanded = PCA(n_components=75)
    X_pca_expanded = pca_expanded.fit_transform(X_dense)

    # --- 10. CALCULATING INERTIA (THE LOOP) ---
    print("\nCalculating Inertia for the Elbow Method...")
    print("⏳ Please wait! This runs K-Means multiple times and will take a couple of minutes.")
    
    inertias = []
    
    # Test cluster sizes from 5 to 100 in steps of 5 (5, 10, 15... 100)
    # We step by 5 so the script finishes in a reasonable amount of time.
    K_values = list(range(5, 101, 5))

    for k in K_values:
        print(f"   -> Training model with {k} clusters...")
        # n_init=3 speeds up the loop slightly while maintaining good accuracy
        kmeans_elbow = KMeans(n_clusters=k, n_init=3, max_iter=100, random_state=42)
        kmeans_elbow.fit(X_pca_expanded)
        inertias.append(kmeans_elbow.inertia_)

    # --- 11. VISUALIZING THE ELBOW ---
    print("\nGenerating elbow.png graph...")
    plt.figure(figsize=(10, 6))
    
    # Plotting the K values against the calculated inertias
    plt.plot(K_values, inertias, marker='o', linestyle='-', color='b')
    
    plt.title('The Elbow Method using Inertia (75 PCA Components)')
    plt.xlabel('Values of K (Number of Clusters)')
    plt.ylabel('Inertia')
    
    # Forces the X-axis to show our specific test numbers
    plt.xticks(K_values, rotation=45) 
    plt.grid(True)
    
    # Save the output graph
    plt.savefig('elbow.png', bbox_inches='tight')
    print("✅ Done! elbow.png has been saved to your folder.")

    # =========================================================================
    # --- PART 3: FINAL CLUSTERING AND ANALYSIS ---
    # =========================================================================
    print("\n--- STARTING PART 3: FINAL ANALYSIS (85 CLUSTERS) ---")
    print("Running final K-Means with optimal K=85...")
    
    # 1. Run the final optimal model
    optimal_kmeans = KMeans(n_clusters=85, n_init=5, max_iter=100, random_state=42)
    final_labels = optimal_kmeans.fit_predict(X_pca_expanded)
    
    # 2. Insert cluster column at the VERY FRONT (Index 0) to match the assignment image
    if 'cluster' in df.columns:
        df = df.drop(columns=['cluster'])
    df.insert(0, 'cluster', final_labels)
    
    # 3. Print the head to verify
    pd.set_option('display.max_columns', None) 
    print("\n--- Final Clustered DataFrame ---")
    print(df.head())

    # 4. Clean GRE data: Extract only the numbers
    df['GRE_clean'] = pd.to_numeric(df['GRE'].astype(str).str.extract(r'(\d+\.?\d*)')[0], errors='coerce')
    df['GRE_V_clean'] = pd.to_numeric(df['GRE V'].astype(str).str.extract(r'(\d+\.?\d*)')[0], errors='coerce')

    # 5. Find the cluster ID numbers for CS and Philosophy
    cs_programs = df[df['Program'].str.lower() == 'computer science']
    phil_programs = df[df['Program'].str.lower() == 'philosophy']
    
    cs_cluster_id = cs_programs['cluster'].mode()[0]
    phil_cluster_id = phil_programs['cluster'].mode()[0]
    
    # Filter the datasets and rename columns to match the exact labels in the screenshot
    df_cs = df[df['cluster'] == cs_cluster_id][['GRE_clean', 'GRE_V_clean']].rename(columns={'GRE_clean': 'GRE', 'GRE_V_clean': 'GRE V'})
    df_phil = df[df['cluster'] == phil_cluster_id][['GRE_clean', 'GRE_V_clean']].rename(columns={'GRE_clean': 'GRE', 'GRE_V_clean': 'GRE V'})

    print(f"\nComputer Science assigned to Cluster {cs_cluster_id}. Found {len(df_cs)} records.")
    print(f"Philosophy assigned to Cluster {phil_cluster_id}. Found {len(df_phil)} records.")

    # 6. Plot Philosophy Boxplot
    print("Generating philosophy.png...")
    plt.figure(figsize=(7, 5))
    df_phil.boxplot(column=['GRE', 'GRE V'])
    plt.title('GRE and GRE Verbal Scores for Philosophy Majors')
    plt.ylabel('Score')
    plt.xlabel('GRE Component')
    plt.savefig('philosophy.png', bbox_inches='tight')
    plt.close('all')

    # 7. Plot Computer Science Boxplot
    print("Generating computer_science.png...")
    plt.figure(figsize=(7, 5))
    df_cs.boxplot(column=['GRE', 'GRE V'])
    plt.title('GRE and GRE Verbal Scores for CS Majors')
    plt.ylabel('Score')
    plt.xlabel('GRE Component')
    plt.savefig('computer_science.png', bbox_inches='tight')
    plt.close('all')

    print("✅ All parts of the assignment have executed successfully!")
    
if __name__ == "__main__":
    main()