from app import app
from flask import render_template

@app.route('/')
def home():
    return render_template('index.html', active_page='home')

# CHECK THIS PART:
@app.route('/projects')
def projects():
    return render_template('projects.html', active_page='projects')

@app.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact')