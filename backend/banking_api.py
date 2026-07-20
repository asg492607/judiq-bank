from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import time
import asyncio
import uuid
from datetime import datetime, timedelta
from security import SecurityManager, get_current_user, require_role, verify_cbs_api_key
from bank_db import BankDatabase

router = APIRouter()


# ─────────────────────────────────────────────
# Auth Endpoints
# ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

@router.post("/auth/register", summary="Register New Officer", tags=["Bank Auth"])
async def register_officer(req: RegisterRequest):
    if len(req.password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters."}
    success = BankDatabase.create_officer(req.name, req.email, req.password)
    if success:
        return {"success": True, "message": f"Officer '{req.name}' registered successfully. You can now log in."}
    return {"success": False, "message": "Username already exists. Please choose another."}


class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/login", summary="Login for Bank Edition", tags=["Bank Auth"])
async def login(req: LoginRequest):
    officer = BankDatabase.verify_officer(req.username, req.password)
    if officer:
        access_token = SecurityManager.create_access_token(data={"sub": req.username, "name": officer["name"], "role": officer["role"]})
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {"name": officer["name"], "email": officer["email"], "role": officer["role"]}
        }
    return {"success": False, "message": "Invalid username or password."}


@router.post("/auth/logout", summary="Logout", tags=["Bank Auth"])
async def logout(current_user: str = Depends(get_current_user)):
    # Token invalidation is client-side (stateless JWT). Backend confirms.
    return {"success": True, "message": "Logged out successfully."}


@router.get("/auth/me", summary="Get Current User Profile", tags=["Bank Auth"])
async def get_me(current_user: str = Depends(get_current_user)):
    officer = BankDatabase.get_officer_info(current_user)
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")
    return {"success": True, "user": officer}


# ─────────────────────────────────────────────
# Dashboard Endpoint
# ─────────────────────────────────────────────

@router.get("/dashboard", response_model=Dict[str, Any], summary="Get Executive Dashboard KPIs", tags=["Dashboard"])
async def get_executive_dashboard(current_user: str = Depends(get_current_user)):
    kpis = BankDatabase.get_dashboard_kpis()
    return {
        "success": True,
        "timestamp": time.time(),
        "kpis": kpis,
        "recovery_trajectory": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "legal_recovery": [120, 190, 300, 500, 200, 300],
            "settlement_recovery": [50, 80, 150, 200, 250, 400]
        },
        "risk_heatmap": {
            "categories": ["Limitation Risk", "Doc Missing", "Fraud High", "Security Weak", "Compliance"],
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
                "description": "AI recommends settlement for 45 SME loans based on recent economic indicators."
            }
        ]
    }


# ─────────────────────────────────────────────
# Search Endpoint
# ─────────────────────────────────────────────

@router.get("/search", summary="Global Case Search", tags=["Search"])
async def search_cases(
    q: str = Query(..., min_length=2, description="Search query"),
    current_user: str = Depends(get_current_user)
):
    results = BankDatabase.search_cases(q)
    return {"success": True, "query": q, "count": len(results), "results": results}


# ─────────────────────────────────────────────
# Case Intake Endpoints
# ─────────────────────────────────────────────

@router.post("/cases/upload", summary="Upload Case Documents", tags=["Case Intake"])
async def upload_case_documents(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    # Validate file type
    allowed_types = ["application/pdf", "text/csv", "application/zip", "application/octet-stream", "text/plain"]
    allowed_extensions = [".pdf", ".csv", ".zip", ".txt", ".docx"]
    
    if file.filename:
        ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type '{ext}' not allowed. Accepted: PDF, CSV, ZIP, TXT, DOCX")

    await asyncio.sleep(1.5)  # Simulate OCR processing

    case_id = f"CASE-{str(uuid.uuid4())[:8].upper()}"
    exposure = 4500000.0  # Mock OCR extracted
    borrower = "Acme Corp Ltd."
    BankDatabase.add_case(case_id, borrower, exposure, "OCR Completed", "High")

    return {
        "success": True,
        "message": f"Successfully processed '{file.filename}'",
        "case_id": case_id,
        "details": {
            "borrower_name": borrower,
            "exposure": exposure,
            "exposure_formatted": f"₹{exposure/10000000:.1f} Cr",
            "category": "Corporate NPA",
            "confidence_score": 0.94,
            "missing_documents": ["Security Cheque", "CIBIL Report"]
        }
    }


@router.get("/cases/recent", summary="Get Recent Intake Cases", tags=["Case Intake"])
async def get_recent_cases(
    limit: int = Query(50, description="Max number of cases to return"),
    offset: int = Query(0, description="Number of cases to skip"),
    current_user: str = Depends(get_current_user)
):
    cases = BankDatabase.get_cases(limit=limit, offset=offset)
    return {"success": True, "cases": cases, "limit": limit, "offset": offset}


@router.get("/cases/{case_id}", summary="Get Single Case Details", tags=["Case Intake"])
async def get_case_detail(case_id: str, current_user: str = Depends(get_current_user)):
    cases = BankDatabase.get_cases()
    case = next((c for c in cases if c["case_id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"success": True, "case": case}


# ─────────────────────────────────────────────
# Recovery Endpoints
# ─────────────────────────────────────────────

@router.get("/recovery/cases", summary="Get Active Recovery Cases", tags=["Recovery"])
async def get_recovery_cases(
    filter: Optional[str] = Query(None, description="Filter: 'unassigned' or empty for all"),
    current_user: str = Depends(get_current_user)
):
    cases = BankDatabase.get_recovery_cases(filter_status=filter)
    return {"success": True, "cases": cases}


class AssignAdvocateRequest(BaseModel):
    case_id: str
    advocate_name: str

@router.post("/recovery/assign", summary="Assign Advocate to Case", tags=["Recovery"])
async def assign_advocate(req: AssignAdvocateRequest, current_user: str = Depends(get_current_user)):
    if not req.advocate_name.strip():
        raise HTTPException(status_code=400, detail="Advocate name cannot be empty.")
    success = BankDatabase.assign_advocate(req.case_id, req.advocate_name.strip())
    if success:
        return {"success": True, "message": f"Successfully assigned '{req.advocate_name}' to case {req.case_id}"}
    return {"success": False, "message": "Failed to assign advocate."}


class UpdateStatusRequest(BaseModel):
    case_id: str
    status: str

@router.post("/recovery/update-status", summary="Update Recovery Case Status", tags=["Recovery"])
async def update_recovery_status(req: UpdateStatusRequest, current_user: str = Depends(get_current_user)):
    valid_statuses = ["Pending Review", "Assigned", "Notice Served", "Property Attached", 
                      "DRT Filing", "Settled", "Closed", "Proposal Sent", "Admitted"]
    if req.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid options: {valid_statuses}")
    success = BankDatabase.update_recovery_status(req.case_id, req.status)
    if success:
        return {"success": True, "message": f"Status updated to '{req.status}' for case {req.case_id}"}
    return {"success": False, "message": "Failed to update status."}


# ─────────────────────────────────────────────
# Risk Scoring Endpoints
# ─────────────────────────────────────────────

@router.get("/risk/portfolio", summary="Get Portfolio Risk Metrics", tags=["Risk Scoring"])
async def get_portfolio_risk(current_user: str = Depends(get_current_user)):
    return {
        "success": True,
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


@router.get("/risk/high-risk", summary="Get High Risk Cases", tags=["Risk Scoring"])
async def get_high_risk_cases(current_user: str = Depends(get_current_user)):
    return {
        "success": True,
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
            },
            {
                "borrower": "Apex Constructions",
                "exposure": "₹56.2 Cr",
                "risk_score": 84,
                "factor": "Project Stalled + Fraud Alert",
                "recommendation": "Forensic Audit + IBC Filing"
            },
            {
                "borrower": "Nova Steel Ltd.",
                "exposure": "₹28.0 Cr",
                "risk_score": 79,
                "factor": "Sector Downturn + Collateral Erosion",
                "recommendation": "Enhance Security / OTS Proposal"
            }
        ]
    }


class ScoreRequest(BaseModel):
    case_id: str
    borrower_name: str
    exposure: float
    dpd: int  # days past due
    sector: str

@router.post("/risk/score", summary="Score a Specific Borrower", tags=["Risk Scoring"])
async def score_borrower(req: ScoreRequest, current_user: str = Depends(get_current_user)):
    await asyncio.sleep(0.5)
    score = min(100, max(0, int(req.dpd * 0.4 + (req.exposure / 10000000) * 2)))
    label = "Critical" if score >= 90 else "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    return {
        "success": True,
        "case_id": req.case_id,
        "risk_score": score,
        "risk_label": label,
        "recommendation": "Initiate SARFAESI" if score >= 70 else "Issue Notice" if score >= 40 else "Monitor"
    }


# ─────────────────────────────────────────────
# Legal Notices Endpoints
# ─────────────────────────────────────────────

@router.get("/notices/tracking", summary="Get Legal Notices Tracking", tags=["Notices"])
async def get_notices_tracking(current_user: str = Depends(get_current_user)):
    notices = BankDatabase.get_notices()
    return {"success": True, "notices": notices}


class NoticeGenerateRequest(BaseModel):
    case_id: str
    notice_type: str

@router.post("/notices/generate", summary="Generate Legal Notice Draft", tags=["Notices"])
async def generate_notice(req: NoticeGenerateRequest, current_user: str = Depends(get_current_user)):
    await asyncio.sleep(1)

    notice_type_labels = {
        "SARFAESI_13_2": "SARFAESI Act, 2002 — Section 13(2) Demand Notice",
        "NI_138": "Negotiable Instruments Act — Section 138 (Cheque Bounce)",
        "ARBITRATION": "Arbitration and Conciliation Act — Arbitration Invocation Notice",
    }
    notice_label = notice_type_labels.get(req.notice_type, req.notice_type)
    deadline_date = (datetime.now() + timedelta(days=60)).strftime("%d %B %Y")
    today_str = datetime.now().strftime("%d %B %Y")

    draft_text = f"""BY REGISTERED POST WITH ACKNOWLEDGEMENT DUE
Date: {today_str}

To,
The Managing Director / Authorised Signatory
[Borrower Name corresponding to Case: {req.case_id}]
[Registered Office Address]

Sub: {notice_label}

Dear Sir/Madam,

LEGAL NOTICE

1. Under instructions from our client, JudiQ Bank Ltd. (hereinafter referred to as "the Bank"), this statutory notice is issued under the applicable provisions of Indian law.

2. Your company/entity availed financial assistance from the Bank under various credit facilities. Despite repeated requests, reminders, and personal visits, you have failed to regularize the outstanding dues, and accordingly the account has been classified as a Non-Performing Asset (NPA) as per RBI guidelines.

3. The total outstanding dues as of {today_str}, inclusive of principal, interest, and applicable charges, amounts to [EXPOSURE AMOUNT] (Rupees [AMOUNT IN WORDS] only).

4. You are hereby called upon to discharge in full your outstanding liability to the Bank within SIXTY (60) DAYS from the date of receipt of this notice (i.e., on or before {deadline_date}), failing which the Bank shall exercise its rights and remedies available under:
   - Section 13(4) of the SARFAESI Act, 2002 (enforcement of security interest)
   - The Recovery of Debts Due to Banks and Financial Institutions Act, 1993
   - All other applicable statutes and contractual provisions

5. PLEASE TAKE FURTHER NOTICE that you are hereby prohibited from transferring, alienating, or otherwise dealing with any of the secured assets specified in the security documents without the prior written consent of the Bank.

6. This notice is without prejudice to any other rights, remedies, and actions available to the Bank under the applicable law, contracts, or otherwise.

Please govern yourselves accordingly.

Issued under authority,

________________________________
Authorised Officer
JudiQ Bank Ltd.
Recovery & Litigation Department
Date: {today_str}

[Document ID: {req.case_id}-{req.notice_type}-{today_str.replace(' ', '')}]
"""

    notice_id = f"NT-{str(uuid.uuid4())[:6].upper()}"
    BankDatabase.add_notice(
        notice_id, req.case_id, "Borrower (Auto-Fetched)",
        notice_label, "Drafted", deadline_date, draft_text.strip()
    )

    return {
        "success": True,
        "notice_id": notice_id,
        "draft_content": draft_text.strip(),
        "deadline": deadline_date
    }


@router.get("/notices/{notice_id}/content", summary="Get Notice Draft Content", tags=["Notices"])
async def get_notice_content(notice_id: str, current_user: str = Depends(get_current_user)):
    content = BankDatabase.get_notice_content(notice_id)
    if not content:
        raise HTTPException(status_code=404, detail="Notice not found")
    return {"success": True, "notice_id": notice_id, "content": content}


class UpdateNoticeStatusRequest(BaseModel):
    notice_id: str
    status: str

@router.post("/notices/update-status", summary="Update Notice Status", tags=["Notices"])
async def update_notice_status(req: UpdateNoticeStatusRequest, current_user: str = Depends(get_current_user)):
    valid = ["Drafted", "Dispatched", "Served", "Acknowledged", "Reply Received", "No Reply"]
    if req.status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {valid}")
    success = BankDatabase.update_notice_status(req.notice_id, req.status)
    return {"success": success, "message": f"Notice {req.notice_id} status updated to '{req.status}'"}


# ─────────────────────────────────────────────
# Litigation Endpoints
# ─────────────────────────────────────────────

@router.get("/litigation/cases", summary="Get Litigation Cases", tags=["Litigation"])
async def get_litigation_cases(current_user: str = Depends(get_current_user)):
    cases = BankDatabase.get_litigation_cases()
    return {"success": True, "cases": cases}


@router.get("/litigation/kpis", summary="Get Litigation KPIs", tags=["Litigation"])
async def get_litigation_kpis(current_user: str = Depends(get_current_user)):
    kpis = BankDatabase.get_litigation_kpis()
    return {"success": True, "kpis": kpis}


class UpdateLitigationHearingRequest(BaseModel):
    case_id: str
    next_hearing: str
    status: str

@router.post("/litigation/update-hearing", summary="Update Hearing Date", tags=["Litigation"])
async def update_hearing(req: UpdateLitigationHearingRequest, current_user: str = Depends(get_current_user)):
    # In a full implementation this would update the DB
    return {"success": True, "message": f"Hearing for {req.case_id} updated to {req.next_hearing}"}


# ─────────────────────────────────────────────
# Compliance Endpoints
# ─────────────────────────────────────────────

@router.get("/compliance/items", summary="Get Compliance Items", tags=["Compliance"])
async def get_compliance_items(current_user: str = Depends(get_current_user)):
    items = BankDatabase.get_compliance_items()
    return {"success": True, "items": items}


@router.get("/compliance/kpis", summary="Get Compliance KPIs", tags=["Compliance"])
async def get_compliance_kpis(current_user: str = Depends(get_current_user)):
    kpis = BankDatabase.get_compliance_kpis()
    return {"success": True, "kpis": kpis}


@router.get("/compliance/audit-log", summary="Get Audit Log", tags=["Compliance"])
async def get_audit_log(current_user: str = Depends(get_current_user)):
    # Mock audit log entries
    return {
        "success": True,
        "audit_log": [
            {"timestamp": "2026-07-20 18:45", "officer": "Admin User", "action": "Generated SARFAESI Notice", "case_id": "REC-2023-001"},
            {"timestamp": "2026-07-20 17:22", "officer": "Admin User", "action": "Assigned Advocate", "case_id": "REC-2023-004"},
            {"timestamp": "2026-07-19 11:00", "officer": "Admin User", "action": "Uploaded Case Document", "case_id": "CASE-XA3B9F1C"},
            {"timestamp": "2026-07-18 09:15", "officer": "Admin User", "action": "Reviewed Risk Score", "case_id": "LIT-2023-0891"},
        ]
    }


# ─────────────────────────────────────────────
# Notifications Endpoints
# ─────────────────────────────────────────────

@router.get("/notifications", summary="Get Notifications", tags=["Notifications"])
async def get_notifications(current_user: str = Depends(get_current_user)):
    notifications = BankDatabase.get_notifications()
    unread = sum(1 for n in notifications if not n["is_read"])
    return {"success": True, "unread_count": unread, "notifications": notifications}


class MarkReadRequest(BaseModel):
    notification_id: int

@router.post("/notifications/mark-read", summary="Mark Notification as Read", tags=["Notifications"])
async def mark_notification_read(req: MarkReadRequest, current_user: str = Depends(get_current_user)):
    success = BankDatabase.mark_notification_read(req.notification_id)
    return {"success": success}


# ─────────────────────────────────────────────
# Settings / Profile Endpoint
# ─────────────────────────────────────────────

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

@router.post("/settings/update-profile", summary="Update Officer Profile", tags=["Settings"])
async def update_profile(req: UpdateProfileRequest, current_user: str = Depends(get_current_user)):
    # In full implementation: update DB record
    # For now we validate and confirm
    if req.new_password and len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")
    return {"success": True, "message": "Profile updated successfully."}


@router.get("/settings/system-info", summary="Get System Info", tags=["Settings"])
async def get_system_info(current_user: str = Depends(get_current_user)):
    return {
        "success": True,
        "system": {
            "version": "12.5.0-ENTERPRISE",
            "backend": "FastAPI + SQLite",
            "frontend": "Vanilla JS + Chart.js",
            "ai_engine": "JudiQ Reasoning Engine v12",
            "uptime": "Online",
            "last_db_backup": datetime.now().strftime("%Y-%m-%d"),
            "api_base_url": "http://127.0.0.1:8000/api/v1/bank"
        }
    }


# ─────────────────────────────────────────────
# Export / Report Endpoints
# ─────────────────────────────────────────────

@router.get("/export/summary", summary="Export Summary Report", tags=["Export"])
async def export_summary(current_user: str = Depends(get_current_user)):
    kpis = BankDatabase.get_dashboard_kpis()
    recovery = BankDatabase.get_recovery_cases()
    litigation = BankDatabase.get_litigation_cases()
    comp_kpis = BankDatabase.get_compliance_kpis()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "success": True,
        "report_type": "Executive Summary",
        "generated_at": timestamp,
        "generated_by": current_user,
        "kpis": kpis,
        "recovery_summary": {
            "total_cases": len(recovery),
            "unassigned": sum(1 for c in recovery if c["advocate"] == "Unassigned")
        },
        "litigation_summary": {
            "total_cases": len(litigation),
            "upcoming_hearings": sum(1 for c in litigation if c.get("next_hearing"))
        },
        "compliance_summary": comp_kpis
    }


# ─────────────────────────────────────────────
# Legacy Portfolio Endpoint (kept for compat)
# ─────────────────────────────────────────────

@router.get("/portfolio", summary="Get Portfolio Intelligence", tags=["Dashboard"])
async def get_portfolio_intelligence(current_user: str = Depends(get_current_user)):
    return {
        "success": True,
        "regions": ["North", "South", "East", "West"],
        "npa_distribution": [1200, 850, 600, 1600]
    }

import pandas as pd
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

@router.post("/cases/bulk-upload", summary="Bulk Upload Cases via Excel/CSV")
async def bulk_upload_cases(file: UploadFile = File(...)):
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    elif file.filename.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(io.BytesIO(contents))
    else:
        raise HTTPException(status_code=400, detail="Invalid file format. Use CSV or Excel.")
    
    cases_list = []
    for _, row in df.iterrows():
        cases_list.append({
            "case_id": str(row.get("case_id", f"CASE-{str(uuid.uuid4())[:8].upper()}")),
            "borrower": str(row.get("borrower", "Unknown")),
            "exposure": float(row.get("exposure", 0.0)),
            "status": str(row.get("status", "OCR Completed")),
            "risk": str(row.get("risk", "High"))
        })
        
    added = BankDatabase.bulk_add_cases(cases_list)
    return {"success": True, "message": f"Successfully processed and added {added} cases."}

@router.get("/notices/export/pdf", summary="Export Notices to PDF")
async def export_notices_pdf():
    notices = BankDatabase.get_notices()
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "JudiQ Bank Edition - Legal Notices Report")
    
    c.setFont("Helvetica", 10)
    y = height - 80
    
    for notice in notices:
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50
            
        c.drawString(50, y, f"Notice ID: {notice['notice_id']} | Borrower: {notice['borrower']}")
        c.drawString(50, y - 15, f"Type: {notice['type']} | Status: {notice['status']} | Deadline: {notice['deadline']}")
        y -= 40
        
    c.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=notices_report.pdf"})

@router.get("/recovery/export/excel", summary="Export Recovery Cases to Excel")
async def export_recovery_excel():
    cases = BankDatabase.get_recovery_cases()
    df = pd.DataFrame(cases)
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Recovery Cases')
        
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=recovery_cases.xlsx"})

class AddAdvocateRequest(BaseModel):
    name: str
    specialization: str
    success_rate: str
    active_cases: int
    billing_rate: str

@router.post("/advocates/add", summary="Onboard New Advocate", tags=["Advocates"])
async def onboard_advocate(req: AddAdvocateRequest, current_user: str = Depends(require_role("Recovery Head"))):
    adv_id = f"ADV-{str(uuid.uuid4())[:6].upper()}"
    BankDatabase.add_advocate(adv_id, req.name, req.specialization, req.success_rate, req.active_cases, req.billing_rate)
    return {"success": True, "message": f"Successfully onboarded {req.name}"}

@router.get("/advocates", summary="Get Advocate Directory", tags=["Advocates"])
async def get_advocates(current_user: str = Depends(get_current_user)):
    advocates = BankDatabase.get_advocates()
    return {"success": True, "advocates": advocates}

# ─────────────────────────────────────────────
# Settings / Configuration Endpoints
# ─────────────────────────────────────────────

@router.get("/settings", summary="Get Bank Configurations", tags=["Settings"])
async def get_settings(current_user: str = Depends(get_current_user)):
    configs = BankDatabase.get_configurations()
    return {"success": True, "settings": configs}

class UpdateSettingRequest(BaseModel):
    key: str
    value: str

@router.post("/settings/update", summary="Update Bank Configuration", tags=["Settings"])
async def update_setting(req: UpdateSettingRequest, current_user: str = Depends(require_role("Admin"))):
    BankDatabase.update_configuration(req.key, req.value)
    return {"success": True, "message": f"Setting {req.key} updated successfully."}

# ─────────────────────────────────────────────
# CBS (Core Banking System) Integration Endpoints
# ─────────────────────────────────────────────

class CBSCasePayload(BaseModel):
    account_number: str
    borrower_name: str
    outstanding_balance: float
    days_past_due: int
    asset_classification: str
    region: Optional[str] = "Unknown"

class CBSIngestRequest(BaseModel):
    batch_id: str
    timestamp: str
    records: List[CBSCasePayload]

@router.post("/cbs/ingest", summary="Ingest NPA Accounts from CBS", tags=["Integration"])
async def ingest_cbs_data(req: CBSIngestRequest, api_key_valid: bool = Depends(verify_cbs_api_key)):
    cases_list = []
    for record in req.records:
        risk = "Low"
        if record.days_past_due > 90:
            risk = "High"
        if record.days_past_due > 180:
            risk = "Critical"
            
        cases_list.append({
            "case_id": record.account_number,
            "borrower": record.borrower_name,
            "exposure": record.outstanding_balance,
            "status": "Newly Ingested",
            "risk": risk
        })
    
    added_count = BankDatabase.bulk_add_cases(cases_list)
    
    conn = BankDatabase.get_connection()
    try:
        p = BankDatabase.get_dialect_placeholder()
        conn.execute(
            f"INSERT INTO bank_notifications (title, message, type, created_at) VALUES ({p}, {p}, {p}, {p})",
            (f"CBS Batch {req.batch_id} Processed", f"Successfully ingested {added_count} NPA accounts from Core Banking System.", "success", datetime.now().isoformat())
        )
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()
    
    return {
        "success": True,
        "message": f"Batch {req.batch_id} processed. {added_count} accounts imported.",
        "records_received": len(req.records),
        "records_imported": added_count
    }

# ─────────────────────────────────────────────
# Backup & Restore Endpoints
# ─────────────────────────────────────────────
from fastapi.responses import FileResponse
import shutil

@router.get("/admin/backup", summary="Download Database Backup", tags=["Admin"])
async def download_backup(current_user: str = Depends(require_role("Admin"))):
    db_path = "bank_data.db"
    backup_path = "bank_data_backup.db"
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        return FileResponse(backup_path, filename=f"judiq_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    raise HTTPException(status_code=404, detail="Database not found")

@router.post("/admin/restore", summary="Restore Database Backup", tags=["Admin"])
async def restore_backup(file: UploadFile = File(...), current_user: str = Depends(require_role("Admin"))):
    db_path = "bank_data.db"
    contents = await file.read()
    with open(db_path, "wb") as f:
        f.write(contents)
    return {"success": True, "message": "Database successfully restored. A restart may be required."}

# ─────────────────────────────────────────────
# Customer Validation / Feedback Endpoint
# ─────────────────────────────────────────────
class FeedbackRequest(BaseModel):
    type: str
    message: str

@router.post("/feedback", summary="Submit User Feedback", tags=["Feedback"])
async def submit_feedback(req: FeedbackRequest, current_user: str = Depends(get_current_user)):
    conn = BankDatabase.get_connection()
    try:
        p = BankDatabase.get_dialect_placeholder()
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS bank_feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, type TEXT, message TEXT, created_at TEXT)"
        )
        conn.execute(
            f"INSERT INTO bank_feedback (user, type, message, created_at) VALUES ({p}, {p}, {p}, {p})",
            (current_user, req.type, req.message, datetime.now().isoformat())
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to save feedback.")
    finally:
        conn.close()
    return {"success": True, "message": "Thank you for your feedback!"}
