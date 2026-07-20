import sqlite3
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from session import DatabaseManager


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _hash_password(password: str) -> str:
    return pwd_context.hash(password)

def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class BankDatabase:
    @staticmethod
    def init_db():
        conn = None
        try:
            conn = DatabaseManager.get_connection()
            serial_primary = (
                "SERIAL PRIMARY KEY"
                if DatabaseManager._active_dialect == "postgres"
                else "INTEGER PRIMARY KEY AUTOINCREMENT"
            )
            cursor = conn.cursor()

            # Officers table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS bank_officers (
                    id {serial_primary},
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'Officer',
                    created_at TEXT
                )
            """)

            # Intake Cases table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS bank_cases (
                    id {serial_primary},
                    case_id TEXT UNIQUE NOT NULL,
                    borrower TEXT NOT NULL,
                    exposure REAL NOT NULL,
                    status TEXT NOT NULL,
                    risk TEXT NOT NULL,
                    created_at TEXT
                )
            """)

            # Recovery Workflow table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS bank_recovery (
                    id {serial_primary},
                    case_id TEXT UNIQUE NOT NULL,
                    borrower TEXT NOT NULL,
                    exposure REAL NOT NULL,
                    strategy TEXT NOT NULL,
                    status TEXT NOT NULL,
                    advocate TEXT DEFAULT 'Unassigned',
                    created_at TEXT
                )
            """)

            # Legal Notices table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS bank_notices (
                    id {serial_primary},
                    notice_id TEXT UNIQUE NOT NULL,
                    case_id TEXT NOT NULL,
                    borrower TEXT NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    deadline TEXT NOT NULL,
                    draft_content TEXT,
                    created_at TEXT
                )
            """)

            # Advocates table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS bank_advocates (
                    id {serial_primary},
                    advocate_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    specialization TEXT NOT NULL,
                    success_rate TEXT NOT NULL,
                    active_cases INTEGER NOT NULL,
                    billing_rate TEXT NOT NULL,
                    created_at TEXT
                )
            """)

            # Litigation Cases table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS bank_litigation (
                    id {serial_primary},
                    case_id TEXT UNIQUE NOT NULL,
                    borrower TEXT NOT NULL,
                    exposure REAL NOT NULL,
                    court TEXT NOT NULL,
                    case_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    next_hearing TEXT,
                    advocate TEXT DEFAULT 'Unassigned',
                    created_at TEXT
                )
            """)

            # Compliance Violations table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS bank_compliance (
                    id {serial_primary},
                    violation_id TEXT UNIQUE NOT NULL,
                    regulation TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    due_date TEXT,
                    created_at TEXT
                )
            """)

            # Notifications table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS bank_notifications (
                    id {serial_primary},
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT DEFAULT 'info',
                    is_read INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)

            # Configurations table
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS bank_configurations (
                    id {serial_primary},
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TEXT
                )
            """)

            conn.commit()

            # Seed default admin
            BankDatabase._seed_defaults(conn)

        except Exception as e:
            print(f"Failed to init bank db: {e}")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def _seed_defaults(conn):
        """Seed default admin user and sample data if DB is empty."""
        p = DatabaseManager.get_dialect_placeholder()
        cursor = conn.cursor()

        # Seed admin user
        cursor.execute("SELECT COUNT(*) FROM bank_officers")
        if cursor.fetchone()[0] == 0:
            hashed = _hash_password("password")
            conn.execute(
                f"INSERT INTO bank_officers (name, email, password, role, created_at) VALUES ({p}, {p}, {p}, {p}, {p})",
                ("Admin User", "admin", hashed, "Recovery Head", datetime.now().isoformat())
            )
            conn.commit()

        # Seed sample intake cases
        cursor.execute("SELECT COUNT(*) FROM bank_cases")
        if cursor.fetchone()[0] == 0:
            sample_cases = [
                ("CASE-A1B2C3D4", "Omega Textiles Ltd.", 84500000, "OCR Completed", "High"),
                ("CASE-E5F6G7H8", "Delta Infra Corp.", 145000000, "OCR Completed", "High"),
                ("CASE-I9J0K1L2", "Gamma Pharma Ltd.", 37000000, "Under Review", "Medium"),
                ("CASE-M3N4O5P6", "Zeta Logistics", 56000000, "OCR Completed", "Medium"),
                ("CASE-Q7R8S9T0", "Kappa Exports", 55000000, "Pending Classification", "Low"),
            ]
            for c in sample_cases:
                try:
                    conn.execute(
                        f"INSERT INTO bank_cases (case_id, borrower, exposure, status, risk, created_at) VALUES ({p},{p},{p},{p},{p},{p})",
                        (*c, datetime.now().isoformat())
                    )
                except Exception:
                    pass
            conn.commit()

        # Seed sample recovery cases
        cursor.execute("SELECT COUNT(*) FROM bank_recovery")
        if cursor.fetchone()[0] == 0:
            sample_recovery = [
                ("REC-2023-001", "Omega Textiles Ltd.", 84500000, "SARFAESI", "Notice Served", "Adv. Sharma"),
                ("REC-2023-002", "Epsilon Retail Pvt.", 23000000, "DRT Filing", "Pending Hearing", "Adv. Verma"),
                ("REC-2023-003", "Delta Infra Corp.", 145000000, "SARFAESI", "Property Attached", "Adv. Patel"),
                ("REC-2023-004", "Gamma Pharma Ltd.", 37000000, "OTS Settlement", "Proposal Sent", "Unassigned"),
                ("REC-2023-005", "Zeta Logistics", 56000000, "IBC/NCLT", "Admitted", "Adv. Iyer"),
            ]
            for r in sample_recovery:
                try:
                    conn.execute(
                        f"INSERT INTO bank_recovery (case_id, borrower, exposure, strategy, status, advocate, created_at) VALUES ({p},{p},{p},{p},{p},{p},{p})",
                        (*r, datetime.now().isoformat())
                    )
                except Exception:
                    pass
            conn.commit()

        # Seed sample litigation cases
        cursor.execute("SELECT COUNT(*) FROM bank_litigation")
        if cursor.fetchone()[0] == 0:
            sample_litigation = [
                ("LIT-2023-0891", "Alpha Industries Ltd.", 340000000, "DRT Mumbai", "Recovery Suit", "Under Examination", "2026-08-15", "Adv. Kapoor"),
                ("LIT-2023-0924", "Beta Steel Works", 125000000, "High Court Delhi", "Writ Petition", "Arguments Ongoing", "2026-08-22", "Adv. Singh"),
                ("LIT-2023-1001", "Sigma Hotels Pvt.", 78000000, "DRT Bangalore", "OA Filing", "Summons Issued", "2026-09-01", "Adv. Reddy"),
                ("LIT-2023-1045", "Kappa Exports", 55000000, "NCLT Mumbai", "IBC Petition", "Admission Hearing", "2026-08-18", "Unassigned"),
                ("LIT-2023-1102", "Mu Realty Ltd.", 450000000, "Supreme Court", "SLP", "Listed", "2026-09-10", "Adv. Mehta"),
            ]
            for l in sample_litigation:
                try:
                    conn.execute(
                        f"INSERT INTO bank_litigation (case_id, borrower, exposure, court, case_type, status, next_hearing, advocate, created_at) VALUES ({p},{p},{p},{p},{p},{p},{p},{p},{p})",
                        (*l, datetime.now().isoformat())
                    )
                except Exception:
                    pass
            conn.commit()

        # Seed sample compliance items
        cursor.execute("SELECT COUNT(*) FROM bank_compliance")
        if cursor.fetchone()[0] == 0:
            sample_compliance = [
                ("COMP-001", "RBI Master Direction", "Quarterly NPA review not submitted", "High", "Open", "2026-08-01"),
                ("COMP-002", "SARFAESI Act S.13(2)", "60-day reply window for 3 notices expired", "Critical", "Action Required", "2026-07-25"),
                ("COMP-003", "Basel III", "Capital adequacy ratio below threshold", "Medium", "Under Review", "2026-09-30"),
                ("COMP-004", "KYC/AML", "Re-KYC pending for 18 accounts", "High", "In Progress", "2026-08-15"),
                ("COMP-005", "FEMA", "ECB reporting due for overseas borrowing", "Low", "Compliant", "2026-10-01"),
            ]
            for c in sample_compliance:
                try:
                    conn.execute(
                        f"INSERT INTO bank_compliance (violation_id, regulation, description, severity, status, due_date, created_at) VALUES ({p},{p},{p},{p},{p},{p},{p})",
                        (*c, datetime.now().isoformat())
                    )
                except Exception:
                    pass
            conn.commit()

        # Seed notifications
        cursor.execute("SELECT COUNT(*) FROM bank_notifications")
        if cursor.fetchone()[0] == 0:
            sample_notifications = [
                ("Limitation Alert", "14 cases approaching limitation period in 30 days.", "alert"),
                ("Settlement Opportunity", "AI recommends OTS for 45 SME loans.", "info"),
                ("New Case Uploaded", "CASE-XA3B9F1C processed via OCR engine.", "success"),
            ]
            for n in sample_notifications:
                conn.execute(
                    f"INSERT INTO bank_notifications (title, message, type, created_at) VALUES ({p},{p},{p},{p})",
                    (*n, datetime.now().isoformat())
                )
            conn.commit()

        # Seed configurations
        cursor.execute("SELECT COUNT(*) FROM bank_configurations")
        if cursor.fetchone()[0] == 0:
            configs = [
                ("SARFAESI_NOTICE_DAYS", "60"),
                ("RISK_SCORE_THRESHOLD_HIGH", "80"),
                ("RISK_SCORE_THRESHOLD_CRITICAL", "95"),
                ("AUTO_ASSIGN_ADVOCATE", "true")
            ]
            for key, val in configs:
                conn.execute(
                    f"INSERT INTO bank_configurations (key, value, updated_at) VALUES ({p},{p},{p})",
                    (key, val, datetime.now().isoformat())
                )
            conn.commit()

    @staticmethod
    def create_officer(name: str, email: str, password: str) -> bool:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            hashed = _hash_password(password)
            conn.execute(
                f"INSERT INTO bank_officers (name, email, password, role, created_at) VALUES ({p}, {p}, {p}, {p}, {p})",
                (name, email, hashed, "Officer", datetime.now().isoformat())
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    @staticmethod
    def verify_officer(username: str, password: str) -> Optional[Dict]:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, name, email, role, password FROM bank_officers WHERE email = {p}",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                stored_hash = row[4]
                if _verify_password(password, stored_hash):
                    return {"id": row[0], "name": row[1], "email": row[2], "role": row[3]}
            return None
        finally:
            conn.close()

    @staticmethod
    def get_officer_info(username: str) -> Optional[Dict]:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, name, email, role FROM bank_officers WHERE email = {p}",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "email": row[2], "role": row[3]}
            return None
        finally:
            conn.close()

    @staticmethod
    def add_case(case_id: str, borrower: str, exposure: float, status: str, risk: str):
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(
                f"INSERT INTO bank_cases (case_id, borrower, exposure, status, risk, created_at) VALUES ({p}, {p}, {p}, {p}, {p}, {p})",
                (case_id, borrower, exposure, status, risk, datetime.now().isoformat())
            )
            conn.execute(
                f"INSERT OR IGNORE INTO bank_recovery (case_id, borrower, exposure, strategy, status, created_at) VALUES ({p}, {p}, {p}, {p}, {p}, {p})",
                (case_id, borrower, exposure, "SARFAESI", "Pending Review", datetime.now().isoformat())
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def bulk_add_cases(cases_list: List[Dict[str, Any]]) -> int:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        added = 0
        try:
            for case in cases_list:
                try:
                    case_id = case.get("case_id")
                    borrower = case.get("borrower")
                    exposure = case.get("exposure")
                    status = case.get("status", "OCR Completed")
                    risk = case.get("risk", "High")
                    
                    conn.execute(f"INSERT INTO bank_cases (case_id, borrower, exposure, status, risk, created_at) VALUES ({p}, {p}, {p}, {p}, {p}, {p})", 
                                 (case_id, borrower, exposure, status, risk, datetime.now().isoformat()))
                    # Auto-add to recovery workflow
                    conn.execute(f"INSERT INTO bank_recovery (case_id, borrower, exposure, strategy, status, created_at) VALUES ({p}, {p}, {p}, {p}, {p}, {p})", 
                                 (case_id, borrower, exposure, "SARFAESI", "Pending Review", datetime.now().isoformat()))
                    added += 1
                except sqlite3.IntegrityError:
                    continue  # Skip existing
            conn.commit()
            return added
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_cases(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT case_id, borrower, exposure, status, risk FROM bank_cases ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
            rows = cursor.fetchall()
            return [
                {
                    "case_id": r[0], "borrower": r[1],
                    "exposure": f"₹{r[2]/10000000:.1f} Cr" if r[2] else "N/A",
                    "status": r[3], "risk": r[4]
                }
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def get_recovery_cases(filter_status: str = None) -> List[Dict[str, Any]]:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            cursor = conn.cursor()
            if filter_status and filter_status == "unassigned":
                cursor.execute("SELECT case_id, borrower, exposure, strategy, status, advocate FROM bank_recovery WHERE advocate = 'Unassigned' ORDER BY id DESC")
            else:
                cursor.execute("SELECT case_id, borrower, exposure, strategy, status, advocate FROM bank_recovery ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                {
                    "case_id": r[0], "borrower": r[1],
                    "exposure": f"₹{r[2]/10000000:.1f} Cr" if r[2] else "N/A",
                    "strategy": r[3], "status": r[4], "advocate": r[5]
                }
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def assign_advocate(case_id: str, advocate_name: str) -> bool:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(f"UPDATE bank_recovery SET advocate = {p}, status = 'Assigned' WHERE case_id = {p}", (advocate_name, case_id))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def update_recovery_status(case_id: str, new_status: str) -> bool:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(f"UPDATE bank_recovery SET status = {p} WHERE case_id = {p}", (new_status, case_id))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def add_notice(notice_id: str, case_id: str, borrower: str, n_type: str, status: str, deadline: str, draft: str):
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(
                f"INSERT INTO bank_notices (notice_id, case_id, borrower, type, status, deadline, draft_content, created_at) VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})",
                (notice_id, case_id, borrower, n_type, status, deadline, draft, datetime.now().isoformat())
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def update_notice_status(notice_id: str, new_status: str) -> bool:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(f"UPDATE bank_notices SET status = {p} WHERE notice_id = {p}", (new_status, notice_id))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def get_notices() -> List[Dict[str, Any]]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT notice_id, borrower, type, status, deadline FROM bank_notices ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                {"notice_id": r[0], "borrower": r[1], "type": r[2], "status": r[3], "deadline": r[4]}
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def get_notice_content(notice_id: str) -> Optional[str]:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT draft_content FROM bank_notices WHERE notice_id = {p}", (notice_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    @staticmethod
    def get_litigation_cases() -> List[Dict[str, Any]]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT case_id, borrower, exposure, court, case_type, status, next_hearing, advocate FROM bank_litigation ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                {
                    "case_id": r[0], "borrower": r[1],
                    "exposure": f"₹{r[2]/10000000:.1f} Cr" if r[2] else "N/A",
                    "court": r[3], "case_type": r[4], "status": r[5],
                    "next_hearing": r[6], "advocate": r[7]
                }
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def get_litigation_kpis() -> Dict[str, Any]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(exposure) FROM bank_litigation")
            r = cursor.fetchone()
            total = r[0] or 0
            exposure = (r[1] or 0) / 10000000

            cursor.execute("SELECT COUNT(*) FROM bank_litigation WHERE next_hearing IS NOT NULL AND next_hearing != ''")
            upcoming = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM bank_litigation WHERE advocate = 'Unassigned'")
            unassigned = cursor.fetchone()[0] or 0

            return {
                "total_cases": total,
                "total_exposure_cr": round(exposure, 1),
                "upcoming_hearings": upcoming,
                "unassigned_cases": unassigned
            }
        finally:
            conn.close()

    @staticmethod
    def get_compliance_items() -> List[Dict[str, Any]]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT violation_id, regulation, description, severity, status, due_date FROM bank_compliance ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                {
                    "violation_id": r[0], "regulation": r[1], "description": r[2],
                    "severity": r[3], "status": r[4], "due_date": r[5]
                }
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def get_compliance_kpis() -> Dict[str, Any]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM bank_compliance")
            total = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM bank_compliance WHERE status IN ('Open', 'Action Required')")
            open_items = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(*) FROM bank_compliance WHERE severity = 'Critical'")
            critical = cursor.fetchone()[0] or 0
            score = max(0, 100 - (open_items * 8) - (critical * 15))
            return {
                "compliance_score": score,
                "total_items": total,
                "open_items": open_items,
                "critical_items": critical
            }
        finally:
            conn.close()

    @staticmethod
    def get_notifications() -> List[Dict[str, Any]]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, message, type, is_read, created_at FROM bank_notifications ORDER BY id DESC LIMIT 20")
            rows = cursor.fetchall()
            return [
                {"id": r[0], "title": r[1], "message": r[2], "type": r[3], "is_read": bool(r[4]), "created_at": r[5]}
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def mark_notification_read(notif_id: int) -> bool:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(f"UPDATE bank_notifications SET is_read = 1 WHERE id = {p}", (notif_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def search_cases(query: str) -> List[Dict[str, Any]]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            like = f"%{query}%"
            cursor.execute(
                "SELECT case_id, borrower, exposure, status, 'intake' as source FROM bank_cases WHERE borrower LIKE ? OR case_id LIKE ? "
                "UNION ALL "
                "SELECT case_id, borrower, exposure, status, 'recovery' as source FROM bank_recovery WHERE borrower LIKE ? OR case_id LIKE ? "
                "UNION ALL "
                "SELECT case_id, borrower, exposure, status, 'litigation' as source FROM bank_litigation WHERE borrower LIKE ? OR case_id LIKE ? "
                "LIMIT 20",
                (like, like, like, like, like, like)
            )
            rows = cursor.fetchall()
            return [
                {
                    "case_id": r[0], "borrower": r[1],
                    "exposure": f"₹{r[2]/10000000:.1f} Cr" if r[2] else "N/A",
                    "status": r[3], "source": r[4]
                }
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def get_dashboard_kpis() -> Dict[str, Any]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(exposure), COUNT(*) FROM bank_cases")
            row = cursor.fetchone()
            total_exp = (row[0] or 0) / 10000000  # convert to Cr
            total_cases = row[1] or 0
            
            return {
                "total_exposure_cr": round(total_exp, 1),
                "exposure_trend": -1.2,
                "active_litigation_cases": total_cases,
                "cases_trend": 0.5,
                "compliance_score_percent": 99.1,
                "compliance_trend": 0.2,
                "predicted_recovery_cr": round(total_exp * 0.25, 1)  # mockup calculation
            }
        finally:
            conn.close()

    @staticmethod
    def add_advocate(adv_id: str, name: str, spec: str, success: str, active: int, billing: str):
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(f"INSERT INTO bank_advocates (advocate_id, name, specialization, success_rate, active_cases, billing_rate, created_at) VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})", 
                         (adv_id, name, spec, success, active, billing, datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_advocates() -> List[Dict[str, Any]]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT advocate_id, name, specialization, success_rate, active_cases, billing_rate FROM bank_advocates ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                {"advocate_id": r[0], "name": r[1], "specialization": r[2], "success_rate": r[3], "active_cases": r[4], "billing_rate": r[5]}
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def get_configurations() -> Dict[str, str]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM bank_configurations")
            rows = cursor.fetchall()
            return {r[0]: r[1] for r in rows}
        finally:
            conn.close()

    @staticmethod
    def update_configuration(key: str, value: str):
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            # SQLite does not support INSERT OR REPLACE in all contexts if not using unique key correctly,
            # but since key is UNIQUE, we can use INSERT OR REPLACE.
            conn.execute(f"INSERT OR REPLACE INTO bank_configurations (id, key, value, updated_at) VALUES ((SELECT id FROM bank_configurations WHERE key = {p}), {p}, {p}, {p})", 
                         (key, key, value, datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
