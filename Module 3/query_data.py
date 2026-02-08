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

        # Q1: Fall 2026 entries
        cur.execute("SELECT COUNT(*) FROM applicants WHERE term = 'Fall 2026';")
        q1 = cur.fetchone()[0]
        print(f"1. Total Fall 2026 Entries: {q1}")

        # Q2: % International (Not American and Not Other)
        cur.execute("""
            SELECT ROUND(
                (COUNT(*) FILTER (WHERE us_or_international = 'International')::numeric / 
                NULLIF(COUNT(*), 0)::numeric) * 100, 2
            ) FROM applicants;
        """)
        q2 = cur.fetchone()[0]
        print(f"2. Percentage of International Students: {fmt_pct(q2)}")

        # Q3: Global Averages (With Range Filters to ignore typos/old scores)
        cur.execute("""
            SELECT 
                AVG(gpa) FILTER (WHERE gpa <= 4.0), 
                AVG(gre) FILTER (WHERE gre >= 130 AND gre <= 170), 
                AVG(gre_v) FILTER (WHERE gre_v >= 130 AND gre_v <= 170), 
                AVG(gre_aw) FILTER (WHERE gre_aw >= 0 AND gre_aw <= 6)
            FROM applicants;
        """)
        avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()
        print(f"3. Global Averages (Overall):")
        print(f"   - GPA: {fmt_avg(avg_gpa)}")
        print(f"   - GRE Quant: {fmt_avg(avg_gre)}")
        print(f"   - GRE Verbal: {fmt_avg(avg_gre_v)}")
        print(f"   - GRE Writing: {fmt_avg(avg_gre_aw)}")

        # Q4: Avg GPA American Fall 2026 (With Sanity Filter)
        cur.execute("""
            SELECT AVG(gpa) FROM applicants 
            WHERE us_or_international = 'American' 
            AND term = 'Fall 2026'
            AND gpa <= 4.0;
        """)
        q4 = cur.fetchone()[0]
        print(f"4. Avg GPA (American, Fall 2026): {fmt_avg(q4)}")

        # Q5: % Acceptances for Fall 2026
        cur.execute("""
            SELECT ROUND(
                (COUNT(*) FILTER (WHERE status = 'Accepted' AND term = 'Fall 2026')::numeric / 
                NULLIF(COUNT(*) FILTER (WHERE term = 'Fall 2026'), 0)::numeric) * 100, 2
            ) FROM applicants;
        """)
        q5 = cur.fetchone()[0]
        print(f"5. Fall 2026 Acceptance Rate: {fmt_pct(q5)}")

        # Q6: Avg GPA Accepted Fall 2026 (With Sanity Filter)
        cur.execute("""
            SELECT AVG(gpa) FROM applicants 
            WHERE term = 'Fall 2026' 
            AND status = 'Accepted'
            AND gpa <= 4.0;
        """)
        q6 = cur.fetchone()[0]
        print(f"6. Avg GPA (Accepted, Fall 2026): {fmt_avg(q6)}")

        # Q7: JHU CS Masters search
        cur.execute("""
            SELECT COUNT(*) FROM applicants 
            WHERE llm_generated_university ILIKE '%Johns Hopkins%' 
            AND degree = 'Masters' AND llm_generated_program ILIKE '%Computer Science%';
        """)
        q7 = cur.fetchone()[0]
        print(f"7. JHU Computer Science Masters Entries: {q7}")

        # Q8: Elite PhD CS Acceptances (Original Fields - Expanded)
        cur.execute("""
            SELECT COUNT(*) FROM applicants 
            WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD'
            AND program ILIKE '%Computer Science%'
            AND (
                  program ILIKE '%Georgetown%' OR 
                  program ILIKE '%MIT%' OR 
                  program ILIKE '%Massachusetts Institute of Technology%' OR
                  program ILIKE '%Stanford%' OR 
                  program ILIKE '%Carnegie%' OR 
                  program ILIKE '%CMU%'
              );
        """)
        q8 = cur.fetchone()[0]
        print(f"8. Elite PhD CS Acceptances (Original Fields): {q8}")

        # Q9: Elite PhD CS Acceptances (LLM Fields)
        # Ensure these names match EXACTLY what is in your database (check via debug script if 0)
        elite_schools = "('Georgetown University', 'MIT', 'Stanford University', 'Carnegie Mellon University')"
        cur.execute(f"""
            SELECT COUNT(*) FROM applicants 
            WHERE status = 'Accepted' AND term = 'Fall 2026' AND degree = 'PhD' 
            AND llm_generated_program ILIKE '%Computer Science%' 
            AND llm_generated_university IN {elite_schools};
        """)
        q9 = cur.fetchone()[0]
        print(f"9. Elite PhD CS Acceptances (LLM Fields): {q9}")
        
        diff = q9 - q8
        print(f"   -> Analysis: LLM fields found {abs(diff)} {'more' if diff >= 0 else 'fewer'} entries.")

        # --- ADDITIONAL RESEARCH QUESTIONS ---
        print("\n--- ADDITIONAL RESEARCH QUESTIONS ---")

        # Question 10: Top 5 most applied-to universities 
        print("10. Top 5 Most Applied-To Universities:")
        cur.execute("""
            SELECT llm_generated_university, COUNT(*) as apps 
            FROM applicants 
            WHERE llm_generated_university IS NOT NULL 
            GROUP BY llm_generated_university 
            ORDER BY apps DESC LIMIT 5;
        """)
        for rank, row in enumerate(cur.fetchall(), 1):
            print(f"    {rank}. {row[0]}: {row[1]} applications")

        # Question 11: Top 5 Lowest Application Counts (Cleaned)
        print("\n11. Top 5 Universities with the Lowest Application Counts:")
        
        # We use single quotes for the text '[] '' ' 
        # (Note the doubled '' which tells SQL "this is one single quote character")
        cur.execute("""
            SELECT 
                TRIM(BOTH '[] '' ' FROM llm_generated_university) AS cleaned_uni, 
                COUNT(*) as apps 
            FROM applicants 
            WHERE llm_generated_university IS NOT NULL 
              AND llm_generated_university != ''
            GROUP BY cleaned_uni 
            ORDER BY apps ASC, cleaned_uni ASC
            LIMIT 5;
        """)
        for rank, row in enumerate(cur.fetchall(), 1):
            # Safe Python cleaning just in case the SQL trim missed internal commas
            display_name = row[0].split(',')[0].strip("[]'\" ")
            print(f"    {rank}. {display_name}: {row[1]} application(s)")

        print("="*60)
        print("Analysis Complete.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_analysis()