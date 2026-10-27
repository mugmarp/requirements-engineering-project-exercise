#!/usr/bin/env python3
"""Build specs/spec_doc01.json from the base text with filler removed.

Content is taken verbatim from the base. Only filler phrases are cut.
Every cut is listed in CUTS so it can be reviewed.
"""
import json

CUTS = [
    ("the practical challenges faced during data collection",
     "the challenges faced during data collection"),
    ("fit the actual operational reality of the business",
     "fit the operational reality of the business"),
    ("During our visit, it became clear that the organizational structure is highly flattened.",
     "The organizational structure at the site is highly flattened."),
    ("and explicitly identify critical data gaps", "and identify critical data gaps"),
    ("Given the constraints of a single site visit, Group K utilized the following techniques:",
     "Given the single site visit, Group K used the following techniques:"),
    ("We utilized", "We used"),
    ("A core component of Requirements Engineering is documenting what cannot be easily obtained. Group K faced the following empirical challenges",
     "As Group K, we faced the following empirical challenges"),
    ("It is evident that the Sales Manager is not typing into the computer while actively directing truck loading in the yard.",
     "The Sales Manager is clearly not typing into the computer while directing truck loading in the yard."),
    ("Ground reality shows the owner visits the site every day, and data is only entered at the end of the day.",
     "The owner visits the site every day and data is entered at the end of the day."),
    ("Group K has successfully navigated the elicitation challenges. We have shaped the project into a highly practical, context-aware",
     "Group K has navigated the elicitation challenges. The project is a context-aware"),
    ("This provides a solid, defensible foundation for Phase 2: Requirements Analysis, where",
     "This provides the foundation for Phase 2, Requirements Analysis, where"),
]

spec = {
    "title": "DOCUMENT 1: REQUIREMENTS ELICITATION & STAKEHOLDER ANALYSIS",
    "meta": [
        "Course: SWE2102 - Requirements Engineering | Group: K",
        "Client Site: Deniz Construction Limited, Ishanyu-Bushenyi Road, Mbarara",
        "Project: Deniz Construction Management System (DCMS)",
    ],
    "blocks": [
        {"type": "h1", "text": "1. INTRODUCTION"},
        {"type": "para", "text": "This document outlines the Requirements Elicitation and Stakeholder Analysis conducted for the Deniz Construction Management System (DCMS). It details the empirical data gathered during our single site visit, the practical challenges faced during data collection, and how the system design was adapted to fit the actual operational reality of the business. Because follow-up visits were not possible and the stakeholder was unwilling to provide further information, this document also establishes the baseline for how unresolvable information gaps are handled through documented assumptions based on the Ugandan SME context."},

        {"type": "h1", "text": "2. STAKEHOLDER ANALYSIS"},
        {"type": "para", "text": "During our visit, it became clear that the organizational structure is highly flattened. The traditional corporate hierarchy does not apply; instead, roles are heavily concentrated. We mapped the stakeholders using a Power/Interest grid to determine our engagement strategy and explicitly identify critical data gaps."},

        {"type": "h2", "text": "2.1 Stakeholder Identification & Power/Interest Mapping"},
        {"type": "table",
         "header": ["Stakeholder", "Role in Current Operations", "Power", "Interest", "Engagement Strategy & Data Status"],
         "rows": [
             ["Business Owner", "Strategic oversight; conducts daily physical site visits to review operations and cash.", "High", "High", "Manage Closely: Status: [GAP] - Not available for interview. System must prioritize the specific operational metrics he reviews during his daily evening visits."],
             ["Sales Manager", "The \"Super-Manager\": supervises workers, handles cash, processes daily deficits, logs sales, and files URA taxes.", "High", "High", "Manage Closely: Status: [FACT] - Interviewed. Acts as the gatekeeper. System must reduce her end-of-day workload to ensure adoption."],
             ["Secretary", "Expected to handle tax records and data entry.", "Medium", "High", "Keep Informed: Status: [GAP] - Never met. No interview data. System will assign these permissions to the Sales Manager by default; the Secretary role is retained in the database schema purely for future organizational scaling."],
             ["Site Workers", "Produce blocks/pavers. Paid daily in cash. Operate without formal legal contracts.", "Low", "Low", "Monitor: Status: [GAP] - Could not speak to them. System only requires a simplified interface for the Manager to log them as \"Present\"."],
             ["URA (External)", "Uganda Revenue Authority. Dictates tax compliance, VAT, and receipting standards.", "High", "Low", "Keep Satisfied: System must ensure financial outputs are compliant with URA audit expectations to prevent penalties."],
             ["Clients/Builders", "Purchase blocks/pavers. Pay upfront. Transport their own goods via trucks.", "Low", "Medium", "Keep Informed: System must generate clear receipts and ensure quick processing to minimize loading delays."],
         ]},

        {"type": "h2", "text": "2.2 Common Pitfalls & Engagement Techniques"},
        {"type": "para", "runs": [
            {"text": "Pitfall Identified (The Gatekeeper Effect): ", "bold": True},
            {"text": "Because the Sales Manager handles almost all operations, she acts as a gatekeeper. She was initially hesitant to share deep financial workflows (e.g., exact tax calculations, cash storage)."}]},
        {"type": "para", "runs": [
            {"text": "Mitigation Technique: ", "bold": True},
            {"text": "We utilized Observation over direct interrogation for sensitive topics. By observing the physical environment (e.g., noting the presence of CCTV cameras, the printer, and the laptop usage timing), we inferred security and workflow requirements without making her defensive."}]},

        {"type": "h1", "text": "3. ELICITATION TECHNIQUES USED"},
        {"type": "para", "text": "Given the constraints of a single site visit, Group K utilized the following techniques:"},
        {"type": "para", "runs": [{"text": "1. Direct Observation (Environmental Scan):", "bold": True}]},
        {"type": "bullets", "items": [
            "Noted that clients transport their own products using trucks, meaning the system does not need a \"Delivery/Logistics\" module, but rather a \"Loading/Dispatch\" confirmation.",
            "Observed the physical presence of a laptop, a printer, and CCTV cameras, indicating a baseline awareness of security and digital record-keeping.",
            "Observed that trucks load in bulk, though the exact counting method (per piece, per pallet) was not explicitly visible."]},
        {"type": "para", "runs": [{"text": "2. Semi-Structured Interview:", "bold": True}]},
        {"type": "bullets", "items": [
            "Conducted a face-to-face interview with the Sales Manager to understand the high-level workflow, payment methods (Cash, Mobile Money, Bank), and primary pain points (specifically \"insecurity\" and \"processing deficits\")."]},

        {"type": "h1", "text": "4. CHALLENGES IN ELICITATION"},
        {"type": "para", "text": "A core component of Requirements Engineering is documenting what cannot be easily obtained. Group K faced the following empirical challenges, which are now locked as documented limitations for the project:"},
        {"type": "numbered", "items": [
            "Stakeholder Hesitance & Information Withholding: The Sales Manager was reluctant to disclose the exact fields on their physical receipts, the specific methodology for calculating URA taxes, and the physical cash-handling/storage protocols.",
            "Inaccessibility of Secondary Stakeholders: The Business Owner was not available for a formal interview, and the Site Workers and Secretary could not be approached directly. (Note: These are unresolvable gaps; their requirements will be handled via standard industry assumptions).",
            "Incomplete Workflow Visibility: While we knew the laptop is used to \"process deficits,\" we could not observe the exact mathematical formula or physical cash reconciliation process.",
            "No Follow-up Feasibility: The client is unwilling to provide more information, and returning to the site for secondary elicitation sessions is not possible. The project scope is locked."]},

        {"type": "h1", "text": "5. OPERATIONAL DEDUCTIONS & SYSTEM DESIGN ADJUSTMENTS"},
        {"type": "para", "text": "Since we could not get explicit answers for every workflow, we deduced the system requirements based on our physical observations and the standard operational context of Ugandan construction SMEs. Where obvious, we applied standard industry baselines; where complex, we applied logical deductions."},

        {"type": "para", "runs": [{"text": "5.1. The \"Super-Manager\" Workflow & The Auto-Calculation Engine", "bold": True}]},
        {"type": "para", "text": "We observed that the laptop is primarily turned on and used right before the Business Owner arrives in the evening. It is evident that the Sales Manager is not typing into the computer while actively directing truck loading in the yard. However, if she only typed \"daily summary totals\" into the system, we would lose the ability to automatically calculate VAT per item, deduct specific blocks from inventory, or track exact drawer balances."},
        {"type": "para", "runs": [
            {"text": "Design Adjustment: ", "bold": True},
            {"text": "The system's workflow is shifted to the evening, but the data entry remains strictly transactional. The Sales Manager will log each individual sale and each operational expense from her paper receipts into the system at the end of the day. The system will then act as an Auto-Calculation Engine, automatically computing the VAT, updating inventory, tracking the separate payment channels, and instantly generating the final End-of-Day Reconciliation report."}]},

        {"type": "para", "runs": [{"text": "5.2. Resolving the \"Deficit\" and Cash Insecurity Issue", "bold": True}]},
        {"type": "para", "text": "The Sales Manager explicitly mentioned using the PC to \"process deficits\" and cited \"insecurity\" regarding cash (aligning with the CCTV cameras we observed). In cash-heavy sites, end-of-day \"deficits\" (shortages) are rarely theft; they are almost always unrecorded petty cash expenses (e.g., buying lunch for the truck loaders, paying for a boda-boda errand) taken directly from the cash drawer."},
        {"type": "para", "runs": [
            {"text": "Design Adjustment: ", "bold": True},
            {"text": "The system must include an \"Operational Expense / Petty Cash Log\". The Sales Manager will log each individual cash-out. The system will automatically deduct these from the \"Cash Virtual Drawer,\" balancing the till and eliminating the \"deficit\" mystery for the owner."}]},

        {"type": "para", "runs": [{"text": "5.3. Multi-Channel Payment Reconciliation", "bold": True}]},
        {"type": "para", "runs": [
            {"text": "Design Adjustment: ", "bold": True},
            {"text": "The system must strictly separate the three payment channels (Cash, Mobile Money, Bank Deposit). Every transactional entry must force the selection of a payment method. The End-of-Day Reconciliation report will calculate the expected balance for each specific channel independently, preventing the mixing of physical cash and digital money."}]},

        {"type": "para", "runs": [{"text": "5.4. Standardizing Receipts and Inventory (Handling the Gaps)", "bold": True}]},
        {"type": "para", "text": "While we couldn't see the exact receipt fields or how the bulk blocks were counted, we applied standard industry baselines for the database design to close these gaps."},
        {"type": "para", "runs": [
            {"text": "Design Adjustment: ", "bold": True},
            {"text": "Receipts will include standard URA-compliant fields (Sequential ID, Date, Customer, Items, VAT, Payment Method). For inventory, since trucks load in bulk and clients self-transport, the database Unit_of_Measure field will be designed to be flexible (VARCHAR) to handle blocks sold by the piece/pallet and pavers by the square meter, without needing complex logistics modules."}]},

        {"type": "para", "runs": [{"text": "5.5. Redefining Cloud Backup and Remote Access", "bold": True}]},
        {"type": "para", "text": "Ground reality shows the owner visits the site every day, and data is only entered at the end of the day. Real-time syncing is unnecessary and would just waste the site's limited internet data."},
        {"type": "para", "runs": [
            {"text": "Design Adjustment: ", "bold": True},
            {"text": "We defined the cloud feature strictly as an Automated Nightly Backup (triggered in the evening after she finishes data entry) to solve the \"Data Vulnerability\" problem of relying on a single laptop. The remote portal for the owner is designed as an Asynchronous Dashboard for reviewing next-day finalized reports and long-term business trends, rather than a live monitoring tool."}]},

        {"type": "para", "runs": [{"text": "5.6. Explicitly Excluded Features", "bold": True}]},
        {"type": "para", "text": "Based on the ground fact that the business \"never gives credit - all payments must be made,\" the system will not include a Credit/Debtors module, credit limits, or accounts receivable tracking. This prevents scope creep and aligns the software strictly with the business's actual financial policy."},

        {"type": "h1", "text": "6. CONCLUSION & TRANSITION"},
        {"type": "para", "text": "By combining our direct observations with logical deductions based on the local business context, Group K has successfully navigated the elicitation challenges. We have shaped the project into a highly practical, context-aware End-of-Day Transactional Reconciliation and Auto-Calculation System. All unresolvable gaps (Secretary, Workers, Receipt Fields) have been documented and will be handled via standard assumptions in the subsequent phases."},
        {"type": "para", "text": "This provides a solid, defensible foundation for Phase 2: Requirements Analysis, where these deductions will be formalized into the Software Requirements Specification (SRS) and mapped to the relational database schema."},
    ],
}


def apply_cuts(text):
    for old, new in CUTS:
        if old in text:
            text = text.replace(old, new)
    return text


def walk(obj):
    if isinstance(obj, str):
        return apply_cuts(obj)
    if isinstance(obj, list):
        return [walk(i) for i in obj]
    if isinstance(obj, dict):
        return {k: walk(v) for k, v in obj.items()}
    return obj


spec = walk(spec)
with open("/home/vm/MUST/REQUIREMENTS/specs/spec_doc01.json", "w", encoding="utf-8") as fh:
    json.dump(spec, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

print("cuts applied:", len(CUTS))
for i, (a, b) in enumerate(CUTS, 1):
    print(f"  {i}. {a[:60]}... -> {b[:60]}...")
print("blocks:", len(spec["blocks"]))
