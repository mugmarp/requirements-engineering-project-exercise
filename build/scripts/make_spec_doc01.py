#!/usr/bin/env python3
"""Generate the Phase 1 Word document spec."""

import json
from pathlib import Path

SPEC = r"""
{
  "title": "REQUIREMENTS ELICITATION AND STAKEHOLDER ANALYSIS",
  "meta": [
    "Course: SWE2102 Requirements Engineering",
    "Group: K",
    "Client Site: Deniz Construction Limited, Ishanyu Bushenyi Road, Mbarara",
    "Project: Deniz Construction Management System (DCMS)"
  ],
  "blocks": [
    { "type": "h1", "text": "1. INTRODUCTION" },
    { "type": "h2", "text": "1.1 Purpose" },
    { "type": "para", "text": "This document presents the Requirements Elicitation and Stakeholder Analysis conducted for the Deniz Construction Management System (DCMS). It records the empirical data gathered during our site visit, the elicitation techniques used, the challenges encountered, and the current As-Is operational reality of the business." },
    { "type": "h2", "text": "1.2 Scope" },
    { "type": "para", "text": "The analysis covers stakeholder identification, power-interest mapping, elicitation techniques applied, field observations, interview findings, documented limitations, and strategic business synthesis to inform the subsequent Requirements Analysis and Specification phase." },
    { "type": "h2", "text": "1.3 Methodology" },
    { "type": "para", "text": "Group K applied Direct Observation and Semi-Structured Interviews during a single site visit. Because further follow-up visits were not feasible and the Sales Manager was unwilling to provide further information, this document also establishes the baseline for how unresolvable information gaps are handled through documented business assumptions based on the Ugandan SME context." },
    { "type": "h2", "text": "1.4 Definitions and Abbreviations" },
    { "type": "bullets", "items": [
      "As-Is: The current operational state of the business before system implementation",
      "DCMS: Deniz Construction Management System",
      "MoMo: Mobile Money",
      "SME: Small and Medium Enterprise",
      "SRS: Software Requirements Specification",
      "URA: Uganda Revenue Authority"
    ] },
    { "type": "h2", "text": "1.5 References" },
    { "type": "bullets", "items": [
      "IEEE Std 830-1998 - Recommended Practice for Software Requirements Specifications",
      "SWE2102 Course Allocation - Group K, Requirements Engineering"
    ] },
    { "type": "h2", "text": "1.6 Document Overview" },
    { "type": "para", "text": "Section 2 provides the Business Context. Section 3 states the Problem Statement. Section 4 covers Stakeholder Analysis. Section 5 details Elicitation Techniques and Field Realities. Section 6 documents Challenges and Limitations. Section 7 presents Strategic Business Synthesis. Section 8 concludes and transitions to the next phase." },

    { "type": "h1", "text": "2. BUSINESS CONTEXT" },
    { "type": "para", "text": "Deniz Construction Limited is a small construction materials business located on Ishanyu-Bushenyi Road, Mbarara, Uganda. The business produces and sells concrete blocks, pavers and kerbs. Operations are highly centralised, a single Sales Manager acts as supervisor, cashier, payroll distributor, record keeper and tax filer. The Business Owner visits the site daily to review operations and cash. The business operates on a strict no-credit policy with three payment channels: Cash, Mobile Money and Bank Deposit. Physical receipts are printed on-site for customers during truck loading. URA tax filing is done online. Deniz keeps records on the office computer and in physical books and receipts. The digital records have no cloud backup. Workers are paid daily in cash without formal contracts." },

    { "type": "h1", "text": "3. PROBLEM STATEMENT" },
    { "type": "para", "text": "Deniz Construction Limited relies on the Sales Manager to oversee daily operations, record sales and reconcile cash. The site visit identified four issues with how this work is carried out." },
    { "type": "bullets", "items": [
      "Responsibilities concentrated in one role. The Sales Manager supervises workers, handles sales, distributes wages, maintains records and files taxes online. Several daily operations therefore depend on her availability.",
      "Manual cash reconciliation. The Sales Manager uses the office computer to work out cash shortages. We could not establish how she records cash expenses or investigates differences between expected and counted cash.",
      "Informal attendance tracking. The Sales Manager relies on memory to identify who reported for work. This makes it difficult to verify attendance later. We did not see how daily wage payments were recorded.",
      "Records and backup. Deniz keeps records on the office computer and in physical books and receipts. There is no cloud backup for the digital records. We could not establish which digital records could be recovered from the paper copies."
    ] },

    { "type": "h1", "text": "4. STAKEHOLDER ANALYSIS" },
    { "type": "para", "text": "The organisational structure is highly flattened. Roles are heavily concentrated, so the traditional corporate hierarchy does not apply. We mapped stakeholders on a Power and Interest grid to determine engagement strategy and identify critical data gaps." },

    { "type": "h2", "text": "4.1 Stakeholder Identification and Power Interest Mapping" },
    {
      "type": "table",
      "header": ["Stakeholder", "Role in Current Operations", "Power", "Interest", "Engagement Strategy and Status"],
      "rows": [
        ["Business Owner", "Strategic oversight. Visits the site daily to review operations and cash.", "High", "High", "Manage Closely. Status: Gap. Never interviewed. The system must prioritise the metrics he reviews during his daily evening visits."],
        ["Sales Manager", "The absolute centre of operations. Acts as supervisor, cashier, payroll distributor and record keeper.", "High", "High", "Manage Closely. Interviewed during the site visit."],
        ["Site Workers", "Produce blocks and pavers. Paid daily in cash. No formal legal contracts.", "Low", "Low", "Monitor. Status: Gap. No chance to speak to them."],
        ["URA (External)", "Uganda Revenue Authority. Dictates tax compliance, VAT and receipting standards.", "High", "Low", "Keep Satisfied. External regulator. No direct engagement but dictates compliance rules."],
        ["Customers and Builders", "Purchase blocks and pavers. Pay upfront. Transport their own goods by truck.", "Low", "Medium", "Keep Informed. The system must ensure quick processing to minimise loading delays."]
      ]
    },

    { "type": "h1", "text": "5. ELICITATION TECHNIQUES AND FIELD REALITIES (THE AS-IS STATE)" },
    { "type": "para", "text": "Group K used Direct Observation and Semi-Structured Interviews. The following facts represent the current operational reality of the business." },

    { "type": "para", "runs": [ { "text": "1. Direct Observation (Environmental Scan)", "bold": true } ] },
    {
      "type": "bullets",
      "items": [
        "Workflow and Hardware: The laptop was powered on and actively used during the day. A printer is on site and physical receipts were being printed for customers as trucks loaded.",
        "Logistics: Customers transport their own products by truck. Trucks load in bulk, but the exact counting method (per piece or per pallet) was not visible.",
        "CCTV. The site has CCTV cameras.",
        "Machinery: Production area has block-making machinery (vibrators, moulds, mixers) observed on site."
      ]
    },
    { "type": "para", "runs": [ { "text": "2. Semi-Structured Interview (Sales Manager)", "bold": true } ] },
    {
      "type": "bullets",
      "items": [
        "Payment Channels: The business accepts Cash, Mobile Money and direct Bank Deposits.",
        "Credit Policy: The business never gives credit; all payments must be made upfront.",
        "Tax Compliance: The Sales Manager processes taxes online via the URA portal, but the exact manual calculation method was not disclosed.",
        "Cash shortages and security. The Sales Manager said she uses the office computer to work out cash shortages. She also raised insecurity as a concern without specifying what it involved.",
        "Labour: There is no formal attendance system. Attendance relies entirely on the Sales Manager's memory and workers are paid daily in cash without legal contracts."
      ]
    },

    { "type": "h1", "text": "6. CHALLENGES IN ELICITATION AND DOCUMENTED LIMITATIONS" },
    { "type": "para", "text": "The visit left the following gaps in what Group K could establish." },
    {
      "type": "numbered",
      "items": [
        "Limited access to financial procedures. The Sales Manager explained that she files taxes online and uses the office computer to work out cash shortages. During the visit, we could not establish how taxes were calculated, where cash was stored or how she reconciled the physical cash count. We saw receipts being printed as trucks loaded, but could not inspect the fields on them.",
        "Inaccessibility of Secondary Stakeholders. The Business Owner was not available for interview and the Site Workers could not be approached directly.",
        "Further follow-up visits were not feasible. The Sales Manager was unwilling to provide further information and a return visit to the site could not be arranged. The project scope is locked."
      ]
    },

    { "type": "h1", "text": "7. STRATEGIC BUSINESS SYNTHESIS" },
    { "type": "para", "text": "Because we cannot return to the site to close the gaps identified in Section 6, we apply strategic business synthesis. These are logical inferences drawn from verified facts combined with standard operational norms of Ugandan construction SMEs. They serve as baseline implications for the subsequent Requirements Analysis phase." },

    { "type": "para", "runs": [ { "text": "1. Cash Shortages and Expense Recording", "bold": true } ] },
    { "type": "para", "text": "Fact. The Sales Manager uses the office computer to work out cash shortages. The cause of past shortages remains unknown." },
    { "type": "para", "text": "Synthesis. Recording cash expenses would let the Sales Manager account for those outflows when comparing expected cash with the physical count." },
    { "type": "para", "text": "Implication for requirements analysis. Provide a way to record individual cash expenses and include them in the expected cash calculation." },

    { "type": "para", "runs": [ { "text": "2. The Dual-Phase Operational Reality", "bold": true } ] },
    { "type": "para", "text": "Fact: The laptop is on during the day and physical receipts are printed for customers. However, the Sales Manager also heavily utilises the PC right before the Business Owner arrives in the evening specifically to process cash deficits." },
    { "type": "para", "text": "Synthesis: The Sales Manager cannot wait until the evening to log sales, because customers require printed receipts immediately upon loading. However, the evening PC usage indicates a distinct, heavy reconciliation burden at the end of the day." },
    { "type": "para", "text": "Implication for Requirements Analysis: The future system must support real-time transaction processing and receipt generation during the day, alongside a dedicated, heavy-duty reconciliation workflow for the evening." },

    { "type": "para", "runs": [ { "text": "3. Receipting and Inventory Baselines", "bold": true } ] },
    { "type": "para", "text": "Fact: Physical receipts are printed on site and trucks load in bulk. Exact receipt fields are unknown." },
    { "type": "para", "text": "Synthesis: To satisfy URA compliance and basic business logic, receipts must contain standard fiscal fields (Sequential ID, Date, VAT, Payment Method). Because clients self-transport and load in bulk, inventory tracking must accommodate flexible units of measure (pieces, pallets, or truckloads)." },
    { "type": "para", "text": "Implication for Requirements Analysis: The SRS must define flexible unit-of-measure handling and standard receipt fields for URA compliance." },

    { "type": "para", "runs": [ { "text": "4. Cloud Backup and Remote Access Specification", "bold": true } ] },
    { "type": "para", "text": "Fact: The Owner visits the site every day. No cloud backup currently exists." },
    { "type": "para", "text": "Synthesis: Because the Owner is physically present daily, a real-time remote monitoring dashboard is operationally redundant. The critical need for cloud technology is strictly for disaster recovery (protecting the single laptop from data loss) and asynchronous historical review." },
    { "type": "para", "runs": [ { "text": "System Implication. ", "bold": true }, { "text": "The cloud feature is specified strictly as an Automated Nightly Backup, triggered in the evening after the final reconciliation is complete, to solve the Data Vulnerability problem of relying on a single laptop. The remote portal for the Owner is an Asynchronous Dashboard for reviewing next-day finalised reports and long-term business trends, rather than a live monitoring tool." } ] },

    { "type": "h1", "text": "8. CONCLUSION AND TRANSITION" },
    { "type": "para", "text": "By combining direct observation with logical business synthesis, Group K has mapped the current As-Is state of Deniz Construction Limited and documented all unresolvable elicitation challenges." },
    { "type": "para", "text": "All gaps (Workers, Receipt Fields, Cash Storage, Tax Calculation Method) are formally documented as limitations." },
    { "type": "para", "text": "This elicitation and stakeholder analysis provides the input for Phase 2: Requirements Analysis and Specification, where the documented facts, synthesis, and implications will be translated into formal Software Requirements (SRS)." }
  ]
}
""".lstrip("\n")


def main():
    json.loads(SPEC)
    output = Path(__file__).resolve().parents[1] / "specs" / "spec_doc01.json"
    output.write_text(SPEC, encoding="utf-8")
    print(f"Generated {output}")


if __name__ == "__main__":
    main()
