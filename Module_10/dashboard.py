"""
dashboard.py

A Dash application that displays the Exploratory Data Analysis of the
Diamonds dataset. It embeds interactive Plotly charts and static Seaborn
images generated during the EDA phase.
"""

import os
import base64
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc


def load_base64_image(image_path: str) -> str:
    """
    Reads a local image file and converts it to a base64 encoded string
    so it can be embedded directly into the Dash HTML layout.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded string formatting for an HTML img src tag.
             Returns an empty string if the file is not found.
    """
    if not os.path.exists(image_path):
        return ""

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"


def create_dashboard() -> Dash:
    """
    Initializes and constructs the layout for the Dash application.

    Returns:
        Dash: The configured Dash application instance.
    """
    # Initialize the app
    app = Dash(__name__)

    # 1. Prepare the Interactive Plotly Figure
    try:
        df = pd.read_csv('diamonds.csv')
        sample_df = df.sample(n=2000, random_state=42)
        scatter_fig = px.scatter(
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
    except FileNotFoundError:
        # Fallback if CSV is missing
        scatter_fig = px.scatter(title="Error: diamonds.csv not found")

    # 2. Load the Seaborn PNGs as Base64 strings
    heatmap_src = load_base64_image('correlation_heatmap.png')
    boxplot_src = load_base64_image('price_by_cut.png')

    # 3. Define the Dashboard Layout
    app.layout = html.Div(
        style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'},
        children=[
            # Requirement: Overarching research question as the dashboard title
            html.H1(
                "Can the price of a diamond be determined based upon its features?",
                style={'textAlign': 'center', 'color': '#2c3e50'}
            ),

            # Requirement: Small amount of explanatory text (Fewer than 4 sentences)
            html.P(
                "Yes. Exploratory analysis reveals that physical size (carat weight) mathematically dictates "
                "the baseline price of a diamond. Secondary features like clarity and cut further influence "
                "the price tiers within those weight boundaries. Noticeably, proportional metrics like depth "
                "have negligible direct correlation with the price.",
                style={'fontSize': '18px', 'lineHeight': '1.6', 'color': '#34495e', 'marginBottom': '40px'}
            ),

            # Interactive Plotly Graph embedded directly
            html.Div(
                children=[dcc.Graph(figure=scatter_fig)],
                style={'marginBottom': '50px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'padding': '20px'}
            ),

            # Flexbox to display the two Seaborn static images side-by-side
            html.Div(
                style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px'},
                children=[
                    html.Div(
                        style={'flex': '1', 'textAlign': 'center', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'padding': '10px'},
                        children=[
                            html.H3("Feature Correlation (Seaborn)", style={'color': '#2c3e50'}),
                            html.Img(src=heatmap_src, style={'maxWidth': '100%', 'height': 'auto'}) if heatmap_src else html.P("Image not found. Please run visualization.py first.")
                        ]
                    ),
                    html.Div(
                        style={'flex': '1', 'textAlign': 'center', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'padding': '10px'},
                        children=[
                            html.H3("Price by Cut Quality (Seaborn)", style={'color': '#2c3e50'}),
                            html.Img(src=boxplot_src, style={'maxWidth': '100%', 'height': 'auto'}) if boxplot_src else html.P("Image not found. Please run visualization.py first.")
                        ]
                    )
                ]
            )
        ]
    )

    return app


def main() -> None:
    """
    Main execution block to run the local Dash server.
    """
    app = create_dashboard()
    print("Starting Dash server... Please open your browser to the URL below.")
    # debug=True allows for auto-reloading if you make code changes.
    # Note: Updated to app.run() for compatibility with modern Dash versions.
    app.run(debug=True)


if __name__ == '__main__':
    main()
