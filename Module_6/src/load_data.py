# pylint: disable=duplicate-code
"""
Module to parse scraped applicant JSON data, clean it, and load it into PostgreSQL.
"""

import json
import os
import re

import psycopg
from psycopg import sql

DB_CONFIG = {
    "host": "localhost",
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "port": "5432"
}

def clean_for_sql(value):
    """Clean string values to prepare them for database insertion."""
    if value is None:
        return None

    val_str = str(value).replace('\x00', '').strip()

    if val_str.lower() in ["", "n/a", "nan", "null"]:
        return None

    return val_str

def clean_numeric(value):
    """Extract and format numeric values from strings."""
    cleaned = clean_for_sql(value)
    if cleaned is None:
        return None

    numeric_part = re.search(r"[-+]?\d*\.\d+|\d+", cleaned)
    if numeric_part:
        return float(numeric_part.group())

    return None

# pylint: disable=too-many-locals, too-many-statements, too-many-branches, no-member
def load_data_from_json():
    """Read data from the JSON file, clean it, and execute database inserts."""
    json_filename = 'llm_extend_applicant_data.json'

    if not os.path.exists(json_filename):
        print(f"Error: {json_filename} not found.")
        return

    conn = None
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Module 5: Secure composition
        cur.execute(sql.SQL("TRUNCATE TABLE applicants RESTART IDENTITY;"))
        conn.commit()

        # Broken into multiple lines to pass the 100 character limit
        insert_query = sql.SQL(
            "INSERT INTO applicants (program, comments, date_added, url, status, "
            "term, us_or_international, gpa, gre, gre_v, gre_aw, degree, "
            "llm_generated_program, llm_generated_university) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        )

        with open(json_filename, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                try:
                    entry = json.loads(line.strip())

                    # Broken into a vertical tuple to pass the 100 character limit
                    record = (
                        clean_for_sql(entry.get('program')),
                        clean_for_sql(entry.get('comments')),
                        clean_for_sql(entry.get('date_added')),
                        clean_for_sql(entry.get('url')),
                        clean_for_sql(entry.get('applicant_status')),
                        clean_for_sql(entry.get('semester_year_start')),
                        clean_for_sql(entry.get('citizenship')),
                        clean_numeric(entry.get('gpa')),
                        clean_numeric(entry.get('gre')),
                        clean_numeric(entry.get('gre_v')),
                        clean_numeric(entry.get('gre_aw')),
                        clean_for_sql(entry.get('masters_or_phd')),
                        clean_for_sql(entry.get('llm-generated-program')),
                        clean_for_sql(entry.get('llm-generated-university'))
                    )

                    cur.execute(insert_query, record)
                except (json.JSONDecodeError, psycopg.DataError):
                    continue

        conn.commit()

        # Module 5 requirement: Enforce LIMIT on queries
        cur.execute(sql.SQL("SELECT * FROM applicants WHERE gre IS NOT NULL LIMIT 3;"))
        samples = cur.fetchall()

        if not samples:
            print("WARNING: No students found!")
        else:
            for student in samples:
                print(f"Record: {student}")

        cur.close()

    except psycopg.Error as error:
        # Avoid catching broad generic Exception
        print(f"Database error occurred: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_data_from_json()
