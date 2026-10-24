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

The system being specified is an end of day transactional reconciliation tool.
The Sales Manager at the site is simultaneously supervisor, cashier, paymaster
and tax filer, so she is a single point of failure. She currently uses a single
office PC in the evening to process cash deficits by hand. The system logs each
individual sale and expense as she enters the day receipts, then automatically
computes VAT, updates inventory, tracks the separate payment channels and
produces the end of day reconciliation report.

## Repository layout

```
CONTEXT.md                                          Verified fact base and assumptions register
DOC-01-Elicitation-and-Stakeholder-Analysis.md     Document 1, markdown source
specs/spec_doc01.json                              Document 1 content specification
scripts/build_docx.py                              DOCX builder, project format standard
scripts/make_spec_doc01.py                         Builds the spec from the base text
OUTPUT/                                            Generated deliverables
context/                                           Course input documents
```

## Document set

| Document | Title | Status |
| --- | --- | --- |
| 1 | Requirements Elicitation and Stakeholder Analysis | Complete |
| 2 | Software Requirements Specification and Database Requirements | Planned |
| 3 | Requirements Traceability Matrix | Planned |
| 4 | Validation and Verification Plan | Planned |
| 5 | Requirements Management Plan | Planned |
| 6 | Conceptual Data Model and Data Dictionary | Planned |
| 7 | Physical Database Design | Planned |
| 8 | Grand Project Presentation Deck | Planned |
| 9 | User Manual | Planned |

## Format standard

All documents are generated from JSON specs by `scripts/build_docx.py` and
conform to one fixed standard.

| Property | Value |
| --- | --- |
| Font | Times New Roman |
| Size | 12 pt |
| Colour | Black |
| Line spacing | 1.15 |
| Bold | Headings, table headers and lead in phrases only |
| Punctuation | Plain ASCII, no quotes, semicolons, hyphens or dashes |

To rebuild Document 1:

```bash
python3 scripts/make_spec_doc01.py
python3 scripts/build_docx.py specs/spec_doc01.json OUTPUT/DOC-01-Elicitation-and-Stakeholder-Analysis.docx
```

## Method note

The repository distinguishes three kinds of statement throughout.

A fact is something observed or stated at the site. A synthesis is a reasoned
inference drawn from facts plus the documented operational norms of Ugandan
construction SMEs, and is always labelled as such. A gap is something that
could not be obtained at all. Unresolvable gaps are written up as documented
limitations rather than filled with plausible detail, because the site could not
be revisited and the project scope is fixed.
