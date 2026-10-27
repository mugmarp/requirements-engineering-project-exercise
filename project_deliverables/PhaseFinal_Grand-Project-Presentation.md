# GRAND PROJECT PRESENTATION DECK

**Course:** SWE2102 Requirements Engineering  
**Group:** K  
**Client Site:** Deniz Construction Limited, Ishanyu Bushenyi Road, Mbarara  
**Project:** Deniz Construction Management System (DCMS)

---

## Slide 1: Title Slide

**Deniz Construction Management System**  
Requirements Engineering and Database Design

Group K  
SWE2102 Requirements Engineering  
Mbarara University of Science and Technology

---

## Slide 2: Group Members

### Project Team

| Name | Registration Number |
|------|---------------------|
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

## Slide 3: The Real Problem

### Operational Bottlenecking and Cash Vulnerability

- The Super Manager Bottleneck: One person acts as supervisor, cashier, payroll distributor and record keeper.
- Unexplained Cash Deficits: Manual computation of cash shortages at the end of the day without a tool to log operational expenses.
- Informal Labor Practices: Daily cash payouts based on memory, with no formal attendance tracking.
- Data Vulnerability: All records reside on a single local laptop with no cloud backup.

---

## Slide 4: Elicitation Techniques and Field Realities

### What We Actually Observed

- Direct Observation: The laptop was powered on and actively used during the day. A printer is on site and physical receipts were being printed for customers as trucks loaded.
- Semi Structured Interview: Conducted with the Sales Manager to understand payment channels (Cash, Mobile Money, Bank), tax filing processes and primary pain points regarding cash insecurity.
- Environmental Scan: Customers transport their own goods. Trucks load in bulk. Site has CCTV cameras, indicating baseline security awareness.

---

## Slide 5: Challenges in Elicitation

### Documented Limitations

- The Gatekeeper Effect: The Sales Manager was hesitant to share deep financial workflows, such as exact tax calculations and cash storage protocols.
- Inaccessibility: The Business Owner, Site Workers and Secretary could not be approached directly. These are unresolvable gaps.
- No Follow up Feasibility: The Sales Manager was unwilling to provide further information and a return visit to the site is not possible. The project scope is locked.

---

## Slide 6: Strategic Business Synthesis

### How We Bridged the Information Gaps

- Deficit Root Cause: In cash heavy local SMEs, end of day shortages are rarely theft. They are almost always unrecorded petty cash expenses. The system must allow logging of these expenses to balance the till.
- Dual Phase Workflow: Because physical receipts are printed during the day, the system cannot be evening only. It must support real time transaction processing followed by a dedicated evening reconciliation module.
- Remote Access Reality: Since the owner visits daily, a live remote dashboard is unnecessary. Cloud technology is strictly for automated nightly disaster recovery and asynchronous historical review.

---

## Slide 7: The Proposed Solution

### Dual Phase Operations Management System

- Phase 1: Real Time Point of Sale. During the day, the system processes individual sales, calculates VAT, updates inventory and prints physical receipts.
- Phase 2: End of Day Reconciliation. In the evening, the system allows the Sales Manager to balance multi channel payment drawers, log operational expenses, compute cash variances and generate a final daily summary report for the Business Owner.
- Excluded Features: Credit and debtors modules are excluded as the business operates on a strict no credit policy.

---

## Slide 8: Database Architecture for SWE1205

### Advanced SQL Implementation

- Normalization: Database normalized to 3NF to eliminate redundancy across Workers, Attendance, Products, Sales and Operational Expenses.
- Stored Procedures: CalculateVAT fetches the rate from a System Settings table and applies it to the subtotal.
- Triggers: TRG Sales Insert automatically reduces Current Stock in the Products table upon sale insertion.
- Role Based Access Control: Views like View Owner Profitability are strictly restricted to the Business Owner role.

---

## Slide 9: Requirements Traceability

### Linking Problems to Code

| Ground Problem | Requirement ID | Requirement Description | Database Implementation |
|----------------|----------------|-------------------------|-------------------------|
| Unexplained cash deficits | REQ FUN EXP 01 | Operational Expense module | Table: Operational_Expenses, Trigger: TRG Expense Insert |
| Informal labor tracking and ghost worker risk | REQ FUN ATT 02 | Reject duplicate attendance entries | Table: Attendance (Composite Unique Key) |
| Manual URA tax transcription errors | REQ FUN TAX 01 | URA Summary Generation | Stored Procedure: GenerateURA Summary |

---

## Slide 10: Conclusion and Next Steps

### Project Delivery and Future Enhancements

- Conclusion: The DCMS architecture is directly driven by the operational bottlenecks observed at Deniz Construction Limited. Every functional requirement maps to a specific database entity, trigger or stored procedure.
- Next Steps: Deployment of the system on the existing office laptop, accompanied by a simplified User Manual for the Sales Manager.
- Future Enhancements: Features such as a formal Secretary role or advanced logistics tracking are logged in a Future Enhancements Backlog for post academic implementation.