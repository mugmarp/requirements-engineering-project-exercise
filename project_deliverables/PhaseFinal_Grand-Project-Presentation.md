# Deniz Construction Management System

Group K | SWE2102 Requirements Engineering | 10 November 2026

## 1. Deniz Construction Management System

Deniz Construction Limited, Mbarara

Group K | SWE2102 Requirements Engineering

Mbarara University of Science and Technology

10 November 2026

**Speaker notes**

Speaker 1 | 30 seconds. Introduce Deniz as a construction materials business producing blocks, pavers and kerbs.

Timing: 14 minutes of presentation content and 1 minute for handoffs, followed by approximately 5 minutes of questions. Speaking slots are rehearsal assignments, not claims of individual contribution. Assign names according to members' actual work.

Source: Groups Presentation Guide for SWE2102, 10 November 2026.

## 2. Group Members

| Name | Registration Number |
|---|---|
| JOAS TAREMWA | 2025/BSE/171/PS |
| ASUMA KADDE KEVIN | 2025/BSE/045/PS |
| SSEBUGWAWO HARRISON | 2025/BSE/161/PS |
| TIBAMANYA DAVIS | 2025/BSE/172/PS |
| EDOU SIMON PETER | 2025/BSE/066/PS |
| MUGENDAWALA MARK PAUL | 2025/BSE/108/PS |
| DAMBYA RACHAEL | 2025/BSE/065/PS |
| OFAMBA JAMES | 2025/BSE/143/PS |
| OSUTA AMEN JOEL | 2025/BSE/152/PS |
| MUSONIRWA IBRAHIM | 2025/BSE/218/PS |

**Speaker notes**

Speaker 1 | 30 seconds. Introduce the ten-member group, then continue to the client problem.

Source: The original Group K roster, retained identically in main and PPT.

## 3. Project overview

**Client and products**

Deniz Construction Limited, Mbarara, produces and sells concrete blocks, pavers and kerbs.

**Operational problems**

One Sales Manager handles supervision, sales, wages, records and taxes. Cash shortages are worked out manually, attendance relies on memory, and digital records lack cloud backup.

**Users and affected stakeholders**

The Sales Manager operates the system. The Owner reviews daily reports. Workers' attendance is recorded by the manager.

**Scope**

Day: record paid sales, update stock and print receipts. Evening: log cash expenses, compare counted cash with expected cash and save the daily report.

**Speaker notes**

Speaker 2 | 2 minutes. Explain the concentration of work in the Sales Manager role and the manual reconciliation problem. Records exist on the computer and in physical books and receipts; the ability to reconstruct digital records from paper was not established.

The scope is a proposed response to those findings. Observing receipts does not establish the existing software's stock or tax calculation logic. Workers are attendance subjects, not confirmed self-service users.

Sources: CURATED_DATA.md, operational facts and locked dual-phase design; Phase 1 source, business context and problem statement.

## 4. Elicitation: methods and limitations

**Stakeholder access**

The Sales Manager was interviewed. The Owner and workers were not interviewed. Customers are affected and URA sets external requirements.

**Direct observation**

Laptop use and receipts printed during truck loading showed that receipting occurs during the day.

**Semi-structured interview**

The Sales Manager described upfront Cash, Mobile Money and Bank Deposit payments, online tax filing and end-of-day cash shortages.

**Challenge**

Only one visit was possible. Existing receipt fields and detailed tax calculations could not be verified. Those gaps were recorded.

**Speaker notes**

Speaker 3 | 1 minute. Describe whom the group reached and explain what direct observation established: daytime laptop use and receipt printing during truck loading.

Speaker 4 | 1 minute. Explain what the interview added: payment channels, the no-credit rule, online tax filing and the cash-shortage problem. Explain the limits of one visit and unavailable stakeholders.

The challenge is incomplete access and verification. Do not infer deliberate withholding or label the Sales Manager defensive. The Owner's preferred first metric and the workers' own account of attendance remain unverified.

Sources: CURATED_DATA.md; Phase 1 source, stakeholder analysis, elicitation methods and documented limitations.

## 5. Key requirements

**Sale entry and receipts (REQ-FUN-SAL-01/04)**

Post a fully paid sale to an open business date. Save the sale and stock changes together, then make its receipt available for printing.

**Cash expenses (REQ-FUN-REC-02)**

Record each cash expense against its business date so cash paid out is included in expected-cash calculations.

**Cash reconciliation (REQ-FUN-REC-04/05)**

Compare physical cash with expected cash. Require an explanation for a difference and save one final report for the date.

**Offline operation (REQ-NFR-PER-01)**

The standalone application shall record sales, update stock and print receipts without internet access. Saved transactions shall remain available after restarting the application.

**Speaker notes**

Speaker 5 | 1.5 minutes. Connect the functional requirements to immediate receipting and explaining cash differences. Receipt printing follows a successful transaction; a print failure must allow reprinting without posting another sale.

Speaker 6 | 1 minute. Explain the offline requirement as a requirement for the future standalone application, not a capability already established by the hosted web prototype.

Planned acceptance test: disconnect internet before opening the installed standalone app; post a paid sale; verify stock deduction; print on the target physical printer; restart the app and reopen the saved receipt. Pass only if all steps succeed without an internet connection. This is an observable pass/fail condition, not an invented response-time target.

Source: Master specification, REQ-FUN-SAL-01/04, REQ-FUN-REC-02/04/05 and REQ-NFR-PER-01. The restart check makes persistence explicit in the presentation's acceptance criterion.

## 6. Project example and reflection

| Stakeholder | Power | Interest | Engagement |
|---|---|---|---|
| Business Owner | High | High | Not interviewed |
| Sales Manager | High | High | Interviewed |
| Site Workers | Low | Low | Not interviewed |
| URA | High | Low | External regulator |

**Lesson from elicitation**

Observation corrected our initial focus on end-of-day processing. Receipts were printed during customer collections, so the system needed daytime sales as well as evening cash reconciliation.

The timing was observed. Receipt fields and tax calculations still required validation.

**Speaker notes**

Speaker 7 | 2 minutes. Explain the stakeholder assessment and then the observation that changed the project scope. The initial end-of-day focus did not cover the full working day.

Power and interest are the group's analytical classifications from Phase 1, not measurements or statements verified in interviews with all stakeholders. In particular, do not claim workers personally expressed low interest. Interview access and the regulator's role are recorded separately.

Lesson: combining observation with the interview helped distinguish the initially reported deficit problem from the wider sales workflow. Observation showed when receipting occurred; it did not establish the receipt fields, automatic stock handling or tax calculations.

Sources: Phase 1 stakeholder power/interest table; CURATED_DATA.md, daytime receipting and dual-phase design.

## 7. Close of Day prototype

![Saved Close of Day report](PhaseFinal_Close-of-Day.png)

Sample figures: UGX 450,000 expected | UGX 445,000 counted | UGX 5,000 deficit

**Speaker notes**

Speaker 8 | 1.5 minutes. The screenshot is from the current web prototype, using the saved sample report for 9 November 2026. Point to the business date and separate Cash, Mobile Money and Bank Deposit activity.

Speaker 9 | 1.5 minutes. Cash sales of UGX 500,000 less cash expenses of UGX 50,000 and zero opening cash give UGX 450,000 expected. Physical cash is UGX 445,000, giving a signed variance of minus UGX 5,000. Explain the required reason and the date lock.

The sample moved to 9 November so 10 November remains open for demonstration. The saved report must reopen unchanged; a second close returns the same snapshot. A different business date retains its own activity.

Source: current DCMS sample database, instance/operations-20261110.sqlite3, business date 2026-11-09. All screenshot figures are synthetic.

Technical Q&A: the SQLite web implementation posts sales and stock atomically in application services. The proposed SWE1205 database design separately describes Sales_Items triggers, stored procedures and linked sale adjustments. Those design artifacts are not all implemented web features. Bank statement allocations do not create sales or rewrite saved cash closes.

## 8. Conclusion and remaining work

**System scope**

Paid sales and receipt printing are handled during the day. Cash expenses, physical cash counts and the final report are handled at close.

**Working web prototype**

Sales, receipts, stock deduction, attendance, reconciliation, sales VAT summaries and bank statement matching.

**Remaining verification**

Build and test the standalone application without internet. Verify physical printing, actual receipt fields, tax treatment and worker requirements with the business.

**Speaker notes**

Speaker 10 | 1.5 minutes. Distinguish the working web prototype from the unbuilt standalone application and the remaining stakeholder validation. Do not propose immediate production deployment on the office laptop.

Tax scope: the web report summarises recorded sales VAT. Input VAT, fiscal corrections, EFRIS submission and tax payable are not implemented. Bank scope: imported statement matching and reversals, not a live bank feed or complete bank balance reconciliation.

Q&A | Approximately 5 minutes. Each member should describe their actual contribution and explain one requirement, elicitation finding or limitation. No contribution assignments have been invented.

Sources: IMPLEMENTATION_STATUS.md and IMPLEMENTATION_PLAN.md; master specification verification cases; presentation guide.
