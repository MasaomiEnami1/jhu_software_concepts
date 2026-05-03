# Modern Software Concepts in Python (EN.605.621)
**Student:** Masaomi Enami

## Repository Overview
This repository contains a comprehensive body of work developed over the course of the semester, focusing on modern Python development, data engineering, and machine learning deployment. The projects demonstrate proficiency in web scraping, SQL database management, Docker containerization, AWS cloud integration, and neural network implementation.

## Repository Organization
The repository is structured by modules, each representing a specific domain of software concepts:
- `/Module_1-13`: Individual project directories containing source code and module-specific documentation.
- `/static` & `/templates`: Frontend assets and HTML for the portfolio website.
- `app.py`: The Flask-based entry point for the project portfolio.
- `projects.json`: The data source for the portfolio project blocks.
- `requirements.txt`: Master dependency list for all modules.

    Module_2/ – Web Scraping & Data Cleaning

    Module_4/ – Software Testing (Pytest)

    Module_6/ – Microservices (Docker Compose, RabbitMQ, Postgres)

    Module_7/ – AWS Integration (S3, Boto3)

    Module_8/ – Data Engineering & Notebooks

    Module_9/ – Unsupervised Learning & Clustering

    Module_10/ – Interactive Dashboards (Plotly/Dash)

    Module_12/ – Neural Networks from Scratch

    Module_13/ – Modern LLM Deployment

    app.py – Flask Portfolio Website

    requirements.txt – Global Project Dependencies

Grader Corrections & Revision Log
Module 2 – Web Scraping Assignment

    Grader Comment: Submission does not clearly show that at least 30,000 entries were collected.

    Revision Made: Migrated the scraping infrastructure from urllib to Playwright browser automation. This bypassed Cloudflare blocks and allowed for the successful collection and verification of 30,000+ records.

    Improvement: Utilizing browser engines for scraping ensures data integrity when dealing with dynamic, protected web environments.

Module 4 – Software Testing Assignment

    Grader Comment: Running the marker-based command does not execute the entire test suite; some tests are deselected.

    Revision Made: Applied explicit @pytest.mark decorators to every test function and updated the pytest execution command to include all relevant categories.

    Improvement: Proper marking ensures that CI/CD pipelines or filtered test runs do not accidentally skip critical validation logic.

Module 6 – Microservices Assignment

    Grader Comment: Docker Compose fails to start because the Postgres initialization script creates a view before the table is created.

    Revision Made: Refactored init.sql to reorder DDL statements, ensuring all CREATE TABLE commands execute before dependent CREATE VIEW or JOIN operations.

    Improvement: Resolves race conditions during container orchestration, ensuring a stable and repeatable deployment.

Module 7 – AWS Integration Assignment

    Grader Comment: Boto3 implementation does not use IAM credentials correctly; output file misnamed.

    Revision Made: Updated the boto3 session management to utilize environment variables/profiles instead of hardcoded logic and renamed the output file to applicant_data_SM.json.

    Improvement: Adheres to AWS security best practices (Principle of Least Privilege) and project-specific naming conventions.

Module 8 – Data Engineering Assignment

    Grader Comment: Missing JSON export, raw status not split, GPA > 4.0 not dropped, and placeholders left in the report.

    Revision Made: Implemented df.to_json(), added string splitting logic for the status field, filtered GPA outliers, and replaced [Insert Value] placeholders with dynamic statistical calculations.

    Improvement: Ensures the notebook functions as a production-ready data pipeline rather than a static document.

Module 9 – Clustering & Visualization Assignment

    Grader Comment: Pylint score (6.14/10), missing legends on plots, and elbow test used improper step sizing.

    Revision Made: Refactored code to achieve a 10/10 Pylint score, added descriptive legends to all four visualizations, and updated the elbow test to iterate through every k value from 1 to 100.

    Improvement: High code quality scores and clear visualizations are essential for professional peer review and stakeholder communication.

Module 10 – Data Visualization Dashboard

    Grader Comment: Dashboard Pylint score (4.83/10) and broken image links in the README.

    Revision Made: Cleaned dashboard.py for PEP 8 compliance and corrected relative file paths for image assets in the documentation.

    Improvement: Professional dashboards must be supported by clean, maintainable code and accurate documentation.

Module 12 – Neural Networks Assignment

    Grader Comment: Missing row count prints and missing explanation for data leakage/train-only stats.

    Revision Made: Added explicit logging of dataframe shapes (before/after filtering) and included a technical write-up in the code comments explaining the necessity of using training-set medians to prevent leakage.

    Improvement: Increases transparency in data preprocessing and demonstrates theoretical competency in machine learning discipline.

4. Final Reflection on Semester Growth

The Most Challenging Module: Module 6 (Dockerized Microservices)

Module 6 presented the most significant architectural hurdle of the semester. While writing Python logic is straightforward, orchestrating a distributed system involving PostgreSQL, RabbitMQ, and multiple worker services required a fundamental shift in mindset. The most difficult aspect was debugging the race conditions during the initial container spin-up—specifically ensuring the database schema was fully instantiated before the web service attempted to create views. Resolving this required a deep dive into Docker’s execution order and shell-scripting workarounds, which solidified my understanding of system reliability.
The Module Reflecting My Strongest Work: Module 13 (Neural Network Deployment)

Module 13 is the pinnacle of my semester’s work because it synthesized every skill I acquired. It wasn't just about the machine learning math; it was about the logistical pipeline required to serve that math to a user. Integrating a custom-built neural network with a Flask-based inference API demonstrated my ability to build "end-to-end" systems. The implementation was clean, the testing was thorough, and it represented the exact type of computational engineering I intend to pursue in my future research.
Skills Most Improved: Software Assurance and Code Quality

Coming into this course, I viewed code primarily as a means to an end. My understanding of Software Assurance has improved most significantly. Adopting a strict 10/10 Pylint standard and achieving 100% test coverage via Pytest changed my perspective on "finished" code. I no longer just ask, "Does it run?"; I now ask, "Is it maintainable, is it documented, and is it resilient to edge cases?" The shift from writing scripts to building verified software packages is the most valuable skill I am taking away from this course.
Evolution of My Understanding of Python

At the beginning of the semester, I viewed Python as a high-level tool primarily for data analysis and quick calculations. My understanding has evolved to see Python as a robust, industrial-grade ecosystem capable of handling asynchronous concurrency, microservice orchestration, and complex cloud integrations. I now see Python not just as a language, but as a framework for solving large-scale logic puzzles and building the connective tissue for modern technical infrastructure.