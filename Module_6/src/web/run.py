from flask import Flask, jsonify
from publisher import publish_task
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Microservice Web App is Running! Send POST requests to /scrape or /analytics."

# --- ROUTE 1: Trigger the Scraper ---
@app.route('/scrape', methods=['POST'])
def trigger_scrape():
    try:
        # 1. Send the task to RabbitMQ
        # We send an empty payload {} because the worker knows what to scrape
        publish_task(kind="scrape_new_data", payload={})
        
        # 2. Return success immediately (HTTP 202 Accepted)
        return jsonify({
            "status": "queued", 
            "task": "scrape_new_data",
            "message": "Scraping job started in background."
        }), 202

    except Exception as e:
        # Log the error (in a real app) and return 503 Service Unavailable
        print(f"ERROR: {e}")
        return jsonify({"error": "Failed to publish task"}), 503


# --- ROUTE 2: Trigger Analytics (Optional/Future) ---
@app.route('/analytics', methods=['POST'])
def trigger_analytics():
    try:
        publish_task(kind="recompute_analytics", payload={})
        return jsonify({
            "status": "queued", 
            "task": "recompute_analytics"
        }), 202
    except Exception as e:
        return jsonify({"error": "Failed to publish task"}), 503

if __name__ == '__main__':
    # We turn off debug mode for safety in this setup
    app.run(host='0.0.0.0', port=8080, debug=False)