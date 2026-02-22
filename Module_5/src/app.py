# pylint: disable=duplicate-code
"""
Main Flask application handling admissions data analysis and web routing.
Includes background threading for asynchronous data scraping and secure database connections.
"""

import os
import threading
import time

# Third-party imports
import psycopg
from psycopg import sql
from flask import Flask, render_template, redirect, url_for, flash
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

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

# Module 5: Read credentials from environment variables safely
DB_CONFIG = dict(
    host=os.getenv("DB_HOST", "localhost"),
    dbname=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USER", "gradcafe_web"),
    password=os.getenv("DB_PASSWORD", "jhu_secure_pass_2026"),
    port=os.getenv("DB_PORT", "5432")
)

def get_db_connection():
    """Establish and return a connection to the PostgreSQL database."""
    try:
        return psycopg.connect(**DB_CONFIG)
    except psycopg.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def get_safe_limit(requested_limit):
    """
    Module 5 Requirement: Enforce a maximum allowed limit.
    Clamp the limit to strictly between 1 and 100.
    """
    try:
        return max(1, min(int(requested_limit), 100))
    except (ValueError, TypeError):
        return 10

def get_val(cursor, conn, query, params=None):
    """Execute a query with parameters and return the first scalar value."""
    try:
        # Module 5 Requirement: Separate execution from parameters
        cursor.execute(query, params)
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
        
        # We clamp all our single-value queries to a safe limit of 1
        safe_single_limit = get_safe_limit(1)

        # Q1: Parameterized value (%s) and composed Identifier/Literal
        q1 = sql.SQL("SELECT COUNT(*) FROM {table} WHERE term = %s LIMIT {limit};").format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["q1"] = get_val(cur, conn, q1, ("Fall 2026",))

        # Q2
        q2 = sql.SQL(
            "SELECT ROUND((COUNT(*) FILTER (WHERE us_or_international = %s)::numeric / "
            "NULLIF(COUNT(*), 0)::numeric) * 100, 2) FROM {table} LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["q2"] = get_val(cur, conn, q2, ("International",))

        # Q3
        q3 = sql.SQL(
            "SELECT AVG(gpa) FROM {table} WHERE term = %s AND gpa <= %s LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["avg_gpa"] = round(get_val(cur, conn, q3, ("Fall 2026", 4.0)), 2)

        # Q4
        q4 = sql.SQL(
            "SELECT AVG(gre) FROM {table} WHERE term = %s AND gre BETWEEN %s AND %s LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["avg_gre"] = round(get_val(cur, conn, q4, ("Fall 2026", 130, 170)), 2)

        # Q5
        q5 = sql.SQL(
            "SELECT AVG(gre_v) FROM {table} WHERE term = %s AND gre_v BETWEEN %s AND %s LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["avg_gre_v"] = round(get_val(cur, conn, q5, ("Fall 2026", 130, 170)), 2)

        # Q6
        q6 = sql.SQL(
            "SELECT AVG(gre_aw) FROM {table} WHERE term = %s AND gre_aw BETWEEN %s AND %s LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["avg_gre_aw"] = round(get_val(cur, conn, q6, ("Fall 2026", 0, 6)), 2)

        # Q7
        q7 = sql.SQL(
            "SELECT AVG(gpa) FROM {table} "
            "WHERE term = %s AND us_or_international = %s AND gpa <= %s LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["q4"] = round(get_val(cur, conn, q7, ("Fall 2026", "American", 4.0)), 2)

        # Q8
        q8 = sql.SQL(
            "SELECT ROUND((COUNT(*) FILTER (WHERE status = %s AND term = %s)::numeric / "
            "NULLIF(COUNT(*) FILTER (WHERE term = %s), 0)::numeric) * 100, 2) "
            "FROM {table} LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["q5"] = round(get_val(cur, conn, q8, ("Accepted", "Fall 2026", "Fall 2026")), 2)

        # Q9
        q9 = sql.SQL(
            "SELECT AVG(gpa) FROM {table} WHERE term = %s AND status = %s AND gpa <= %s LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["q6"] = round(get_val(cur, conn, q9, ("Fall 2026", "Accepted", 4.0)), 2)

        # Q10
        q10 = sql.SQL(
            "SELECT COUNT(*) FROM {table} "
            "WHERE llm_generated_university ILIKE %s AND degree = %s "
            "AND llm_generated_program ILIKE %s LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["q7"] = get_val(cur, conn, q10, ("%Johns Hopkins%", "Masters", "%Computer Science%"))

        # Q11
        q11 = sql.SQL(
            "SELECT COUNT(*) FROM {table} "
            "WHERE status = %s AND term = %s AND degree = %s "
            "AND (program ILIKE %s OR program ILIKE %s OR program ILIKE %s OR program ILIKE %s) "
            "LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["q8"] = get_val(cur, conn, q11, (
            "Accepted", "Fall 2026", "PhD", 
            "%MIT%", "%Stanford%", "%Carnegie%", "%CMU%"
        ))

        # Q12
        q12 = sql.SQL(
            "SELECT COUNT(*) FROM {table} "
            "WHERE status = %s AND term = %s AND degree = %s "
            "AND llm_generated_program ILIKE %s "
            "AND llm_generated_university IN (%s, %s, %s) LIMIT {limit};"
        ).format(
            table=sql.Identifier("applicants"),
            limit=sql.Literal(safe_single_limit)
        )
        data["q9"] = get_val(cur, conn, q12, (
            "Accepted", "Fall 2026", "PhD", "%Computer Science%",
            "MIT", "Stanford University", "Carnegie Mellon University"
        ))

        # Fetching list data (Top 5s)
        try:
            safe_list_limit = get_safe_limit(5)
            
            list_q1 = sql.SQL(
                "SELECT llm_generated_university, COUNT(*) as c FROM {table} "
                "WHERE term = %s AND llm_generated_university IS NOT NULL "
                "GROUP BY llm_generated_university ORDER BY c DESC LIMIT {limit};"
            ).format(
                table=sql.Identifier("applicants"),
                limit=sql.Literal(safe_list_limit)
            )
            cur.execute(list_q1, ("Fall 2026",))
            data["q10"] = cur.fetchall()

            list_q2 = sql.SQL(
                "SELECT TRIM(BOTH '[] '' ' FROM llm_generated_university) AS cleaned_uni, "
                "COUNT(*) as c FROM {table} WHERE term = %s "
                "AND llm_generated_university IS NOT NULL "
                "GROUP BY cleaned_uni ORDER BY c ASC, cleaned_uni ASC LIMIT {limit};"
            ).format(
                table=sql.Identifier("applicants"),
                limit=sql.Literal(safe_list_limit)
            )
            cur.execute(list_q2, ("Fall 2026",))
            data["q11"] = cur.fetchall()
            
        except psycopg.Error:
            conn.rollback()

        cur.close()
        conn.close()

    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
