# Requirements Engineering Project Exercise

Group K, SWE2102 Requirements Engineering, BSE Year II
Mbarara University of Science and Technology (MUST)

Client case study: Deniz Construction Limited, Ishanyu-Bushenyi Road, Mbarara, Uganda

## About Deniz Construction Limited

Deniz Construction Limited is a small Ugandan construction materials SME located on Ishanyu-Bushenyi Road, Mbarara. The business produces and sells concrete blocks, pavers, and kerbs. Operations are run by a single Sales Manager who acts as supervisor, cashier, payroll distributor, record keeper, and tax filer. The Business Owner visits the site daily to review operations and cash.

**Contact:** 0749858413, 0791069287, 0700 640 242

**Product Catalogue:**

| Category | Products |
|---|---|
| Solid Blocks | 4×8×16, 6×8×16, 8×8×16 inches |
| Hollow Blocks | 4×8×16, 6×8×16, 8×8×16 inches |
| Pavers | 60mm and 80mm thickness (Interlocking, Rectangular, Hexagonal) |
| Kerbs | Garden and Road kerbs |

**Key Operational Facts:**
- Three payment channels: Cash, Mobile Money, Bank Deposit
- Strict no credit policy — all payments upfront
- Physical receipts printed on-site for customers during truck loading
- URA tax filing done online (VAT 18%)
- No cloud backup — records on single laptop plus physical receipts and books
- Workers paid daily in cash, no formal contracts, initial attendance capture is Sales Manager's memory; payroll record keeping for verification likely exists but not observed
- Production area has block-making machinery (vibrators, moulds, mixers) observed on site
- Site has CCTV cameras
- Customers transport their own purchases by truck

## Project Overview

This repository holds the Requirements Engineering deliverables produced for a small Ugandan construction materials business. The work applies the five phases of Requirements Engineering (Elicitation, Analysis, Specification, Validation and Management) to a real site, and feeds a downstream SWE1205 Database Programming build.

The system being specified is a Dual Phase Operations Management System.

- **Phase 1 (Day):** Real Time Point of Sale — processes individual sales, calculates VAT, updates inventory, prints physical receipts for customers as trucks load.
- **Phase 2 (Evening):** End of Day Reconciliation Engine — balances multi channel payment drawers (Cash, Mobile Money, Bank Deposit), logs operational expenses, computes cash variances (deficit/surplus), generates daily summary report for the Business Owner.

## Repository Layout

```
CURATED_DATA.md                                         Curated knowledge base (facts, synthesis, gaps, decisions)
Phase1_Elicitation-and-Stakeholder-Analysis.docx       Phase 1 deliverable
Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx  Phases 2-5 master deliverable
Phase2-5_Project-Deliverables-Guide.docx               Deliverables guide
PhaseFinal_Grand-Project-Presentation.pptx             Phase Final: presentation deck (PPTX)
PhaseFinal_Grand-Project-Presentation-Backup.docx      Phase Final: presentation deck (DOCX backup)
build/                                                 Build pipeline (specs + scripts)
project_deliverables/                                  Generated deliverables
reference_data/                                        Raw input documents + chat export
```

## Document Set

| Document | Title | Phase | Status | File |
|---|---|---|---|---|
| 1 | Requirements Elicitation and Stakeholder Analysis | Phase 1 | Complete | Phase1_Elicitation-and-Stakeholder-Analysis.docx |
| 2 | Specification, Traceability, and Management (Master) | Phases 2-5 | Complete | Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx |
| 9 | Grand Project Presentation Deck | Phase Final | Complete | PhaseFinal_Grand-Project-Presentation.pptx |
| 10 | User Manual / SOP | Phase Final | Pending | — |
| — | Project Deliverables Guide | Reference | Complete | Phase2-5_Project-Deliverables-Guide.docx |

**Note:** Documents 3 through 8 from the original roadmap (SRS, RTM, V&V Plan, Management Plan, ER Diagram, Physical DB Design) have been consolidated into the single Master Document (Document 2) per the corrected roadmap.

## Phase Mapping

| Course Period | RE Phase | Deliverables | File |
|---|---|---|---|
| Week 2 (Sep 15) | Phase 1: Elicitation & Stakeholder Analysis | Stakeholder Register, Power/Interest Matrix, Elicitation Report, Field Visit Log, Challenges & Synthesis | Phase1_Elicitation-and-Stakeholder-Analysis.docx |
| Weeks 3-4 | Phase 2 & 3: Analysis & Specification | SRS (IEEE 830), Functional & Non-Functional Requirements, Use Cases, RTM | Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx (Parts 1-2) |
| Weeks 5-6 | Phase 4 & 5: Validation & Management | V&V Plan, Requirements Management Plan, Change Control, Version Control | Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx (Parts 3-4) |
| SWE1205 | Database & System Design | ER Diagram, Data Dictionary, Stored Procedures, Triggers, Views | Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx (Part 5) |
| End of Semester | Phase Final: Grand Presentation | Presentation Deck, User Manual / SOP | PhaseFinal_Grand-Project-Presentation.pptx + Doc 10 (pending) |
| Ongoing | Reference | Project Deliverables Guide | Phase2-5_Project-Deliverables-Guide.docx |

## Architecture

The system follows a Dual Phase architecture established from ground observations:

- **Phase 1 (Day):** Real Time Point of Sale — processes individual sales, calculates VAT, updates inventory, prints physical receipts for customers as trucks load.
- **Phase 2 (Evening):** End of Day Reconciliation Engine — balances multi channel payment drawers (Cash, Mobile Money, Bank Deposit), logs operational expenses, computes cash variances (deficit/surplus), generates daily summary report for the Business Owner.

## Key Corrections from Original Roadmap

| Original Assumption | Corrected Reality |
|---|---|
| End of Day batch only system | Dual Phase: Real Time POS by day + Evening Reconciliation |
| Credit/Debtors module needed | Excluded: strict no credit policy |
| Real time remote dashboard for Owner | Excluded: Owner visits daily; async dashboard only |
| Sept 15 presentation deadline | Removed: date passed; Grand Presentation is end of semester |
| Concept Note as source | Discarded: ground truth overrides |
| Phase 1 includes system design | Corrected: Phase 1 is As Is only; design in SRS |

## Format Standard

All documents are generated from JSON specs by `build/scripts/build_docx.py` and `build/scripts/build_pptx.py` and conform to fixed standards.

### Word Documents (.docx)

| Property | Value |
|---|---|
| Font | Times New Roman |
| Size | 12 pt |
| Colour | Black |
| Line spacing | 1.15 |
| Bold | Headings, table headers and lead in phrases only |
| Punctuation | Plain ASCII, no quotes, semicolons, hyphens or dashes |
| Page | A4, 25.4 mm margins |

### PowerPoint Presentations (.pptx)

| Property | Value |
|---|---|
| Font | Arial |
| Size | 18 pt body, 20 pt subtitle, 32 pt title |
| Colour | Black |
| Background | White |
| Bold | Headings, table headers, lead in phrases only |
| Punctuation | Plain ASCII, no quotes, semicolons, hyphens or dashes |

## Build Commands

To rebuild Document 1:
```bash
python3 build/scripts/make_spec_doc01.py
python3 build/scripts/build_docx.py build/specs/spec_doc01.json project_deliverables/Phase1_Elicitation-and-Stakeholder-Analysis.docx
```

To rebuild Master Document (Phases 2-5):
```bash
python3 build/scripts/build_docx.py build/specs/spec_master.json project_deliverables/Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx
```

To rebuild Presentation Deck:
```bash
python3 build/scripts/build_pptx.py build/specs/spec_presentation_pptx.json project_deliverables/PhaseFinal_Grand-Project-Presentation.pptx
```

To rebuild Project Deliverables Guide:
```bash
python3 build/scripts/build_docx.py build/specs/spec_guide.json project_deliverables/Phase2-5_Project-Deliverables-Guide.docx
```

## Evidence Standard

The repository distinguishes three kinds of statement throughout.

- **Fact:** Something observed or stated at the site.
- **Synthesis:** A reasoned inference drawn from facts plus the documented operational norms of Ugandan construction SMEs, always labelled as such.
- **Gap:** Something that could not be obtained at all. Unresolvable gaps are written up as documented limitations rather than filled with plausible detail, because the site could not be revisited and the project scope is fixed.

## Repository

URL: https://github.com/mugmarp/requirements-engineering-project-exercise
Branch: main