import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "postgres", 
    "user": "postgres",
    "password": "postgres", 
    "port": "5432"
}

def verify():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Get the total count
        cur.execute("SELECT COUNT(*) FROM applicants;")
        total = cur.fetchone()[0]
        print(f"Total rows in database: {total}")
        
        # 2. Fetch the first 3 rows using the CORRECT column names
        # We use llm_generated_university because that is what is in your CREATE TABLE statement
        cur.execute("SELECT program, gpa, llm_generated_university FROM applicants LIMIT 3;")
        rows = cur.fetchall()
        
        print("\nFirst 3 records sample:")
        for row in rows:
            print(f"Program: {row[0]} | GPA: {row[1]} | University: {row[2]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error checking table: {e}")

if __name__ == "__main__":
    verify()