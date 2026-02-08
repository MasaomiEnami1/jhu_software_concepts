from flask import Flask, render_template
import psycopg2
import os

# --- CONFIGURATION ---
# Pointing to your specific folder to ensure the correct index.html is loaded
template_dir = r"C:\Users\Masaomi Enami\Python Project\jhu_software_concepts\Module 3\templates"
app = Flask(__name__, template_folder=template_dir)

# Your working database configuration
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

def get_val(cursor, query):
    try:
        cursor.execute(query)
        result = cursor.fetchone()[0]
        return result if result is not None else 0
    except:
        return 0

@app.route('/')
def index():
    conn = get_db_connection()
    data = {}

    if conn:
        cur = conn.cursor()
        
        # Q1: Total Entries
        data["q1"] = get_val(cur, "SELECT COUNT(*) FROM applicants;")
        
        # Q2: International %
        data["q2"] = round(get_val(cur, "SELECT (COUNT(*) FILTER (WHERE us_or_international = 'International') * 100.0 / NULLIF(COUNT(*), 0)) FROM applicants;"), 2)

        # Q3: Sample Majors
        cur.execute("SELECT DISTINCT program FROM applicants LIMIT 5;")
        data["q3"] = [row[0] for row in cur.fetchall()]

        # Q3 (Extra Metrics): Average GPA, GRE, GRE V, GRE AW
        data["avg_gpa"] = round(get_val(cur, "SELECT AVG(gpa) FROM applicants;"), 2)
        data["avg_gre"] = round(get_val(cur, "SELECT AVG(gre) FROM applicants;"), 2)
        data["avg_gre_v"] = round(get_val(cur, "SELECT AVG(gre_v) FROM applicants;"), 2)
        data["avg_gre_aw"] = round(get_val(cur, "SELECT AVG(gre_aw) FROM applicants;"), 2)

        # Q4: American GPA
        data["q4"] = round(get_val(cur, "SELECT AVG(gpa) FROM applicants WHERE us_or_international = 'American';"), 2)

        # Q5: Acceptance %
        data["q5"] = round(get_val(cur, "SELECT (COUNT(*) FILTER (WHERE status = 'Accepted') * 100.0 / NULLIF(COUNT(*), 0)) FROM applicants;"), 2)

        # Q6: Accepted GPA
        data["q6"] = round(get_val(cur, "SELECT AVG(gpa) FROM applicants WHERE status = 'Accepted';"), 2)
        
        # Q7-Q9: Special Queries
        data["q7"] = get_val(cur, "SELECT COUNT(*) FROM applicants WHERE llm_generated_university ILIKE '%Johns Hopkins%';")
        data["q8"] = get_val(cur, "SELECT COUNT(*) FROM applicants WHERE url ILIKE '%mit%' OR url ILIKE '%stanford%' OR url ILIKE '%berkeley%' OR url ILIKE '%cmu%';")
        data["q9"] = get_val(cur, "SELECT COUNT(*) FROM applicants WHERE llm_generated_university IN ('Massachusetts Institute of Technology', 'Stanford University', 'Carnegie Mellon University', 'University of California, Berkeley');")

        # Q10 & Q11: Rankings
        cur.execute("SELECT llm_generated_university, COUNT(*) as c FROM applicants WHERE llm_generated_university IS NOT NULL GROUP BY llm_generated_university ORDER BY c DESC LIMIT 5;")
        data["q10"] = cur.fetchall()

        cur.execute("SELECT llm_generated_university, COUNT(*) as c FROM applicants WHERE llm_generated_university IS NOT NULL GROUP BY llm_generated_university ORDER BY c ASC LIMIT 5;")
        data["q11"] = cur.fetchall()

        cur.close()
        conn.close()
    
    return render_template('index.html', data=data)

if __name__ == '__main__':
    # Running strictly on Port 5001 as requested
    print("STARTING SERVER ON http://127.0.0.1:5001")
    app.run(debug=True, port=5001)