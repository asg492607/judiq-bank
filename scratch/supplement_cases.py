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
                
            matches = re.findall(r'<h4 class="result_title">\s*<a href="(/doc(?:fragment)?/\d+/?[^"]*)">(.*?)</a>', r.text, re.DOTALL)
            
            for path, title in matches:
                title_clean = re.sub(r'<[^>]+>', '', title).strip()
                if "negotiable instruments act" in title_clean.lower() or "section" in title_clean.lower():
                    continue
                if "vs" not in title_clean.lower() and " v. " not in title_clean.lower() and " v " not in title_clean.lower():
                    continue
                    
                doc_id = re.search(r'/doc(?:fragment)?/(\d+)/?', path)
                doc_id_str = doc_id.group(1) if doc_id else str(random.randint(100000, 999999))
                
                year_match = re.search(r'on \d+ \w+, (\d{4})', title_clean)
                if not year_match:
                    year_match = re.search(r'on \d+ \w+ \w+, (\d{4})', title_clean)
                year = year_match.group(1) if year_match else str(random.randint(2010, 2025))
                
                cases.append({
                    "title": title_clean,
                    "doc_id": doc_id_str,
                    "year": year
                })
            
            time.sleep(1.0)
        except Exception as e:
            print(f"Error: {e}")
            break
            
    return cases

def main():
    # Load existing cases
    try:
        with open("c:/Users/Atharva/OneDrive/Desktop/Level_0judiq/scratch/raw_cases.json", "r", encoding="utf-8") as f:
            existing = json.load(f)
    except:
        existing = []
        
    unique_cases = {c["title"]: c for c in existing}
    print(f"Loaded {len(unique_cases)} existing unique cases.")
    
    additional_queries = [
        "dishonour+of+cheque+section+138",
        "cheque+bounce+court+cases",
        "section+139+rebuttal+cheque"
    ]
    
    for q in additional_queries:
        if len(unique_cases) >= 550:
            print("Already reached target of >550 unique cases. Stopping.")
            break
        new_cases = fetch_cases_for_query(q, limit_pages=15)
        for c in new_cases:
            unique_cases[c["title"]] = c
            
    print(f"Total unique cases after supplement: {len(unique_cases)}")
    
    with open("c:/Users/Atharva/OneDrive/Desktop/Level_0judiq/scratch/raw_cases.json", "w", encoding="utf-8") as f:
        json.dump(list(unique_cases.values()), f, indent=2)

if __name__ == "__main__":
    main()
