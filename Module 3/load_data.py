import pandas as pd
import psycopg2
from psycopg2 import extras
import sys

# 1. DATABASE CONNECTION SETTINGS
# Replace these with your actual Postgres details
DB_CONFIG = {
    "host": "localhost",      # Or your Replit host URL
    "database": "postgres",   # Your database name
    "user": "postgres",       # Your username
    "password": "your_password", 
    "port": "5432"
}

def load_data():
    conn = None
    try:
        # 2. CONNECT TO POSTGRESQL
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 3. CREATE THE TABLE (If it doesn't exist)
        # This ensures your p_id is an auto-incrementing integer
        create_table_query = """
        CREATE TABLE IF NOT EXISTS applicants (
            p_id SERIAL PRIMARY KEY,
            program TEXT,
            comments TEXT,
            date_added DATE,
            url TEXT,
            status TEXT,
            term TEXT,
            us_or_international TEXT,
            gpa FLOAT,
            gre_q FLOAT,
            gre_v FLOAT,
            gre_aw FLOAT,
            degree TEXT,
            llm_generated_program TEXT,
            llm_generated_university TEXT
        );
        """
        cur.execute(create_table_query)
        print("Table 'applicants' is ready.")

        # 4. READ AND PREPARE DATA
        # Replace 'cleaned_data.csv' with your actual filename from Module 2
        df = pd.read_csv('cleaned_data.csv')

        # Critical Step: Convert empty values (NaN) to None so SQL understands them as NULL
        df = df.where(pd.notnull(df), None)

        # 5. DEFINE THE INSERT QUERY
        # We list the columns exactly as they appear in the table
        columns = [
            "program", "comments", "date_added", "url", "status", "term",
            "us_or_international", "gpa", "gre_q", "gre_v", "gre_aw",
            "degree", "llm_generated_program", "llm_generated_university"
        ]
        
        # This creates a string: INSERT INTO applicants (col1, col2...) VALUES %s
        query = f"INSERT INTO applicants ({', '.join(columns)}) VALUES %s"

        # 6. EXECUTE THE INSERT
        # We convert the dataframe rows into a list of tuples
        values = [tuple(row) for row in df[columns].values]
        
        extras.execute_values(cur, query, values)
        
        # 7. COMMIT AND CLOSE
        conn.commit()
        print(f"Successfully loaded {len(values)} rows into the database.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    load_data()