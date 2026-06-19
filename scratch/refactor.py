import os
import shutil
import glob
import re

ROOT_DIR = r"c:\Users\Atharva\OneDrive\Desktop\Level_0judiq"
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
APP_DIR = os.path.join(BACKEND_DIR, "app")

print("--- FLATTENING BACKEND ---")
py_files = []
# Find all .py files in backend/app
for root, dirs, files in os.walk(APP_DIR):
    for file in files:
        if file.endswith(".py"):
            py_files.append(os.path.join(root, file))

# Move them to backend/
moved_backend_files = []
for file_path in py_files:
    filename = os.path.basename(file_path)
    if filename == "__init__.py":
        continue # skip init files
    
    dest_path = os.path.join(BACKEND_DIR, filename)
    if os.path.exists(dest_path):
        print(f"Warning: {filename} already exists in backend/. Overwriting.")
    shutil.move(file_path, dest_path)
    moved_backend_files.append(dest_path)
    print(f"Moved {filename} to backend/")

# Move strategy_engine.py from root if exists
strategy_engine = os.path.join(ROOT_DIR, "strategy_engine.py")
if os.path.exists(strategy_engine):
    dest_path = os.path.join(BACKEND_DIR, "strategy_engine.py")
    shutil.move(strategy_engine, dest_path)
    moved_backend_files.append(dest_path)
    print("Moved strategy_engine.py to backend/")

# Update imports in all backend python files
print("\n--- FIXING BACKEND IMPORTS ---")
for file_path in moved_backend_files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace 'from app.services.draft_engine import' -> 'from draft_engine import'
    # Replace 'from app.core.config import' -> 'from config import'
    # Replace 'from app.models.something import' -> 'from something import'
    # Basically replace 'app.*.module' with 'module'
    
    # Pattern: from app.folder.module import ...
    # -> from module import ...
    new_content = re.sub(r'from\s+app\.[a-zA-Z0-9_]+\.([a-zA-Z0-9_]+)\s+import', r'from \1 import', content)
    
    # Pattern: from app.module import ...
    new_content = re.sub(r'from\s+app\.([a-zA-Z0-9_]+)\s+import', r'from \1 import', new_content)
    
    # Pattern: import app.services.module
    new_content = re.sub(r'import\s+app\.[a-zA-Z0-9_]+\.([a-zA-Z0-9_]+)', r'import \1', new_content)
    
    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Fixed imports in {os.path.basename(file_path)}")

# Remove app folder
if os.path.exists(APP_DIR):
    shutil.rmtree(APP_DIR)
    print("Deleted backend/app/ directory")

print("\n--- FLATTENING FRONTEND ---")
# Move root frontend files to frontend/
for root_file in ["index.html", "script.js", "styles.css"]:
    src = os.path.join(ROOT_DIR, root_file)
    if os.path.exists(src):
        dest = os.path.join(FRONTEND_DIR, root_file)
        shutil.move(src, dest)
        print(f"Moved {root_file} from root to frontend/")

# Check if frontend/js exists and move contents
JS_DIR = os.path.join(FRONTEND_DIR, "js")
if os.path.exists(JS_DIR):
    for root, dirs, files in os.walk(JS_DIR):
        for file in files:
            src = os.path.join(root, file)
            dest = os.path.join(FRONTEND_DIR, file)
            shutil.move(src, dest)
            print(f"Moved {file} to frontend/")
    shutil.rmtree(JS_DIR)
    print("Deleted frontend/js/ directory")

print("\nDONE!")
