import psycopg2
import json
import os

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "database": "postgres", 
    "user": "postgres",
    "password": "postgres", 
    "port": "5432"
}

def clean_for_sql(value):
    """
    1. Removes NUL (0x00) characters that crash PostgreSQL.
    2. Converts Grad Cafe strings like 'N/A' or empty text to None (SQL NULL).
    """
    if value is None:
        return None
    
    # Convert to string and strip hidden NUL characters
    val_str = str(value).replace('\x00', '').strip()
    
    # Check for empty or N/A values for numeric/text cleaning
    if val_str.lower() in ["", "n/a", "nan", "null"]:
        return None
        
    return val_str

def clean_numeric(value):
    """Specific helper for GPA/GRE numbers."""
    cleaned = clean_for_sql(value)
    if cleaned is None:
        return None
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def load_data_from_json():
    json_filename = 'llm_extend_applicant_data.json'
    
    if not os.path.exists(json_filename):
        print(f"Error: {json_filename} not found.")
        return

    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Successfully connected to the database.")

        insert_query = """
            INSERT INTO applicants (
                program, comments, date_added, url, status, term, 
                us_or_international, gpa, gre, gre_v, gre_aw, 
                degree, llm_generated_program, llm_generated_university
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        print("Deep cleaning data and loading...")
        count = 0

        with open(json_filename, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue 
                
                try:
                    entry = json.loads(line)
                    
                    # We wrap EVERY entry.get() with clean_for_sql or clean_numeric
                    record = (
                        clean_for_sql(entry.get('program')),
                        clean_for_sql(entry.get('comments')),
                        clean_for_sql(entry.get('date_added')),
                        clean_for_sql(entry.get('url')),
                        clean_for_sql(entry.get('status')),
                        clean_for_sql(entry.get('term')),
                        clean_for_sql(entry.get('us_or_international')),
                        clean_numeric(entry.get('gpa')),
                        clean_numeric(entry.get('gre')),
                        clean_numeric(entry.get('gre_v')),
                        clean_numeric(entry.get('gre_aw')),
                        clean_for_sql(entry.get('degree')),
                        clean_for_sql(entry.get('llm_generated_program')),
                        clean_for_sql(entry.get('llm_generated_university'))
                    )
                    cur.execute(insert_query, record)
                    count += 1
                except (json.JSONDecodeError, psycopg2.DataError) as e:
                    print(f"Skipping row due to error: {e}")

        conn.commit()
        print(f"Success! {count} records loaded.")
        cur.close()

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if conn:
            conn.rollback() 
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_data_from_json()