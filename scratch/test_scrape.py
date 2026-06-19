import requests
import re

def test():
    url = "https://indiankanoon.org/search/?formInput=section+138+negotiable+instruments+act"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            # Look for result titles in HTML
            matches = re.findall(r'<a href="/doc/[^"]+">([^<]+)</a>', r.text)
            for m in matches[:10]:
                print(m.strip())
            print(f"Total matches: {len(matches)}")
        else:
            print(r.text[:500])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
