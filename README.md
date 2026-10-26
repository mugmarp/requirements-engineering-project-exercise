# Requirements Engineering Project Exercise

Group K, SWE2102 Requirements Engineering, BSE Year II
Mbarara University of Science and Technology (MUST)

Client case study: Deniz Construction Limited, Ishanyu-Bushenyi Road, Mbarara, Uganda

## Project overview

This repository holds the Requirements Engineering deliverables produced for a
small Ugandan construction materials business. The work applies the five phases
of Requirements Engineering (Elicitation, Analysis, Specification, Validation
and Management) to a real site, and feeds a downstream SWE1205 Database
Programming build.

The system being specified is a Dual Phase Operations Management System.
During the day, it functions as a Real Time Point of Sale to process individual
sales, calculate VAT, update inventory, and print physical receipts. In the
evening, it functions as an End of Day Reconciliation Engine, allowing the
Sales Manager to balance multi channel payment drawers, log operational
expenses, compute cash variances, and generate a daily summary report for the
Business Owner.

## Repository layout

```
CONTEXT.md                                          Verified fact base and assumptions register
DOC-01-Elicitation-and-Stakeholder-Analysis.md     Document 1, markdown source
DOC-09-Grand-Project-Presentation-Deck.pptx        Document 9, presentation
MASTER-Requirements-Specification-Traceability-Management.docx  Master: SRS + RTM + V&V + Management + DB
PROJECT-DELIVERABLES-GUIDE.docx                    Deliverables guide
specs/                                              JSON content specifications
scripts/                                            Build toolchain
project_deliverables/                              Generated deliverables
context/                                           Course input documents
```

## Document set

| Document | Title | Status |
|---|---|---|
| 1 | Requirements Elicitation and Stakeholder Analysis | Complete |
| 2 | Specification, Traceability, and Management | Complete |
| 9 | Grand Project Presentation Deck | Complete |
| 10 | User Manual / SOP | Pending |
| - | Project Deliverables Guide | Complete |

Note: Documents 3 through 8 from the original roadmap (SRS, RTM, V&V Plan, Management Plan, ER Diagram, Physical DB Design) have been consolidated into the single Master Document (Document 2) per the corrected roadmap.

## Architecture

The system follows a Dual Phase architecture established from ground observations:

- **Phase 1 (Day):** Real Time Point of Sale - processes individual sales, calculates VAT, updates inventory, prints physical receipts for customers as trucks load.
- **Phase 2 (Evening):** End of Day Reconciliation Engine - balances multi channel payment drawers (Cash, Mobile Money, Bank Deposit), logs operational expenses, computes cash variances (deficit/surplus), generates daily summary report for the Business Owner.

## Format standard

All documents are generated from JSON specs by `scripts/build_docx.py` and `scripts/build_pptx.py` and conform to fixed standards.

### Word documents (.docx)
| Property | Value |
|---|---|
| Font | Times New Roman |
| Size | 12 pt |
| Colour | Black |
| Line spacing | 1.15 |
| Bold | Headings, table headers and lead in phrases only |
| Punctuation | Plain ASCII, no quotes, semicolons, hyphens or dashes |

### PowerPoint presentations (.pptx)
| Property | Value |
|---|---|
| Font | Arial |
| Size | 18 pt body, 20 pt subtitle, 32 pt title |
| Colour | Black |
| Background | White |
| Bold | Headings, table headers, lead in phrases only |

To rebuild Document 1:
```bash
python3 scripts/make_spec_doc01.py
python3 scripts/build_docx.py specs/spec_doc01.json project_deliverables/DOC-01-Elicitation-and-Stakeholder-Analysis.docx
```

To rebuild Master Document:
```bash
python3 scripts/build_docx.py specs/spec_master.json project_deliverables/MASTER-Requirements-Specification-Traceability-Management.docx
```

To rebuild Presentation Deck:
```bash
python3 scripts/build_pptx.py specs/spec_presentation_pptx.json project_deliverables/DOC-09-Grand-Project-Presentation.pptx
```

To rebuild Project Deliverables Guide:
```bash
python3 scripts/build_docx.py specs/spec_guide.json project_deliverables/PROJECT-DELIVERABLES-GUIDE.docx
```

The repository distinguishes three kinds of statement throughout.

A fact is something observed or stated at the site. A synthesis is a reasoned
inference drawn from facts plus the documented operational norms of Ugandan
construction SMEs, and is always labelled as such. A gap is something that
could not be obtained at all. Unresolvable gaps are written up as documented
limitations rather than filled with plausible detail, because the site could not
be revisited and the project scope is fixed.