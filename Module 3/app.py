from flask import Flask, render_template
import psycopg2
import os

# --- CONFIGURATION ---
template_dir = r"C:\Users\Masaomi Enami\Python Project\jhu_software_concepts\Module 3\templates"
app = Flask(__name__, template_folder=template_dir)

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
    """Helper to return a single value and reset if a query fails."""
    try:
        cursor.execute(query)
        result = cursor.fetchone()[0]
        return result if result is not None else 0
    except Exception as e:
        print(f"Query Failed: {query}\nError: {e}")
        conn.rollback() 
        return 0

@app.route('/')
def index():
    conn = get_db_connection()
    data = {}

    if conn:
        cur = conn.cursor()
        
        # --- Q1: Total Fall 2026 Entries ---
        # Fixed: Changed 'season' to 'term'
        data["q1"] = get_val(cur, conn, "SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026';")
        
        # --- Q2: % International Students ---
        data["q2"] = round(get_val(cur, conn, """
            SELECT (COUNT(*) FILTER (WHERE us_or_international = 'International')::numeric / 
            NULLIF(COUNT(*), 0)::numeric) * 100 FROM applicants;"""), 2)

        # --- Q3: Global Averages (Fall 2026) ---
        data["avg_gpa"] = round(get_val(cur, conn, "SELECT AVG(gpa) FROM applicants WHERE term = 'Fall 2026' AND gpa <= 4.0;"), 2)
        data["avg_gre"] = round(get_val(cur, conn, "SELECT AVG(gre) FROM applicants WHERE term = 'Fall 2026' AND gre BETWEEN 130 AND 170;"), 2)
        data["avg_gre_v"] = round(get_val(cur, conn, "SELECT AVG(gre_v) FROM applicants WHERE term = 'Fall 2026' AND gre_v BETWEEN 130 AND 170;"), 2)
        data["avg_gre_aw"] = round(get_val(cur, conn, "SELECT AVG(gre_aw) FROM applicants WHERE term = 'Fall 2026' AND gre_aw BETWEEN 0 AND 6;"), 2)

        # --- Q4: American GPA (Fall 2026) ---
        data["q4"] = round(get_val(cur, conn, "SELECT AVG(gpa) FROM applicants WHERE term = 'Fall 2026' AND us_or_international = 'American' AND gpa <= 4.0;"), 2)

        # --- Q5: Acceptance Rate (Fall 2026) ---
        # Check if your column is 'status' or 'decision_status'. Assuming 'status' based on previous context.
        data["q5"] = round(get_val(cur, conn, """
            SELECT (COUNT(*) FILTER (WHERE status = 'Accepted' AND term = 'Fall 2026')::numeric / 
            NULLIF(COUNT(*) FILTER (WHERE term = 'Fall 2026'), 0)::numeric) * 100 FROM applicants;"""), 2)

        # --- Q6: Accepted GPA (Fall 2026) ---
        data["q6"] = round(get_val(cur, conn, "SELECT AVG(gpa) FROM applicants WHERE term = 'Fall 2026' AND status = 'Accepted' AND gpa <= 4.0;"), 2)
        
        # --- Q7: JHU CS Masters Search ---
        data["q7"] = get_val(cur, conn, """
            SELECT COUNT(*) FROM applicants 
            WHERE llm_generated_university ILIKE '%Johns Hopkins%' 
            AND degree = 'Masters' AND llm_generated_program ILIKE '%Computer Science%';""")
        
        # --- Q8 & Q9: Elite PhD CS Acceptances ---
        data["q8"] = get_val(cur, conn, """
            SELECT COUNT(*) FROM applicants 
            WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD'
            AND (program ILIKE '%MIT%' OR program ILIKE '%Stanford%' OR program ILIKE '%Carnegie%' OR program ILIKE '%CMU%');""")
        
        data["q9"] = get_val(cur, conn, """
            SELECT COUNT(*) FROM applicants 
            WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD' 
            AND llm_generated_program ILIKE '%Computer Science%' 
            AND llm_generated_university IN ('MIT', 'Stanford University', 'Carnegie Mellon University');""")

        # --- Q10: Top 5 Most Applied ---
        try:
            cur.execute("""
                SELECT llm_generated_university, COUNT(*) as c 
                FROM applicants WHERE term = 'Fall 2026' AND llm_generated_university IS NOT NULL 
                GROUP BY llm_generated_university ORDER BY c DESC LIMIT 5;""")
            data["q10"] = cur.fetchall()
        except:
            conn.rollback()
            data["q10"] = []

        # --- Q11: Top 5 Lowest Applied ---
        try:
            cur.execute("""
                SELECT TRIM(BOTH '[] '' ' FROM llm_generated_university) AS cleaned_uni, COUNT(*) as c 
                FROM applicants WHERE term = 'Fall 2026' AND llm_generated_university IS NOT NULL 
                GROUP BY cleaned_uni ORDER BY c ASC, cleaned_uni ASC LIMIT 5;""")
            data["q11"] = cur.fetchall()
        except:
            conn.rollback()
            data["q11"] = []

        cur.close()
        conn.close()
    
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)