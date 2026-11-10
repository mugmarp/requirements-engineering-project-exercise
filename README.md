# Requirements Engineering Project Exercise

Group K, SWE2102 Requirements Engineering, BSE Year II
Mbarara University of Science and Technology (MUST)

Client case study: Deniz Construction Limited, Ishanyu-Bushenyi Road, Mbarara, Uganda

## About Deniz Construction Limited

Deniz Construction Limited is a small Ugandan construction materials SME located on Ishanyu-Bushenyi Road, Mbarara. The business produces and sells concrete blocks, pavers and kerbs. Operations are highly centralised, a single Sales Manager acts as supervisor, cashier, payroll distributor, record keeper and tax filer. The Business Owner visits the site daily to review operations and cash.

**Contact:** 0749858413, 0791069287, 0700 640 242

**Product Catalogue:**

| Category | Products |
|---|---|
| Solid Blocks | 4×8×16, 6×8×16, 8×8×16 inches |
| Hollow Blocks | 4×8×16, 6×8×16, 8×8×16 inches |
| Pavers | 60mm and 80mm thickness (Interlocking, Rectangular, Hexagonal) |
| Kerbs | Garden and Road kerbs |

**Key Operational Facts:**
- Three payment channels: Cash, Mobile Money and Bank Deposit
- Strict no credit policy — all payments upfront
- Physical receipts printed on-site for customers during truck loading
- URA tax filing done online (VAT 18%)
- No cloud backup — records on single laptop plus physical receipts and books
- Workers paid daily in cash, no formal contracts, initial attendance capture is Sales Manager's memory, payroll record keeping for verification likely exists but not observed
- Production area has block-making machinery (vibrators, moulds, mixers) observed on site
- Site has CCTV cameras
- Customers transport their own purchases by truck

## Project Overview

This repository holds the Requirements Engineering deliverables produced for a small Ugandan construction materials business. The work applies the five phases of Requirements Engineering (Elicitation, Analysis, Specification, Validation and Management) to a real site, and feeds a downstream SWE1205 Database Programming build.

The system being specified is a Dual Phase Operations Management System.

- **Phase 1 (Day):** Real Time Point of Sale — processes individual sales, calculates VAT, updates inventory, prints physical receipts for customers as trucks load.
- **Phase 2 (Evening):** End of Day Reconciliation Engine — balances multi channel payment drawers (Cash, Mobile Money, Bank Deposit), logs operational expenses, computes cash variances (deficit/surplus), generates daily summary report for the Business Owner.

## Run the web prototype

The application opens on **Operations Dashboard**. Use the sidebar for Daily records, Daily Sales, Reconciliation, Receipts and Attendance. A selected working date stays with the daily workflows. The dashboard's period filter controls historical reporting independently of today's actions.

From the repository root, create a fresh five-month synthetic dataset and start the server:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m dcms --database instance/overview-demo.sqlite3 init --history
.venv/bin/python -m dcms --database instance/overview-demo.sqlite3 serve --port 8081
```

Open [the local dashboard](http://127.0.0.1:8081). The generator defaults to the current Kampala date and starts five calendar months earlier. Use `init --history --end-date 2026-11-10` to reproduce the presentation dataset. Initialization requires a fresh database path and preserves existing databases. After initialization, run only the `serve` command to reopen the same dataset.

The 10 November dataset includes 756 receipts, 251 cash expenses, 10 fictional workers, 1,290 attendance entries, 128 saved reconciliations and 25 explicitly non-operating dates. It documents opening stock instead of inventing replenishment history. Customer identities, working patterns, rates and volumes are synthetic. Today remains open. The prior date, **9 November 2026**, contains the saved UGX 5,000 deficit example. Today’s Attendance, New sale and Reconcile today actions always target today, even while reviewing older records. **All history** shows the full five months.

For the original small worked example, use `init --demo` with a different fresh database path. That fixture retains the 10 November reconciliation inputs and 11 November open date used in the original tests and presentation rehearsal.

The **Attendance** tab lets the Sales Manager add workers with unique codes and daily rates, then mark them Present or Absent for an open business date. Only Present workers enter the payroll eligibility total. Closing the day saves the headcount and eligibility amount and locks that date's attendance. Record wages as cash expenses when actually paid. Existing databases migrate automatically at server startup. Reports closed before attendance was introduced keep their original financial totals and have no captured attendance figures.

Run the checks with `.venv/bin/python -m unittest discover -s tests -v`. To change the sample VAT rate, use `.venv/bin/python -m dcms --database instance/demo.sqlite3 set-vat 18`. Changes apply to future sales.

For hosting, put the database on persistent local storage for a single app instance. Set `DCMS_DB_PATH`, `DCMS_USERS_FILE` and a stable `DCMS_SECRET_KEY` through the host's environment. Use HTTPS and `--secure-cookies`. The login dropdown offers Sales Manager (`sales_manager`, daily operations) and CEO (`ceo`, read-only reports). Both requested sample passwords are `demo`. See [deployment and account setup](DEPLOYMENT.md). The older `DCMS_DEMO_PASSWORD` HTTP Basic mode remains available when no account file is configured. Use sample data in the hosted prototype. The standalone offline desktop app is a separate release described in the [implementation plan](IMPLEMENTATION_PLAN.md).

## Repository Layout

```
CURATED_DATA.md                                         Curated knowledge base (facts, synthesis, gaps, decisions)
Phase1_Elicitation-and-Stakeholder-Analysis.docx       Phase 1 deliverable
Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx  Phases 2-5 master deliverable
Phase2-5_Project-Deliverables-Guide.docx               Deliverables guide
PhaseFinal_Grand-Project-Presentation.pptx             Phase Final: presentation deck (PPTX)
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
| 10 | User Manual / SOP | Phase Final | Complete | User-Manual-SOP.docx |
| — | Project Deliverables Guide | Reference | Complete | Phase2-5_Project-Deliverables-Guide.docx |

**Note:** Documents 3 through 8 from the original roadmap (SRS, RTM, V&V Plan, Management Plan, ER Diagram, Physical DB Design) have been consolidated into the single Master Document (Document 2) per the corrected roadmap.

## Phase Mapping

| Course Period | RE Phase | Deliverables | File |
|---|---|---|---|
| Week 2 (Sep 15) | Phase 1: Elicitation & Stakeholder Analysis | Stakeholder Register, Power/Interest Matrix, Elicitation Report, Field Visit Log, Challenges & Synthesis | Phase1_Elicitation-and-Stakeholder-Analysis.docx |
| Weeks 3-4 | Phase 2 & 3: Analysis & Specification | SRS (IEEE 830), Functional & Non-Functional Requirements, Use Cases, RTM | Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx (Parts 1-2) |
| Weeks 5-6 | Phase 4 & 5: Validation & Management | V&V Plan, Requirements Management Plan, Change Control, Version Control | Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx (Parts 3-4) |
| SWE1205 | Database & System Design | ER Diagram, Data Dictionary, Stored Procedures, Triggers, Views | Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx (Part 5) |
| End of Semester | Phase Final: Grand Presentation | Presentation Deck, User Manual / SOP | PhaseFinal_Grand-Project-Presentation.pptx + User-Manual-SOP.docx |
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

All documents are generated from JSON specs by `build/scripts/build_docx.py` and `build/scripts/build_pptx.mjs` and conform to fixed standards.

### Word Documents (.docx)

| Property | Value |
|---|---|
| Font | Times New Roman |
| Size | 12 pt |
| Colour | Black |
| Line spacing | 1.15 |
| Bold | Headings, table headers and lead in phrases only |
| Punctuation | Plain ASCII only. No curly quotes, no semicolons, no colons mid-sentence, no Oxford commas (no comma before and). Hyphens and dashes only in compound words. Bullets and numbered lists may use standard punctuation. |
| Page | A4, 25.4 mm margins |

### PowerPoint Presentations (.pptx)

| Property | Value |
|---|---|
| Font | Arial |
| Size | 18 pt body, 20 pt subtitle, 32 pt title |
| Colour | Black |
| Background | White |
| Bold | Headings, table headers, lead in phrases only |
| Punctuation | Plain ASCII only. No curly quotes, no semicolons, no colons mid-sentence, no Oxford commas (no comma before and). Hyphens and dashes only in compound words. Bullets and numbered lists may use standard punctuation. |

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

To rebuild the presentation deck, use Node.js with `@oai/artifact-tool` available to the builder. The third argument supplies the screenshot for slide 7. The optional fourth and fifth outputs regenerate Markdown and the document-outline JSON from the canonical slide JSON.
```bash
node build/scripts/build_pptx.mjs build/specs/spec_presentation_pptx.json project_deliverables/PhaseFinal_Grand-Project-Presentation.pptx project_deliverables/PhaseFinal_Close-of-Day.png project_deliverables/PhaseFinal_Grand-Project-Presentation.md build/specs/spec_presentation.json
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

## Requirements Engineering Methods

The following table maps each RE phase to the techniques applied and the deliverable where they are documented.

| Phase | Technique | Applied In |
|---|---|---|
| **Elicitation** | Direct Observation, Semi-Structured Interview, Environmental Scan | `Phase1_Elicitation-and-Stakeholder-Analysis.docx` — Sections 1.3, 5 |
| **Analysis** | Power/Interest Stakeholder Mapping, Gap Analysis, Strategic Business Synthesis | `Phase1_Elicitation-and-Stakeholder-Analysis.docx` — Sections 4, 6, 7 |
| **Specification** | IEEE 830 Structure, Hierarchical Requirement IDs (REQ-FUN/NFR-XXX-NN), Use Cases | `Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx` — Parts 1-2 |
| **Traceability** | Requirements Traceability Matrix (Problem → Requirement → DB Artifact) | `Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx` — Part 2 |
| **Validation** | Walkthroughs, URA Compliance Check, Gap Closure Verification | `Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx` — Part 3 |
| **Verification** | Unit Tests (VAT, Inventory, Receipt, Drawer, Variance, Attendance, RBAC), Integration Test | `Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx` — Part 3 |
| **Management** | Change Control Board (Owner + Group K), Version Control (Git), Requirements Attributes | `Phase2-5_SRS-Traceability-VV-Management-DB-Design.docx` — Part 4 |

## Repository

URL: https://github.com/mugmarp/requirements-engineering-project-exercise
Branch: main

## Taxes, Workers and Banking

The current module preview uses `instance/operations-20261110.sqlite3`. To reopen it:

```bash
.venv/bin/python -m dcms --database instance/operations-20261110.sqlite3 serve --port 8081
```

- **Taxes:** Choose a calendar month, inspect sales excluding VAT, recorded sales VAT and totals including VAT, drill into receipts, or export CSV. This is a sales report, not a VAT return, input-tax claim or calculation of VAT payable. EFRIS submission and fiscal document generation are not connected. The monthly filing reminder follows [URA guidance](https://ura.go.ug/en/ask-ura-commissioner-general-42/). Confirm the actual VAT registration, TIN, taxable supply classifications, tax point and adjustment treatment before operational use. PAYE, withholding, income tax and purchase/input VAT are outside this report. See the [URA EFRIS handbook](https://ura.go.ug/en/efris-handbook/).
- **Workers:** Register a worker with a start date and daily rate. Open the worker record to schedule a future rate or last working date. Historical attendance uses saved rate snapshots. A worker is shown only within their roster dates. Attendance corrections require a reason and check for a stale previous status. Unmarked workers are shown explicitly and require acknowledgement before a day closes. Wage eligibility is a gross amount, separate from cash wages paid and payroll deductions.
- **Banking:** Register a UGX account using a label, bank name and last four digits. Select that account on new Bank Deposit sales. Import a statement using CSV preview, then confirm. Allocate statement credits against existing bank-paid receipts; partial and combined allocations are supported. Reversals require a reason and retain events. Matching does not create sales, alter cash or rewrite closed daily reports. Bank fees and transfers are shown for separate review, not automatically treated as sales. No live feed, bank login or transfer is implemented.

Statement CSV columns must be exactly `id,date,reference,description,credit,debit`. Dates use `YYYY-MM-DD`; amounts use plain UGX decimal values without thousands separators. Supply stable transaction IDs from the source; identical IDs within an account are skipped, while changed values are rejected atomically. Import at most 500 rows per batch. Source files with different formats need deliberate conversion to this template. These are internal import/export formats, not URA upload templates.

VAT settings now have effective dates. For example, an administrator can schedule a rate using `set-vat PERCENT --effective-from YYYY-MM-DD`. The effective date must follow existing sales. Changing a rate never recalculates a posted receipt. The stored invoice-level rounding policy remains a prototype convention to verify during fiscal integration.

The sample-data indicator comes from dataset metadata. Worker names, customer names, expenses and calendar reasons no longer repeat “Demo”. Historical generation skips today's shift events that have not yet occurred. Earlier presentation databases are preserved; use a new filename to regenerate samples. Imported sample bank rows are illustrative and do not establish a real bank balance.
