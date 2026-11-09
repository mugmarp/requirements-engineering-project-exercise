"""Posting and reconciliation rules shared by the web and future desktop UIs."""

import hashlib
import json
import re
from collections import Counter
from contextvars import ContextVar
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from .db import write

CHANNELS = {
    "cash": "Cash",
    "mobile_money": "Mobile Money",
    "bank_deposit": "Bank Deposit",
}
MAX_AMOUNT = 99_999_999_999


class DomainError(ValueError):
    status = 422


class Conflict(DomainError):
    status = 409


class Missing(DomainError):
    status = 404


# Internal clock override used only by the fresh-database historical demo builder.
_recorded_time = ContextVar("dcms_recorded_time", default=None)


def timestamp():
    return (_recorded_time.get() or datetime.now(timezone.utc)).isoformat(timespec="seconds")


def text_value(value, label, limit, *, required=True):
    value = value.strip()
    if not value and required:
        raise DomainError(f"Enter {label}.")
    if len(value) > limit:
        raise DomainError(f"{label.capitalize()} must be at most {limit} characters.")
    return value


def integer_value(value, label, minimum=1, maximum=1_000_000):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,12}", value.strip()):
        raise DomainError(f"Enter a whole number for {label}.")
    result = int(value)
    if not minimum <= result <= maximum:
        raise DomainError(f"{label.capitalize()} must be between {minimum} and {maximum}.")
    return result


def money_value(value, label, *, positive=False):
    value = value.strip()
    if not re.fullmatch(r"[0-9]{1,9}(?:\.[0-9]{1,2})?", value):
        raise DomainError(f"Enter {label} as an amount in UGX with up to two decimal places.")
    whole, _, fraction = value.partition(".")
    amount = int(whole) * 100 + int(fraction.ljust(2, "0"))
    if positive and amount == 0:
        raise DomainError(f"{label.capitalize()} must be greater than zero.")
    return amount


def business_date(value):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise DomainError("Choose a valid business date.") from error
    if parsed.isoformat() != value:
        raise DomainError("Choose a valid business date.")
    return value


def find_day(db, day):
    row = db.execute("SELECT * FROM business_days WHERE business_date = ?", (day,)).fetchone()
    if row is None:
        raise Missing("This business date has not been opened.")
    return row


def require_open(db, day):
    row = find_day(db, day)
    if row["status"] != "open":
        raise Conflict("This business date is closed. Choose an open date to post activity.")
    return row


def open_day(db, day):
    business_date(day)
    with write(db):
        if db.execute("SELECT 1 FROM non_operating_days WHERE business_date = ?", (day,)).fetchone():
            raise Conflict("This date is marked non-operating. Choose an operating date.")
        db.execute(
            "INSERT INTO business_days (business_date) VALUES (?) ON CONFLICT DO NOTHING",
            (day,),
        )


def bump_revision(db, day):
    db.execute("UPDATE business_days SET revision = revision + 1 WHERE business_date = ?", (day,))


def set_opening_cash(db, day, amount):
    amount = money_value(amount, "opening cash")
    with write(db):
        row = require_open(db, day)
        if row["opening_cash"] != amount:
            db.execute("UPDATE business_days SET opening_cash = ? WHERE business_date = ?", (amount, day))
            bump_revision(db, day)


def record_expense(db, day, description, amount, request_key):
    description = text_value(description, "an expense description", 180)
    amount = money_value(amount, "expense amount", positive=True)
    request_key = text_value(request_key, "an expense request key", 64)
    with write(db):
        existing = db.execute(
            "SELECT business_date, description, amount FROM expenses WHERE request_key = ?",
            (request_key,),
        ).fetchone()
        if existing:
            if tuple(existing) != (day, description, amount):
                raise Conflict("This expense request was already used. Start a new entry.")
            return
        require_open(db, day)
        db.execute(
            """INSERT INTO expenses (business_date, description, amount, recorded_at, request_key)
               VALUES (?, ?, ?, ?, ?)""",
            (day, description, amount, timestamp(), request_key),
        )
        bump_revision(db, day)


def vat_rate(db, day=None):
    day = day or datetime.now(ZoneInfo('Africa/Kampala')).date().isoformat()
    return db.execute('SELECT basis_points FROM vat_rates WHERE effective_from<=? ORDER BY effective_from DESC LIMIT 1',(day,)).fetchone()[0]


def set_vat_rate(db, basis_points, effective_from=None):
    if not 0 <= basis_points <= 10_000:
        raise DomainError("The VAT rate must be between 0 and 100 percent.")
    effective_from = business_date(effective_from or datetime.now(ZoneInfo('Africa/Kampala')).date().isoformat())
    with write(db):
        if db.execute('SELECT 1 FROM sales WHERE business_date>=? LIMIT 1',(effective_from,)).fetchone():
            raise Conflict('Choose a tax effective date after existing sales. Posted tax snapshots cannot be rewritten.')
        db.execute('INSERT INTO vat_rates VALUES (?,?) ON CONFLICT(effective_from) DO UPDATE SET basis_points=excluded.basis_points',(effective_from,basis_points))
        db.execute("UPDATE settings SET value = ? WHERE key = 'vat_basis_points'", (basis_points,))


def calculate_vat(subtotal, basis_points):
    return (subtotal * basis_points + 5_000) // 10_000


def post_sale(db, day, *, customer, channel, reference, received, request_key, lines, bank_account_id=None):
    customer = text_value(customer, "a customer name", 100)
    reference = text_value(reference, "a payment reference", 100, required=False)
    received = money_value(received, "the amount received", positive=True)
    request_key = text_value(request_key, "a sale request key", 64)
    if channel not in CHANNELS:
        raise DomainError("Select Cash, Mobile Money or Bank Deposit.")
    if not 1 <= len(lines) <= 50:
        raise DomainError("Add between 1 and 50 product lines.")

    quantities = Counter()
    for product_id, quantity in lines:
        key = integer_value(product_id, "product")
        quantities[key] += integer_value(quantity, "quantity", maximum=10_000)
        if quantities[key] > 10_000:
            raise DomainError("The total quantity per product cannot exceed 10,000.")
    payload = [day, customer, channel, reference, received, sorted(quantities.items())]
    if bank_account_id:
        bank_account_id = integer_value(str(bank_account_id), 'bank account')
        if channel != 'bank_deposit':
            raise DomainError('Select a bank account only for Bank Deposit payments.')
        payload.append(bank_account_id)
    request_hash = hashlib.sha256(json.dumps(payload).encode()).hexdigest()

    with write(db):
        existing = db.execute(
            "SELECT id, request_hash FROM sales WHERE request_key = ?", (request_key,)
        ).fetchone()
        if existing:
            if existing["request_hash"] != request_hash:
                raise Conflict("This sale request was already used. Start a new sale.")
            return existing["id"]

        require_open(db, day)
        if bank_account_id and not db.execute('SELECT 1 FROM bank_accounts WHERE id=?',(bank_account_id,)).fetchone():
            raise DomainError('Choose an existing bank account.')
        if channel == 'bank_deposit' and not bank_account_id and db.execute('SELECT 1 FROM bank_accounts LIMIT 1').fetchone():
            raise DomainError('Choose the receiving bank account for this payment.')
        items = []
        for product_id, quantity in quantities.items():
            product = db.execute(
                "SELECT * FROM products WHERE id = ? AND active = 1", (product_id,)
            ).fetchone()
            if product is None:
                raise DomainError("A product is no longer available. Choose another product.")
            items.append((product, quantity, product["unit_price"] * quantity))

        subtotal = sum(line_total for _, _, line_total in items)
        rate = vat_rate(db, day)
        vat = calculate_vat(subtotal, rate)
        total = subtotal + vat
        if total > MAX_AMOUNT:
            raise DomainError("The sale total exceeds the maximum amount.")
        if received != total:
            raise DomainError("The amount received must equal the sale total.")

        sale_id = db.execute(
            """INSERT INTO sales (business_date, posted_at, customer, channel, payment_reference,
                subtotal, vat_rate, vat, total, received, request_key, request_hash)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (day, timestamp(), customer, channel, reference, subtotal, rate, vat, total,
             received, request_key, request_hash),
        ).lastrowid
        if bank_account_id:
            db.execute('INSERT INTO sale_bank_accounts(sale_id,account_id) VALUES (?,?)',(sale_id,bank_account_id))
        for product, quantity, line_total in items:
            update = db.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
                (quantity, product["id"], quantity),
            )
            if update.rowcount != 1:
                raise Conflict(f"Insufficient stock for {product['description']}. The sale was not posted.")
            db.execute(
                "INSERT INTO sale_lines VALUES (?, ?, ?, ?, ?, ?, ?)",
                (sale_id, product["id"], product["description"], product["unit"],
                 quantity, product["unit_price"], line_total),
            )
        bump_revision(db, day)
        return sale_id


def receipt(db, sale_id):
    sale = db.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
    if sale is None:
        raise Missing("Receipt not found.")
    lines = db.execute(
        "SELECT * FROM sale_lines WHERE sale_id = ? ORDER BY product_id", (sale_id,)
    ).fetchall()
    return sale, lines


def close_snapshot(db, day):
    return db.execute("SELECT * FROM daily_closes WHERE business_date = ?", (day,)).fetchone()


def _activity(db, day, row):
    channel_totals = dict.fromkeys(CHANNELS, 0)
    for entry in db.execute(
        "SELECT channel, SUM(total) AS total FROM sales WHERE business_date = ? GROUP BY channel",
        (day,),
    ):
        channel_totals[entry["channel"]] = entry["total"]
    expenses = db.execute(
        "SELECT * FROM expenses WHERE business_date = ? ORDER BY id", (day,)
    ).fetchall()
    total_expenses = sum(expense["amount"] for expense in expenses)
    return {
        "opening_cash": row["opening_cash"],
        "channel_totals": channel_totals,
        "expenses": expenses,
        "total_expenses": total_expenses,
        "expected_cash": row["opening_cash"] + channel_totals["cash"] - total_expenses,
    }


def preview_close(db, day):
    # Read the revision and the values from the same database snapshot.
    db.execute("BEGIN")
    try:
        row = find_day(db, day)
        return row, _activity(db, day, row)
    finally:
        db.rollback()


def close_day(db, day, *, actual_cash, explanation, revision, expected_unmarked=None):
    with write(db):
        existing = close_snapshot(db, day)
        if existing:
            return existing
        row = require_open(db, day)
        if integer_value(revision, "preview revision", minimum=0, maximum=999_999_999_999) != row["revision"]:
            raise Conflict("Activity changed. Review the updated totals before closing the date.")
        actual = money_value(actual_cash, "the physical cash count")
        explanation = text_value(explanation, "a variance explanation", 500, required=False)
        activity = _activity(db, day, row)
        variance = actual - activity["expected_cash"]
        if variance and not explanation:
            raise DomainError("Explain the cash difference before closing the date.")
        totals = activity["channel_totals"]
        roster, workers_present, payroll_eligible = attendance_summary(db, day)
        unmarked=sum(1 for worker in roster if worker['status'] is None)
        if expected_unmarked is not None and unmarked:
            if str(unmarked) != str(expected_unmarked):
                raise Conflict('Review the current unmarked attendance count before closing this date.')
        db.execute(
            """INSERT INTO daily_closes (business_date, opening_cash, cash_activity,
                mobile_money_activity, bank_activity, expenses, expected_cash, actual_cash,
                variance, explanation, closed_at, workers_present, payroll_eligible) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (day, row["opening_cash"], totals["cash"], totals["mobile_money"], totals["bank_deposit"],
             activity["total_expenses"], activity["expected_cash"], actual, variance,
             explanation, timestamp(), workers_present, payroll_eligible),
        )
        db.execute("UPDATE business_days SET status = 'closed' WHERE business_date = ?", (day,))
        return close_snapshot(db, day)


def add_worker(db, code, name, daily_rate, *, day=None, start_date=None):
    code = text_value(code, "a worker code", 30)
    name = text_value(name, "a worker name", 100)
    rate = money_value(daily_rate, "the daily rate", positive=True)
    start_date = business_date(start_date or day or datetime.now(ZoneInfo('Africa/Kampala')).date().isoformat())
    with write(db):
        if day is not None:
            require_open(db, day)
        existing = db.execute("SELECT * FROM workers WHERE lower(worker_code) = lower(?)", (code,)).fetchone()
        if existing:
            if (existing["name"], existing["daily_rate"]) != (name, rate):
                raise Conflict("That worker code already belongs to another worker entry.")
            return existing["id"]
        worker_id = db.execute(
            "INSERT INTO workers (worker_code, name, daily_rate,started_on) VALUES (?, ?, ?,?)",
            (code, name, rate,start_date),
        ).lastrowid
        db.execute('INSERT INTO worker_rates VALUES (?,?,?)',(worker_id,start_date,rate))
        return worker_id


def mark_attendance(db, day, worker_id, status, *, expected_status=None, reason=None):
    worker_id = integer_value(worker_id, "worker")
    if status not in ("present", "absent"):
        raise DomainError("Select Present or Absent.")
    with write(db):
        require_open(db, day)
        worker = db.execute("SELECT * FROM workers WHERE id = ?", (worker_id,)).fetchone()
        if worker is None:
            raise Missing("Worker not found.")
        if day < worker['started_on'] or (worker['ended_on'] and day > worker['ended_on']):
            raise DomainError('This worker is not on the roster for this date.')
        current = db.execute(
            "SELECT status FROM attendance WHERE business_date = ? AND worker_id = ?", (day, worker_id)
        ).fetchone()
        if current and current["status"] == status:
            return
        if expected_status is not None and expected_status != (current['status'] if current else ''):
            raise Conflict('Attendance changed in another session. Review the current status.')
        if current and reason is not None:
            reason = text_value(reason, 'a reason for the attendance correction', 250)
        rate = db.execute('SELECT daily_rate FROM worker_rates WHERE worker_id=? AND effective_from<=? ORDER BY effective_from DESC LIMIT 1',(worker_id,day)).fetchone()[0]
        db.execute('INSERT INTO attendance_changes(worker_id,business_date,previous_status,new_status,reason,changed_at) VALUES (?,?,?,?,?,?)',
                   (worker_id,day,current['status'] if current else None,status,reason or ('Initial attendance entry' if current is None else 'Service attendance correction'),timestamp()))
        db.execute(
            """INSERT INTO attendance (business_date, worker_id, status, daily_rate, recorded_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT (business_date, worker_id) DO UPDATE
               SET status = excluded.status, recorded_at = excluded.recorded_at""",
            (day, worker_id, status, rate, timestamp()),
        )
        bump_revision(db, day)


def attendance_summary(db, day):
    rows = db.execute(
        """SELECT workers.id, workers.worker_code, workers.name,
                  COALESCE(attendance.daily_rate, (SELECT daily_rate FROM worker_rates r WHERE r.worker_id=workers.id AND r.effective_from<=? ORDER BY r.effective_from DESC LIMIT 1)) AS daily_rate,
                  attendance.status
           FROM workers LEFT JOIN attendance
             ON attendance.worker_id = workers.id AND attendance.business_date = ?
           WHERE workers.started_on<=? AND (workers.ended_on IS NULL OR workers.ended_on>=?)
           ORDER BY workers.id""",
        (day,day,day,day),
    ).fetchall()
    present = [row for row in rows if row["status"] == "present"]
    return rows, len(present), sum(row["daily_rate"] for row in present)


def update_worker(db, worker_id, *, effective_from, daily_rate, ended_on=''):
    worker_id=integer_value(str(worker_id),'worker')
    effective_from=business_date(effective_from)
    rate=money_value(daily_rate,'the daily rate',positive=True)
    ended_on=business_date(ended_on) if ended_on else None
    with write(db):
        worker=db.execute('SELECT * FROM workers WHERE id=?',(worker_id,)).fetchone()
        if worker is None: raise Missing('Worker not found.')
        if effective_from<worker['started_on'] or (ended_on and ended_on<worker['started_on']):
            raise DomainError('Dates cannot precede the worker start date.')
        if db.execute('SELECT 1 FROM attendance WHERE worker_id=? AND business_date>=? LIMIT 1',(worker_id,effective_from)).fetchone():
            raise Conflict('Choose a rate effective date after recorded attendance. Historical rates must remain unchanged.')
        if ended_on and db.execute('SELECT 1 FROM attendance WHERE worker_id=? AND business_date>? LIMIT 1',(worker_id,ended_on)).fetchone():
            raise Conflict('End date would exclude recorded attendance.')
        db.execute('INSERT INTO worker_rates VALUES (?,?,?) ON CONFLICT(worker_id,effective_from) DO UPDATE SET daily_rate=excluded.daily_rate',(worker_id,effective_from,rate))
        db.execute('UPDATE workers SET ended_on=? WHERE id=?',(ended_on,worker_id))
