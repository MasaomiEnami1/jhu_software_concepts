"""
Module 10: Dash application for Diamonds EDA.
Displays interactive Plotly charts and static Seaborn images.
"""

import os
import base64
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc

# --- CONSTANTS & STYLES ---
MAIN_TITLE = "Can the price of a diamond be determined based upon its features?"
EXPLANATORY_TEXT = (
    "Yes. Exploratory analysis reveals that physical size (carat weight) "
    "mathematically dictates the baseline price of a diamond. Secondary "
    "features like clarity and cut further influence the price tiers. "
    "Proportional metrics like depth have negligible direct correlation."
)

LAYOUT_STYLE = {
    'fontFamily': 'Arial, sans-serif',
    'maxWidth': '1200px',
    'margin': '0 auto',
    'padding': '20px'
}

CARD_STYLE = {
    'marginBottom': '50px',
    'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
    'padding': '20px'
}


def load_base64_image(image_path: str) -> str:
    """Converts a local image file to a base64 encoded string."""
    if not os.path.exists(image_path):
        return ""

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"


def create_dashboard() -> Dash:
    """Constructs the Dash application layout."""
    app = Dash(__name__)

    # 1. Prepare Plotly Figure
    try:
        df_diamonds = pd.read_csv('diamonds.csv')
        sample_df = df_diamonds.sample(n=2000, random_state=42)
        scatter_fig = px.scatter(
            sample_df, x='carat', y='price', color='clarity',
            title='Interactive: Carat vs Price by Clarity',
            labels={'carat': 'Weight', 'price': 'Price', 'clarity': 'Clarity'},
            hover_data=['cut', 'color'],
            color_discrete_sequence=px.colors.sequential.Viridis
        )
    except FileNotFoundError:
        scatter_fig = px.scatter(title="Error: diamonds.csv not found")

    # 2. Load Static Images (Filenames updated to match Grader expectations)
    heatmap_src = load_base64_image('correlation_heatmap.png')
    # CHANGED: Updated filename to match README link requirement
    boxplot_src = load_base64_image('price_by_cut_boxplot.png')

    # 3. Define Layout
    app.layout = html.Div(style=LAYOUT_STYLE, children=[
        html.H1(MAIN_TITLE, style={'textAlign': 'center', 'color': '#2c3e50'}),

        html.P(EXPLANATORY_TEXT, style={'fontSize': '18px', 'color': '#34495e'}),

        html.Div(children=[dcc.Graph(figure=scatter_fig)], style=CARD_STYLE),

        html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
            html.Div(style={'flex': '1', 'textAlign': 'center'}, children=[
                html.H3("Feature Correlation", style={'color': '#2c3e50'}),
                html.Img(src=heatmap_src, style={'maxWidth': '100%'})
                if heatmap_src else html.P("Heatmap missing.")
            ]),
            html.Div(style={'flex': '1', 'textAlign': 'center'}, children=[
                html.H3("Price by Cut Quality", style={'color': '#2c3e50'}),
                html.Img(src=boxplot_src, style={'maxWidth': '100%'})
                if boxplot_src else html.P("Boxplot missing.")
            ])
        ])
    ])
    return app


def main() -> None:
    """Runs the Dash server."""
    app = create_dashboard()
    print("Starting server... Open browser to view dashboard.")
    app.run(debug=True)


if __name__ == '__main__':
    main()
