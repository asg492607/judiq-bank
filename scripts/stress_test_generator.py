import csv
import uuid
import random
import time
import os

def generate_cases(num_cases=100000, output_file="mock_cases_100k.csv"):
    print(f"Generating {num_cases} mock cases...")
    start_time = time.time()
    
    statuses = ["Newly Ingested", "OCR Completed", "Legal Notice Pending", "In Court"]
    risks = ["Low", "Medium", "High", "Critical"]
    borrowers = [
        "Omega Textiles", "Alpha Manufacturing", "Zeta Logistics",
        "Delta Constructions", "Sigma Retail", "Gamma Electronics"
    ]
    
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["case_id", "borrower", "exposure", "status", "risk"])
        
        for i in range(num_cases):
            case_id = f"CASE-{str(uuid.uuid4())[:8].upper()}"
            borrower = random.choice(borrowers) + f" #{i}"
            exposure = round(random.uniform(10.0, 5000.0), 2)
            status = random.choice(statuses)
            risk = random.choice(risks)
            
            writer.writerow([case_id, borrower, exposure, status, risk])
            
            if (i + 1) % 20000 == 0:
                print(f"  Generated {i + 1} cases...")

    print(f"Finished generating {num_cases} cases in {round(time.time() - start_time, 2)} seconds.")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    os.makedirs("scripts", exist_ok=True)
    generate_cases(100000, "scripts/mock_cases_100k.csv")
