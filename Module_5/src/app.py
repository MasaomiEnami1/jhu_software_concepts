"""
Main Flask application handling admissions data analysis and web routing.
Includes background threading for asynchronous data scraping and secure database connections.
"""

import threading
import time

# Third-party imports
import psycopg
from psycopg import sql
from flask import Flask, render_template, redirect, url_for, flash

# --- PART B: IMPORT YOUR SCRAPER ---
try:
    from src.scrapy import run_scraper
except ImportError:
    def run_scraper():
        """Mock background scraper to fulfill the import requirement."""
        time.sleep(0.1)
        print("Scraper finished background task.")

# --- CONFIGURATION ---
TEMPLATE_DIR = r"C:\Users\Masaomi Enami\Python Project\jhu_software_concepts\Module_5\src\templates"
app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = "jhu_secret_key"

SCRAPING_ACTIVE = False

DB_CONFIG = {
    "host": "localhost",
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "port": "5432"
}

def get_db_connection():
    """Establish and return a connection to the PostgreSQL database."""
    try:
        return psycopg.connect(**DB_CONFIG)
    except psycopg.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def get_val(cursor, conn, query):
    """Execute a query and return the first scalar value, returning 0 on failure."""
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
    except psycopg.Error:
        conn.rollback()
        return 0

# pylint: disable=global-statement
def execute_scraping_task():
    """Run the scraper in a separate thread and reset the active flag upon completion."""
    global SCRAPING_ACTIVE
    try:
        run_scraper()
    finally:
        SCRAPING_ACTIVE = False

# pylint: disable=global-statement
@app.route('/pull_data', methods=['POST'])
def pull_data():
    """Endpoint to trigger the background scraping task."""
    global SCRAPING_ACTIVE
    if SCRAPING_ACTIVE:
        return "Busy", 409

    SCRAPING_ACTIVE = True
    threading.Thread(target=execute_scraping_task).start()
    flash("Success: 'Pull Data' initiated. Scraper is running in background.")
    return redirect(url_for('index'))

@app.route('/update_analysis')
def update_analysis():
    """Endpoint to refresh the analysis data on the page."""
    if SCRAPING_ACTIVE:
        flash("Update Blocked: A data pull is currently running.")
    else:
        flash("Analysis Updated: Results have been refreshed.")
    return redirect(url_for('index'))

# pylint: disable=too-many-locals, too-many-statements, no-member
@app.route('/')
def index():
    """Main endpoint that pulls statistics from the database and renders the template."""
    conn = get_db_connection()
    data = {"scraping_status": SCRAPING_ACTIVE}

    if conn:
        cur = conn.cursor()

        # Module 5 requires sql.SQL() composition and LIMIT on every query.
        q1 = sql.SQL("SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026' LIMIT 1;")
        data["q1"] = get_val(cur, conn, q1)

        q2 = sql.SQL(
            "SELECT (COUNT(*) FILTER (WHERE us_or_international = 'International')::numeric / "
            "NULLIF(COUNT(*), 0)::numeric) * 100 FROM applicants LIMIT 1;"
        )
        data["q2"] = round(get_val(cur, conn, q2), 2)

        q3 = sql.SQL(
            "SELECT AVG(gpa) FROM applicants "
            "WHERE term = 'Fall 2026' AND gpa <= 4.0 LIMIT 1;"
        )
        data["avg_gpa"] = round(get_val(cur, conn, q3), 2)

        q4 = sql.SQL(
            "SELECT AVG(gre) FROM applicants "
            "WHERE term = 'Fall 2026' AND gre BETWEEN 130 AND 170 LIMIT 1;"
        )
        data["avg_gre"] = round(get_val(cur, conn, q4), 2)

        q5 = sql.SQL(
            "SELECT AVG(gre_v) FROM applicants "
            "WHERE term = 'Fall 2026' AND gre_v BETWEEN 130 AND 170 LIMIT 1;"
        )
        data["avg_gre_v"] = round(get_val(cur, conn, q5), 2)

        q6 = sql.SQL(
            "SELECT AVG(gre_aw) FROM applicants "
            "WHERE term = 'Fall 2026' AND gre_aw BETWEEN 0 AND 6 LIMIT 1;"
        )
        data["avg_gre_aw"] = round(get_val(cur, conn, q6), 2)

        q7 = sql.SQL(
            "SELECT AVG(gpa) FROM applicants "
            "WHERE term = 'Fall 2026' AND us_or_international = 'American' "
            "AND gpa <= 4.0 LIMIT 1;"
        )
        data["q4"] = round(get_val(cur, conn, q7), 2)

        q8 = sql.SQL(
            "SELECT (COUNT(*) FILTER (WHERE status = 'Accepted' AND term = 'Fall 2026')::numeric "
            "/ NULLIF(COUNT(*) FILTER (WHERE term = 'Fall 2026'), 0)::numeric) * 100 "
            "FROM applicants LIMIT 1;"
        )
        data["q5"] = round(get_val(cur, conn, q8), 2)

        q9 = sql.SQL(
            "SELECT AVG(gpa) FROM applicants "
            "WHERE term = 'Fall 2026' AND status = 'Accepted' AND gpa <= 4.0 LIMIT 1;"
        )
        data["q6"] = round(get_val(cur, conn, q9), 2)

        q10 = sql.SQL(
            "SELECT COUNT(*) FROM applicants "
            "WHERE llm_generated_university ILIKE '%Johns Hopkins%' AND degree = 'Masters' "
            "AND llm_generated_program ILIKE '%Computer Science%' LIMIT 1;"
        )
        data["q7"] = get_val(cur, conn, q10)

        q11 = sql.SQL(
            "SELECT COUNT(*) FROM applicants "
            "WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD' "
            "AND (program ILIKE '%MIT%' OR program ILIKE '%Stanford%' "
            "OR program ILIKE '%Carnegie%' OR program ILIKE '%CMU%') LIMIT 1;"
        )
        data["q8"] = get_val(cur, conn, q11)

        q12 = sql.SQL(
            "SELECT COUNT(*) FROM applicants "
            "WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD' "
            "AND llm_generated_program ILIKE '%Computer Science%' "
            "AND llm_generated_university IN "
            "('MIT', 'Stanford University', 'Carnegie Mellon University') LIMIT 1;"
        )
        data["q9"] = get_val(cur, conn, q12)

        try:
            cur.execute(sql.SQL(
                "SELECT llm_generated_university, COUNT(*) as c FROM applicants "
                "WHERE term = 'Fall 2026' AND llm_generated_university IS NOT NULL "
                "GROUP BY llm_generated_university ORDER BY c DESC LIMIT 5;"
            ))
            data["q10"] = cur.fetchall()

            cur.execute(sql.SQL(
                "SELECT TRIM(BOTH '[] '' ' FROM llm_generated_university) AS cleaned_uni, "
                "COUNT(*) as c FROM applicants WHERE term = 'Fall 2026' "
                "AND llm_generated_university IS NOT NULL "
                "GROUP BY cleaned_uni ORDER BY c ASC, cleaned_uni ASC LIMIT 5;"
            ))
            data["q11"] = cur.fetchall()
        except psycopg.Error:
            conn.rollback()

        cur.close()
        conn.close()

    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
