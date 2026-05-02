import json
import os
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_data(total_needed=30000):
    # Dynamic pathing ensures it works regardless of "Module 2" or "Module_2"
    folder_path = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(folder_path, "raw_data.json")
    
    results = []
    page = 1

    print("--- Portfolio Mode: Scraping Started ---")
    print(f"Goal: {total_needed} entries. This will take approximately 1-2 hours.")
    print("The script will remain silent until completion. Do not close the terminal.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        browser_page = context.new_page()

        while len(results) < total_needed:
            try:
                url = f"https://www.thegradcafe.com/survey/?q=*&p={page}"
                
                # Using domcontentloaded to bypass slow-loading ads
                response = browser_page.goto(url, wait_until="domcontentloaded", timeout=90000)
                
                if response.status != 200:
                    break

                # Wait for the table to exist on the page
                browser_page.wait_for_selector("table", timeout=10000)
                
                soup = BeautifulSoup(browser_page.content(), 'html.parser')
                rows = soup.select("table tr")

                if not rows or len(rows) < 5:
                    break

                for i in range(len(rows)):
                    cols = rows[i].find_all('td')
                    if len(cols) >= 4:
                        inst = cols[0].get_text(strip=True)
                        if inst.lower() in ["institution", ""]: continue

                        # Logic to capture stats and comments from sibling rows
                        stats_raw = ""
                        comm_raw = "No comment"
                        
                        try:
                            next_row = rows[i+1]
                            if next_row and "institution" not in str(next_row):
                                stats_raw = next_row.get_text(" ", strip=True)
                                next_next_row = rows[i+2]
                                if next_next_row and "institution" not in str(next_next_row):
                                    comm_raw = next_next_row.get_text(" ", strip=True)
                        except IndexError:
                            pass

                        results.append({
                            "u_raw": inst,
                            "p_raw": cols[1].get_text(" ", strip=True),
                            "d_raw": cols[2].get_text(strip=True),
                            "s_raw": cols[3].get_text(strip=True),
                            "stats_raw": stats_raw,
                            "comm_raw": comm_raw
                        })
                        
                        if len(results) >= total_needed: break
                
                # Counter removed as requested
                time.sleep(1.5) 
                page += 1
                
            except Exception:
                # Silently break on error to save whatever data was collected
                break

        browser.close()

    # Save data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    
    print("\n" + "="*40)
    print("SCRAPE COMPLETE")
    print(f"Total Entries Collected: {len(results)}")
    print(f"File Saved to: {output_file}")
    print("="*40)

if __name__ == "__main__":
    scrape_data(30000)