from flask import Flask, render_template, redirect, url_for, flash
import psycopg2
import threading
import os

# --- PART B: IMPORT YOUR SCRAPER ---
try:
    from src.scrapy import run_scraper
except ImportError:
    def run_scraper():
        import time
        time.sleep(0.1) 
        print("Scraper finished background task.")

# --- CONFIGURATION ---
template_dir = r"C:\Users\Masaomi Enami\Python Project\jhu_software_concepts\Module 3\templates"
app = Flask(__name__, template_folder=template_dir)
app.secret_key = "jhu_secret_key" 

scraping_active = False

DB_CONFIG = {
    "host": "localhost",
    "database": "postgres", 
    "user": "postgres",
    "password": "postgres", 
    "port": "5432"
}

def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_val(cursor, conn, query):
    try:
        cursor.execute(query)
        result = cursor.fetchone()[0]
        return result if result is not None else 0
    except Exception as e:
        conn.rollback() 
        return 0

# --- HELPER FOR THREADING (Enables 100% Coverage) ---
def execute_scraping_task():
    global scraping_active
    try:
        run_scraper()
    finally:
        scraping_active = False

@app.route('/pull_data', methods=['POST'])
def pull_data():
    global scraping_active
    if scraping_active:
        flash("A data pull is already in progress. Please wait for it to complete.")
    else:
        scraping_active = True
        threading.Thread(target=execute_scraping_task).start() 
        flash("Success: 'Pull Data' initiated. Scraper is running in background.")
    return redirect(url_for('index'))

@app.route('/update_analysis')
def update_analysis():
    global scraping_active
    if scraping_active:
        flash("Update Blocked: A data pull is currently running.")
    else:
        flash("Analysis Updated: Results have been refreshed.")
    return redirect(url_for('index'))

@app.route('/')
def index():
    conn = get_db_connection()
    data = {"scraping_status": scraping_active}
    if conn:
        cur = conn.cursor()
        data["q1"] = get_val(cur, conn, "SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026';")
        data["q2"] = round(get_val(cur, conn, "SELECT (COUNT(*) FILTER (WHERE us_or_international = 'International')::numeric / NULLIF(COUNT(*), 0)::numeric) * 100 FROM applicants;"), 2)
        data["avg_gpa"] = round(get_val(cur, conn, "SELECT AVG(gpa) FROM applicants WHERE term = 'Fall 2026' AND gpa <= 4.0;"), 2)
        data["avg_gre"] = round(get_val(cur, conn, "SELECT AVG(gre) FROM applicants WHERE term = 'Fall 2026' AND gre BETWEEN 130 AND 170;"), 2)
        data["avg_gre_v"] = round(get_val(cur, conn, "SELECT AVG(gre_v) FROM applicants WHERE term = 'Fall 2026' AND gre_v BETWEEN 130 AND 170;"), 2)
        data["avg_gre_aw"] = round(get_val(cur, conn, "SELECT AVG(gre_aw) FROM applicants WHERE term = 'Fall 2026' AND gre_aw BETWEEN 0 AND 6;"), 2)
        data["q4"] = round(get_val(cur, conn, "SELECT AVG(gpa) FROM applicants WHERE term = 'Fall 2026' AND us_or_international = 'American' AND gpa <= 4.0;"), 2)
        data["q5"] = round(get_val(cur, conn, "SELECT (COUNT(*) FILTER (WHERE status = 'Accepted' AND term = 'Fall 2026')::numeric / NULLIF(COUNT(*) FILTER (WHERE term = 'Fall 2026'), 0)::numeric) * 100 FROM applicants;"), 2)
        data["q6"] = round(get_val(cur, conn, "SELECT AVG(gpa) FROM applicants WHERE term = 'Fall 2026' AND status = 'Accepted' AND gpa <= 4.0;"), 2)
        data["q7"] = get_val(cur, conn, "SELECT COUNT(*) FROM applicants WHERE llm_generated_university ILIKE '%Johns Hopkins%' AND degree = 'Masters' AND llm_generated_program ILIKE '%Computer Science%';")
        data["q8"] = get_val(cur, conn, "SELECT COUNT(*) FROM applicants WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD' AND (program ILIKE '%MIT%' OR program ILIKE '%Stanford%' OR program ILIKE '%Carnegie%' OR program ILIKE '%CMU%');")
        data["q9"] = get_val(cur, conn, "SELECT COUNT(*) FROM applicants WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD' AND llm_generated_program ILIKE '%Computer Science%' AND llm_generated_university IN ('MIT', 'Stanford University', 'Carnegie Mellon University');")
        try:
            cur.execute("SELECT llm_generated_university, COUNT(*) as c FROM applicants WHERE term = 'Fall 2026' AND llm_generated_university IS NOT NULL GROUP BY llm_generated_university ORDER BY c DESC LIMIT 5;")
            data["q10"] = cur.fetchall()
            cur.execute("SELECT TRIM(BOTH '[] '' ' FROM llm_generated_university) AS cleaned_uni, COUNT(*) as c FROM applicants WHERE term = 'Fall 2026' AND llm_generated_university IS NOT NULL GROUP BY cleaned_uni ORDER BY c ASC, cleaned_uni ASC LIMIT 5;")
            data["q11"] = cur.fetchall()
        except:
            conn.rollback()
        cur.close()
        conn.close()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)