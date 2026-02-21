import json
import os
import re

def clean_data():
    path = r"C:\Users\Masaomi Enami\Python Project\jhu_software_concepts\Module 2"
    raw_path = os.path.join(path, "raw_data.json")
    
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_list = json.load(f)

    cleaned = []
    for item in raw_list:
        # Check if the keys exist, otherwise use the data we have
        p_raw = item.get('program', "")
        u_raw = item.get('university', "")
        stats = item.get('raw_stats', "")
        status_raw = item.get('status', "")

        # If the keys were still named the old way, this catches them:
        if not p_raw: p_raw = item.get('p_raw', "")
        if not u_raw: u_raw = item.get('u_raw', "")
        if not stats: stats = item.get('stats_raw', "")
        if not status_raw: status_raw = item.get('s_raw', "")

        # Clean Program and Degree
        degree = "PhD" if "PhD" in p_raw else "Masters" if any(x in p_raw for x in ["Masters", "MS", "MA"]) else "Other"
        p_name_clean = p_raw.replace("PhD", "").replace("Masters", "").replace("MS", "").replace("MA", "").strip()

        # Regex for Term
        term_match = re.search(r'(Fall|Spring|Summer|Winter)\s*(\d{4})', stats)
        
        entry = {
            "program": f"{p_name_clean}, {u_raw}" if p_name_clean and u_raw else "Unknown Program",
            "comments": item.get('comments', item.get('comm_raw', "No comment")),
            "date_added": item.get('date_added', item.get('d_raw', "")),
            "url": item.get('url', item.get('url_raw', "")),
            "status": "Accepted" if "Accepted" in status_raw else "Rejected" if "Rejected" in status_raw else "Wait listed" if "Wait" in status_raw else "Other",
            "term": term_match.group(0) if term_match else "No term info",
            "US/International": "International" if "International" in stats else "American" if "American" in stats else "No origin info",
            "Degree": degree
        }
        cleaned.append(entry)

    output_path = os.path.join(path, 'applicant_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, indent=4)
    print(f"Success! Cleaned {len(cleaned)} rows.")

if __name__ == "__main__":
    clean_data()