1) README

Name: Masaomi Enami (JHED ID: A1E92A)

Module Info: Module 2 — Web Scraping and Data Standardization

Assignment: Grad Cafe Data Pipeline & LLM Normalization

Due Date: February 1, 2026
Overview

This project is a unified data pipeline designed to extract, clean, and standardize graduate school admission results from The Grad Cafe. It utilizes BeautifulSoup for structural web scraping, Regex for data extraction, and a Self-Hosted TinyLlama 1.1B LLM for semantic normalization of messy program and university labels.
Build & Run Pipeline

To reconstruct the dataset from scratch, follow these steps:
1. Scraping

Run the scraper to collect raw HTML data from the survey pages.
Bash

python scrape.py

Outputs: raw_data.json
2. Cleaning

Run the cleaner to parse raw strings into structured fields (GPA, GRE, Degree, etc.).
Bash

python clean.py

Outputs: applicant_data.json
3. LLM Standardization

Navigate to the sub-package and run the local model to normalize names.
Bash

cd llm_hosting
pip install -r requirements.txt
python app.py --file "../raw_data.json" --stdout > ../llm_extend_applicant_data.json

Implementation Approach
Data Extraction (scrape.py)

The primary challenge was the non-standard table structure where one entry spans multiple <tr> rows.

    Data Structure: I used a list of dictionaries to store "buckets" of raw text.

    Sibling-Row Algorithm: I implemented a "Look-Ahead" logic. The script identifies a header row via the institution class. It then uses .find_next_sibling('tr') to capture the following two rows only if they lack the institution class. This prevents "off-by-one" errors where a student without a comment would accidentally inherit the next student's university name.

    Compliance: I enforced a 1.2s crawl-delay and custom User-Agent headers to satisfy robots.txt requirements.

Logic & Regular Expressions (clean.py)

Once raw data was collected, I used the re (Regular Expression) module to solve the "messy labels" problem:

    Degree Separation: I used conditional keyword matching to split "Program Name" (e.g., Finance) from "Degree" (e.g., PhD).

    Metric Extraction: I applied specific regex patterns for GPA (\d\.\d{1,2}) and GRE scores (anchored to 'V', 'Q', and 'AW' characters).

    Descriptive Defaults: To ensure the data was "analysis-ready," I mapped all missing values to explicit strings (e.g., "No GPA") instead of leaving them as nulls.

LLM Normalization (llm_hosting/)

To handle variations like "JHU" vs "Johns Hopkins," I integrated a local TinyLlama-1.1B-Chat model.

    Prompting: I used a "Few-Shot" prompting strategy within app.py, providing the model with examples of messy-to-standard transitions.

    Canon Mapping: I extended the canon_universities list to act as a pragmatic safeguard, forcing the LLM output to align with a standardized master list.

Known Bugs

    Character Encoding: On some Windows systems, rare emojis in Grad Cafe comments may cause a UnicodeEncodeError. I have mitigated this using encoding='utf-8' in all file operations, but some symbols may still render as "".

    International GPA Scales: The current Regex is optimized for 4.0 scales. Entries using 10.0 or 100% scales may be incorrectly labeled as "No GPA." Fix strategy: A future update would involve a secondary Regex pass to identify and normalize percentage-based strings.

    Pagination Limits: If the script is interrupted at exactly 30,000 rows, the final JSON closing bracket may fail to write. Fix strategy: Implement a try/finally block to ensure the file saves correctly upon interruption.

Contributing

This project is part of the JHU Software Concepts curriculum. For development tips or issues regarding the LLM sub-package, please refer to the llm_hosting/README.md.