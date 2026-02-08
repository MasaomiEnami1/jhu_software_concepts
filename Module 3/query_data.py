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
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("--- GRAD CAFE DATA ANALYSIS RESULTS ---")
        print("-" * 50)

        # Question 1: Total Fall 2026 entries
        cur.execute("SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026';")
        fall_2026_count = cur.fetchone()[0]
        print(f"1. Total Fall 2026 Entries: {fall_2026_count}")

        # Question 2: % of International students
        cur.execute("""
            SELECT ROUND(
                (COUNT(*) FILTER (WHERE us_or_international = 'International')::numeric / 
                NULLIF(COUNT(*), 0)::numeric) * 100, 2
            ) FROM applicants;
        """)
        int_pct = cur.fetchone()[0]
        print(f"2. Percentage of International Students: {int_pct}%")

        # Question 3: Global Averages (GPA and GRE)
        cur.execute("SELECT AVG(gpa), AVG(gre), AVG(gre_v), AVG(gre_aw) FROM applicants;")
        avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()
        print(f"3. Global Averages:")
        print(f"   - GPA: {avg_gpa:.2f}" if avg_gpa else "   - GPA: N/A")
        print(f"   - GRE Quant: {avg_gre:.2f}" if avg_gre else "   - GRE Quant: N/A")
        print(f"   - GRE Verbal: {avg_gre_v:.2f}" if avg_gre_v else "   - GRE Verbal: N/A")
        print(f"   - GRE Writing: {avg_gre_aw:.2f}" if avg_gre_aw else "   - GRE Writing: N/A")

        # Question 4: Avg GPA of American students for Fall 2026
        cur.execute("""
            SELECT AVG(gpa) FROM applicants 
            WHERE us_or_international = 'American' AND term = 'Fall 2026';
        """)
        q4 = cur.fetchone()[0]
        print(f"4. Avg GPA (American, Fall 2026): {q4:.2f}" if q4 else "4. Avg GPA (American, Fall 2026): N/A")

        # Question 7: JHU Computer Science Masters search
        # Note: Using the column names 'llm_generated_university' and 'llm_generated_program'
        cur.execute("""
            SELECT COUNT(*) FROM applicants 
            WHERE llm_generated_university ILIKE '%Johns Hopkins%' 
            AND degree = 'Masters' 
            AND llm_generated_program ILIKE '%Computer Science%';
        """)
        jhu_count = cur.fetchone()[0]
        print(f"7. JHU Computer Science Masters Entries: {jhu_count}")

        cur.close()
        conn.close()
        print("-" * 50)
        print("Analysis Complete.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_analysis()