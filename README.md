# JudiQ Bank Edition | Litigation & Recovery OS

JudiQ Bank Edition is a comprehensive enterprise-grade operating system designed to streamline and automate legal litigation, compliance tracking, and financial recovery operations for modern banking institutions. It provides a unified dashboard to manage the complete lifecycle of Non-Performing Assets (NPAs), from AI-driven case intake to legal notice dispatch and court hearing management.

## 🌟 Key Features

### 1. Executive Dashboard & Analytics
- Live tracking of Total NPA Exposure and AI Predicted Recovery figures.
- Dynamic visual charts mapping recovery trends and portfolio risk distribution.
- Real-time activity feeds logging platform-wide events and status changes.

### 2. AI-Powered Case Intake
- Simulated drag-and-drop OCR document upload for rapid case ingestion.
- Automated extraction of borrower details, financial exposure, and confidence scoring.
- Intelligent tagging and routing of intake data into the recovery pipeline.

### 3. Legal Notice Automation
- Centralized queue for pending and dispatched legal notices (e.g., Section 138, SARFAESI).
- Interactive, AI-assisted Legal Notice Generator for rapid drafting.
- One-click approval and dispatch workflows.

### 4. Recovery & Strategy Management
- Complete oversight of the recovery case portfolio with filtering by status (Unassigned, Active, Settled).
- Seamless Advocate Assignment flow with customizable external counsel mapping.
- KPI tracking for specific resolution strategies such as One-Time Settlements (OTS).

### 5. Litigation Command Center
- Tracking of active court matters, jurisdictions, and upcoming hearing dates.
- Interactive calendar updates and disposition status changes (e.g., Adjourned, Reserved for Orders).
- Granular mapping of case exposure against specific court workflows.

### 6. Compliance Engine
- Automated tracking of regulatory and procedural violations.
- Real-time Compliance Score computation with a visual gauge chart.
- Audit logging for open and resolved critical items.

## 🛠 Technology Stack

- **Backend:** Python, FastAPI
- **Database:** SQLite (with automated dynamic seeding)
- **Authentication:** Token-based JWT (JSON Web Tokens)
- **Frontend:** Vanilla JavaScript, HTML5, CSS3 (Enterprise Blue/White Theme)
- **Charting:** Chart.js

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ installed on your system.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/asg492607/judiq-bank.git
   cd judiq-bank
   ```

2. **Install Backend Dependencies:**
   ```bash
   pip install fastapi uvicorn pydantic psutil passlib bcrypt pyjwt
   ```

### Running the Platform

The platform uses two separate servers for security and proper API routing. You will need to start both.

**1. Start the Backend API Server:**
Open a terminal in the `backend` directory and run:
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*(The backend will automatically create the `analytics.db` database and seed it with sample data upon startup.)*

**2. Start the Frontend Web Server:**
Open a separate terminal in the root directory and serve the `frontend` folder:
```bash
python -m http.server 5500 --directory ./frontend
```

**3. Access the Platform:**
Open your web browser and navigate to:
```
http://127.0.0.1:5500/index.html
```

### Default Login Credentials
- **Username:** `admin`
- **Password:** `password`

## 🔒 Security & Architecture
- **Password Hashing:** User passwords are encrypted using `bcrypt` and `passlib`.
- **Stateless Sessions:** All API endpoints are protected using JWT `Bearer` tokens passed via HTTP Headers.
- **Dynamic Seeding:** The platform auto-generates realistic NPA cases, compliance alerts, and litigation data on first boot to provide an immediate interactive experience.

## 📝 License
This project is proprietary and confidential. All rights reserved.
