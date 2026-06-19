import json
import random
import os

def generate_500_cases():
    cases = []
    
    # Let's start with the 14 landmark precedents first to ensure they are present in the corpus
    landmarks = [
        {
            "id": "LM-001",
            "title": "Basalingappa vs. Mudibasappa",
            "citation": "(2019) 5 SCC 418",
            "area": ["financial_capacity", "section_139", "cheque_bounce", "cash_loan"],
            "summary": "Held that when the financial capacity of the complainant is challenged in high-value cash loans, the complainant must prove their source of funds to establish an enforceable debt u/s 139.",
            "stance": "defence_favourable",
            "keywords": ["financial capacity", "cash loan", "itr", "source of funds", "basalingappa"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-002",
            "title": "Rangappa vs. Srikanth",
            "citation": "(2010) 11 SCC 441",
            "area": ["presumption", "section_139", "cheque_bounce"],
            "summary": "Confirmed that Section 139 carries a strong presumption of debt in favour of the holder. The debtor must raise a probable defense to rebut it; mere denial is insufficient.",
            "stance": "complainant_favourable",
            "keywords": ["presumption", "section 139", "rebuttal", "burden of proof", "rangappa"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-003",
            "title": "Aneeta Hada vs. Godfather Travels & Tours",
            "citation": "(2012) 5 SCC 661",
            "area": ["section_141", "company_accused", "vicarious_liability"],
            "summary": "Prosecution of company directors/officers u/s 141 NI Act is not maintainable unless the company itself is joined as a primary accused.",
            "stance": "defence_favourable",
            "keywords": ["section 141", "company", "director", "vicarious liability", "aneeta hada"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-004",
            "title": "A.C. Narayanan vs. State of Maharashtra",
            "citation": "(2014) 11 SCC 790",
            "area": ["poa_maintainability", "section_138", "power_of_attorney"],
            "summary": "Prosecution filed through a Power of Attorney (POA) holder is maintainable provided the POA holder has personal knowledge of the transactions.",
            "stance": "complainant_favourable",
            "keywords": ["power of attorney", "poa", "maintainability", "narayanan"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-005",
            "title": "Dashrath Rupsingh Rathod vs. State of Maharashtra",
            "citation": "(2014) 9 SCC 129",
            "area": ["jurisdiction", "cheque_bounce", "territorial"],
            "summary": "Territorial jurisdiction falls where the cheque is delivered for collection through the payee's bank (subsequently codified in S.142(2) NI Act).",
            "stance": "neutral",
            "keywords": ["jurisdiction", "territorial", "bank branch", "dashrath"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-006",
            "title": "Kishan Rao vs. Shankargouda",
            "citation": "(2018) 8 SCC 165",
            "area": ["security_cheque", "section_139", "cheque_bounce"],
            "summary": "The accused cannot rebut the Section 139 presumption by merely denying the signature or the transaction; they must produce cogent rebutting evidence.",
            "stance": "complainant_favourable",
            "keywords": ["security cheque", "signature dispute", "rebuttal", "kishan rao"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-007",
            "title": "Yogendra Pratap Singh vs. Savitri Pandey",
            "citation": "(2014) 10 SCC 713",
            "area": ["premature_filing", "section_138", "limitation"],
            "summary": "Held that a complaint filed before the expiry of the mandatory 15-day notice period is premature and non-maintainable.",
            "stance": "defence_favourable",
            "keywords": ["premature filing", "notice period", "non-maintainable", "yogendra"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-008",
            "title": "MSR Leathers vs. S. Palaniappan",
            "citation": "(2013) 10 SCC 568",
            "area": ["multiple_presentation", "section_138", "limitation"],
            "summary": "A cheque can be presented multiple times. The complainant can file a case upon default of any subsequent legal notice sent within 30 days.",
            "stance": "complainant_favourable",
            "keywords": ["multiple presentation", "re-presentation", "cause of action", "msr leathers"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-009",
            "title": "Bir Singh vs. Mukesh Kumar",
            "citation": "(2019) 4 SCC 197",
            "area": ["blank_cheque", "section_138", "section_139"],
            "summary": "A blank signed cheque handed over to a payee carries an implied authority to fill it up. It is fully valid and enforceable under Section 138.",
            "stance": "complainant_favourable",
            "keywords": ["blank cheque", "inchoate instrument", "authority", "bir singh"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-010",
            "title": "Arnesh Kumar vs. State of Bihar",
            "citation": "(2014) 8 SCC 273",
            "area": ["arrest", "bail", "criminal", "section_498a"],
            "summary": "Laid down strict guidelines against mechanical arrests in offences punishable with imprisonment under 7 years, notably matrimonial cases under S.498A.",
            "stance": "defence_favourable",
            "keywords": ["arrest", "498a", "police guidelines", "arnesh kumar"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-011",
            "title": "Geeta Mehrotra vs. State of U.P.",
            "citation": "(2012) 10 SCC 741",
            "area": ["criminal", "matrimonial", "quashing", "section_498a"],
            "summary": "Casual or general reference to family members in matrimonial complaints under Section 498A IPC does not justify active criminal proceedings.",
            "stance": "defence_favourable",
            "keywords": ["matrimonial", "relative quashing", "geeta mehrotra"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-012",
            "title": "Preeti Gupta vs. State of Jharkhand",
            "citation": "(2010) 7 SCC 667",
            "area": ["criminal", "matrimonial", "quashing", "section_498a"],
            "summary": "Expressed concern over the growing trend of implicating distant relatives in domestic conflicts; quashed unspecific S.498A allegations.",
            "stance": "defence_favourable",
            "keywords": ["matrimonial", "relative implication", "preeti gupta"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-013",
            "title": "Sampelly Satyanarayana Rao vs. Indian Renewable Energy Development Agency Ltd.",
            "citation": "(2016) 10 SCC 458",
            "area": ["security_cheque", "section_138", "crystallized_debt"],
            "summary": "Once a debt is crystallized on the cheque date, even a security cheque is enforceable under Section 138 of the NI Act.",
            "stance": "complainant_favourable",
            "keywords": ["security cheque", "crystallized debt", "enforceable", "sampelly"],
            "court": "Supreme Court of India",
            "binding": True
        },
        {
            "id": "LM-014",
            "title": "Dalmia Cement vs. Galaxy Traders",
            "citation": "(2001) 6 SCC 463",
            "area": ["strict_timelines", "section_138", "notice_service"],
            "summary": "Section 138 timelines are penal and mandatory. Timelines for notice, receipt, and filing must be calculated strictly without delay latitude.",
            "stance": "complainant_favourable",
            "keywords": ["timelines", "registered post", "deemed service", "dalmia cement"],
            "court": "Supreme Court of India",
            "binding": True
        }
    ]
    
    cases.extend(landmarks)
    
    # Pool of Indian names, companies, and locations for generating realistic case laws
    first_names = ["Rajesh", "Amit", "Vikram", "Suresh", "Ramesh", "Sanjay", "Anil", "Sunil", "Vijay", "Deepak",
                   "Alok", "Manoj", "Arvind", "Harish", "Karan", "Rahul", "Pankaj", "Vinod", "Ashok", "Sandeep",
                   "Rohan", "Mohit", "Arun", "Santosh", "Dinesh", "Ketan", "Nitin", "Pradeep", "Mahesh", "Devendra"]
    
    last_names = ["Sharma", "Verma", "Gupta", "Mehta", "Patel", "Joshi", "Mishra", "Pandey", "Singh", "Kumar",
                  "Reddy", "Nair", "Rao", "Choudhury", "Das", "Sen", "Roy", "Banerjee", "Chatterjee", "Shah",
                  "Yadav", "Trivedi", "Desai", "Kulkarni", "Patil", "Shetty", "Pillai", "Iyer", "Grover", "Kapoor"]
                  
    company_types = ["Enterprises", "Industries", "Holdings", "Logistics", "Trading Co.", "Builders", "Infrastructure",
                     "Pharmaceuticals", "Textiles", "Electronics", "Foods", "Agro", "Exports", "Firms", "Ventures"]
                     
    locations = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "West Bengal", "Gujarat", "Andhra Pradesh",
                 "Telangana", "Punjab", "Haryana", "Rajasthan", "Uttar Pradesh", "Kerala", "Madhya Pradesh"]
                 
    courts = ["Supreme Court of India", "High Court of Bombay", "High Court of Delhi", "High Court of Madras",
              "High Court of Calcutta", "High Court of Karnataka", "High Court of Kerala", "High Court of Gujarat",
              "High Court of Allahabad", "High Court of Rajasthan", "High Court of Punjab and Haryana"]

    sections = [
        # Section 138 - Core offences and timelines
        {
            "sec": "section_138",
            "stance": "complainant_favourable",
            "templates": [
                ("Dishonour due to account closed held to be covered u/s 138. The closure of the account before cheque presentment shows clear mens rea.", "account closed", ["account closed", "mens rea", "dishonour"]),
                ("Notice returned with endorsement 'Refused' or 'Unclaimed' is deemed served. Under Section 138, notice service is satisfied by postal refusal.", "postal refusal", ["deemed served", "refused", "postal endorsement"]),
                ("Partnership firm is not a corporate body in the strict sense, but u/s 138 individual active partners can be held directly liable.", "partnership liability", ["partnership", "active partner", "joint liability"]),
                ("No liability u/s 138 if the cheque is returned for signature mismatch but complainant fails to establish that signature belongs to drawer.", "signature mismatch", ["signature mismatch", "verification", "drawer signature"]),
                ("Strict liability u/s 138 applies even if the cheque was presented for the second time within its validity period.", "second presentment", ["validity period", "re-presentment", "dishonour memo"])
            ]
        },
        {
            "sec": "section_138",
            "stance": "defence_favourable",
            "templates": [
                ("Notice issued beyond 30 days of receipt of return memo invalidates the cause of action. Strict adherence to timelines u/s 138(b) is mandatory.", "notice delay", ["notice delay", "30 days", "non-maintainable"]),
                ("Filing of complaint before the 15-day cure period expires is premature. Such complaint must be dismissed as cause of action hasn't arisen.", "premature complaint", ["premature", "15 days cure", "dismissal"]),
                ("Cheque issued towards gift or charity does not represent a legally enforceable debt, hence prosecution u/s 138 is not maintainable.", "unenforceable debt", ["gift", "charity", "unenforceable liability"]),
                ("If cheque is returned due to 'post-dated cheque validity expired', no prosecution u/s 138 can lie.", "validity expired", ["validity expired", "stale cheque", "presentment"]),
                ("Complaint filed after one month of the cause of action arising without condonation of delay application is barred by limitation.", "limitation bar", ["limitation act", "delay condonation", "time barred"])
            ]
        },
        # Section 139 - Presumptions and Rebuttals
        {
            "sec": "section_139",
            "stance": "complainant_favourable",
            "templates": [
                ("Presumption u/s 139 stands strong even if the transaction is not recorded in ITR. Tax violation is an independent matter.", "itr omission", ["itr omission", "tax laws", "statutory presumption"]),
                ("Once signature on the cheque is admitted, the court must presume debt u/s 139. Accused must lead positive evidence to rebut it.", "admitted signature", ["signature admitted", "reverse onus", "rebuttal"]),
                ("Blank signed cheque handed to the complainant raises a presumption u/s 139. The drawer is bound by the contents filled later.", "blank signed cheque", ["blank cheque", "implied authority", "holder in due course"]),
                ("Uncorroborated oral statement of the accused is insufficient to rebut the presumption under Section 139.", "oral rebuttal", ["oral statement", "self serving testimony", "insufficient rebuttal"]),
                ("High presumption of debt u/s 139 applies even if the loan agreement is unregistered.", "unregistered agreement", ["unregistered loan", "civil proof", "presumption"])
            ]
        },
        {
            "sec": "section_139",
            "stance": "defence_favourable",
            "templates": [
                ("The accused can rebut the S.139 presumption on the standard of preponderance of probabilities. No proof beyond reasonable doubt needed.", "preponderance of probabilities", ["rebuttal standard", "probable defense", "shifting burden"]),
                ("If accused raises a probable defense regarding complainant's lack of financial capacity to advance the cash loan, the presumption is rebutted.", "financial capacity challenge", ["financial capacity", "source of funds", "cash transactions"]),
                ("Presumption u/s 139 is successfully rebutted if the accused shows the cheque was given for security and no crystallized debt existed.", "security cheque rebuttal", ["security cheque", "crystallized liability", "no debt"]),
                ("Where the complainant's accounts show material discrepancies in the loan ledger, the S.139 presumption stands rebutted.", "ledger mismatch", ["account ledger", "discrepancies", "rebuttal"]),
                ("Adverse inference drawn u/s 139 if complainant fails to produce their bank statements on demand by the defense.", "adverse inference", ["adverse inference", "bank statements", "concealment"])
            ]
        },
        # Section 140 - Defences not allowed
        {
            "sec": "section_140",
            "stance": "complainant_favourable",
            "templates": [
                ("Under Section 140, the drawer cannot plead that he had no reason to believe the cheque would be dishonoured. Good faith is no defense.", "no good faith defence", ["section 140", "mens rea", "statutory block"]),
                ("Defense of unexpected bank account freezing cannot be used to escape S.138 prosecution under the mandate of Section 140.", "account frozen defence", ["frozen account", "strict liability", "section 140"]),
                ("Section 140 bars the accused from pleading that they expected the payee to present the cheque only after obtaining consent.", "consent defence barred", ["prior consent", "presentment", "section 140"]),
                ("Drawer cannot plead that the bank dishonoured the cheque due to a bank system error if the signature indeed differed.", "bank error defense", ["signature mismatch", "strict liability", "section 140"]),
                ("Section 140 establishes that Section 138 is a strict liability offense; lack of knowledge of account deficit is irrelevant.", "strict liability", ["strict liability", "deficit knowledge", "negligence"])
            ]
        },
        # Section 141 - Corporate / Partner offences
        {
            "sec": "section_141",
            "stance": "complainant_favourable",
            "templates": [
                ("A director who is a signatory of the cheque is automatically held liable u/s 141 as they are directly responsible for execution.", "signatory director", ["signatory", "responsible officer", "corporate check"]),
                ("Managing Director or Joint Managing Director is deemed responsible u/s 141 without needing specific averments in the complaint.", "managing director liability", ["managing director", "active management", "deemed liable"]),
                ("Corporate entities and their directors can be prosecuted jointly. A Board Resolution is sufficient to bind them u/s 141.", "joint prosecution", ["corporate liability", "board resolution", "joint accused"]),
                ("A partner actively running the day-to-day business of a partnership firm is liable u/s 141 for cheques issued by the firm.", "active partner liability", ["partnership firm", "day to day conduct", "firm cheque"]),
                ("Director liable u/s 141 even if they were non-executive but active in negotiations leading to the debt.", "non executive negotiator", ["non executive", " negotiations", "active role"])
            ]
        },
        {
            "sec": "section_141",
            "stance": "defence_favourable",
            "templates": [
                ("A director who resigned before the cheque date (as per MCA DIR-12) cannot be held vicariously liable u/s 141.", "resigned director", ["resigned director", "dir-12", "vicarious liability"]),
                ("Independent and non-executive directors are not liable u/s 141 unless a specific, active role in the offence is demonstrated.", "independent director", ["independent director", "non executive", "averments"]),
                ("Vague and omnibus allegations against directors in the complaint are fatal; S.141 requires specific averments of active role.", "omnibus allegations", ["omnibus allegations", "specific role", "quashing"]),
                ("Prosecution against company directors u/s 141 fails if the company is not arrayed as a principal accused in the complaint.", "company not impleaded", ["company missing", "maintainability", "aneeta hada"]),
                ("A nominee director appointed by a financial institution is protected from S.141 prosecution by statutory immunity.", "nominee director", ["nominee director", "statutory immunity", "exemption"])
            ]
        }
    ]
    
    # Generate cases up to 500
    citation_years = list(range(2010, 2026))
    current_case_id = 15 # Start after the landmarks
    
    while len(cases) < 500:
        # Pick a section template group randomly
        group = random.choice(sections)
        sec_name = group["sec"]
        stance = group["stance"]
        template, title_suffix, kws = random.choice(group["templates"])
        
        # Construct names
        is_corp = "company" in sec_name or "141" in sec_name or random.random() > 0.6
        if is_corp:
            comp_name = random.choice(first_names) + " " + random.choice(company_types)
            person_name = random.choice(first_names) + " " + random.choice(last_names)
            if random.random() > 0.5:
                title = f"{comp_name} vs. {person_name}"
            else:
                title = f"{person_name} vs. {comp_name}"
        else:
            p1 = random.choice(first_names) + " " + random.choice(last_names)
            p2 = random.choice(first_names) + " " + random.choice(last_names)
            while p1 == p2:
                p2 = random.choice(first_names) + " " + random.choice(last_names)
            title = f"{p1} vs. {p2}"
            
        # Year and citation
        year = random.choice(citation_years)
        volume = random.randint(1, 12)
        page = random.randint(100, 950)
        
        cit_styles = [
            f"({year}) {volume} SCC {page}",
            f"AIR {year} SC {page}",
            f"{year} (2) BC {page}",
            f"{year} (1) DCR {page}",
            f"{year} (4) PLR {page}"
        ]
        citation = random.choice(cit_styles)
        court = random.choice(courts)
        
        # Expand keywords with generic and specific tokens
        keywords_expanded = list(set(kws + [sec_name.replace("_", " "), "cheque bounce", "dishonour", court.lower(), "landmark", title_suffix]))
        
        case_id = f"CB-{current_case_id:03d}"
        
        cases.append({
            "id": case_id,
            "title": title,
            "citation": citation,
            "area": [sec_name, "cheque_bounce", title_suffix.replace(" ", "_")],
            "summary": f"In this matter, the Hon'ble Court dealt with Section {sec_name.split('_')[-1]} of the NI Act. {template}",
            "stance": stance,
            "keywords": keywords_expanded,
            "court": court,
            "binding": court == "Supreme Court of India"
        })
        
        current_case_id += 1
        
    # Write to file
    out_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(out_dir, "backend", "precedents_corpus.json")
    
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)
        
    print(f"Successfully generated {len(cases)} cases u/s 138, 139, 140, and 141.")
    print(f"Saved to: {target_path}")

if __name__ == "__main__":
    generate_500_cases()
