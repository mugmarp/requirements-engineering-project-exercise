# DOCUMENT 1: REQUIREMENTS ELICITATION AND STAKEHOLDER ANALYSIS

**Course:** SWE2102 Requirements Engineering

**Group:** K

**Client Site:** Deniz Construction Limited, Ishanyu Bushenyi Road, Mbarara

**Project:** Deniz Construction Management System (DCMS)

---

## 1. INTRODUCTION

This document outlines the Requirements Elicitation and Stakeholder Analysis conducted for the Deniz Construction Management System (DCMS). It details the empirical data gathered during our single site visit, the challenges faced during data collection, and the current As Is operational reality of the business. Because follow up visits were not possible and the primary stakeholder was unwilling to provide further information, this document also establishes the baseline for how unresolvable information gaps are handled through documented business assumptions based on the Ugandan SME context.

## 2. STAKEHOLDER ANALYSIS

The organizational structure at the site is highly flattened. Roles are heavily concentrated, so the traditional corporate hierarchy does not apply. We mapped stakeholders on a Power and Interest grid to determine our engagement strategy and identify critical data gaps.

### 2.1 Stakeholder Identification and Power Interest Mapping

| Stakeholder | Role in Current Operations | Power | Interest | Engagement Strategy and Status |
| :--- | :--- | :--- | :--- | :--- |
| Business Owner | Strategic oversight. Visits the site daily to review operations and cash. | High | High | Manage Closely. Status: gap. Never interviewed. The system must eventually prioritize the metrics he reviews during his daily evening visits. |
| Sales Manager | The absolute center of operations. Acts as supervisor, cashier, payroll distributor, and record keeper. | High | High | Manage Closely. Status: fact. Interviewed. Acts as the gatekeeper. |
| Secretary | Named in initial project scoping to handle tax records and data entry. | Medium | High | Keep Informed. Status: gap. Never met. Ground observation confirms the Sales Manager currently performs all data entry. |
| Site Workers | Produce blocks and pavers. Paid daily in cash. No formal legal contracts. | Low | Low | Monitor. Status: gap. No chance to speak to them. |
| URA (External) | Uganda Revenue Authority. Dictates tax compliance, VAT and receipting standards. | High | Low | Keep Satisfied. External regulator. No direct engagement but dictates compliance rules. |
| Customers and Builders | Purchase blocks and pavers. Pay upfront. Transport their own goods by truck. | Low | Medium | Keep Informed. The system must eventually ensure quick processing to minimize their loading delays. |

### 2.2 Common Pitfalls and Engagement Techniques

**Pitfall Identified: The Gatekeeper Effect.**Because the Sales Manager handles almost all operations, she acts as a gatekeeper. She was hesitant to share deep financial workflows, for example, the exact tax calculations and the cash storage arrangements.

**Mitigation Technique.**We used observation over direct interrogation for sensitive topics. By observing the physical environment, for example, the CCTV cameras, the printer, and the laptop usage timing, we inferred security and workflow realities without making her defensive.

## 3. ELICITATION TECHNIQUES AND FIELD REALITIES (THE AS IS STATE)

Given the single site visit, Group K used Direct Observation and Semi Structured Interviews. The following facts represent the current operational reality of the business.

**1. Direct Observation (Environmental Scan)**

- Workflow and Hardware: The laptop was powered on and actively used during the day. A printer is on site, and physical receipts were being printed for customers as trucks loaded.
- Logistics: Customers transport their own products by truck. Trucks load in bulk, but the exact counting method (per piece or per pallet) was not visible.
- Security: The site has CCTV cameras, indicating a baseline awareness of physical security and cash handling risks.

**2. Semi Structured Interview (Sales Manager)**

- Payment Channels: The business accepts Cash, Mobile Money, and direct Bank Deposits.
- Credit Policy: The business never gives credit; all payments must be made upfront.
- Tax Compliance: The Sales Manager processes taxes online via the URA portal, but the exact manual calculation method was not disclosed.
- Pain Points: The Sales Manager explicitly raised insecurity regarding cash handling and stated she uses the PC to process deficits (cash shortages) manually.
- Labor: There is no formal attendance system. Attendance relies entirely on the Sales Manager memory, and workers are paid daily in cash without legal contracts.

## 4. CHALLENGES IN ELICITATION AND DOCUMENTED LIMITATIONS

As Group K, we faced the following empirical challenges, which are now locked as documented limitations for the project.

1. Stakeholder Hesitance and Information Withholding. The Sales Manager was reluctant to disclose the exact fields on the physical receipts, the method used to calculate URA taxes, and the physical cash storage protocols.
2. Inaccessibility of Secondary Stakeholders. The Business Owner was not available for interview, and the Site Workers and Secretary could not be approached directly.
3. Incomplete Workflow Visibility. We knew the laptop is used to process deficits, but we could not observe the exact formula or the physical cash reconciliation process.
4. No Follow up Feasibility. The Sales Manager was unwilling to provide further information, and a return visit to the site is not possible. The project scope is locked.

## 5. STRATEGIC BUSINESS SYNTHESIS (FILLING THE GAPS)

Because we cannot return to the site to close the gaps identified in Section 4, we must apply strategic business synthesis. These are logical inferences drawn from our verified facts combined with the standard operational norms of Ugandan construction SMEs. They serve as the baseline assumptions for the subsequent Requirements Analysis phase.

**1. The Nature of Deficits and Cash Insecurity**

Fact: The Sales Manager processes deficits manually and cited insecurity (CCTV is present).

Synthesis: In cash heavy Ugandan SMEs, end of day cash shortages are rarely malicious theft. They are almost always caused by unrecorded petty cash expenses (for example, buying lunch for truck loaders or paying for transport) taken directly from the cash drawer.

Assumption for Next Phases: The business requires a mechanism to log operational cash outs to reconcile the physical till against the receipt totals.

**2. The Dual Phase Operational Reality**

Fact: The laptop is on during the day, and physical receipts are printed for customers. However, the Sales Manager also heavily utilizes the PC right before the Business Owner arrives in the evening specifically to process cash deficits.

Synthesis: The Sales Manager cannot wait until the evening to log sales, because customers require printed receipts immediately upon loading. However, the evening PC usage indicates a distinct, heavy reconciliation burden at the end of the day.

Assumption for Next Phases: The future system must support real time transaction processing and receipt generation during the day, alongside a dedicated, heavy duty reconciliation workflow for the evening.

**3. Receipting and Inventory Baselines**

Fact: Physical receipts are printed on site, and trucks load in bulk. Exact receipt fields are unknown.

Synthesis: To satisfy URA compliance and basic business logic, receipts must contain standard fiscal fields (Sequential ID, Date, VAT, Payment Method). Because clients self transport and load in bulk, inventory tracking must accommodate flexible units of measure (pieces, pallets, or truckloads).

**4. Cloud Backup and Remote Access**

Fact: The owner visits the site every day. No cloud backup currently exists.

Synthesis: Because the owner is physically present daily, a real time remote monitoring dashboard is operationally redundant. The critical need for cloud technology is strictly for disaster recovery (protecting the single laptop from data loss) and asynchronous historical review.

## 6. CONCLUSION AND TRANSITION

By combining direct observation with logical business synthesis, Group K has mapped the current As Is state of Deniz Construction Limited and documented all unresolvable elicitation challenges.

The project is grounded in the reality of a Super Manager bottleneck, multi channel cash handling vulnerabilities, and informal labor practices. All gaps (Secretary, Workers, Receipt Fields) are formally documented as limitations.

This provides the foundation for Phase 2: Requirements Analysis and Specification, where these business assumptions and facts will be translated into formal Software Requirements (SRS) and mapped to the relational database schema.
