import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import time

def scrape_data(total_needed=30000):
    # Fix 1: Use a relative path so it works on any machine
    folder_path = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(folder_path, "raw_data.json")
    
    # Fix 2: Use Cloudscraper to bypass the "bot" firewall
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    base_url = "https://www.thegradcafe.com/survey/index.php"
    results = []
    page = 1

    print(f"Targeting {total_needed} entries. This will take some time...")

    while len(results) < total_needed:
        try:
            # Fix 3: Use a params dictionary for cleaner URL handling
            params = {'q': '*', 'p': page}
            response = scraper.get(base_url, params=params, timeout=20)
            
            if response.status_code != 200:
                print(f"\n[Error] Status {response.status_code}. You might be rate-limited.")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # Select all table rows
            rows = soup.select("table tr") 

            if not rows or len(rows) < 5:
                print(f"\n[Warning] No data found on page {page}. The site might be blocking us.")
                break

            for row in rows:
                cols = row.find_all('td')
                # Validate that this is a data row, not a header or ad
                if len(cols) >= 4:
                    inst = cols[0].get_text(strip=True)
                    if inst.lower() in ["institution", ""]: 
                        continue
                        
                    results.append({
                        "u_raw": inst,
                        "p_raw": cols[1].get_text(" ", strip=True),
                        "d_raw": cols[2].get_text(strip=True),
                        "s_raw": cols[3].get_text(strip=True),
                    })
                    
                    if len(results) >= total_needed:
                        break
            
            # Progress bar logic
            print(f"Progress: {len(results)}/{total_needed} (Page {page})", end="\r")
            
            # Fix 4: Be polite. A 1.5s delay prevents your IP from being banned.
            time.sleep(1.5) 
            page += 1
            
        except Exception as e:
            print(f"\n[Critical Error] {e}")
            break

    # Save the data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    
    print("\n" + "="*30)
    print("SCRAPE COMPLETE")
    print(f"Total saved: {len(results)}")
    print(f"Final file: {output_file}")
    print("="*30)

if __name__ == "__main__":
    # Fix 5: Ensure the target is actually 30,000
    scrape_data(30000)