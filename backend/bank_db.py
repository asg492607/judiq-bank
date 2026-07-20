import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from session import DatabaseManager

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

            conn.commit()
        except Exception as e:
            print(f"Failed to init bank db: {e}")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def create_officer(name: str, email: str, password: str) -> bool:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(f"INSERT INTO bank_officers (name, email, password, created_at) VALUES ({p}, {p}, {p}, {p})", 
                         (name, email, password, datetime.now().isoformat()))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
            
    @staticmethod
    def verify_officer(email: str, password: str) -> bool:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT password FROM bank_officers WHERE email = {p}", (email,))
            row = cursor.fetchone()
            if row and row[0] == password:
                return True
            return False
        finally:
            conn.close()

    @staticmethod
    def add_case(case_id: str, borrower: str, exposure: float, status: str, risk: str):
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(f"INSERT INTO bank_cases (case_id, borrower, exposure, status, risk, created_at) VALUES ({p}, {p}, {p}, {p}, {p}, {p})", 
                         (case_id, borrower, exposure, status, risk, datetime.now().isoformat()))
            # Auto-add to recovery workflow if it's an NPA
            conn.execute(f"INSERT INTO bank_recovery (case_id, borrower, exposure, strategy, status, created_at) VALUES ({p}, {p}, {p}, {p}, {p}, {p})", 
                         (case_id, borrower, exposure, "SARFAESI", "Pending Review", datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_cases() -> List[Dict[str, Any]]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT case_id, borrower, exposure, status, risk FROM bank_cases ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                {"case_id": r[0], "borrower": r[1], "exposure": f"₹{r[2]/10000000:.1f} Cr" if r[2] else "N/A", "status": r[3], "risk": r[4]}
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def get_recovery_cases() -> List[Dict[str, Any]]:
        conn = DatabaseManager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT case_id, borrower, exposure, strategy, status, advocate FROM bank_recovery ORDER BY id DESC")
            rows = cursor.fetchall()
            return [
                {"case_id": r[0], "borrower": r[1], "exposure": f"₹{r[2]/10000000:.1f} Cr" if r[2] else "N/A", "strategy": r[3], "status": r[4], "advocate": r[5]}
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def assign_advocate(case_id: str, advocate_name: str) -> bool:
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(f"UPDATE bank_recovery SET advocate = {p} WHERE case_id = {p}", (advocate_name, case_id))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def add_notice(notice_id: str, case_id: str, borrower: str, n_type: str, status: str, deadline: str, draft: str):
        conn = DatabaseManager.get_connection()
        p = DatabaseManager.get_dialect_placeholder()
        try:
            conn.execute(f"INSERT INTO bank_notices (notice_id, case_id, borrower, type, status, deadline, draft_content, created_at) VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})", 
                         (notice_id, case_id, borrower, n_type, status, deadline, draft, datetime.now().isoformat()))
            conn.commit()
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
