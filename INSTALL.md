# JudiQ Enterprise V3 - Installation Guide

## 1. Prerequisites
- Python 3.10+
- SQLite (included with Python)
- Windows/Linux/macOS supported

## 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/asg492607/judiq-bank.git
cd judiq-bank

# Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Configuration
JudiQ utilizes SQLite for local persistence by default. For enterprise environments, you can override database configs using `.env` variables (e.g., `DATABASE_URL`). 
Ensure you define your Master API Key for Core Banking Systems integrations:
```bash
export CBS_API_KEY="your-secure-api-key"
```

## 4. Running the Application
The backend server runs on FastAPI/Uvicorn.
```bash
# Start the backend server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Then, simply open `frontend/index.html` in your web browser.

## 5. Security & Backups
- **Authentication**: JWT-based stateless tokens.
- **Backups**: The SQLite database (`bank_data.db`) can be securely dumped via the `GET /api/v1/bank/admin/backup` endpoint by Admin users.
- **Logging**: Production logs are rotating and written to `logs/judiq_enterprise.log`.
