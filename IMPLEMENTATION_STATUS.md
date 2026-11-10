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

## Return navigation and workflow integrity — 10 November 2026

The dashboard/UI history work was pushed to `main` as `dd371a3` before this review. The following follow-up changes are local.

- Every screen has an explicit return link and contextual breadcrumbs. A per-tab navigation trail returns to the originating screen, including its dashboard period or table filter. Cancel uses the same destination. Direct entries have a normal application-link fallback, and return paths stay on the current origin.
- Sales, cash count, expenses, opening cash and worker registration detect unsaved edits. Leaving prompts to keep editing or explicitly discard. Reload/tab-close protection uses the browser's standard unload prompt. These are unsaved-entry guards, not automatic draft persistence.
- Paid-sale posting, cash expenses, opening-cash changes, worker registration and day-close have review dialogs. Attendance corrections review the previous and new status; initial marking remains quick. Final confirmation disables repeated submissions. Existing server-side transaction and idempotency checks remain authoritative.
- Day-close is blocked in the interface while expense or opening-cash edits remain unsaved. Submitting one form warns when another form's unsaved entries would be lost on refresh.
- Worker creation now checks the date is open inside the worker transaction. Invalid worker and opening-cash submissions preserve the attempted fields. Expired forms and missing routes render the application's navigation rather than an isolated server error page.
- Successful expense, float, worker and attendance changes display feedback. Printing remains a separate action on a saved receipt/report.

Validation: 19 automated tests pass, including closed-day worker creation, field preservation, error navigation and the existing stock, payment, duplicate-submission, stale-close and concurrent-posting checks. JavaScript syntax and whitespace checks pass. Browser verification covered Dashboard → New sale → Back with the reporting period preserved; Cancel/Keep editing/Discard; paid-sale review and posting; receipt-list filter restoration; pending-expense close blocking; close review cancellation and successful closure; and closed-day sales navigation. Posting tests used `/tmp/dcms-navigation-review.sqlite3`, a separate copy. The original demo retained 756 receipts, 128 saved closes and an open 10 November date. Both databases passed SQLite integrity checks.

Confirmation dialogs require JavaScript and establish user intent, not authorization. Production role permissions, audit history, correction/refund workflows and physical printer acceptance remain separate work already identified in the implementation plan.

## Taxes, worker records and banking — 10 November 2026

Added Workers, Taxes and Banking to the shared navigation. These changes, together with the preceding return-navigation fixes, are local after `dd371a3`.

Sales VAT Summary groups stored sale snapshots by calendar month and applied rate, provides receipt drill-down, printing and CSV export, and distinguishes output VAT from VAT payable. It includes URA source links and a following-month filing reminder. Registration/TIN are unverified, purchase/input VAT is not captured, credit/debit notes and refunds are not implemented, and EFRIS is not connected. Business-date aggregation is not asserted to establish statutory tax-point treatment. No PAYE, withholding or income-tax calculator was added. Effective-dated VAT configuration prevents current rates from silently applying to earlier business dates; posted receipts are unchanged.

Workers now have roster dates and effective-dated rates. Historical attendance keeps its recorded rates and excludes workers outside their roster dates. Registration is accessible from a dedicated Workers screen and from Attendance. Corrections require a reason and compare the expected previous status. Their event history is visible on the worker record. Closing requires explicit review of unmarked attendance. Individual wage payments and authenticated operator identities remain outside this prototype.

Banking now records UGX account labels and last four digits, receiving accounts on new bank-paid sales, CSV preview/import, unmatched credits and receipts, partial/multiple allocations and reasoned reversals. Duplicate transaction IDs, over-allocation, account mismatches, delayed request retries and stale reversals are checked transactionally. Allocation events preserve the correction trail. Posted sales and saved cash closes remain unchanged. Fees/transfers are left for separate review. There is no live feed, bank login, transfer or complete bank ledger/balance reconciliation.

The refreshed dataset is `instance/operations-20261110.sqlite3`; prior databases were retained. Before the simulated morning shift it has 752 receipts, 250 cash expenses, 10 workers, 1,280 attendance entries and 128 saved closes. It includes 79 illustrative bank statement rows and 66 initial allocations. Today's future shift events are omitted rather than future-timestamped. Ordinary names/descriptions/calendar reasons no longer carry repeated “Demo” labels; one environment notice identifies sample data. Printed receipts remain explicitly internal and not EFRIS-fiscalised.

Validation: 28 automated tests pass. They cover rate periods, stored tax totals, CSV export, worker roster/rate history, correction reasons and stale statuses, unmarked attendance review, statement preview, atomic duplicate/conflict imports, allocations and reversals, late request retries, unchanged financial snapshots and sample timestamp bounds. Browser checks in an isolated copy verified tax layout, worker registration, attendance correction/history, statement preview and confirmed import, allocation and reasoned reversal, and narrow-screen table containment. No bank credentials or live integration were used.

Sources checked on 10 November 2026:

- [URA VAT filing guidance](https://ura.go.ug/en/ask-ura-commissioner-general-42/)
- [URA EFRIS handbook](https://ura.go.ug/en/efris-handbook/)
- [URA EFRIS system integration guidance](https://ura.go.ug/en/efris-brochure-23-24/)
- [ERPNext bank reconciliation](https://docs.frappe.io/erpnext/bank-reconciliation)

Before a production release, confirm the business's actual tax position and fiscal integration requirements, add authenticated permissions and actor audit records, and validate fiscal rounding, input VAT and adjustment handling. These remain separate acceptance gates; the new screens do not establish production tax compliance.

## Hosted deployment and account access — 10 November 2026

Prepared Ubuntu hosting with Waitress, systemd and Caddy, using persistent SQLite storage and a single application process. Added session login with an account dropdown, Sales Manager operations access and CEO read-only oversight. Both requested sample passwords are `demo`; server account hashes and runtime secrets remain outside Git. Editing controls are omitted for CEO, and all operational POST requests are also rejected server-side. Added account tests covering CSRF, logout, secure cookies, role restrictions, throttling and redirect validation. See `DEPLOYMENT.md` for server paths and update commands. Per-operation actor attribution is still separate work.

## Documentation and presentation alignment - 10 November 2026

Updated the eight-slide deck, removed the member roster, separated stakeholder classification from power and interest, and added two derived user stories under two epics with acceptance criteria and existing requirement/test links. Updated Phase 1, the master SRS, the user manual and the deliverables guide using the established generators. The manual distinguishes hosted behaviour from planned standalone functionality. Added presentation/interview guidance and proposed inventory observations, explicitly distinguishing them from work actually performed. Added deployment stop/resume instructions. Generated files were rendered for visual review.

## Requested hosted shutdown - 10 November 2026

After pushing the documentation changes, stopped and disabled dcms and its dedicated Caddy service over SSH. Verified both inactive/disabled, no HTTP, HTTPS or app listener, and public HTTPS connection failure. Preserved code, accounts and database. SQLite integrity passed and counts remained 752 sales, 1,001 sale lines and 129 business dates. The VM remains running and swap was unchanged. Resume only when requested, using DEPLOYMENT.md.

## Screenshot gallery and reactivation - 10 November 2026

Reactivated dcms and its dedicated Caddy proxy at the user request. Captured twelve unedited browser screenshots from the hosted application, including login, dashboard overview and analytics, daily records, saved reconciliation, workers, sales VAT, banking, attendance, a saved receipt, the new-sale form and CEO read-only reporting. Both accounts were signed out after capture. No operational forms were submitted. Added the full gallery and capture context in screenshots/README.md, with two 300-pixel-wide linked previews in the repository README. The site is left running.
