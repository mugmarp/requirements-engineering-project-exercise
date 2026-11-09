# DCMS implementation status

Status as of 9 November 2026. The web prototype and updated presentation are on [main at 3b300ab](https://github.com/mugmarp/requirements-engineering-project-exercise/commit/3b300ab).

## Completed work

- **Requirements.** Clarified the Phase 1 problem statement and elicitation limits. Updated the master specification and SOP to use business-date reconciliation, atomic inventory deduction and a saved daily report. The [implementation plan](IMPLEMENTATION_PLAN.md) separates the hosted web prototype from the standalone offline desktop release.
- **Web prototype.** Built a Flask application using SQLite and a repeatable sample dataset. The interface has Daily Sales, Close of Day, receipt history and Attendance. The [Python service layer](dcms/services.py) holds the transaction rules for reuse in the desktop app.
- **Daily Sales.** The app calculates VAT from a configurable rate, records full payment through Cash, Mobile Money or Bank Deposit, and saves a multi-line sale and its stock deductions together. An oversold line rolls back the whole sale. Repeating a sale submission returns its existing receipt. Saved receipts can be opened and printed again.
- **Close of Day.** The app calculates each channel's recorded activity for the selected business date. It records opening cash and individual cash expenses, compares expected cash with the physical count, and requires an explanation for any nonzero variance. Closing saves one report and blocks further financial postings to that date. A repeat close returns the saved report. Mobile Money and bank figures are recorded activity, with external verification outside prototype scope.
- **Presentation.** The [eight-slide deck](project_deliverables/PhaseFinal_Grand-Project-Presentation.pptx) keeps the ten-member roster on slide 2 and shows the [saved Close of Day screenshot](project_deliverables/PhaseFinal_Close-of-Day.png) on slide 7. The example shows UGX 450,000 expected, UGX 445,000 counted and a UGX 5,000 deficit.

## Attendance module update

The Sales Manager can register workers with unique codes, names and positive daily rates. Each business date stores one Present or Absent record per worker. Repeated submissions of the same status preserve one record. The eligibility list totals only Present workers using the daily rate recorded with their attendance. Marking a worker present does not record a wage payment. Paid wages must be recorded as cash expenses.

Closing a date also saves its headcount and payroll eligibility amount. Attendance changes are blocked after close. Existing saved closes retain their original financial report, with attendance figures unavailable for those older records. The server applies the migration on startup.

Nine automated tests pass after this update, including worker entry through the web forms, duplicate attendance, status corrections, date separation, eligibility calculation and locked close snapshots. This update is local and follows the prototype commit referenced above.

## Run the demo

From the repository root, set up the Python environment and create a fresh sample database.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m dcms --database instance/demo.sqlite3 init --demo
.venv/bin/python -m dcms --database instance/demo.sqlite3 serve
```

Open [DCMS on localhost](http://127.0.0.1:8080). On **10 November 2026**, open Close of Day, enter `445000`, add a sample explanation and save the report. Use **11 November 2026** to demonstrate a new sale separately. The database is excluded from Git. Use a new database filename for a fresh rehearsal.

## Verification completed

- All seven automated tests passed. They cover whole-sale rollback, concurrent stock deductions, repeated sale and expense submissions, stale close previews, competing sale and close requests, persisted reports and web form protection. Run them with `.venv/bin/python -m unittest discover -s tests -v`.
- The Chrome walkthrough posted a two-item sale, generated its receipt as a PDF, and saved the sample Close of Day report. An actual Waitress restart preserved both the posted receipt and the saved report.
- The rebuilt PowerPoint passed package and layout checks and was reviewed after rendering.

## Pending work

- Deploy the web prototype to a host with persistent storage, HTTPS and restricted demo access. The build has been verified locally with sample data.
- Build the standalone desktop interface, local backup and restore, and the Windows `.exe` and Debian-compatible `.deb` packages. Verify installation, offline operation, upgrades and physical printing on the target machines.
- Before a live pilot, implement and verify financial corrections and refunds, production roles and audit history, and confirm receipt, tax and printer details. Actual payroll disbursement tracking, reorder alerts, full Owner report metrics, URA reporting and cloud backup remain pending.
