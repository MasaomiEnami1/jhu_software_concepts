"""
Module to scrape admission data from TheGradCafe and save it to a JSON file.
"""

import json
import os
import urllib.request
import urllib.error

from bs4 import BeautifulSoup

# pylint: disable=too-many-locals, too-many-nested-blocks
def scrape_data(total_needed=100):
    """
    Scrape admission results from TheGradCafe up to the specified amount
    and save them to a JSON file.
    """
    # Dynamically locate the project root directory so it saves in Module_5
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

                # Use enumerate instead of range(len())
                for _, row in enumerate(rows):
                    cols = row.find_all('td')

                    # Main Student Row Identity
                    if len(cols) >= 4 and cols[0].get_text(strip=True):
                        stats_raw = ""
                        comm_raw = "No comment"

                        # Check for Stats (Row 2)
                        r2 = row.find_next_sibling('tr')
                        if r2 and not r2.find('td', class_='institution'):
                            stats_raw = r2.get_text(" ", strip=True)

                            # Check for Comments (Row 3)
                            r3 = r2.find_next_sibling('tr')
                            if r3 and not r3.find('td', class_='institution'):
                                text = r3.get_text(" ", strip=True)

                                # Check to ensure it's not a bugged repeat row
                                if len(text) > 0 and "February" not in text:
                                    # Clean UI junk
                                    for junk in ["Open options", "See More", "Report"]:
                                        text = text.replace(junk, "")

                                    # Collapse newlines and spaces
                                    comm_raw = " ".join(text.split())

                        # Extract URL safely to avoid long lines
                        url_tag = row.find('a', href=True)
                        if url_tag:
                            url_raw = f"https://www.thegradcafe.com{url_tag['href']}"
                        else:
                            url_raw = url

                        results.append({
                            "u_raw": cols[0].get_text(strip=True),
                            "p_raw": cols[1].get_text(" ", strip=True),
                            "d_raw": cols[2].get_text(strip=True),
                            "s_raw": cols[3].get_text(strip=True),
                            "stats_raw": stats_raw,
                            "comm_raw": comm_raw,
                            "url_raw": url_raw
                        })

                        # Break multiple statements into separate lines
                        if len(results) >= total_needed:
                            break

            print(f"Collected: {len(results)}", end="\r")
            page += 1

        # Catch specific web request errors instead of a broad Exception
        except urllib.error.URLError as e:
            print(f"\nStopped: {e}")
            break

    # Save the file cleanly to the project root
    output_path = os.path.join(base_dir, "raw_data.json")
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(results, file, indent=4)

if __name__ == "__main__":
    scrape_data(100)
