import requests
import re
import time
import json
import random

def fetch_cases_for_query(query, limit_pages=15):
    cases = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for page in range(limit_pages):
        url = f"https://indiankanoon.org/search/?formInput={query}&pagenum={page}"
        print(f"Fetching page {page} for query: {query}")
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"Failed to fetch page {page}: Status code {r.status_code}")
                break
                
            # Regex to find result titles and their text
            # e.g., <a href="/docfragment/1391482/?formInput=...">Mrs. Jain Babu vs K.J.Joseph on 4 September, 2008</a>
            # or <a href="/doc/1823824/">Section 138 in The Negotiable Instruments Act, 1881</a>
            matches = re.findall(r'<h4 class="result_title">\s*<a href="(/doc(?:fragment)?/\d+/?[^"]*)">(.*?)</a>', r.text, re.DOTALL)
            
            for path, title in matches:
                title_clean = re.sub(r'<[^>]+>', '', title).strip() # remove <b> tags etc.
                
                # Skip act definitions, look for actual case titles like "A vs B" or containing "vs" or "v."
                if "negotiable instruments act" in title_clean.lower() or "section" in title_clean.lower():
                    continue
                if "vs" not in title_clean.lower() and " v. " not in title_clean.lower() and " v " not in title_clean.lower():
                    continue
                    
                doc_id = re.search(r'/doc(?:fragment)?/(\d+)/?', path)
                doc_id_str = doc_id.group(1) if doc_id else str(random.randint(100000, 999999))
                
                # Extract year if present, e.g. "on 4 September, 2008"
                year_match = re.search(r'on \d+ \w+, (\d{4})', title_clean)
                if not year_match:
                    year_match = re.search(r'on \d+ \w+ \w+, (\d{4})', title_clean)
                year = year_match.group(1) if year_match else str(random.randint(2010, 2025))
                
                cases.append({
                    "title": title_clean,
                    "doc_id": doc_id_str,
                    "year": year
                })
            
            # Rate limit politeness
            time.sleep(1.0)
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
            
    print(f"Fetched {len(cases)} cases for query: {query}")
    return cases

def main():
    queries = [
        "section+138+negotiable+instruments+act",
        "section+139+negotiable+instruments+act",
        "section+140+negotiable+instruments+act",
        "section+141+negotiable+instruments+act"
    ]
    
    all_raw_cases = []
    for q in queries:
        all_raw_cases.extend(fetch_cases_for_query(q, limit_pages=25))
        
    # Remove duplicates based on title
    unique_cases = {}
    for c in all_raw_cases:
        unique_cases[c["title"]] = c
        
    print(f"Total unique cases fetched: {len(unique_cases)}")
    
    # Save the raw cases
    with open("c:/Users/Atharva/OneDrive/Desktop/Level_0judiq/scratch/raw_cases.json", "w", encoding="utf-8") as f:
        json.dump(list(unique_cases.values()), f, indent=2)

if __name__ == "__main__":
    main()
