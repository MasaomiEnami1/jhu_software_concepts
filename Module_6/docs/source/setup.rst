Overview & Setup
================

This application provides analytics for Grad Cafe data.

Required Environment Variables
------------------------------
* ``DATABASE_URL``: The connection string for your PostgreSQL database.
  Example: ``postgresql://postgres:password@localhost:5432/postgres``

Running the Application
-----------------------
1. Install dependencies: ``pip install -r requirements.txt``
2. Start the Flask server: ``python src/app.py``
3. Access the dashboard at ``http://127.0.0.1:5000/analysis``

Running Tests
-------------
Execute the full suite with:
``pytest -m "web or buttons or analysis or db or integration"``