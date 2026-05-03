import pika
import time
import os
import sys

def main():
    # 1. Get connection details from environment variables
    user = os.getenv('DATABASE_USER', 'user')
    password = os.getenv('DATABASE_PASSWORD', 'password')
    host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    
    # 2. Connection Parameters
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(host=host, credentials=credentials)

    # 3. THE SUBSTANTIVE FIX: Retry Connection Loop
    connection = None
    while connection is None:
        try:
            print(f"[*] Attempting to connect to RabbitMQ at {host}...")
            connection = pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            print("[!] RabbitMQ is not ready yet. Retrying in 5 seconds...")
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)
    
    print('[*] Worker connected successfully. Waiting for messages...')

    def callback(ch, method, properties, body):
        print(f" [x] Received task: {body.decode()}")
        # Your processing logic here
        time.sleep(1) 
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)