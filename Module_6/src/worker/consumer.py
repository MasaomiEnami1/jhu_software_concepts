import pika
import psycopg2
import json
import os
import time
import sys
import datetime

# --- CONFIGURATION ---
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2f")
# Note: In docker-compose, we use the service name 'db' as the host
DB_DSN = os.environ.get("DATABASE_URL", "postgresql://user:password@db:5432/applicant_db")
QUEUE_NAME = "tasks_q"
EXCHANGE_NAME = "tasks"
ROUTING_KEY = "tasks"

# --- DATABASE HELPERS ---
def get_db_connection():
    """Establishes a new database connection."""
    return psycopg2.connect(DB_DSN)

def get_watermark(cursor, source_name):
    """Fetches the last_seen value for a given source."""
    cursor.execute("SELECT last_seen FROM ingestion_watermarks WHERE source = %s", (source_name,))
    row = cursor.fetchone()
    return row[0] if row else None

def update_watermark(cursor, source_name, new_value):
    """Updates the watermark to the new max value."""
    cursor.execute("""
        INSERT INTO ingestion_watermarks (source, last_seen, updated_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (source) DO UPDATE 
        SET last_seen = EXCLUDED.last_seen, updated_at = NOW();
    """, (source_name, new_value))

# --- TASK HANDLERS ---

def handle_scrape_new_data(conn, payload):
    """
    1. Check watermark (what did we last see?)
    2. "Scrape" data newer than watermark (simulated here reading from JSON)
    3. Insert into DB (idempotent)
    4. Update watermark
    """
    print(" [>] Starting Scrape Job...")
    cur = conn.cursor()
    
    # 1. Get Watermark
    last_seen_id = get_watermark(cur, "applicant_scraper")
    print(f"     Current Watermark (Last ID): {last_seen_id}")

    # 2. Simulate Scraping (Replace this block with your REAL scraper logic)
    # For this assignment, we read the mounted JSON file
    data_path = os.getenv("DATA_FILE", "/data/applicant_data.json") # Default to mounted path
    
    if not os.path.exists(data_path):
        print(f"     [!] Warning: Data file {data_path} not found.")
        return

    with open(data_path, 'r') as f:
        all_applicants = json.load(f)

    # Filter: Only take applicants with ID > last_seen
    new_applicants = []
    current_max_id = int(last_seen_id) if last_seen_id else 0
    
    for app in all_applicants:
        # Assuming 'id' is our sort key. 
        # In a real scraper, this might be 'application_date'
        app_id = int(app.get('id', 0))
        if app_id > current_max_id:
            new_applicants.append(app)
            if app_id > current_max_id:
                current_max_id = app_id

    print(f"     Found {len(new_applicants)} new records to ingest.")

    # 3. Insert Data (Idempotent)
    insert_query = """
        INSERT INTO applicants (id, first_name, last_name, email, role, status, experience_years)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    
    for app in new_applicants:
        cur.execute(insert_query, (
            app.get('id'),
            app.get('first_name'),
            app.get('last_name'),
            app.get('email'),
            app.get('role', 'Unknown'),
            app.get('status', 'New'),
            app.get('experience_years', 0)
        ))
    
    # 4. Update Watermark
    if new_applicants:
        update_watermark(cur, "applicant_scraper", str(current_max_id))
        print(f"     Watermark updated to: {current_max_id}")
    
    cur.close()

def handle_recompute_analytics(conn, payload):
    """
    Recomputes analytics. In a real app, this might refresh a Materialized View.
    """
    print(" [>] Recomputing Analytics...")
    cur = conn.cursor()
    
    # Example: Refresh a materialized view (if you had one)
    # cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY applicant_stats;")
    
    # For this assignment, we'll just run a heavy query to log stats
    cur.execute("SELECT count(*), avg(experience_years) FROM applicants")
    stats = cur.fetchone()
    print(f"     Analytics Updated: Total Applicants={stats[0]}, Avg Exp={stats[1]:.2f}")
    
    cur.close()

# --- MAIN WORKER LOOP ---

def main():
    # 1. Connect to RabbitMQ
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # 2. Declare Durable Infrastructure (Idempotent)
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='direct', durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=ROUTING_KEY)

    # 3. Set QoS (Backpressure)
    channel.basic_qos(prefetch_count=1)

    print(f" [*] Waiting for tasks in '{QUEUE_NAME}'. To exit press CTRL+C")

    def callback(ch, method, properties, body):
        db_conn = None
        try:
            # A. Parse Task
            task = json.loads(body)
            kind = task.get("kind")
            payload = task.get("payload", {})
            print(f" [x] Received: {kind}")

            # B. Open DB Connection (Start Transaction)
            db_conn = get_db_connection()
            
            # C. Route to Handler
            if kind == "scrape_new_data":
                handle_scrape_new_data(db_conn, payload)
            elif kind == "recompute_analytics":
                handle_recompute_analytics(db_conn, payload)
            else:
                print(f" [!] Unknown task kind: {kind}")

            # D. Commit & Ack (Atomic Success)
            db_conn.commit()
            print(" [x] Transaction Committed. Task Done.")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f" [!] Error: {e}")
            if db_conn:
                db_conn.rollback() # Undo any partial SQL writes
                print(" [!] Transaction Rolled Back.")
            
            # Reject message, do NOT requeue (prevents infinite error loops)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        finally:
            if db_conn:
                db_conn.close()

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)