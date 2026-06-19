import requests

def save_sample():
    url = "https://indiankanoon.org/search/?formInput=section+138+negotiable+instruments+act"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        with open("c:/Users/Atharva/OneDrive/Desktop/Level_0judiq/scratch/sample_page.html", "w", encoding="utf-8") as f:
            f.write(r.text[:50000])
        print("Sample saved successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    save_sample()
