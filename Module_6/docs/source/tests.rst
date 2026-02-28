Testing Guide
=============

Test Markers
------------
We use markers to categorize our suite:
* ``web``: UI and route tests.
* ``buttons``: Functional tests for buttons and status codes (409).
* ``db``: Database integrity and idempotency.

UI Selectors
------------
Tests target the following stable selectors:
* ``data-testid="pull-data-btn"``
* ``data-testid="update-analysis-btn"``

Fixtures & Doubles
------------------
* ``client``: Flask test client for HTTP simulation.
* **Mock Scraper**: Injected to prevent live network calls during testing.