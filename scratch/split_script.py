import os
import re

SCRIPT_PATH = "c:/Users/Atharva/OneDrive/Desktop/Level_0judiq/frontend/script.js"
OUT_DIR = "c:/Users/Atharva/OneDrive/Desktop/Level_0judiq/frontend/js/modules_new"

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

sections = []
current_section_name = "header"
current_lines = []

for line in lines:
    if line.startswith("// ════════════════════════════════════════════════"):
        continue
    
    match = re.match(r"// ([A-Z ]+) -?.*", line)
    if match and "════" not in line:
        name = match.group(1).strip()
        if name in ["CONFIGURATION", "RELIABILITY LAYER", "APPLICATION STATE", "WIZARD STEP DEFINITIONS", "TOAST NOTIFICATION SYSTEM", "LOADING OVERLAY SYSTEM", "API DATA PROCESSOR LAYER", "WIZARD UI LOGIC", "CASE ANALYSIS", "AI REASONING LAYER"]:
            if current_lines:
                sections.append((current_section_name, current_lines))
            current_section_name = name
            current_lines = [line]
            continue
    
    current_lines.append(line)

if current_lines:
    sections.append((current_section_name, current_lines))

for name, content in sections:
    filename = name.lower().replace(" ", "_").replace("_-", "_").replace("__", "_") + ".js"
    with open(os.path.join(OUT_DIR, filename), "w", encoding="utf-8") as f:
        f.writelines(content)
    print(f"Created {filename} with {len(content)} lines")

print("Done")
