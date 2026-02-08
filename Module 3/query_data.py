import psycopg2

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "database": "postgres", 
    "user": "postgres",
    "password": "postgres", 
    "port": "5432"
}

def run_analysis():
    try:
        # 1. Establish connection to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("\n" + "="*60)
        print("GRAD CAFE FINAL DATA ANALYSIS REPORT")
        print("="*60)

        # Helper functions to handle formatting and None values
        def fmt_avg(val): return f"{val:.2f}" if val is not None else "N/A"
        def fmt_pct(val): return f"{val:.2f}%" if val is not None else "N/A"

        # Question 1: How many entries do you have in your database who have applied for Fall 2026?
        cur.execute("SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026';")
        q1 = cur.fetchone()[0]
        print(f"1. Total Fall 2026 Entries: {q1}")

        # Question 2: What percentage of entries are from international students (not American or Other)?
        cur.execute("""
            SELECT ROUND(
                (COUNT(*) FILTER (WHERE us_or_international = 'International')::numeric / 
                NULLIF(COUNT(*), 0)::numeric) * 100, 2
            ) FROM applicants;
        """)
        q2 = cur.fetchone()[0]
        print(f"2. Percentage of International Students: {fmt_pct(q2)}")

        # Question 3: Average GPA, GRE, GRE V, GRE AW of applicants providing these metrics?
        cur.execute("SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw) FROM applicants;")
        avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()
        print(f"3. Global Averages (Overall):")
        print(f"   - GPA: {fmt_avg(avg_gpa)}")
        print(f"   - GRE Quant: {fmt_avg(avg_gre)}")
        print(f"   - GRE Verbal: {fmt_avg(avg_gre_v)}")
        print(f"   - GRE Writing: {fmt_avg(avg_gre_aw)}")

        # Question 4: Average GPA of American students in Fall 2026?
        cur.execute("""
            SELECT AVG(gpa) FROM applicants 
            WHERE us_or_international = 'American' AND term = 'Fall 2026';
        """)
        q4 = cur.fetchone()[0]
        print(f"4. Avg GPA (American, Fall 2026): {fmt_avg(q4)}")

        # Question 5: What percent of entries for Fall 2026 are Acceptances?
        cur.execute("""
            SELECT ROUND(
                (COUNT(*) FILTER (WHERE status = 'Accepted' AND term = 'Fall 2026')::numeric / 
                NULLIF(COUNT(*) FILTER (WHERE term = 'Fall 2026'), 0)::numeric) * 100, 2
            ) FROM applicants;
        """)
        q5 = cur.fetchone()[0]
        print(f"5. Fall 2026 Acceptance Rate: {fmt_pct(q5)}")

        # Question 6: What is the average GPA of applicants who applied for Fall 2026 who are Acceptances?
        cur.execute("""
            SELECT AVG(gpa) FROM applicants 
            WHERE term = 'Fall 2026' AND status = 'Accepted';
        """)
        q6 = cur.fetchone()[0]
        print(f"6. Avg GPA (Accepted, Fall 2026): {fmt_avg(q6)}")

        # Question 7: JHU Masters in Computer Science entries?
        cur.execute("""
            SELECT COUNT(*) FROM applicants 
            WHERE llm_generated_university ILIKE '%Johns Hopkins%' 
            AND degree = 'Masters' 
            AND llm_generated_program ILIKE '%Computer Science%';
        """)
        q7 = cur.fetchone()[0]
        print(f"7. JHU Computer Science Masters Entries: {q7}")

        # --- SETTING UP FOR QUESTIONS 8 & 9 ---
        elite_schools = "('Georgetown University', 'MIT', 'Stanford University', 'Carnegie Mellon University')"

        # Question 8: Elite PhD CS Acceptances (2026) using Original (Downloaded) Fields
        # We search the raw 'program' text for school keywords
        cur.execute(f"""
            SELECT COUNT(*) FROM applicants 
            WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD'
            AND program ILIKE '%Computer Science%'
            AND (program ILIKE '%Georgetown%' OR program ILIKE '%MIT%' 
                 OR program ILIKE '%Stanford%' OR program ILIKE '%Carnegie%');
        """)
        q8 = cur.fetchone()[0]
        print(f"8. Elite PhD CS Acceptances (Original Fields): {q8}")

        # Question 9: Elite PhD CS Acceptances (2026) using LLM Generated Fields
        cur.execute(f"""
            SELECT COUNT(*) FROM applicants 
            WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD'
            AND llm_generated_program ILIKE '%Computer Science%'
            AND llm_generated_university IN {elite_schools};
        """)
        q9 = cur.fetchone()[0]
        print(f"9. Elite PhD CS Acceptances (LLM Fields): {q9}")
        
        # Calculate the impact of using LLM cleaning
        diff = q9 - q8
        print(f"   -> Analysis: LLM cleanup found {abs(diff)} {'more' if diff >= 0 else 'fewer'} matches.")

        print("="*60)
        print("Analysis Complete.")

        # Close communication
        cur.close()
        conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_analysis()