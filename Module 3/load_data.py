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
    Cleans strings by removing hidden NUL characters (0x00) 
    and converting 'N/A' strings to Python None (SQL NULL).
    """
    if value is None:
        return None
    val_str = str(value).replace('\x00', '').strip()
    if val_str.lower() in ["", "n/a", "nan", "null"]:
        return None
    return val_str

def clean_numeric(value):
    """Safely converts GPA/GRE strings to float values."""
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
        # 1. Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Successfully connected to the database.")

        # 2. Clear the table before loading (Restarting IDs at 1)
        print("Emptying existing table data...")
        cur.execute("TRUNCATE TABLE applicants RESTART IDENTITY;")
        conn.commit()

        # 3. SQL Insert Statement
        insert_query = """
            INSERT INTO applicants (
                program, comments, date_added, url, status, term, 
                us_or_international, gpa, gre, gre_v, gre_aw, 
                degree, llm_generated_program, llm_generated_university
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        print("Mapping JSON keys and loading records...")
        count = 0

        # 4. Open and process the file line-by-line
        with open(json_filename, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue 
                
                try:
                    entry = json.loads(line)
                    
                    # Mapping logic based on your specific JSON structure:
                    record = (
                        clean_for_sql(entry.get('program')),
                        clean_for_sql(entry.get('comments')),
                        clean_for_sql(entry.get('date_added')),
                        clean_for_sql(entry.get('url')),
                        clean_for_sql(entry.get('applicant_status')),       # Mapped status
                        clean_for_sql(entry.get('semester_year_start')),   # Mapped term
                        clean_for_sql(entry.get('citizenship')),           # Mapped nationality
                        clean_numeric(entry.get('gpa')),
                        clean_numeric(entry.get('gre')),
                        clean_numeric(entry.get('gre_v')),
                        clean_numeric(entry.get('gre_aw')),
                        clean_for_sql(entry.get('masters_or_phd')),        # Mapped degree
                        clean_for_sql(entry.get('llm-generated-program')), # Mapped with hyphens
                        clean_for_sql(entry.get('llm-generated-university'))# Mapped with hyphens
                    )
                    cur.execute(insert_query, record)
                    count += 1
                except (json.JSONDecodeError, psycopg2.DataError):
                    # Silently skip malformed rows to keep the load moving
                    continue

        # 5. Commit all changes
        conn.commit()
        print(f"Success! {count} records loaded into the database.")

        # --- DATA VIEW SECTION ---
        # Fetching 3 sample students using SELECT * to display full records
        print("\n--- SAMPLE DATA PREVIEW (3 STUDENTS) ---")
        cur.execute("SELECT * FROM applicants LIMIT 3;")
        samples = cur.fetchall()
        
        # Get column names for labeling
        col_names = [desc[0] for desc in cur.description]
        
        for i, student in enumerate(samples, 1):
            print(f"\n[Student Record #{i}]")
            print("-" * 40)
            for col, val in zip(col_names, student):
                print(f"{col.ljust(25)}: {val}")
        print("-" * 40)

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