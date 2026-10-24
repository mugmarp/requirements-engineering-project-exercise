# Deniz Construction — Verified Context & Fact Base

Status: **single source of truth** for the RE project. Every line is tagged.
- **[FACT]** — stated by you, in your own words, from the ground visit or from the chat. Do not change.
- **[SYNTH]** — Qwen's strategic synthesis, pending your confirmation. Changeable.
- **[GAP]** — no data exists. Cannot be closed. Must be handled by assumption, not invention.
- **[DATE]** — deadline or point-in-time claim. Flagged where inconsistent.

---

## 0. Current working directory

Everything lives in `/home/vm/MUST/REQUIREMENTS/`

- `qwen_deniz_conversation.md` — the full 92-turn Qwen share export (verbatim)
- `context/Group-ALLOCATIONS_1_requirements_engineering.pdf` — the class allocation sheet
- `context/DENIZconceptDOC.pdf` — **not present on this machine.** See §9.

---

## 1. Who you are

- BSE II (Year 2), Software Engineering, **MUST** (Mbarara University of Science and Technology)
- **Group K**, SWE2102 — Requirements Engineering
- Also taking **SWE1205** — Database Programming (referenced repeatedly as the downstream course)
- The actual system build is a database project; the RE work feeds it

**Group K members** (from turn 10, you supplied these):

| Name | Reg No |
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

---

## 2. The organisation

**[FACT]** Client: **Deniz Construction Limited**
**[FACT]** Location: **Ishanyu-Bushenyi Road, Mbarara**, Uganda
**[FACT]** Sector: construction materials SME — produces/sells concrete blocks, pavers
**[FACT]** Size: **small** — "the business seems small", "not yet a large business"
**[FACT]** Contact numbers recorded: **0749858413** and **0791069287**
**[SYNTH]** "Deniz Construction Management System (DCMS)" was the working project name. Qwen proposed renaming to **DPSS — Deniz Point-of-Sale & Site Operations System**. *Not confirmed; project stays DCMS.*
**[SYNTH]** Product mix: solid blocks, hollow blocks, compound pavers. Sold by piece, pallet, or truckload.

---

## 3. Stakeholders

| Stakeholder | Evidence | Notes |
|---|---|---|
| **Owner** (business owner) | [FACT] "the business owner checks every day" | High power, high interest. [GAP] Never interviewed — no direct statement of his needs |
| **Sales Manager** | [FACT] interviewed once; "she" | The absolute center of operations: supervisor, cashier, payroll, records, tax filing. [FACT] Interviewed. Acts as the gatekeeper. |
| **Secretary** | [FACT] named in the original concept note | [GAP] **Never met.** Ground observation confirms the Sales Manager currently performs all data entry and reconciliation. Role retained in schema for future scaling only. |
| **Site workers / Foreman** | [FACT] exist | [GAP] **No chance to talk to them** — a stated, unresolvable gap |
| **Customers / Builders** | [FACT] "clients would mostly be the ones to transport the purchased products" | Buyers of blocks. Pay upfront. Transport own goods by truck. |
| **URA** (Uganda Revenue Authority) | [FACT] "she processes the taxes online" | External regulator; no direct engagement |
| **IT support / maintainer** | [SYNTH] | Not yet identified |

**[GAP] The Secretary is a named stakeholder with zero elicited data.** This is the largest single hole in the stakeholder map.

---

## 4. What you actually observed on the ground

**[FACT] The one site visit already happened.** You went. You could not go back.

| Observation | Status |
|---|---|
| Attendance | Workers **do not take any attendance**. All attendance relies on the Sales Manager's side |
| Sales Manager's role | **Supervisor**, "acting as every territory" — she absorbs most roles |
| Org maturity | "not yet a large business" |
| Backup | **No cloud backup** |
| Payments | **Mobile Money**, **clients depositing into the business bank account**, and **cash** |
| Credit | **Never gives credit — all payments must be made** |
| Tax | "she processes the taxes online" — you **could not see how tax is calculated or filled** |
| Receipts | Receipts exist, **a printer is on site** — but you **could not get what fields are on them** |
| Workers spoken to | **No** — "there was no chance to talk to the workers" |
| Insecurity | Sales Manager raised "insecurity" as a challenge — **never clarified over what** |
| Cameras | Site **does have some cameras** |
| Transport | Clients transport their own purchases (the blocks etc.) |
| Owner behaviour | **Checks every day** → therefore **no remote transfer of business data** |
| Worker contracts | **No legal contract** — "just as many in Uganda or Africa at large" |
| PC | Business has a **PC on site for record keeping**; Sales Manager "mainly uses the PC to process deficit" |
| PC usage timing | **[FACT]** "the laptop was on even when being used" — **during the day it is on and receipts are printed** |
| Truck loading | **[FACT]** "we saw trucks loading in somewhat bulk" — counting method **not identified** |
| Cash storage | **[GAP]** "we could not identify that" |
| Owner's first question | **[FACT]** "i do not think first thing to ask is money, but still we could not identify that" |
| Receipt fields | **[GAP]** "we could not get what field are on the Receipts" |
| Laptop interaction | **[FACT]** "we have seen her interacting with the PC before we could enter into her office again some time" — she interacts with the PC during the day, prints receipts |
| Receipt printing | **[FACT]** Physical receipts are printed for customers as trucks load |

**[FACT] You cannot go back.** "we can not go back to get any more info, and they do not will to give any more info"
**[FACT] You cannot change the project.** "we can not change the the project because we picked it already"

---

## 5. The real problem (post-visit, fact-based)

**[FACT] What was actually found — the reason the concept note is described as "basically dummy":**

- Attendance is entirely the Sales Manager's memory
- The Sales Manager is simultaneously supervisor, cashier, and paymaster — "she's basically the only top management"
- Cash + Mobile Money + bank deposit are three separate payment channels with **no reconciliation tool**
- She **"processes deficit"** on the PC — i.e. she manually computes cash shortages
- There is **no cloud backup**
- She raised **"insecurity"** but would not specify
- She **prints physical receipts** for customers at the time of sale during the day
- She uses the PC during the day for transactions, and in the evening for reconciliation/deficit processing

**[SYNTH] Qwen's consolidated problem statement (superseded by corrected dual-phase design):**
> Operational Bottlenecking and Cash-Handling Vulnerability due to the Sales Manager acting as a single point of failure for supervision, sales, and cash disbursement, combined with informal labor practices and physical cash security risks.

Sub-problems: the "Super-Manager" bottleneck; cash insecurity & till deficits; informal labour with daily cash payouts from memory; manual tax & multi-channel payment reconciliation.

**[SYNTH] CORRECTED SYSTEM DESIGN — Dual-Phase (turns 87, 89, 91):**
The system is a **Real-Time Point of Sale (POS) and Operations Management System** featuring a **dedicated End-of-Day Reconciliation Module**.

- **Phase 1 (Day): Real-Time Transactional Processing** — When a truck arrives, the Sales Manager opens the system, enters quantity, selects payment method (Cash, Mobile Money, Bank), system instantly calculates 18% VAT, deducts stock via trigger, prints physical receipt for client.
- **Phase 2 (Evening): End-of-Day Reconciliation & Deficit Resolution** — She opens the Reconciliation Module; system shows Expected Cash = sum of Cash sales; she logs Operational Expenses (petty cash); system deducts from Cash Virtual Drawer; she enters Actual Cash in hand; system computes Variance (Deficit/Surplus); generates Daily Summary Report for Owner.

This is **not** an "End-of-Day Transactional Auto-Calculation Engine" — that was an incorrect assumption corrected in turns 86-91. It is a **Real-Time POS + End-of-Day Reconciliation Module**.

---

## 6. SWE2102 — the class presentation

**[FACT] From `context/Group-ALLOCATIONS_1_requirements_engineering.pdf`:**

| Date | Group | Topic |
|---|---|---|
| 8 Sep | F | Intro to RE; Overview of SE; Importance of software requirements; Role of RE; Types of Requirements; **Introduction to** the RE Process |
| **15 Sep** | **K** | **Requirements Elicitation; Elicitation Techniques (Interviews, questionnaires, workshops, brainstorming, observations, prototyping, use cases & scenarios); Challenges in Elicitation; Stakeholder Analysis** |
| 22 Sep | C | Requirements Specification; Writing Effective Requirements; Characteristics of good requirements; Templates & standards; SRS documents; IEEE standards for SRS; Natural Language vs Formal Specifications |
| 29 Sep | G | *(same specification topic as C)* |
| 06 Oct | A | Requirements Validation; Techniques; Reviews/inspections/walkthroughs; Prototyping & simulation; Requirements Traceability; Traceability matrices; Validation Tools |
| 13 Oct | I | Requirements Management; Importance of managing changing requirements; Version control & configuration management; Change Management; Change control boards; Impact analysis & risk; Tools (JIRA, IBM DOORS) |
| 20 Oct | B | Agile Requirements Engineering |
| 27 Oct | E | Case Studies and Best Practices |
| 03 Nov | D | Requirements Engineering Tools and Techniques |
| 10 Nov | J | Requirements in the SDLC |

**[FACT] Group K presents 15 September.** Topic = **Elicitation** (not Specification, not Validation).

**[FACT] Critical correction you gave (turn 25):** the group allocation is **primarily for the class presentation**. Separately, **each group has its own project** that must apply **all phases** with **robust documentation**. A **grand presentation** happens at the end for all group projects. **Applying the phases is NOT tied to those class presentation dates.**

**[FACT] The Sept 15 date has passed** — you stated on 6 Oct that it was "nothing like freedom or more time". The class presentation either happened or was missed; it is not a live deadline.

**[DATE] Inconsistencies to resolve — do not assume:**
- Turn 28 is dated **06 October 2026**; the share page header says **October 10, 2026**; the export was made **24 October 2026**. The conversation spans roughly two weeks.
- Qwen repeatedly wrote **"Sept 15th presentation"** and **"September 15th"** throughout later turns (42, 44, 46), even after your 6 Oct message. **These are stale references — the date had already passed.** The *grand* presentation is end-of-semester.
- Qwen once wrote a presentation section titled "How to Use This for Your SWE2102 Class Presentation (Sept 15)" *inside* a response to the fact-based restructure. That is a stale carry-over, not new information.

**[SYNTH] Slide deck already produced (turns 8–10).** 10 slides, plain white, Calibri 24 (you capped it at ≤25), bold only where needed, no images, member list in table form. Group members table included. **This deck is done and is not the current work.**

---

## 7. The requirement set built so far

**Phase 1 — Elicitation** (turn 28): full stakeholder interview guide (Owner / Sales Manager / Secretary), observation checklist (time-motion study, artifact analysis of the "blue books", infrastructure check), Ugandan-context questions (Mobile Money, literacy, power), deliverables to collect (photos, URA form, laptop specs).

**Phase 2 — Analysis & Specification** (turn 30): ghost-worker logic, credit-sales logic, inventory-shrinkage logic; NFRs (offline, RBAC, audit trail, usability); ER mapping; stored procedures (`CalculateVAT`) and triggers (stock update); validation "what-if" questions; deliverables (ER diagram, use case diagrams, SRS outline).

**Deepened SRS requirements** (turns 38, 40, 46) — the ones with IDs:

| ID | Requirement |
|---|---|
| FR-01.01 | Attendance logging — unique Worker_ID + Date; reject duplicate same-day entries |
| FR-01.02 | Payroll linkage — SQL JOIN Workers×Attendance for daily payroll |
| FR-02.01 | Automated VAT calculation — MySQL stored procedure `CalculateVAT`, 18% of subtotal |
| FR-02.02 | Sequential receipting & voiding — no hard delete; mark VOIDED with mandatory reason |
| FR-03.01 | Automated stock deduction — AFTER INSERT trigger on Sales |
| FR-03.02 | Inventory alerts — flag when Current_Stock ≤ Reorder_Level |
| FR-04.2 | Void only if no payment recorded against the receipt |
| FR-04.3 | Void metadata — retain receipt number, flag VOID, mandatory reason |
| FR-01 | Batch end-of-day entry — input daily totals by payment method |
| FR-02 | Daily reconciliation report — expected cash, actual cash, variance, notes |
| FR-03 | Receipt generation — 8 mandatory fields incl. payment method |
| FR-04 | Flexible unit of measure — `Unit_of_Measure` VARCHAR |
| FR-05 | Petty cash / operational expense log — eliminates unexplained deficits |
| FR-06 | Operational-first dashboard — operations metrics above financials |
| NFR-01.01 | Offline resilience — up to 500 local transactions, sync within 5 min of reconnection |
| NFR-02.01 | RBAC — Secretary blocked from Total_Profit and Tax_Liability |
| NFR-02.2 | Void log & voided amounts visible only to Owner/Auditor |
| NFR-03.01 | Usability — high-contrast icons, ≤3 taps to log one worker |
| NFR-04.01 | RBAC at DB + UI level |
| NFR-04.02 | Mobile-responsive owner dashboard |
| NFR-05.01 | Automated encrypted cloud backup, Sundays 23:00 EAT |
| NFR-05.02 | Hardware compatibility — reports under 3 seconds |
| UC-04 | Use case: Process a Voided Receipt (main flow + alternative flow) |

**[GAP] The requirement IDs are not yet unified.** FR-01.01 and FR-01 are different numbering schemes from different turns. FR-04.2/FR-04.3 from turn 32 collide with FR-04 from turn 46. **A traceability matrix cannot be built until the IDs are reconciled.**

**[SYNTH] Numbers in the above that are invented targets, not facts:** 500 local transactions, 5-minute sync, ≤3 taps, ≤5 clicks, 3-second reports, 4 GB RAM, Windows 10, 18% VAT, 11:00 PM Sunday backup, 2-hour training. None of these came from the site.

---

## 8. Locked constraints

1. **[FACT] One site visit only.** No follow-up. The stakeholder is unwilling to give more.
2. **[FACT] Project cannot be changed.** It is already picked.
3. **[FACT] No credit sales.** ⇒ no debtors module, no credit-limit logic needed.
4. **[FACT] Owner visits daily.** ⇒ any "remote access" requirement is questionable.
5. **[FACT] Workers were never spoken to.** ⇒ attendance UX requirements rest on synthesis alone.
6. **[FACT] The Secretary was never spoken to.** ⇒ tax/URA requirements rest on synthesis alone.
7. **[FACT] No cloud backup exists today.** ⇒ backup is a genuine gap, not a nicety.
8. **[FACT] Three payment channels:** cash, Mobile Money, bank deposit.
9. **[FACT] URA filing is online** but the calculation method was never observed.
10. **[FACT] Physical receipts printed at time of sale during the day.** System must support real-time POS receipt printing.
11. **[FACT] Evening reconciliation exists.** Sales Manager uses PC in evening for deficit processing and daily summary.
12. **[FACT] Sales Manager is the absolute center of operations.** Supervisor, cashier, payroll, records, tax filing. She is the gatekeeper.

---

## 9. Open items — these are the real risks

| # | Item | Why it matters |
|---|---|---|
| 1 | **`DENIZconceptDOC.pdf` is not on this machine** | Turn 13 references it; Qwen built Phase 1/2 partly on it. Every "from the Concept Note" claim is unverifiable here |
| 2 | **Project name is DCMS** | Qwen proposed renaming to DPSS; you never confirmed. Project stays DCMS. |
| 3 | **Grand presentation date** | Unknown. Qwen keeps saying Sept 15, which has passed |
| 4 | **Requirement ID collisions** | Blocks traceability matrix |
| 5 | **No metric provenance** | 500/5min/3s/18%/4GB all invented — must be labelled as assumptions |
| 6 | **Two stale Qwen errors** | (a) EFRIS mentioned without evidence; (b) "Sept 15" repeated after it passed |
| 7 | **Secretary + workers data voids** | Largest elicitation gaps; must be declared as documented limitations |
| 8 | **SWE1205 database scope** | Is the deliverable an SRS, a schema, or a working app? Not stated |
| 9 | **Dual-phase system not yet reflected in requirement IDs** | Current IDs still reflect end-of-day batch design; need new IDs for real-time POS + evening reconciliation |

---

## 10. What is proven vs assumed

**Proven (from you, directly):**
The site visit happened; the Sales Manager is the single point of failure; no attendance; no cloud backup; three payment channels; no credit; tax filed online; receipts exist with a printer; workers and Secretary never spoken to; no second visit possible; project cannot change; owner checks daily; site has cameras; clients self-transport; workers have no contracts; laptop is on during the day and prints receipts; she processes deficits in the evening; she interacts with PC during the day.

**Assumed (Qwen's synthesis, needs your sign-off):**
Petty cash explains the deficits; cash kept in a locked drawer; owner asks about physical output first; VAT is 18%; specific hardware specs; specific performance targets; product unit-of-measure conventions; the rename to DPSS (rejected).

**Unknown (cannot be closed):**
Receipt field layout; URA calculation method; how truckloads are counted; where cash is kept; who the IT maintainer is; the owner's actual first question; the Secretary's workflow; the workers' attendance reality.

---

## 11. Ground rules for the work ahead

- Nothing gets silently upgraded from [SYNTH] to [FACT]. If you confirm it, it becomes [FACT] and the change is logged.
- Every assumption in the SRS carries an ID and a rationale traceable to a [FACT] or to "Ugandan SME operational model".
- [GAP] items are written into the SRS as **explicit limitations**, not filled with plausible detail.
- Qwen's stale references (Sept 15, EFRIS) are treated as noise unless you confirm them.
- Where the concept note conflicted with the ground truth, **the ground truth wins**.
- **Internal working files (CONTEXT.md, concept note, chat history) are never referenced in final deliverables.** The lecturer sees only "The Site Visit," "Ground Observations," and "Stakeholder Interviews."

---

## 12. Corrected Document 1 status

Document 1 has been corrected to match the dual-phase reality (turns 89, 91). Key changes from the version committed at `4ab797c`:

- System is **Real-Time POS + End-of-Day Reconciliation Module** (not "End-of-Day Transactional Auto-Calculation Engine")
- Section 5 restructured to 5.1 Dual-Phase Workflow, 5.2 Deficit/Petty Cash, 5.3 Receipts/Inventory, 5.4 Cloud/Remote Access
- "End-of-Day Transactional Auto-Calculation Engine" replaced with "Real-Time Point of Sale (POS) and Operations Management System featuring a dedicated End-of-Day Reconciliation Module"
- "End-of-Day Transactional Reconciliation and Auto-Calculation System" in conclusion replaced with "Real-Time Point of Sale (POS) and Operations Management System with an Integrated End-of-Day Reconciliation Module"
- Section 4: "the stakeholder was unwilling" → "the Sales Manager was unwilling"
- Section 4: "the client is unwilling" → "the Sales Manager was unwilling"
- Section 3: Added observation that "The laptop was powered on and actively used during the day, and physical receipts were being printed for customers on-site"
- Sales Manager role description: "The absolute center of operations. Acts as supervisor, cashier, payroll distributor, and record keeper."
- Secretary row: "Ground observation confirms the Sales Manager currently performs all data entry and reconciliation. This role is retained in the schema for future scaling only."

The version committed at `4ab797c` is outdated and will be replaced.

---

## 13. MUST Academic Calendar (from your paste)

Academic Year 2026/2027, Semester 1:
- Registration of first-year students: Aug 10–28, 2026
- Orientation for first-year students: Aug 10–14, 2026
- Reporting date for continuing students: Aug 15, 2026
- Semester 1 lectures begin: Aug 17, 2026
- Semester length: 17 weeks (15 teaching + 2 exam weeks)
- Must follows semester system since 2006