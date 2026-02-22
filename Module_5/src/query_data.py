# pylint: disable=duplicate-code, use-dict-literal
"""
Module for executing data analysis queries against the PostgreSQL database.
Outputs formatting reports on applicant statistics.
"""

import os
import psycopg
from psycopg import sql
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
DB_CONFIG = dict(
    host=os.getenv("DB_HOST", "localhost"),
    dbname=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USER", "gradcafe_web"),
    password=os.getenv("DB_PASSWORD", "jhu_secure_pass_2026"),
    port=os.getenv("DB_PORT", "5432")
)

def get_safe_limit(requested_limit):
    """Clamp the limit to strictly between 1 and 100."""
    try:
        return max(1, min(int(requested_limit), 100))
    except (ValueError, TypeError):
        return 10

def fmt_avg(val):
    """Format an average value to 2 decimal places, handling None."""
    if val is not None:
        return f"{val:.2f}"
    return "N/A"

def fmt_pct(val):
    """Format a percentage value to 2 decimal places, handling None."""
    if val is not None:
        return f"{val:.2f}%"
    return "N/A"

# pylint: disable=too-many-locals, too-many-statements, no-member
def run_analysis():
    """Connect to the database, run analysis queries, and print the results."""
    conn = None
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        safe_single = get_safe_limit(1)

        print("\n" + "="*60)
        print("GRAD CAFE FINAL DATA ANALYSIS REPORT")
        print("="*60)

        # Q1
        q1 = sql.SQL("SELECT COUNT(*) FROM {table} WHERE term = %s LIMIT {limit};").format(
            table=sql.Identifier("applicants"), limit=sql.Literal(safe_single)
        )
        cur.execute(q1, ("Fall 2026",))
        print(f"1. Total Fall 2026 Entries: {cur.fetchone()[0]}")

        # Q2
        q2 = sql.SQL(
            "SELECT ROUND((COUNT(*) FILTER (WHERE us_or_international = %s)::numeric / "
            "NULLIF(COUNT(*), 0)::numeric) * 100, 2) FROM {table} LIMIT {limit};"
        ).format(table=sql.Identifier("applicants"), limit=sql.Literal(safe_single))
        cur.execute(q2, ("International",))
        print(f"2. Percentage of International Students: {fmt_pct(cur.fetchone()[0])}")

        # Q3
        q3 = sql.SQL(
            "SELECT AVG(gpa) FILTER (WHERE gpa <= %s), "
            "AVG(gre) FILTER (WHERE gre >= %s AND gre <= %s), "
            "AVG(gre_v) FILTER (WHERE gre_v >= %s AND gre_v <= %s), "
            "AVG(gre_aw) FILTER (WHERE gre_aw >= %s AND gre_aw <= %s) "
            "FROM {table} LIMIT {limit};"
        ).format(table=sql.Identifier("applicants"), limit=sql.Literal(safe_single))
        cur.execute(q3, (4.0, 130, 170, 130, 170, 0, 6))
        avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = cur.fetchone()
        
        print("3. Global Averages (Overall):")
        print(f"   - GPA: {fmt_avg(avg_gpa)}\n   - GRE Quant: {fmt_avg(avg_gre)}")
        print(f"   - GRE Verbal: {fmt_avg(avg_gre_v)}\n   - GRE Writing: {fmt_avg(avg_gre_aw)}")

        # Q4
        q4 = sql.SQL(
            "SELECT AVG(gpa) FROM {table} WHERE us_or_international = %s "
            "AND term = %s AND gpa <= %s LIMIT {limit};"
        ).format(table=sql.Identifier("applicants"), limit=sql.Literal(safe_single))
        cur.execute(q4, ("American", "Fall 2026", 4.0))
        print(f"4. Avg GPA (American, Fall 2026): {fmt_avg(cur.fetchone()[0])}")

        # Q5
        q5 = sql.SQL(
            "SELECT ROUND((COUNT(*) FILTER (WHERE status = %s AND term = %s)::numeric / "
            "NULLIF(COUNT(*) FILTER (WHERE term = %s), 0)::numeric) * 100, 2) "
            "FROM {table} LIMIT {limit};"
        ).format(table=sql.Identifier("applicants"), limit=sql.Literal(safe_single))
        cur.execute(q5, ("Accepted", "Fall 2026", "Fall 2026"))
        print(f"5. Fall 2026 Acceptance Rate: {fmt_pct(cur.fetchone()[0])}")

        # Q6
        q6 = sql.SQL(
            "SELECT AVG(gpa) FROM {table} WHERE term = %s AND status = %s AND gpa <= %s LIMIT {limit};"
        ).format(table=sql.Identifier("applicants"), limit=sql.Literal(safe_single))
        cur.execute(q6, ("Fall 2026", "Accepted", 4.0))
        print(f"6. Avg GPA (Accepted, Fall 2026): {fmt_avg(cur.fetchone()[0])}")

        # Q7
        q7 = sql.SQL(
            "SELECT COUNT(*) FROM {table} WHERE llm_generated_university ILIKE %s "
            "AND degree = %s AND llm_generated_program ILIKE %s LIMIT {limit};"
        ).format(table=sql.Identifier("applicants"), limit=sql.Literal(safe_single))
        cur.execute(q7, ("%Johns Hopkins%", "Masters", "%Computer Science%"))
        print(f"7. JHU Computer Science Masters Entries: {cur.fetchone()[0]}")

        # Q8
        q8 = sql.SQL(
            "SELECT COUNT(*) FROM {table} WHERE status = %s AND term = %s AND degree = %s "
            "AND program ILIKE %s AND (program ILIKE %s OR program ILIKE %s OR "
            "program ILIKE %s OR program ILIKE %s OR program ILIKE %s OR program ILIKE %s) LIMIT {limit};"
        ).format(table=sql.Identifier("applicants"), limit=sql.Literal(safe_single))
        cur.execute(q8, (
            "Accepted", "Fall 2026", "PhD", "%Computer Science%", 
            "%Georgetown%", "%MIT%", "%Massachusetts Institute of Technology%", 
            "%Stanford%", "%Carnegie%", "%CMU%"
        ))
        val_q8 = cur.fetchone()[0]
        print(f"8. Elite PhD CS Acceptances (Original Fields): {val_q8}")

        # Q9
        q9 = sql.SQL(
            "SELECT COUNT(*) FROM {table} WHERE status = %s AND term = %s AND degree = %s "
            "AND llm_generated_program ILIKE %s AND llm_generated_university IN (%s, %s, %s, %s) LIMIT {limit};"
        ).format(table=sql.Identifier("applicants"), limit=sql.Literal(safe_single))
        cur.execute(q9, (
            "Accepted", "Fall 2026", "PhD", "%Computer Science%",
            "Georgetown University", "MIT", "Stanford University", "Carnegie Mellon University"
        ))
        val_q9 = cur.fetchone()[0]
        print(f"9. Elite PhD CS Acceptances (LLM Fields): {val_q9}")

        diff = val_q9 - val_q8
        comparison_text = 'more' if diff >= 0 else 'fewer'
        print(f"   -> Analysis: LLM fields found {abs(diff)} {comparison_text} entries.")

        # --- ADDITIONAL RESEARCH QUESTIONS ---
        safe_list = get_safe_limit(5)
        print("\n--- ADDITIONAL RESEARCH QUESTIONS ---")

        # Q10
        print("10. Top 5 Most Applied-To Universities:")
        q10 = sql.SQL(
            "SELECT llm_generated_university, COUNT(*) as apps FROM {table} "
            "WHERE llm_generated_university IS NOT NULL "
            "GROUP BY llm_generated_university ORDER BY apps DESC LIMIT {limit};"
        ).format(table=sql.Identifier("applicants"), limit=sql.Literal(safe_list))
        cur.execute(q10)
        for rank, row in enumerate(cur.fetchall(), 1):
            print(f"    {rank}. {row[0]}: {row[1]} applications")

        # Q11
        print("\n11. Top 5 Universities with the Lowest Application Counts:")
        q11 = sql.SQL(
            "SELECT TRIM(BOTH '[] '' ' FROM llm_generated_university) AS cleaned_uni, "
            "COUNT(*) as apps FROM {table} "
            "WHERE llm_generated_university IS NOT NULL AND llm_generated_university != %s "
            "GROUP BY cleaned_uni ORDER BY apps ASC, cleaned_uni ASC LIMIT {limit};"
        ).format(table=sql.Identifier("applicants"), limit=sql.Literal(safe_list))
        cur.execute(q11, ("",))
        for rank, row in enumerate(cur.fetchall(), 1):
            display_name = row[0].split(',')[0].strip("[]'\" ")
            print(f"    {rank}. {display_name}: {row[1]} application(s)")

        print("="*60)
        print("Analysis Complete.")

        cur.close()

    except psycopg.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_analysis()
