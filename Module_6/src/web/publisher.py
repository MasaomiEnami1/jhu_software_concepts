import os
import json
import pika
import datetime

# Configuration Constants
EXCHANGE = 'tasks'
QUEUE = 'tasks_q'
ROUTING_KEY = 'tasks'

def _open_channel():
    """
    Establishes a connection to RabbitMQ and declares the necessary
    Exchange and Queue topology.
    """
    # 1. Read the URL from the environment (defined in docker-compose.yml)
    url = os.environ.get("RABBITMQ_URL")
    if not url:
        raise ValueError("RABBITMQ_URL environment variable is not set")

    # 2. Create the connection
    params = pika.URLParameters(url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    # 3. Declare Topology (Idempotent)
    # Durable Direct Exchange: Survives restarts
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    
    # Durable Queue: Holds messages even if RabbitMQ restarts
    ch.queue_declare(queue=QUEUE, durable=True)
    
    # Binding: Connects the Exchange to the Queue via the Routing Key
    ch.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)

    # Optional: Enable confirmations to ensure RabbitMQ accepts the message
    ch.confirm_delivery()

    return conn, ch

def publish_task(kind: str, payload: dict | None = None, headers: dict | None = None) -> None:
    """
    Publishes a structured task message to the RabbitMQ exchange.
    """
    conn = None
    try:
        # 1. Build the payload
        # We use a compact JSON separator (",", ":") to save bytes
        message_body = json.dumps(
            {
                "kind": kind,
                "ts": datetime.datetime.utcnow().isoformat(),
                "payload": payload or {}
            },
            separators=(",", ":")
        ).encode("utf-8")

        # 2. Open Connection
        conn, ch = _open_channel()

        # 3. Publish
        ch.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,       # Persistent message (saved to disk)
                content_type='application/json',
                headers=headers or {}
            ),
            mandatory=True # Raise error if message can't be routed
        )
        
        print(f" [x] Published '{kind}' task")

    except Exception as e:
        print(f"ERROR: Failed to publish task: {e}")
        # Re-raise the exception so the Flask app knows to return a 503 error
        raise e
        
    finally:
        # 4. Clean up connection
        if conn and not conn.is_closed:
            conn.close()