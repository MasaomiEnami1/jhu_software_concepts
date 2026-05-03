import json
import os
from flask import Flask, render_template

app = Flask(__name__)

def load_portfolio_data():
    """Dynamically loads all module data from the JSON file."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, 'projects.json')
    
    if not os.path.exists(json_path):
        return []
        
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
@app.route('/projects')
def projects_page():
    data = load_portfolio_data()
    # Ensure modules are displayed in order
    data.sort(key=lambda x: x['id'])
    return render_template('projects.html', projects=data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)