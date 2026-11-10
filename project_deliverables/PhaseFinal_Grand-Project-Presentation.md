# Deniz Construction Management System

Group K | SWE2102 Requirements Engineering | 10 November 2026

## 1. Deniz Construction Management System

Deniz Construction Limited, Mbarara

Group K | SWE2102 Requirements Engineering

Mbarara University of Science and Technology

10 November 2026

**Speaker notes**

Speaker 1 | 30 seconds. Introduce the client, the project and Group K.

Timing. Fourteen minutes of content and one minute for handoffs, followed by about five minutes of questions. Each of the ten members should speak briefly and prepare to explain their actual contribution. Speaking slots are rehearsal assignments, not contribution claims.

Source: Groups Presentation Guide for SWE2102, 10 November 2026.

## 2. Project overview

**Client and products**

Deniz Construction Limited, Mbarara, produces and sells concrete blocks, pavers and kerbs.

**Operational problems**

One Sales Manager handles supervision, sales, wages, records and taxes. Cash shortages are worked out manually, attendance relies on memory, and digital records lack cloud backup.

**Users and affected stakeholders**

The Sales Manager operates the system. The Owner reviews daily reports. Workers' attendance is recorded by the manager.

**Scope**

Day: record paid sales, update stock and print receipts. Evening: log cash expenses, compare counted cash with expected cash and save the daily report.

**Speaker notes**

Speaker 2 | 1.5 minutes. Explain the concentration of work in the Sales Manager role and the manual reconciliation problem. Records exist on the computer and in physical books and receipts; the ability to reconstruct digital records from paper was not established.

The scope is a proposed response to those findings. Observing receipts does not establish the existing software's stock or tax calculation logic. Workers are attendance subjects, not confirmed self-service users.

Sources: CURATED_DATA.md, operational facts and locked dual-phase design; Phase 1 source, business context and problem statement.

## 3. Primary and secondary stakeholders

| Stakeholder | Classification | Role or direct impact |
|---|---|---|
| Sales Manager | Primary | Daily sales, attendance and cash reconciliation |
| Business Owner | Primary | Operational and financial oversight |
| Site Workers | Primary | Attendance and daily wage eligibility |
| Customers / Builders | Primary | Purchases, payments and receipts |
| URA | Secondary | External tax and fiscal requirements |

Primary stakeholders participate directly or are directly affected. Secondary stakeholders provide external oversight or support.

**Speaker notes**

Speaker 3 | 1.5 minutes. State the classification rule before explaining the table. Primary and secondary are not rankings of importance and are independent of whether someone was interviewed.

The Sales Manager is the main system operator. The Owner is a primary stakeholder and report user, labelled CEO in the prototype. Workers and customers are affected parties without application accounts.

Keep the detailed power and interest assessment in Phase 1. Worker and customer interest was not elicited. The Secretary was named earlier but not met, so classification and duties remain unverified.

Source. Phase 1, Sections 4.1 and 4.2. Stakeholder classification is group analysis based on direct participation or effect, not an additional field finding.

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

Speaker 4 | 1 minute. Explain direct observation and what it established about receipt printing during truck loading.

Speaker 5 | 1.5 minutes. Explain the semi-structured interview and the limits of one visit. Name one finding, one challenge and the unresolved receipt and tax details.

The challenge is incomplete access and verification. Do not infer deliberate withholding or label the Sales Manager defensive. The Owner's preferred first metric and the workers' own account of attendance remain unverified.

Sources: CURATED_DATA.md; Phase 1 source, stakeholder analysis, elicitation methods and documented limitations.

Interview Q&A. Topics covered include the normal working day, payment methods, upfront payment, records, cash shortages, attendance and online tax filing. Suitable question wordings include: Walk us through a normal day; what payment methods are accepted; can customers take products before payment; how are cash differences investigated; how is attendance determined? These are reconstructed topic prompts, not claimed verbatim interview notes.

Proposed inventory observation. Follow one product type through an opening physical count, new production, customer loading, returns and damage. Use the same unit in physical counts, receipts and records. Expected closing stock equals opening stock plus production and returns, minus dispatches, damage and other recorded removals. Compare with a closing physical count and reconcile books with computer records. This observation was not completed during the visit. Bulk truck loading was observed, but the counting method and a physical stock reconciliation were not verified.

## 5. Key requirements

**Sale entry and receipts (REQ-FUN-SAL-01/04)**

Post a fully paid sale to an open business date. Save the sale and stock changes together, then make its receipt available for printing.

**Cash expenses (REQ-FUN-REC-02)**

Record each cash expense against its business date so cash paid out is included in expected-cash calculations.

**Cash reconciliation (REQ-FUN-REC-04/05)**

Compare physical cash with expected cash. Require an explanation for a difference and save one final report for the date.

**Offline operation (REQ-NFR-PER-01)**

Standalone target: with internet off, save a sale, update stock and print a receipt. After restart, the sale and stock must remain correct.

**Speaker notes**

Speaker 6 | 1.5 minutes. Link each requirement to user needs. Explain the observable offline pass/fail condition as a future standalone target, not a capability established by the hosted web prototype.

Planned acceptance test: disconnect internet before opening the installed standalone app; post a paid sale; verify stock deduction; print on the target physical printer; restart the app and reopen the saved receipt. Pass only if all steps succeed without an internet connection. This is an observable pass/fail condition, not an invented response-time target.

Source: Master specification, REQ-FUN-SAL-01/04, REQ-FUN-REC-02/04/05 and REQ-NFR-PER-01. The restart check makes persistence explicit in the presentation's acceptance criterion.

## 6. Two user stories

**US-01 Record a fully paid sale**

As a Sales Manager, I want to record a fully paid sale and issue a receipt, so that each collection has a payment record and stock stays accurate.

Accept when payment is complete, insufficient stock rejects the whole sale, and retrying the same submission creates no duplicate.

**US-02 Reconcile and close the date**

As a Sales Manager, I want to compare counted cash with expected cash and explain any difference, so that the Owner can review the financial position for the day.

Accept when differences require a reason, closing saves and locks the date, and a repeated close returns the saved report.

**Speaker notes**

Speaker 7 | 1 minute. Explain US-01 under EPIC-01, Daily sales and receipting. It connects the observed customer collection workflow to an atomic paid sale and printable receipt.

Speaker 8 | 1 minute. Explain US-02 under EPIC-02, Daily cash reconciliation. Expected cash is opening cash plus cash sales minus cash expenses. Variance is counted cash minus expected cash.

The master specification, Section 5, contains full acceptance criteria, existing requirement links and named verification cases. Physical printer output and stakeholder acceptance remain unverified.

An epic groups a larger capability. A user story describes an outcome. Acceptance criteria define observable completion. Tasks are implementation work, and a backlog is the prioritised collection. These are derived stories, not stakeholder quotations.

The presentation guide assigns Group K Elicitation. Stories are supporting project examples. The dedicated Agile user-story prompt belongs to Group B, so do not replace the elicitation discussion with an Agile lecture.

Sources. Master specification, Section 5, US-01 and US-02. Presentation guide, Group K and Group B prompts.

## 7. Close of Day prototype

![Saved Close of Day report](PhaseFinal_Close-of-Day.png)

Sample figures: UGX 450,000 expected | UGX 445,000 counted | UGX 5,000 deficit

**Speaker notes**

Speaker 9 | 2 minutes. Show the saved sample report for 9 November 2026. Zero opening cash plus UGX 500,000 cash sales minus UGX 50,000 cash expenses gives UGX 450,000 expected. The UGX 445,000 count produces a UGX 5,000 deficit and requires a reason.

The sample moved to 9 November so 10 November remains open for demonstration. The saved report must reopen unchanged; a second close returns the same snapshot. A different business date retains its own activity.

Source: current DCMS sample database, instance/operations-20261110.sqlite3, business date 2026-11-09. All screenshot figures are synthetic.

Technical Q&A: the SQLite web implementation posts sales and stock atomically in application services. The proposed SWE1205 database design separately describes Sales_Items triggers, stored procedures and linked sale adjustments. Those design artifacts are not all implemented web features. Bank statement allocations do not create sales or rewrite saved cash closes.

Presenter detail. Recorded Mobile Money and Bank Deposit activity is not physical cash. Wage eligibility is not proof of payment and must not be subtracted again unless an actual payout is recorded as an expense. The variance explanation records the manager account of the discrepancy, not independent proof of its cause. A saved close is not an Owner approval.

## 8. Reflection and remaining work

**Lesson from elicitation**

Daytime receipt printing corrected our end-of-day focus. The system needed immediate sales recording as well as evening reconciliation.

**Working web prototype**

Paid sales, printable receipts, stock, attendance, cash reconciliation, VAT summaries and statement matching. Sales Manager and CEO account access.

**Remaining work**

Build the standalone offline application. Verify physical printing, receipt fields and tax treatment. Stakeholder acceptance and automatic nightly backup remain outstanding.

**Speaker notes**

Speaker 10 | 2.5 minutes. Explain the lesson: observation and the interview together revealed both phases of the working day. Receipt timing was observed, but receipt fields, existing stock logic and detailed tax calculations were not established.

Current release. Hosted web application at https://dcms.tirallab.page. Sales Manager performs operations. CEO is the Owner report account with read-only access. Role authentication does not establish per-change operator attribution or database-level roles.

Remaining work. Standalone installation and offline acceptance, target physical printer testing, automated encrypted cloud backup and stakeholder acceptance. Sales VAT summaries are not input VAT, final tax payable or EFRIS submission. Banking is statement allocation, not a live bank feed.

Q&A. Approximately five minutes. Each member should explain their actual contribution and one decision, requirement or course concept. No personal contribution has been invented.

Sources. Phase 1 findings, master specification delivery stages and Section 5, implementation status, deployment guide and SWE2102 presentation guide.
