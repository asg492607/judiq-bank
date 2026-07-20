from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, Any, List
from pydantic import BaseModel
import time
import asyncio
import uuid
from security import SecurityManager
from bank_db import BankDatabase

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any], summary="Get Executive Dashboard KPIs")
async def get_executive_dashboard():
    kpis = BankDatabase.get_dashboard_kpis()
    
    return {
        "success": True,
        "timestamp": time.time(),
        "kpis": kpis,
        "recovery_trajectory": {
            "labels": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            "legal_recovery": [120, 190, 300, 500, 200, 300],
            "settlement_recovery": [50, 80, 150, 200, 250, 400]
        },
        "risk_heatmap": {
            "categories": ['Limitation Risk', 'Doc Missing', 'Fraud High', 'Security Weak', 'Compliance'],
            "case_counts": [145, 320, 45, 210, 12]
        },
        "insights": [
            {
                "type": "alert",
                "title": "Limitation Risk Detected",
                "description": "14 cases in the West region are approaching their limitation period within 30 days."
            },
            {
                "type": "success",
                "title": "Settlement Opportunity",
                "description": "AI recommends settlement for 45 SME loans in the standard bracket based on recent economic indicators."
            }
        ]
    }

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

@router.post("/auth/register", summary="Register New Officer")
async def register_officer(req: RegisterRequest):
    success = BankDatabase.create_officer(req.name, req.email, req.password)
    if success:
        return {"success": True, "message": f"Officer {req.name} registered successfully."}
    return {"success": False, "message": "Email already exists."}

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/login", summary="Login for Bank Edition")
async def login(req: LoginRequest):
    if BankDatabase.verify_officer(req.username, req.password):
        access_token = SecurityManager.create_access_token(data={"sub": req.username})
        return {"success": True, "access_token": access_token, "token_type": "bearer"}
    return {"success": False, "message": "Invalid credentials"}

@router.get("/portfolio", summary="Get Portfolio Intelligence")
async def get_portfolio_intelligence():
    return {
        "success": True,
        "regions": ["North", "South", "East", "West"],
        "npa_distribution": [1200, 850, 600, 1600]
    }

@router.post("/cases/upload", summary="Upload Case Documents")
async def upload_case_documents(file: UploadFile = File(...)):
    await asyncio.sleep(1.5)
    
    case_id = f"CASE-{str(uuid.uuid4())[:8].upper()}"
    exposure = 4500000.0  # Mock OCR extracted
    borrower = "Acme Corp Ltd."
    BankDatabase.add_case(case_id, borrower, exposure, "OCR Completed", "High")
    
    return {
        "success": True,
        "message": f"Successfully processed {file.filename}",
        "case_id": case_id,
        "details": {
            "borrower_name": borrower,
            "exposure": exposure,
            "category": "Corporate NPA",
            "confidence_score": 0.94,
            "missing_documents": ["Security Cheque"]
        }
    }

@router.get("/cases/recent", summary="Get Recent Intake Cases")
async def get_recent_cases():
    cases = BankDatabase.get_cases()
    return {
        "success": True,
        "cases": cases
    }

@router.get("/recovery/cases", summary="Get Active Recovery Cases")
async def get_recovery_cases():
    cases = BankDatabase.get_recovery_cases()
    return {
        "cases": cases
    }

class AssignAdvocateRequest(BaseModel):
    case_id: str
    advocate_name: str

@router.post("/recovery/assign", summary="Assign Advocate to Case")
async def assign_advocate(req: AssignAdvocateRequest):
    success = BankDatabase.assign_advocate(req.case_id, req.advocate_name)
    if success:
        return {"success": True, "message": f"Successfully assigned {req.advocate_name} to case {req.case_id}"}
    return {"success": False, "message": "Failed to assign advocate."}

@router.get("/risk/portfolio", summary="Get Portfolio Risk Metrics")
async def get_portfolio_risk():
    return {
        "kpis": {
            "high_risk_accounts": 14,
            "ews_alerts": 42,
            "avg_portfolio_risk": "68/100"
        },
        "risk_matrix": {
            "categories": ["Low", "Medium", "High", "Critical"],
            "exposure_cr": [850, 420, 115, 34]
        }
    }

@router.get("/risk/high-risk", summary="Get High Risk Cases")
async def get_high_risk_cases():
    return {
        "cases": [
            {
                "borrower": "Pioneer Industries",
                "exposure": "₹34.5 Cr",
                "risk_score": 92,
                "factor": "Skipped 2 EMIs + Legal Dispute",
                "recommendation": "Initiate SARFAESI Notice"
            },
            {
                "borrower": "Global Traders LLC",
                "exposure": "₹12.8 Cr",
                "risk_score": 88,
                "factor": "Adverse Media + Rating Downgrade",
                "recommendation": "Immediate Management Meeting"
            }
        ]
    }

@router.get("/notices/tracking", summary="Get Legal Notices Tracking")
async def get_notices_tracking():
    notices = BankDatabase.get_notices()
    return {
        "notices": notices
    }

class NoticeGenerateRequest(BaseModel):
    case_id: str
    notice_type: str

@router.post("/notices/generate", summary="Generate Legal Notice Draft")
async def generate_notice(req: NoticeGenerateRequest):
    await asyncio.sleep(1)
    
    draft_text = f"""
BY REGISTERED POST WITH A/D
Date: [Current Date]

To,
The Managing Director
[Borrower Name corresponding to {req.case_id}]
[Registered Address]

Sub: Statutory Notice under Section 13(2) of the SARFAESI Act, 2002.
(Type: {req.notice_type})

Dear Sir/Madam,

1. Under instructions from our client, JudiQ Bank Ltd., we hereby issue this notice regarding the financial assistance granted to your company.
2. Despite repeated requests and reminders, you have failed to maintain the financial discipline and the account has been classified as a Non-Performing Asset (NPA).
3. The total outstanding dues as of date amount to [Exposure Amount], which you are liable to pay along with future interest and incidental expenses.
4. You are hereby called upon to discharge in full your liabilities to the Bank within 60 days from the date of this notice, failing which the Bank shall exercise its rights under Section 13(4) of the SARFAESI Act.

Please take notice that you are prohibited from transferring by way of sale, lease, or otherwise any of the secured assets without prior written consent of the Bank.

Yours faithfully,

Authorized Officer
JudiQ Bank Ltd.
    """
    
    notice_id = f"NT-{str(uuid.uuid4())[:6].upper()}"
    BankDatabase.add_notice(notice_id, req.case_id, "Fetched Borrower", req.notice_type, "Drafted", "Pending", draft_text.strip())
    
    return {
        "success": True,
        "draft_content": draft_text.strip()
    }
