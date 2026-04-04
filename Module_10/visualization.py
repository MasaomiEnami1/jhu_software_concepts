"""
visualization.py

Exploratory Data Analysis on the Kaggle Diamonds dataset.
Generates three visualizations (two Seaborn, one Plotly) to explore the
features that determine diamond prices, answering the core research question.
"""

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px


def ensure_output_dir(directory: str) -> None:
    """
    Ensures the output directory exists.

    Args:
        directory (str): The path of the directory to create.
    """
    os.makedirs(directory, exist_ok=True)


def load_diamond_data(filepath: str) -> pd.DataFrame:
    """
    Loads the diamonds dataset from a CSV file.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded dataset.
    """
    return pd.read_csv(filepath)


def create_correlation_heatmap(dataframe: pd.DataFrame, out_path: str) -> None:
    """
    Generates and saves a correlation heatmap of numerical features.
    Demonstrates Rule #2 (relevant variables) and Rule #3 (consistent scales).

    Args:
        dataframe (pd.DataFrame): The input dataset.
        out_path (str): The file path to save the PNG image.
    """
    plt.figure(figsize=(10, 8))

    # Selecting only numerical columns to prevent errors
    numeric_cols = ['carat', 'depth', 'table', 'price', 'x', 'y', 'z']
    corr_matrix = dataframe[numeric_cols].corr()

    # Consistent 'viridis' color palette used across all plots
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap='viridis',
        fmt='.2f',
        linewidths=0.5
    )
    plt.title('Correlation Matrix of Diamond Attributes', fontsize=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def create_price_by_cut_boxplot(dataframe: pd.DataFrame, out_path: str) -> None:
    """
    Generates and saves a boxplot of price distributions by cut quality.
    Demonstrates Rule #5 (do not truncate axis values - boxplots naturally scale).

    Args:
        dataframe (pd.DataFrame): The input dataset.
        out_path (str): The file path to save the PNG image.
    """
    plt.figure(figsize=(10, 6))

    # Ordering the categorical variables logically
    cut_order = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']

    sns.boxplot(
        x='cut',
        y='price',
        data=dataframe,
        order=cut_order,
        palette='viridis',
        hue='cut',
        legend=False
    )
    plt.title('Diamond Price Distribution by Cut Quality', fontsize=14)
    plt.xlabel('Cut Quality', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def create_carat_vs_price_scatter(dataframe: pd.DataFrame, out_path: str) -> None:
    """
    Generates an interactive Plotly scatter plot of carat vs price,
    colored by clarity. Saves both a static PNG and an interactive HTML file.

    Args:
        dataframe (pd.DataFrame): The input dataset.
        out_path (str): The file path to save the PNG image.
    """
    # Sample data to avoid overplotting (Rule #6: Relevant scale for trends)
    sample_df = dataframe.sample(n=2000, random_state=42)

    fig = px.scatter(
        sample_df,
        x='carat',
        y='price',
        color='clarity',
        title='Interactive: Carat vs Price by Clarity',
        labels={
            'carat': 'Carat Weight',
            'price': 'Price (USD)',
            'clarity': 'Clarity Level'
        },
        hover_data=['cut', 'color'],
        color_discrete_sequence=px.colors.sequential.Viridis
    )

    # Save static PNG to satisfy the image embedding requirement
    fig.write_image(out_path, scale=2)

    # Save interactive HTML to perfectly satisfy the "interactive" requirement
    html_path = out_path.replace('.png', '.html')
    fig.write_html(html_path)


def main() -> None:
    """
    Main execution flow for generating visualizations.
    """
    # Outputting to the current directory (assuming script is run inside module_10)
    output_dir = '.'
    data_file = 'diamonds.csv'

    try:
        df = load_diamond_data(data_file)
    except FileNotFoundError:
        print(f"Error: {data_file} not found. Please place it in the module_10 folder.")
        return

    ensure_output_dir(output_dir)

    # Generate the 3 required plots
    create_correlation_heatmap(df, os.path.join(output_dir, 'correlation_heatmap.png'))
    create_price_by_cut_boxplot(df, os.path.join(output_dir, 'price_by_cut.png'))
    create_carat_vs_price_scatter(df, os.path.join(output_dir, 'carat_vs_price.png'))

    print("Visualizations successfully generated and saved to the current directory.")


if __name__ == "__main__":
    main()
