# Presentation speaking guide

Group K's allocated topic is Elicitation. The eight slides allow about fourteen minutes of content and one minute for handoffs, followed by about five minutes of questions. Each member should speak and explain their actual contribution. Rehearse rather than reading paragraphs verbatim.

## Slide 1 - Introduce the project

Introduce Group K, Deniz Construction Limited in Mbarara and the construction materials business. Explain that the presentation follows the problem, elicitation findings, requirements and working prototype. Allow about thirty seconds.

## Slide 2 - Problem and scope

Explain the concentration of responsibilities in the Sales Manager role, manual cash reconciliation, memory-based attendance and digital backup vulnerability. Records exist on the computer and in physical books and receipts. Explain daytime paid sales and receipts, followed by evening cash reconciliation. Do not claim the business had no records.

## Slide 3 - Stakeholders

Define primary as direct participation or direct effect. Sales Manager, Owner, workers and customers are primary. URA provides external oversight and is secondary. This is separate from power and interest, interview availability and application access. The main operator is Sales Manager. The Owner report account is labelled CEO. Workers and customers do not have app accounts. The Secretary role remains unverified.

## Slide 4 - Elicitation

Explain direct observation and the semi-structured Sales Manager interview during one visit. Observation showed receipt printing during customer collections. The interview covered payment channels, upfront payment, online tax filing, attendance and cash shortages. The finding changed an initial end-of-day focus into a dual-phase design. Receipt fields, detailed tax calculations and Owner/worker perspectives were not verified. Do not claim deliberate information withholding.

## Slide 5 - Requirements

Link sale entry and receipts to immediate collections, expense logging to cash paid out, and reconciliation to explaining differences. The offline NFR is a future standalone acceptance target. Disconnect internet, post a sale, check stock, print its receipt, restart and verify persistence. The current hosted application needs internet.

## Slide 6 - Stories

US-01 expresses the Sales Manager's need to record a fully paid sale and issue a receipt. Explain payment matching, stock rejection, atomic save and duplicate-submission safety. US-02 expresses the need to compare cash and explain differences. Explain the mandatory reason, saved report, date lock and safe repeated close. These are derived stories, not stakeholder quotations. The SRS contains the detailed criteria.

An epic groups a broad capability such as Daily sales and receipting. A story describes a smaller user outcome. Acceptance criteria define observable completion. Tasks are implementation work. A backlog is a prioritised collection of stories, fixes and technical work. Keep this explanation for questions rather than replacing the elicitation discussion.

## Slide 7 - Saved reconciliation report

Identify the saved sample report for 9 November 2026. Point to the separate Cash, Mobile Money and Bank Deposit totals. Non-cash payments do not belong in the physical cash count.

| Calculation | UGX |
|---|---:|
| Opening cash | 0 |
| Cash sales | 500,000 |
| Less cash expenses | 50,000 |
| Expected cash | 450,000 |
| Counted cash | 445,000 |
| Variance: counted minus expected | -5,000 |

A negative result is a deficit. A positive result is a surplus. A nonzero difference requires an explanation before closing. Closing saves the report and locks the date. Repeating the close returns the existing report. Do not invent the shortage's cause or imply Owner approval from a saved close.

The nine workers and UGX 167,500 describe attendance and wage eligibility. Eligibility is not proof of payment. Do not subtract it again from cash unless an actual payout was recorded as a cash expense. The example figures are synthetic.

## Slide 8 - Reflection

Explain that observation and interviewing revealed different parts of the workflow. Daytime receipt printing corrected an end-of-day-only focus. Distinguish working web features from remaining standalone work, target printer verification, nightly backup and stakeholder acceptance. Tax summaries are not fiscal submission or final tax payable. Bank matching is not a live bank connection.

## Interview question preparation

The following are suitable reconstructed prompts for topics covered, not a claim of preserved verbatim wording:

- Walk us through a normal working day and your responsibilities.
- What payment methods do customers use?
- Can customers take products before completing payment?
- How do you record sales on the computer and in books?
- What do you do when counted cash differs from expected cash?
- How do you identify workers who attended and determine daily wages?
- How do you prepare and submit tax information?

Proposed follow-up questions for unverified details include inspecting a receipt, checking expense records, asking about opening cash, tracing product counting and examining recovery from computer failure. The Owner's own reporting priorities require confirmation.

## Inventory discrepancy question

Observe how products enter stock through production and leave through dispatch. Follow one product type, count it physically and use the same unit in all records. Check loading quantities against sales, books against computer entries, and how damage, returns and replacements are recorded.

Expected closing stock = opening stock + production + returns - dispatches - damage - other recorded removals.

Compare this expectation with a closing physical count. These are proposed observations. During the actual visit, bulk truck loading was observed but the counting method and a stock reconciliation were not verified. Do not claim a confirmed cause of inventory differences. The current app deducts sales stock but does not implement a complete production or stock-adjustment ledger.

## Likely tutor questions

- Why semi-structured interviews? Prepared topics provided direction while follow-up questions explored the manager's answers.
- What did observation add? It revealed daytime receipt printing, which helped establish the need for immediate sale recording.
- Did you interview everyone? No. The Sales Manager was interviewed; other perspectives remain gaps.
- Did users accept the application? Formal stakeholder acceptance remains outstanding. Passing tests verifies implementation, not acceptance.
- Does the web app work offline? Hosted access needs internet. Offline operation belongs to the later standalone release.
- What did you personally contribute? Describe actual work and one decision you can explain. Do not invent assignments.
