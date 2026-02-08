from flask import Flask, render_template
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "database": "postgres", 
    "user": "postgres",
    "password": "postgres", 
    "port": "5432"
}

def initialize_database():
    """
    Checks for the 'Data Type' table and creates/populates it if missing.
    Runs automatically when the app starts.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'Data Type'
            );
        """)
        table_exists = cur.fetchone()[0]

        if not table_exists:
            print("--- Table 'Data Type' not found. Creating it now... ---")
            
            # 1. Create Table
            cur.execute('''
                CREATE TABLE "Data Type" (
                    column_name TEXT,
                    data_type TEXT,
                    description TEXT
                );
            ''')

            # 2. Prepare Data
            metadata_rows = [
                ("p_id", "integer", "Unique identifier"),
                ("program", "text", "Department and University"),
                ("comments", "text", "User comments"),
                ("date_added", "date", "Submission date"),
                ("status", "text", "Accepted/Rejected/Waitlisted"),
                ("term", "text", "Application Term (e.g., Fall 2026)"),
                ("us_or_international", "text", "Student Citizenship Status"),
                ("gpa", "float", "Undergraduate GPA (0.0-4.0)"),
                ("gre", "float", "GRE Quant Score"),
                ("gre_v", "float", "GRE Verbal Score"),
                ("gre_aw", "float", "GRE Analytical Writing Score"),
                ("llm_generated_university", "text", "Standardized University Name")
            ]

            # 3. Insert Data
            insert_query = 'INSERT INTO "Data Type" (column_name, data_type, description) VALUES (%s, %s, %s);'
            cur.executemany(insert_query, metadata_rows)
            
            conn.commit()
            print("--- Successfully created and populated 'Data Type' table. ---")
        else:
            print("--- 'Data Type' table already exists. Skipping setup. ---")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Database Initialization Error: {e}")

def get_db_results():
    results = {}
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 1. Total Fall 2026 Entries
        cur.execute("SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026';")
        results['q1'] = cur.fetchone()[0]

        # 2. % International
        cur.execute("""
            SELECT ROUND((COUNT(*) FILTER (WHERE us_or_international = 'International')::numeric / 
            NULLIF(COUNT(*), 0)::numeric) * 100, 2) FROM applicants;
        """)
        results['q2'] = cur.fetchone()[0]

        # 3. Global Averages (Cleaned)
        cur.execute("""
            SELECT 
                AVG(gpa) FILTER (WHERE gpa <= 4.0), 
                AVG(gre) FILTER (WHERE gre >= 130 AND gre <= 170), 
                AVG(gre_v) FILTER (WHERE gre_v >= 130 AND gre_v <= 170), 
                AVG(gre_aw) FILTER (WHERE gre_aw >= 0 AND gre_aw <= 6)
            FROM applicants;
        """)
        avg_data = cur.fetchone()
        results['avg_gpa'] = f"{avg_data[0]:.2f}" if avg_data[0] else "N/A"
        results['avg_gre_q'] = f"{avg_data[1]:.2f}" if avg_data[1] else "N/A"
        results['avg_gre_v'] = f"{avg_data[2]:.2f}" if avg_data[2] else "N/A"
        results['avg_gre_aw'] = f"{avg_data[3]:.2f}" if avg_data[3] else "N/A"

        # 4. Top 5 Universities
        cur.execute("""
            SELECT llm_generated_university, COUNT(*) as apps 
            FROM applicants 
            WHERE llm_generated_university IS NOT NULL 
            GROUP BY llm_generated_university 
            ORDER BY apps DESC LIMIT 5;
        """)
        results['top_unis'] = cur.fetchall()

        # 5. Metadata Table
        cur.execute('SELECT * FROM "Data Type";')
        results['metadata'] = cur.fetchall()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Query Error: {e}")
        # Return empty/default data so the page doesn't crash completely
        results = {
            'q1': 'Error', 'q2': 'Error', 
            'avg_gpa': 'N/A', 'avg_gre_q': 'N/A', 'avg_gre_v': 'N/A', 'avg_gre_aw': 'N/A',
            'top_unis': [], 'metadata': []
        }
    return results

# --- RUN SETUP ON STARTUP ---
# We call this once when the script loads
initialize_database()

@app.route('/')
def index():
    data = get_db_results()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)