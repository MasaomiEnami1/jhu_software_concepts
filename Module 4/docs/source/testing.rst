Testing Guide
=============

This guide explains how to run the test suite and the strategy for ensuring 100% coverage.

Running Tests
-------------
To run the entire suite using the required markers, use:

.. code-block:: bash

   pytest -m "web or buttons or analysis or db or integration"

Test Markers
------------
* **web**: Validates Flask route status codes and HTML structure.
* **buttons**: Tests button endpoints and "busy gating" (409 logic).
* **analysis**: Verifies rounding and label formatting.
* **db**: Tests PostgreSQL schema, inserts, and idempotency.
* **integration**: End-to-end flows from data pull to page render.

UI Selectors
------------
Tests rely on the following stable selectors for reliability:
* ``data-testid="pull-data-btn"``
* ``data-testid="update-analysis-btn"``

Test Doubles & Fixtures
-----------------------
* **client**: A Flask test client fixture for simulating HTTP requests.
* **Mock Scraper**: Used to simulate Grad Cafe responses without hitting the live internet.