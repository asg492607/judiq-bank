import requests
import time
import os

API_URL = "http://127.0.0.1:8000/api/v1/bank/cases/bulk-upload"
CSV_FILE = "scripts/mock_cases_100k.csv"

def run_stress_test():
    print(f"Starting stress test: Uploading {CSV_FILE} to {API_URL}")
    if not os.path.exists(CSV_FILE):
        print("Error: CSV file not found. Run generator first.")
        return

    # Using dummy auth token if needed, but endpoint doesn't currently require auth dependency?
    # Oh wait, we should check if bulk-upload requires auth. 
    # In banking_api.py: @router.post("/cases/bulk-upload", summary="Bulk Upload Cases via Excel/CSV")
    # It does not have current_user = Depends(...)! So it is open for now.
    
    start_time = time.time()
    
    with open(CSV_FILE, 'rb') as f:
        files = {'file': (CSV_FILE, f, 'text/csv')}
        try:
            response = requests.post(API_URL, files=files)
            end_time = time.time()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            elapsed = round(end_time - start_time, 2)
            print(f"Total time for 100k upload: {elapsed} seconds")
            
        except Exception as e:
            print(f"Failed to upload: {e}")

if __name__ == "__main__":
    run_stress_test()
