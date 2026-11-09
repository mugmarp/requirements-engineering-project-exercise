# DCMS implementation status

The latest local update is described under "Dashboard and historical demo" below. The earlier implementation record follows.

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


## UI update — 9 November 2026

The existing Flask application now follows the ERPNext interface observed in the in-app browser. The reference review covered the Selling dashboard, Stock dashboard, invoice entry, record lists, Stock Balance report and quick item creation dialog.

- Shared icon rail and collapsible Operations sidebar, with selected-page states and business-date context.
- Compact page headers, neutral surfaces, pale form inputs, consistent buttons and status badges.
- Business dates, receipts and attendance displayed as tables with client-side filters and empty-result messages.
- Daily Sales item grid includes live unit rates and line amounts alongside quantities. Existing payment, VAT and stock validations remain in the service layer.
- Reconciliation uses channel summary cards, aligned cash calculations, an expense table and a clear variance result.
- Academic footer removed. The sample-data notice remains in the sidebar.
- Responsive navigation and contained table scrolling. Print styles remove the application navigation.

Validation: all nine existing tests passed. Browser checks covered page navigation, live item totals, adding/removing item rows, receipt filtering and its no-results state, receipt detail navigation, the saved UGX 5,000 deficit report, and sales navigation at a 390px viewport. The sales page had no document-level horizontal overflow at that width. Physical printing was not tested.

Preview command, using port 8081 when 8080 is already occupied:

```bash
.venv/bin/python -m dcms --database instance/presentation.sqlite3 serve --port 8081
```

This update changes the existing application UI. It does not add ERPNext's warehouse, accounting, tax configuration or POS configuration modules.


## Dashboard and historical demo — 10 November 2026

The application now opens on Operations Dashboard. Daily records replaces the former Business dates landing page. Persistent sidebar navigation exposes every implemented module, preserves the selected working date and provides a return to today. Changing dates retains the originating workflow. Sales navigation on a closed date leads to its saved receipts.

The dashboard has separate today actions and period-filtered reporting. It includes attendance and expected cash for today, receipt counts, sales including VAT, cash expenses, saved-close counts, a sales trend, channel breakdown, product quantities with separate units, recent receipts, recent reports, open dates awaiting close and calendar completeness. Today, last 7 days, last 30 days, all-history and custom-date filters are supported. Chart values have an accessible table. Viewing the dashboard never opens a business date.

The historical demo generator uses a deterministic sequence and a context-local service clock. It creates records through the posting services with coherent historical timestamps and full payment. A documented opening-stock allocation supports the sales deductions. Explicit non-operating dates remain separate from dates with no records. Wage cash payouts remain expenses separate from attendance eligibility. All prices, rates, identities, volumes and scheduling remain synthetic.

For the 10 June–10 November 2026 sample:

| Records | Count |
|---|---:|
| Operating dates | 129 |
| Explicit non-operating dates | 25 |
| Receipts | 756 |
| Sale lines | 1,007 |
| Cash expenses | 251 |
| Fictional workers | 10 |
| Attendance entries | 1,290 |
| Saved reconciliations | 128 |

Today remains open, and 9 November preserves the UGX 5,000 shortage worked example. The current local preview uses `instance/history-demo-v2.sqlite3` on port 8081; the previous presentation database remains intact. Generated databases are ignored by Git and can be reproduced using `init --history --end-date 2026-11-10` with a new database filename.

Validation: fourteen tests pass. The added checks cover dashboard aggregation, date filtering, calendar completeness, historical timestamps, stock conservation, receipt math, attendance snapshots, close arithmetic, the shortage example, empty-installation behavior, workflow-preserving navigation and linked-page rendering. JavaScript syntax and Git whitespace checks pass.
