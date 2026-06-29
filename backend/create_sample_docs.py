"""Generate 6 sample healthcare policy PDFs using PyMuPDF."""
import fitz
import os

DOCS_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")
os.makedirs(DOCS_DIR, exist_ok=True)

FONT = "helv"
TITLE_SIZE = 18
HEADING_SIZE = 13
BODY_SIZE = 11
LINE_HEIGHT = 16
MARGIN = 60
PAGE_W = 595
PAGE_H = 842

def new_page(doc):
    page = doc.new_page(width=PAGE_W, height=PAGE_H)
    return page, MARGIN

def add_title(page, y, text):
    page.insert_text((MARGIN, y), text, fontname=FONT, fontsize=TITLE_SIZE, color=(0.05, 0.1, 0.4))
    return y + TITLE_SIZE + 10

def add_heading(page, y, text, doc=None):
    if y > PAGE_H - 120:
        page = doc.new_page(width=PAGE_W, height=PAGE_H)
        y = MARGIN
    page.insert_text((MARGIN, y), text, fontname="hebo", fontsize=HEADING_SIZE, color=(0.1, 0.3, 0.6))
    return page, y + HEADING_SIZE + 6

def add_body(page, y, text, doc=None):
    words = text.split()
    line, lines = [], []
    for w in words:
        line.append(w)
        if len(" ".join(line)) > 82:
            lines.append(" ".join(line[:-1]))
            line = [w]
    if line:
        lines.append(" ".join(line))
    for l in lines:
        if y > PAGE_H - 80:
            page = doc.new_page(width=PAGE_W, height=PAGE_H)
            y = MARGIN
        page.insert_text((MARGIN, y), l, fontname=FONT, fontsize=BODY_SIZE, color=(0.15, 0.15, 0.15))
        y += LINE_HEIGHT
    return page, y + 8


DOCS = [
    {
        "filename": "prior_authorization_policy_2026.pdf",
        "title": "Prior Authorization Policy Manual 2026",
        "sections": [
            ("1. Overview", "This policy manual establishes prior authorization requirements for all procedures, services, and medications covered under commercial and Medicare Advantage plans effective January 1, 2026. Prior authorization is required before certain services are rendered to ensure medical necessity and coverage eligibility."),
            ("2. Imaging Services — MRI", "All MRI procedures (CPT codes 70553, 71552, 72148, 72141, 72156) require prior authorization for commercial plan members. Authorization must be obtained through the designated provider portal at least 72 hours prior to the scheduled service date. Emergency MRI requests may be submitted within 24 hours post-service with supporting clinical documentation. Failure to obtain prior authorization may result in claim denial."),
            ("3. CT Scans and Advanced Imaging", "CT scans of the abdomen, pelvis, chest, and head (CPT codes 74177, 74178, 71250, 70450) require prior authorization for commercial plans when ordered as non-emergency outpatient procedures. Inpatient CT scans are covered under the global inpatient authorization. Documentation required includes physician order, diagnosis code, and clinical notes supporting medical necessity."),
            ("4. Mental Health and Behavioral Services", "Outpatient mental health services require prior authorization beginning with the 13th visit in a calendar year. Inpatient psychiatric admissions require notification within 24 hours of admission. Substance use disorder treatment including residential rehabilitation requires pre-authorization. CPT codes 90832, 90834, 90837 are subject to these limits."),
            ("5. Specialty Medications and Biologics", "Specialty biologic medications administered in office (J-codes) require prior authorization for all plan types. Step therapy is required: members must demonstrate clinical failure of at least two preferred alternatives before biologic approval. Documentation must include treatment history, prior therapy failures, and physician attestation. Effective January 1, 2026 for all commercial and Medicare Advantage members."),
            ("6. Surgical Procedures", "Elective surgical procedures with CPT codes in the 10000-69999 range require prior authorization. Medically necessary procedures require supporting documentation including operative notes, diagnostic results, and physician certification. Emergency surgeries are exempt but require retrospective notification within 48 hours."),
            ("7. Durable Medical Equipment", "Durable medical equipment (DME) including CPAP machines (CPT E0601), wheelchairs (E1130-E1220), and hospital beds (E0250) require prior authorization for rental or purchase exceeding $500. Documentation required: physician order, certificate of medical necessity, and diagnosis codes."),
            ("8. Authorization Process", "Providers must submit requests via the online portal or fax to the utilization management department. Standard review: decision within 3 business days. Urgent review: decision within 72 hours. Emergency situations: retrospective review within 30 days. Denial appeals must be submitted within 60 days of denial notification."),
        ],
    },
    {
        "filename": "telehealth_coverage_policy.pdf",
        "title": "Telehealth and Virtual Care Coverage Policy 2026",
        "sections": [
            ("1. Scope and Eligibility", "This policy governs telehealth and virtual care services covered under all plan types including Commercial, Medicare Advantage, and Medicaid plans effective January 1, 2026. Telehealth services are covered for eligible members who receive care from credentialed providers using audio-video technology or, in limited cases, audio-only when video is not feasible."),
            ("2. Covered Telehealth Services", "The following services are covered via telehealth: Primary care visits (CPT 99202-99215), Mental health therapy (CPT 90832-90837), Psychiatry consultations (CPT 90791, 90792), Specialist consultations, Follow-up appointments, Chronic disease management, and Medication management. Telehealth services are reimbursed at the same rate as in-person visits for equivalent service codes."),
            ("3. Medicare Advantage Telehealth Expansion", "Effective January 1, 2026, Medicare Advantage members have expanded telehealth access with no geographic restrictions. Members may use telehealth services from any location including their home. No prior authorization is required for routine telehealth visits under Medicare Advantage plans. This expansion aligns with CMS telehealth flexibilities extended through December 31, 2026."),
            ("4. Audio-Only Services", "Audio-only services are covered for members without access to video technology. Covered audio-only CPT codes include 99441-99443 for telephone evaluation and management. Providers must document reason for audio-only modality. Audio-only services are limited to 10 per calendar year per member for commercial plans."),
            ("5. Provider Requirements", "Telehealth providers must be credentialed and licensed in the member's state of residence. Providers must use HIPAA-compliant telehealth platforms. Prescribing via telehealth is permitted for most medications with the exception of controlled substances, which require an in-person evaluation as per DEA regulations."),
            ("6. Billing and Documentation", "Telehealth claims must include place of service code 02 (Telehealth provided other than in patient's home) or 10 (Telehealth provided in patient's home). Modifier GT or 95 must be appended to CPT codes for audio-video services. Modifier 93 applies to audio-only services. Failure to include appropriate modifiers will result in claim rejection."),
            ("7. Exclusions", "The following services are not covered via telehealth: Physical examinations requiring hands-on assessment, Laboratory tests and imaging services, Surgical procedures, Emergency department visits, Anesthesia services, and Dental or vision services. Members requiring these services must present in person."),
        ],
    },
    {
        "filename": "claims_billing_guidelines.pdf",
        "title": "Claims Billing and Coding Guidelines 2026",
        "sections": [
            ("1. General Billing Requirements", "All claims must be submitted within 90 days of the date of service for commercial plans and within 365 days for Medicare Advantage plans. Claims submitted after the timely filing deadline will be denied without appeal rights. Clean claims submitted electronically will be processed within 30 days. Paper claims will be processed within 45 days."),
            ("2. Office Visit Coding — Evaluation and Management", "Office and outpatient evaluation and management (E/M) services are coded using CPT codes 99202-99215. New patient visits use codes 99202-99205. Established patient visits use codes 99211-99215. Since January 1, 2021, E/M code selection is based on medical decision making (MDM) complexity or total time. Documentation must support the level of service billed."),
            ("3. CPT 99213 Documentation Requirements", "CPT code 99213 (Office/outpatient visit, established patient, moderate MDM) requires documentation of at least two of the following: medical history, examination findings, or data review. Medical necessity documentation is required when CPT 99213 is billed more than 4 times in a rolling 90-day period for the same diagnosis code. Excessive billing without documentation triggers clinical review."),
            ("4. Diagnosis Code Requirements", "All claims must include at least one ICD-10-CM diagnosis code at the highest level of specificity. Unspecified codes should be avoided when a more specific code is available. Claims with Z-codes as primary diagnosis are subject to additional review. Diagnosis codes must support the medical necessity of all services billed."),
            ("5. Modifiers", "Modifier 25: Significant, separately identifiable E/M service on same day as procedure. Modifier 59: Distinct procedural service. Modifier 76: Repeat procedure. Modifier GT: Telehealth via interactive audio-video. Modifier 93: Synchronous telemedicine via telephone only. Incorrect modifier use may result in claim denials or overpayment recovery."),
            ("6. Laboratory and Diagnostic Services", "Laboratory claims must include ordering provider NPI. Comprehensive metabolic panels (CPT 80053) require medical necessity documentation when ordered more frequently than once per 90 days without a change in clinical condition. Duplicate lab billing within the same encounter will be rejected. Reference laboratory services require appropriate chain-of-custody documentation."),
            ("7. Coordination of Benefits", "When a member has dual coverage, the primary payer must be billed first. Coordination of benefits (COB) rules determine primary versus secondary payer. Medicare is primary for Medicare Advantage members except where employer group health plan (EGHP) rules apply. COB disputes must be resolved before claim payment is finalized."),
            ("8. Claim Denials and Appeals", "Denied claims may be appealed within 180 days of denial date. First-level appeal is reviewed by the payer's internal appeal committee. Second-level appeal includes external independent review organization (IRO). Members have the right to request an expedited appeal for urgent situations within 72 hours."),
        ],
    },
    {
        "filename": "emergency_services_policy.pdf",
        "title": "Emergency Services and Urgent Care Coverage Policy 2026",
        "sections": [
            ("1. Emergency Service Definition", "Emergency medical services are defined as services required for conditions that could reasonably be expected to place the member's health in serious jeopardy, result in serious impairment to bodily functions, or result in serious dysfunction of any bodily organ or part. This definition follows the prudent layperson standard and applies regardless of the final diagnosis."),
            ("2. Emergency Department Coverage", "Emergency department (ED) visits are covered for all plan types without prior authorization. CPT codes 99281-99285 for ED evaluation and management are covered. Members are not required to obtain referrals or authorization for emergency care. However, follow-up outpatient care after the emergency may require prior authorization if the service is normally subject to prior auth requirements."),
            ("3. Retrospective Authorization for Emergency Services", "When a member receives emergency care at an out-of-network facility, retrospective authorization is required within 24 hours of admission for inpatient stays following emergency admission. The previous 48-hour window has been reduced to 24 hours effective January 1, 2026. Claims for emergency services must include emergency diagnosis codes (ICD-10 codes beginning with S, T, or appropriate Z codes)."),
            ("4. Observation Services", "Hospital observation status (CPT 99218-99220, 99234-99236) is covered when ordered by an attending physician. Observation stays are billed as outpatient services. Members in observation status are responsible for outpatient cost-sharing, not inpatient cost-sharing. Observation stays exceeding 48 hours require clinical review and potential conversion to inpatient status."),
            ("5. Ambulance Services", "Emergency ambulance transportation is covered when medically necessary and transport was to the nearest appropriate facility. Ground ambulance (A0427-A0434) and air ambulance (A0431, A0436) are covered for emergencies. Non-emergency ambulance transport requires prior authorization. Balance billing protection applies: members are protected from surprise billing for ambulance services."),
            ("6. Out-of-Network Emergency Protections", "Federal No Surprises Act protections apply: members are protected from out-of-network cost-sharing for emergency services at out-of-network facilities. Members pay in-network cost-sharing amounts. Providers are prohibited from balance billing for emergency services. Independent dispute resolution (IDR) process resolves payment disputes between payers and out-of-network providers."),
            ("7. Mental Health Emergency Services", "Psychiatric emergencies are treated the same as medical emergencies. Crisis intervention services (CPT 90839, 90840) are covered without prior authorization. Mobile crisis teams are covered under expanded behavioral health benefits. Involuntary psychiatric holds are covered with retrospective notification within 24 hours."),
        ],
    },
    {
        "filename": "specialty_drug_formulary.pdf",
        "title": "Specialty Drug and Formulary Coverage Policy 2026",
        "sections": [
            ("1. Formulary Tiers", "The formulary is organized into four tiers: Tier 1 (preferred generic), Tier 2 (non-preferred generic), Tier 3 (preferred brand), and Tier 4 (specialty and high-cost medications). Members pay the lowest cost-sharing for Tier 1 medications and the highest for Tier 4 specialty drugs. Formulary exceptions may be requested when a non-formulary medication is medically necessary."),
            ("2. Prior Authorization for Specialty Drugs", "All specialty medications (Tier 4) require prior authorization before dispensing. Specialty drugs are defined as medications with a cost exceeding $600 per 30-day supply or requiring special handling, storage, or administration. Prior authorization criteria are based on FDA-approved indications, clinical guidelines, and evidence-based medicine. Authorization is valid for 12 months with annual renewal required."),
            ("3. Step Therapy Requirements", "Step therapy (also called fail-first) is required for specialty biologics, disease-modifying antirheumatic drugs (DMARDs), and certain oncology supportive care medications. Members must have documented clinical failure or contraindication to at least two preferred alternative therapies before specialty drug approval. Step therapy requirements apply to all commercial and Medicare Advantage members effective January 1, 2026."),
            ("4. Biologics and Biosimilars", "FDA-approved biosimilars are preferred over reference biologics when clinically appropriate and interchangeable. Biosimilar substitution is permitted unless the prescribing physician indicates medical necessity for the reference product (do not substitute). Covered biologics include TNF inhibitors (adalimumab, etanercept), IL inhibitors, and checkpoint inhibitors for oncology indications."),
            ("5. Oncology Medications", "Oral oncolytics and targeted therapy agents require prior authorization with oncology clinical criteria. Documentation required includes cancer type, stage, prior treatment history, ECOG performance status, and relevant biomarker testing results. Specialty oncology pharmacy network participation is required for dispensing. Coverage includes FDA-approved uses and National Comprehensive Cancer Network (NCCN) Category 1 and 2A recommendations."),
            ("6. Medication Management and Monitoring", "Members on specialty medications are enrolled in the Specialty Pharmacy Management Program. Clinical pharmacists conduct medication therapy management (MTM) reviews every 6 months. Adherence monitoring is conducted via claims data. Members demonstrating non-adherence are contacted for clinical support. Specialty medications are dispensed through the specialty pharmacy network only."),
            ("7. Formulary Exceptions and Appeals", "Formulary exceptions may be requested when a non-formulary or higher-tier drug is medically necessary. Exception requests require physician attestation of medical necessity and documentation of formulary alternative failure or contraindication. Standard exception decisions are made within 72 hours. Urgent exception decisions are made within 24 hours."),
        ],
    },
    {
        "filename": "medical_necessity_guidelines.pdf",
        "title": "Medical Necessity and Coverage Determination Guidelines 2026",
        "sections": [
            ("1. Medical Necessity Definition", "Medical necessity is defined as health care services or supplies needed to diagnose or treat an illness, injury, condition, disease, or its symptoms, and that meet accepted standards of medicine. Services must be: (1) ordered by a licensed healthcare provider, (2) necessary and appropriate for the diagnosis or treatment, (3) consistent with national clinical guidelines, and (4) not primarily for the convenience of the patient or provider."),
            ("2. Coverage Determination Process", "Coverage determinations are made based on the member's benefit plan, clinical criteria, and evidence-based medical guidelines. The plan uses criteria from nationally recognized sources including InterQual, Milliman Care Guidelines, and specialty society guidelines. Clinical reviewers are licensed healthcare professionals with relevant clinical expertise. Initial determinations are made within 30 days for standard requests and 72 hours for urgent requests."),
            ("3. Preventive Care Services", "Preventive care services are covered at 100% with no cost-sharing when delivered by in-network providers. Covered preventive services include USPSTF Grade A and B recommendations, ACIP immunization schedules, and preventive care guidelines for children and adolescents (Bright Futures). CPT codes for preventive visits: 99381-99387 (new patient) and 99391-99397 (established patient)."),
            ("4. Chronic Disease Management", "Members with chronic conditions including diabetes, hypertension, heart failure, COPD, and asthma are enrolled in disease management programs. Disease management services are covered including nurse care coordination, diabetes self-management training (DSMT, CPT 98960-98962), and cardiac rehabilitation (CPT 93798). HbA1c testing for diabetic members is covered quarterly without prior authorization."),
            ("5. Experimental and Investigational Services", "Services classified as experimental or investigational are excluded from coverage unless the member is enrolled in an approved clinical trial. Clinical trial coverage includes routine costs associated with participation in Phase II-IV cancer clinical trials. Coverage is provided for trials sponsored by federal agencies or conducted under an IND application. Investigational medical devices may be covered under the Coverage with Evidence Development (CED) program."),
            ("6. Second Opinion Coverage", "Members have the right to obtain a second medical opinion from any in-network specialist without referral. Second opinions for surgical procedures are strongly encouraged. Out-of-network second opinions are covered at in-network rates when in-network specialists are not available in the service area within a reasonable distance. Documentation of the second opinion may be required for certain high-cost procedures."),
            ("7. Coverage for Pediatric Services", "Pediatric preventive care is covered as described in the Bright Futures guidelines through age 21. Developmental screenings, autism spectrum disorder screenings, and behavioral health assessments are covered without cost-sharing. Pediatric dental, vision, and hearing benefits are included as essential health benefits for members under age 19 in qualified health plans."),
            ("8. Mental Health Parity", "Mental health and substance use disorder (MH/SUD) benefits must be provided on the same basis as medical and surgical benefits. Parity applies to: financial requirements, quantitative treatment limits, and non-quantitative treatment limits. Prior authorization criteria for MH/SUD services must be comparable to medical/surgical criteria. Annual parity analyses are conducted and available upon request."),
        ],
    },
]

def create_pdf(doc_info):
    doc = fitz.open()
    page, y = new_page(doc)

    # Title
    y = add_title(page, y, doc_info["title"])
    page.insert_text((MARGIN, y), "Effective January 1, 2026  |  Confidential — For Internal Use", fontname=FONT, fontsize=9, color=(0.5, 0.5, 0.5))
    y += 28

    # Horizontal rule
    page.draw_line((MARGIN, y), (PAGE_W - MARGIN, y), color=(0.7, 0.7, 0.9), width=1)
    y += 16

    for heading, body in doc_info["sections"]:
        page, y = add_heading(page, y, heading, doc)
        y += 2
        page, y = add_body(page, y, body, doc)
        y += 6

    path = os.path.join(DOCS_DIR, doc_info["filename"])
    doc.save(path)
    doc.close()
    print(f"Created: {path}")

if __name__ == "__main__":
    for d in DOCS:
        create_pdf(d)
    print(f"\nAll {len(DOCS)} sample PDFs created in {DOCS_DIR}")
