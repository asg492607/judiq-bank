import sys
from strategy_engine import StrategyEngine
from scoring_engine import ScoringEngineV12
from decision_support_engine import DecisionSupportEngine
from draft_engine import DraftEngine

def test_engines():
    print("Testing JUDIQ 2026 Updates...")
    
    # Mock data to trigger new rules
    case_data = {
        "cheque_present": True,
        "dishonour_memo": True,
        "notice_sent": True,
        "debt_proven": True,
        "amount": 600000, # Trigger Sushil Kumar
        "loan_via_bank": False,
        "complainant_itr_available": False,
        "dishonour_reason": "signature mismatch", # Trigger signature mismatch trap
        "notice_mode": "email", # Trigger email trap
        "communication_records": True, # Trigger BSA Section 63
        "accused_type": "Pvt Ltd/Ltd Company",
        "directors_named": True,
        "director_names": "John Doe",
        "director_roles": "Chief Financial Officer" # Trigger specific roles
    }
    concepts = [
        {"concept": "security_cheque", "confidence": 0.9},
        {"concept": "financial_capacity_risk", "confidence": 0.8}
    ]
    contradictions = []
    evidence_assessment = {}

    try:
        # Test Scoring Engine
        print("\n--- SCORING ENGINE ---")
        score_result = ScoringEngineV12.calculate_score_with_trace(case_data, concepts, contradictions, evidence_assessment)
        for trace in score_result["reasoning_trace"]:
            print(trace)

        # Test Decision Support Engine
        print("\n--- DECISION SUPPORT ENGINE ---")
        risks = DecisionSupportEngine.identify_risks_and_rebuttals(concepts, case_data)
        for risk in risks:
            print(f"Risk: {risk['risk']} | Rebuttal: {risk['rebuttal']}")

        gaps = DecisionSupportEngine.suggest_evidence_gaps(case_data)
        for gap in gaps:
            print(f"Gap: {gap}")

        # Test Strategy Engine
        print("\n--- STRATEGY ENGINE ---")
        strat_result = StrategyEngine.generate_litigation_map(case_data, score_result["score"], concepts)
        print("Prosecution Leverage:", strat_result["prosecution_map"]["statutory_leverage"])
        print("Defence Landmark:", strat_result["defence_map"]["landmark_defence"])

        # Test Draft Engine
        print("\n--- DRAFT ENGINE ---")
        draft_complaint = DraftEngine.generate_draft("COMPLAINT", score_result["score"], concepts, case_data)
        if "SPECIFY EXACT ROLES" in draft_complaint or "Chief Financial Officer" in draft_complaint:
            print("SUCCESS: Director roles found in complaint.")
        if "Section 63(4)" in draft_complaint or "BSA" in draft_complaint:
            print("SUCCESS: BSA Section 63 found in complaint.")

        draft_143a = DraftEngine.generate_draft("APPLICATION_143A", score_result["score"], concepts, case_data)
        if "severe financial hardship" in draft_143a:
            print("SUCCESS: Financial Hardship found in 143A.")

        draft_63 = DraftEngine.generate_draft("CERTIFICATE_65B", score_result["score"], concepts, case_data)
        if "BHARATIYA SAKSHYA ADHINIYAM" in draft_63:
            print("SUCCESS: BSA Certificate generated successfully.")

        print("\nAll systems operational.")

    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    test_engines()
