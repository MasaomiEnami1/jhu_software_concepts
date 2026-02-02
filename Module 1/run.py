from app import app # This refers to the 'app' variable inside the 'app' folder

if __name__ == "__main__":
    # Using Port 8080
    app.run(host='0.0.0.0', port=8080, debug=True)
    