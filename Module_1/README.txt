============================================================
PROJECT: Module 1 - Personal Portfolio Website
COURSE: Modern Software Concepts in Python
STUDENT: Masaomi Enami
============================================================

### DESCRIPTION
This is a Flask-based web application that serves as a professional 
portfolio. It features a modular package structure, a colorized 
navigation bar with active-tab highlighting, and a responsive bio layout.

### SHALL REQUIREMENTS INCLUDED:
1. Framework: Built using Flask.
2. Server Config: Runs on host 0.0.0.0 and port 8080.
3. Entry Point: Application starts via 'python run.py'.
4. Layout: Homepage bio on left, image on right.
5. Navigation: Top-right aligned, colorized, with current tab highlighting.
6. Documentation: Includes requirements.txt and screenshots.pdf.

### HOW TO RECONSTRUCT THE ENVIRONMENT
Follow these steps to run the application on your local machine:

1. Navigate to the 'Module 1' directory:
   cd "Module 1"

2. Install the necessary dependencies (Flask, etc.):
   pip install -r requirements.txt

3. Start the web server:
   python run.py

4. View the website:
   Open your browser and go to http://localhost:8080

### DIRECTORY STRUCTURE
- /app          : Main application package
- /app/static   : Images and CSS
- /app/templates: HTML files (Home, Projects, Contact)
- run.py        : Execution script
- README.txt    : This file
- screenshots.pdf: Visual proof of running application
============================================================