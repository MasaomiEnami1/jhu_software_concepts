Architecture
============

The system is divided into three core layers:

1. **Web Layer (Flask)**
   - Responsible for rendering the analysis dashboard.
   - Manages "Busy Gating" logic to prevent concurrent scrapes/updates.

2. **ETL Layer (Scrapy & Load)**
   - **Scraper**: Extracts raw data from Grad Cafe.
   - **Loader**: Cleans and transforms data before inserting it into PostgreSQL.

3. **Data Layer (PostgreSQL)**
   - Stores normalized grad school application records.
   - Enforces uniqueness constraints to prevent duplicate data.