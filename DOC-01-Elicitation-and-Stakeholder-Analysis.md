# DOCUMENT 1: REQUIREMENTS ELICITATION AND STAKEHOLDER ANALYSIS

**Course:** SWE2102 Requirements Engineering

**Group:** K

**Client Site:** Deniz Construction Limited, Ishanyu Bushenyi Road, Mbarara

**Project:** Deniz Construction Management System (DCMS)

---

## 1. INTRODUCTION

This document outlines the Requirements Elicitation and Stakeholder Analysis conducted for the Deniz Construction Management System (DCMS). It details the empirical data gathered during our site visit, the challenges faced during data collection, and how the system design was adapted to fit the operational reality of the business. Follow up visits were not possible and the stakeholder was unwilling to provide further information, so this document also sets the baseline for how unresolvable information gaps are handled through standard operational assumptions based on the Ugandan SME context.

## 2. STAKEHOLDER ANALYSIS

The organizational structure at the site is highly flattened. Roles are heavily concentrated, so the traditional corporate hierarchy does not apply. We mapped stakeholders on a Power and Interest grid to determine our engagement strategy and identify critical data gaps.

### 2.1 Stakeholder Identification and Power Interest Mapping

| Stakeholder | Role in Current Operations | Power | Interest | Engagement Strategy and Status |
| :--- | :--- | :--- | :--- | :--- |
| Business Owner | Strategic oversight. Visits the site daily to review operations and cash. | High | High | Manage Closely. Status: GAP. Not available for interview. System must prioritize the metrics he reviews during his daily evening visits. |
| Sales Manager | Supervises workers, handles cash, processes daily deficits, logs sales and files URA taxes. | High | High | Manage Closely. Status: FACT. Interviewed. Acts as the gatekeeper. System must reduce her end of day workload to ensure adoption. |
| Secretary | Expected to handle tax records and data entry. | Medium | High | Keep Informed. Status: GAP. Never met. No interview data. Ground observation confirms the Sales Manager currently performs all data entry and reconciliation. The Secretary role is retained in the schema for future scaling and has no active requirements in Phase 1. |
| Site Workers | Produce blocks and pavers. Paid daily in cash. No formal legal contracts. | Low | Low | Monitor. Status: GAP. Could not speak to them. System only needs a simple interface for the Manager to log them as Present. |
| URA (External) | Uganda Revenue Authority. Dictates tax compliance, VAT and receipting standards. | High | Low | Keep Satisfied. System must ensure financial outputs meet URA audit expectations to prevent penalties. |
| Clients and Builders | Purchase blocks and pavers. Pay upfront. Transport their own goods by truck. | Low | Medium | Keep Informed. System must generate clear receipts and process sales quickly to minimize loading delays. |

### 2.2 Common Pitfalls and Engagement Techniques

**Pitfall Identified, the Gatekeeper Effect.**Because the Sales Manager handles almost all operations, she acts as a gatekeeper. She was hesitant to share deep financial workflows, for example the exact tax calculations and the cash storage arrangements.

**Mitigation Technique.**We used observation over direct interrogation for sensitive topics. By observing the physical environment, for example the CCTV cameras, the printer and the laptop usage timing, we inferred security and workflow requirements without making her defensive.

## 3. ELICITATION TECHNIQUES USED

Given the single site visit, Group K used the following techniques.

**1. Direct Observation, Environmental Scan**

- Clients transport their own products by truck, so the system needs no delivery or logistics module, only a loading and dispatch confirmation.
- The site has a laptop, a printer and CCTV cameras, indicating a baseline awareness of security and digital record keeping.
- Trucks load in bulk, but the counting method, whether per piece or per pallet, was not visible.

**2. Semi Structured Interview**

- We interviewed the Sales Manager face to face to understand the high level workflow, the payment methods of cash, mobile money and bank transfer, and the primary pain points, specifically the insecurity concern and the processing of deficits.

## 4. CHALLENGES IN ELICITATION

As Group K, we faced the following empirical challenges, which are now locked as documented limitations for the project.

1. Stakeholder Hesitance and Information Withholding. The Sales Manager was reluctant to disclose the exact fields on the physical receipts, the method used to calculate URA taxes, and the cash handling and storage protocols.
2. Inaccessibility of Secondary Stakeholders. The Business Owner was not available for interview, and the Site Workers and Secretary could not be approached directly. These are unresolvable gaps. Their requirements will be handled through standard industry assumptions.
3. Incomplete Workflow Visibility. We knew the laptop is used to process deficits, but we could not observe the exact formula or the physical cash reconciliation process.
4. No Follow up Feasibility. The client is unwilling to provide more information and a return visit is not possible. The project scope is locked.

## 5. OPERATIONAL DEDUCTIONS AND DESIGN ADJUSTMENTS

Where we could not get explicit answers, we deduced requirements from physical observations and the standard operational context of Ugandan construction SMEs. Obvious items were set as industry baselines. Complex items were resolved through logical deduction.

**1. Resolving the Deficit and Cash Insecurity Issue**

The Sales Manager explicitly mentioned using the PC to process deficits and cited insecurity regarding cash, which aligns with the CCTV cameras we observed. In cash heavy sites, end of day deficits, meaning shortages, are rarely theft. They are almost always unrecorded petty cash expenses, for example buying lunch for the truck loaders or paying for a boda boda errand, taken directly from the cash drawer.

**Design Adjustment.**The system must include an Operational Expense and Petty Cash Log. The Sales Manager will log each individual cash out as it happens or at the end of the day. The system will automatically deduct these from the Cash Virtual Drawer, balancing the till and eliminating the deficit mystery for the owner.

**2. Adjusting the System Workflow and Auto Calculation**

We observed that the laptop is used right before the Business Owner arrives in the evening. The Sales Manager is clearly not typing into the computer while directing truck loading in the yard. However, if she only typed daily totals into the system, we would lose the ability to automatically calculate VAT per item, deduct specific blocks from inventory, or track exact drawer balances.

**Design Adjustment.**The system workflow is shifted to the evening, but the data entry remains transactional. The Sales Manager will log each individual sale and each operational expense from her paper receipts into the system at the end of the day. The system then acts as an Auto Calculation Engine, automatically computing the VAT, updating inventory, tracking the separate payment channels of cash, mobile money and bank, and generating the final End of Day Reconciliation and Deficit report for the Owner.

**3. Standardizing Receipts and Inventory, Obvious Baselines**

We could not see the exact receipt fields or how bulk blocks were counted, so we applied standard industry baselines. Receipts must include the sequential ID, the date, the VAT and the payment method. Because trucks load in bulk and clients self transport, the Unit of Measure field is a flexible variable length text field, covering blocks sold by piece or pallet and pavers by square meter. No logistics module is needed.

**4. Redefining the Cloud Backup and Remote Access**

The owner visits the site every day and data is entered at the end of the day. Real time syncing is unnecessary and would waste the limited internet data available at the site.

**Design Adjustment.**We defined the cloud feature strictly as an Automated Nightly Backup, triggered in the evening after she finishes data entry, to solve the Data Vulnerability problem of relying on a single laptop. The remote portal for the owner is an Asynchronous Dashboard for reviewing next day finalized reports and long term business trends, rather than a live monitoring tool.

## 6. CONCLUSION AND TRANSITION

By combining direct observation with logical deduction based on the local business context, Group K has navigated the elicitation challenges. The project is now a context aware End of Day Reconciliation and Deficit Resolution System. All unresolvable gaps, being the Secretary, the Workers and the Receipt Fields, are documented here and will be handled through standard assumptions in later phases.

This provides the foundation for Phase 2, Requirements Analysis, where these deductions will be formalized into the Software Requirements Specification and mapped to the relational database schema.
