Grad School Cafe Data Analysis
Project Overview

This project is a web-based data analysis tool designed to scrape, store, and analyze graduate school application data from the Grad Cafe. The application utilizes Python, Flask, and PostgreSQL to provide real-time insights into application trends for the Fall 2026 semester.
Features

    Automated Data Scraping: Integrates a web scraper to collect application entries directly from the web.

    Database Management: Stores collected data in a structured PostgreSQL database for persistent storage and analysis.

    Interactive Dashboard: A Flask-powered webpage displaying 11 key metrics, including applicant counts, average GPAs, GRE scores, and university rankings.

    Part B Management Tools:

        Pull Data Button: Triggers the background scraper to add new data to the database without freezing the UI.

        Update Analysis Button: Refreshes the metrics on the dashboard to include newly pulled data.

Project Structure
Plaintext

module_3/
├── app.py              # Main Flask application and server logic
├── scrapy.py           # Web scraping logic from Module 2
├── load_data.py        # Script to migrate JSON data to PostgreSQL
├── query_data.py       # Console-based query tool for terminal output
├── limitations.pdf     # Essay on the limitations of anonymous data
├── requirements.txt    # List of required Python libraries
├── README.md           # Project documentation
├── templates/
│   └── index.html      # Styled frontend dashboard
└── screenshots/        # Evidence of console and webpage functionality

Setup and Installation

    Database Configuration:

        Ensure PostgreSQL is running on localhost:5432.

        Configure the DB_CONFIG in app.py with your credentials.

    Install Dependencies:

        Run the following command in your terminal:
        Bash

        pip install -r requirements.txt

    Run the Application:

        Start the web server:
        Bash

        python app.py

        Open your browser and navigate to http://127.0.0.1:5001.