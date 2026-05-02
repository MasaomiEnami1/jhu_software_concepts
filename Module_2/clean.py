import json
import os
import re

def clean_data():
    # FIXED: Use dynamic pathing instead of hardcoded C:\Users\...
    base_path = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base_path, "raw_data.json")
    output_path = os.path.join(base_path, 'applicant_data.json')
    
    if not os.path.exists(raw_path):
        print(f"Error: {raw_path} not found. Run scrape.py first.")
        return

    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_list = json.load(f)

    cleaned = []
    for item in raw_list:
        # Standardize keys from scraper
        p_raw = item.get('p_raw', "")
        u_raw = item.get('u_raw', "")
        stats = item.get('stats_raw', "")
        status_raw = item.get('s_raw', "")

        # Logic for Degree
        degree = "PhD" if "PhD" in p_raw else "Masters" if any(x in p_raw for x in ["Masters", "MS", "MA"]) else "Other"
        p_name_clean = p_raw.replace("PhD", "").replace("Masters", "").replace("MS", "").replace("MA", "").strip()

        # Regex for Term (Matches "Fall 2024", etc.)
        term_match = re.search(r'(Fall|Spring|Summer|Winter)\s*(\d{4})', stats)
        
        entry = {
            "program": f"{p_name_clean}, {u_raw}" if p_name_clean and u_raw else "Unknown Program",
            "comments": item.get('comm_raw', "No comment"),
            "date_added": item.get('d_raw', ""),
            "url": item.get('url_raw', ""),
            "status": "Accepted" if "Accepted" in status_raw else "Rejected" if "Rejected" in status_raw else "Wait listed" if "Wait" in status_raw else "Other",
            "term": term_match.group(0) if term_match else "No term info",
            "US/International": "International" if "International" in stats else "American" if "American" in stats else "No origin info",
            "Degree": degree
        }
        cleaned.append(entry)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, indent=4)
    print(f"Success! Cleaned {len(cleaned)} rows. File saved to {output_path}")

if __name__ == "__main__":
    clean_data()