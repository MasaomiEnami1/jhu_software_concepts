from flask import Flask, render_template, redirect, url_for, flash
import psycopg2
import threading
import os

# --- PART B: IMPORT YOUR SCRAPER ---
# Ensure scrapy.py has a function named run_scraper()
try:
    from scrapy import run_scraper
except ImportError:
    def run_scraper():
        import time
        time.sleep(10) # Simulates background work
        print("Scraper finished background task.")

# --- CONFIGURATION ---
template_dir = r"C:\Users\Masaomi Enami\Python Project\jhu_software_concepts\Module 3\templates"
app = Flask(__name__, template_folder=template_dir)
app.secret_key = "jhu_secret_key" # Required for flash messages

# Global flag to track scraper status
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

# --- PART B: PULL DATA ROUTE ---
@app.route('/pull_data', methods=['POST'])
def pull_data():
    global scraping_active
    if scraping_active:
        flash("A data pull is already in progress. Please wait for it to complete.")
    else:
        scraping_active = True
        def task():
            global scraping_active
            try:
                run_scraper() # Calls your scrapy.py script
            finally:
                scraping_active = False
        
        threading.Thread(target=task).start() # Runs in background
        flash("Success: 'Pull Data' initiated. The scraper is now adding new records in the background.")
    return redirect(url_for('index'))

# --- PART B: UPDATE ANALYSIS ROUTE ---
@app.route('/update_analysis')
def update_analysis():
    global scraping_active
    if scraping_active:
        flash("Update Blocked: A data pull is currently running. Please wait until it finishes.")
    else:
        flash("Analysis Updated: Results have been refreshed with the latest data.")
    return redirect(url_for('index'))

@app.route('/')
def index():
    conn = get_db_connection()
    # Pass the scraper status to the HTML
    data = {"scraping_status": scraping_active}

    if conn:
        cur = conn.cursor()
        
        # --- Standard Analysis Queries ---
        data["q1"] = get_val(cur, conn, "SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026';")
        data["q2"] = round(get_val(cur, conn, "SELECT (COUNT(*) FILTER (WHERE us_or_international = 'International')::numeric / NULLIF(COUNT(*), 0)::numeric) * 100 FROM applicants;"), 2)
        
        # Q3: Academic Averages
        data["avg_gpa"] = round(get_val(cur, conn, "SELECT AVG(gpa) FROM applicants WHERE term = 'Fall 2026' AND gpa <= 4.0;"), 2)
        data["avg_gre"] = round(get_val(cur, conn, "SELECT AVG(gre) FROM applicants WHERE term = 'Fall 2026' AND gre BETWEEN 130 AND 170;"), 2)
        data["avg_gre_v"] = round(get_val(cur, conn, "SELECT AVG(gre_v) FROM applicants WHERE term = 'Fall 2026' AND gre_v BETWEEN 130 AND 170;"), 2)
        data["avg_gre_aw"] = round(get_val(cur, conn, "SELECT AVG(gre_aw) FROM applicants WHERE term = 'Fall 2026' AND gre_aw BETWEEN 0 AND 6;"), 2)

        # Other Queries
        data["q4"] = round(get_val(cur, conn, "SELECT AVG(gpa) FROM applicants WHERE term = 'Fall 2026' AND us_or_international = 'American' AND gpa <= 4.0;"), 2)
        data["q5"] = round(get_val(cur, conn, "SELECT (COUNT(*) FILTER (WHERE status = 'Accepted' AND term = 'Fall 2026')::numeric / NULLIF(COUNT(*) FILTER (WHERE term = 'Fall 2026'), 0)::numeric) * 100 FROM applicants;"), 2)
        data["q6"] = round(get_val(cur, conn, "SELECT AVG(gpa) FROM applicants WHERE term = 'Fall 2026' AND status = 'Accepted' AND gpa <= 4.0;"), 2)
        data["q7"] = get_val(cur, conn, "SELECT COUNT(*) FROM applicants WHERE llm_generated_university ILIKE '%Johns Hopkins%' AND degree = 'Masters' AND llm_generated_program ILIKE '%Computer Science%';")
        data["q8"] = get_val(cur, conn, "SELECT COUNT(*) FROM applicants WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD' AND (program ILIKE '%MIT%' OR program ILIKE '%Stanford%' OR program ILIKE '%Carnegie%' OR program ILIKE '%CMU%');")
        data["q9"] = get_val(cur, conn, "SELECT COUNT(*) FROM applicants WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD' AND llm_generated_program ILIKE '%Computer Science%' AND llm_generated_university IN ('MIT', 'Stanford University', 'Carnegie Mellon University');")

        # Q10 & Q11: Rankings
        try:
            cur.execute("SELECT llm_generated_university, COUNT(*) as c FROM applicants WHERE term = 'Fall 2026' AND llm_generated_university IS NOT NULL GROUP BY llm_generated_university ORDER BY c DESC LIMIT 5;")
            data["q10"] = cur.fetchall()
            
            # Q11: Lowest Application Counts
            cur.execute("SELECT TRIM(BOTH '[] '' ' FROM llm_generated_university) AS cleaned_uni, COUNT(*) as c FROM applicants WHERE term = 'Fall 2026' AND llm_generated_university IS NOT NULL GROUP BY cleaned_uni ORDER BY c ASC, cleaned_uni ASC LIMIT 5;")
            data["q11"] = cur.fetchall()
        except:
            conn.rollback()

        cur.close()
        conn.close()
    
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)