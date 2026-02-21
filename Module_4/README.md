Module 4: System Stability & Documentation Summary
1. Automated Testing & Quality Assurance

The primary goal of this module was to transition the Grad Cafe Analytics platform into a production-ready, stable state.
Coverage & Execution

    100.00% Coverage: Verified 100% statement coverage across all application modules (app.py, load_data.py, query_data.py, scrapy.py).

    Pytest Markers: Implemented a strict marking policy. The suite is executed via:
    pytest -m "web or buttons or analysis or db or integration"

    Zero-Hanging Execution: Integrated a pytest_sessionfinish hook utilizing os._exit() to ensure background scraper threads do not hang the terminal upon test completion.

Test Categories (SHALL Requirements)

    Web: Verified GET /analysis returns 200 and contains required UI components (Title, Buttons, "Answer:" labels).

    Buttons & Busy Gating: Implemented and verified HTTP 409 Conflict logic. The system now rejects concurrent requests when a scrape or update is already in progress.

    Analysis Formatting: Used regex assertions to ensure all percentages are rendered with exactly two decimal places (e.g., 39.28%).

    Database Integration: Verified that POST /pull-data results in non-null record insertion and respects Idempotency (unique constraints prevent duplicate rows).

2. CI/CD Pipeline (GitHub Actions)

A minimal, high-performance CI pipeline was established in .github/workflows/tests.yml.

    Service Containers: The pipeline initializes a real PostgreSQL 15 instance to ensure tests run against a production-grade database rather than a mock.

    Automated Validation: Every push to main triggers a build that installs dependencies, runs the test suite, and enforces the 100% coverage threshold.

    Evidence: Successful execution is documented in actions_success.png.

3. Sphinx Documentation

Comprehensive technical documentation has been built using Sphinx and the Read the Docs theme.
Documentation Sections

    Overview & Setup: Documentation on environment variables (DATABASE_URL), dependency installation, and application startup.

    Architecture: A detailed breakdown of the Web Layer (Flask), ETL Layer (Scrapy/Loader), and Data Layer (PostgreSQL).

    API Reference: Utilizes Sphinx autodoc to provide live documentation of all class methods, functions, and Flask routes.

    Testing Guide: Documentation of stable UI selectors (data-testid), test fixtures, and instructions for running marked tests.

4. Technical Guardrails Compliance

    SHALL NOT Hard-code: All paths in conf.py and .readthedocs.yaml are relative. Database credentials are managed via environment variables.

    SHALL NOT use sleep(): Busy-state testing is handled through state injection and mocking rather than arbitrary wait times.

    SHALL NOT use Live Internet: The test suite is fully deterministic and runs offline using mocked scraper responses.

Final Project Structure
Plaintext

module_4/
├── src/               # Flask App, Scrapy, Database logic
├── tests/             # Pytest suite (test_flask_page.py, test_buttons.py, etc.)
├── docs/              # Sphinx source files and configuration
├── .github/           # GitHub Actions workflows
├── pytest.ini         # Test configuration and markers
├── requirements.txt   # Project dependencies
└── .readthedocs.yaml  # Read the Docs build configuration