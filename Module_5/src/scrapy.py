import urllib.request
from bs4 import BeautifulSoup
import json
import os
import time

def scrape_data(total_needed=00):
    path = r"C:\Users\Masaomi Enami\Python Project\jhu_software_concepts\Module 2"
    base_url = "https://www.thegradcafe.com/survey/index.php?q=*&p="
    headers = {'User-Agent': 'Mozilla/5.0'}
    results = []
    page = 1

    while len(results) < total_needed:
        try:
            url = base_url + str(page)
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                soup = BeautifulSoup(response.read(), 'html.parser')
                rows = soup.find_all('tr')
                
                for i in range(len(rows)):
                    cols = rows[i].find_all('td')
                    # Main Student Row Identity
                    if len(cols) >= 4 and cols[0].get_text(strip=True):
                        
                        stats_raw = ""
                        comm_raw = "No comment" # Default value
                        
                        # Check for Stats (Row 2)
                        r2 = rows[i].find_next_sibling('tr')
                        if r2 and not r2.find('td', class_='institution'):
                            stats_raw = r2.get_text(" ", strip=True)
                            
                            # Check for Comments (Row 3)
                            r3 = r2.find_next_sibling('tr')
                            if r3 and not r3.find('td', class_='institution'):
                                text = r3.get_text(" ", strip=True)
                                
                                # Check to ensure it's not a bugged repeat row
                                if len(text) > 0 and "February" not in text:
                                    # --- CLEANING LOGIC START ---
                                    # 1. Remove specific UI junk text
                                    for junk in ["Open options", "See More", "Report"]:
                                        text = text.replace(junk, "")
                                    
                                    # 2. Collapse newlines (\r\n) and multiple spaces into one single line
                                    comm_raw = " ".join(text.split())
                                    # --- CLEANING LOGIC END ---

                        results.append({
                            "u_raw": cols[0].get_text(strip=True),
                            "p_raw": cols[1].get_text(" ", strip=True),
                            "d_raw": cols[2].get_text(strip=True),
                            "s_raw": cols[3].get_text(strip=True),
                            "stats_raw": stats_raw,
                            "comm_raw": comm_raw,
                            "url_raw": f"https://www.thegradcafe.com{rows[i].find('a', href=True)['href']}" if rows[i].find('a', href=True) else url
                        })
                        if len(results) >= total_needed: break
            
            print(f"Collected: {len(results)}", end="\r")
            page += 1
            
        except Exception as e:
            print(f"\nStopped: {e}")
            break

    with open(os.path.join(path, "raw_data.json"), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    scrape_data(100)