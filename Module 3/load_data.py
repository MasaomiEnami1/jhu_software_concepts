import psycopg2

def connect_to_db():
    try:
        # These credentials must match what you set up in Stage 1
        connection = psycopg2.connect(
            host="localhost",          # Your computer
            database="postgres",   # Database name
            user="postgres",           # Default user
            password="postgres",  # The password you created during install
            port="5432"                # Default Postgres port
        )
        
        # The cursor is what actually executes SQL commands
        cursor = connection.cursor()
        
        print("Successfully connected to the database!")
        
        # Always close the connection when done
        cursor.close()
        connection.close()
        
    except Exception as error:
        print(f"Error connecting to database: {error}")

if __name__ == "__main__":
    connect_to_db()