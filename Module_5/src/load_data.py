import psycopg2
import json
import os
import re

DB_CONFIG = {"host": "localhost", "database": "postgres", "user": "postgres", "password": "postgres", "port": "5432"}

def clean_for_sql(value):
    if value is None: return None
    val_str = str(value).replace('\x00', '').strip()
    if val_str.lower() in ["", "n/a", "nan", "null"]: return None
    return val_str

def clean_numeric(value):
    cleaned = clean_for_sql(value)
    if cleaned is None: return None
    numeric_part = re.search(r"[-+]?\d*\.\d+|\d+", cleaned)
    return float(numeric_part.group()) if numeric_part else None

def load_data_from_json():
    json_filename = 'llm_extend_applicant_data.json'
    if not os.path.exists(json_filename):
        print(f"Error: {json_filename} not found.")
        return
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE applicants RESTART IDENTITY;")
        conn.commit()
        insert_query = "INSERT INTO applicants (program, comments, date_added, url, status, term, us_or_international, gpa, gre, gre_v, gre_aw, degree, llm_generated_program, llm_generated_university) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        with open(json_filename, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                try:
                    entry = json.loads(line.strip())
                    record = (clean_for_sql(entry.get('program')), clean_for_sql(entry.get('comments')), clean_for_sql(entry.get('date_added')), clean_for_sql(entry.get('url')), clean_for_sql(entry.get('applicant_status')), clean_for_sql(entry.get('semester_year_start')), clean_for_sql(entry.get('citizenship')), clean_numeric(entry.get('gpa')), clean_numeric(entry.get('gre')), clean_numeric(entry.get('gre_v')), clean_numeric(entry.get('gre_aw')), clean_for_sql(entry.get('masters_or_phd')), clean_for_sql(entry.get('llm-generated-program')), clean_for_sql(entry.get('llm-generated-university')))
                    cur.execute(insert_query, record)
                except (json.JSONDecodeError, psycopg2.DataError): continue
        conn.commit()
        cur.execute("SELECT * FROM applicants WHERE gre IS NOT NULL LIMIT 3;")
        samples = cur.fetchall()
        if not samples:
            print("WARNING: No students found!")
        else:
            for student in samples:
                print(f"Record: {student}")
        cur.close()
    except Exception as e:
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    load_data_from_json()