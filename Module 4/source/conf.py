import os
import sys
# This tells Sphinx to look in the src folder relative to this conf.py file
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
project = 'Grad Cafe Analytics'
copyright = '2026, Masaomi Enami'
author = 'Masaomi Enami'
release = '1.0'

# -- General configuration ---------------------------------------------------
# You MUST add these extensions to fulfill the 'autodoc' requirement
extensions = [
    'sphinx.ext.autodoc',    # Pulls docstrings from your code
    'sphinx.ext.napoleon',   # Makes docstrings look professional
    'sphinx.ext.viewcode',   # Adds 'source' links in the docs
    'sphinx_rtd_theme',  
]

templates_path = ['_templates']
exclude_patterns = []
language = 'en'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']