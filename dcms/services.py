"""Posting and reconciliation rules shared by the web and future desktop UIs."""

import hashlib
import json
import re
from collections import Counter
from datetime import date, datetime, timezone

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


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


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


def vat_rate(db):
    return db.execute("SELECT value FROM settings WHERE key = 'vat_basis_points'").fetchone()[0]


def set_vat_rate(db, basis_points):
    if not 0 <= basis_points <= 10_000:
        raise DomainError("The VAT rate must be between 0 and 100 percent.")
    with write(db):
        db.execute("UPDATE settings SET value = ? WHERE key = 'vat_basis_points'", (basis_points,))


def calculate_vat(subtotal, basis_points):
    return (subtotal * basis_points + 5_000) // 10_000


def post_sale(db, day, *, customer, channel, reference, received, request_key, lines):
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
        items = []
        for product_id, quantity in quantities.items():
            product = db.execute(
                "SELECT * FROM products WHERE id = ? AND active = 1", (product_id,)
            ).fetchone()
            if product is None:
                raise DomainError("A product is no longer available. Choose another product.")
            items.append((product, quantity, product["unit_price"] * quantity))

        subtotal = sum(line_total for _, _, line_total in items)
        rate = vat_rate(db)
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


def close_day(db, day, *, actual_cash, explanation, revision):
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
        _, workers_present, payroll_eligible = attendance_summary(db, day)
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


def add_worker(db, code, name, daily_rate):
    code = text_value(code, "a worker code", 30)
    name = text_value(name, "a worker name", 100)
    rate = money_value(daily_rate, "the daily rate", positive=True)
    with write(db):
        existing = db.execute("SELECT * FROM workers WHERE worker_code = ?", (code,)).fetchone()
        if existing:
            if (existing["name"], existing["daily_rate"]) != (name, rate):
                raise Conflict("That worker code already belongs to another worker entry.")
            return existing["id"]
        return db.execute(
            "INSERT INTO workers (worker_code, name, daily_rate) VALUES (?, ?, ?)",
            (code, name, rate),
        ).lastrowid


def mark_attendance(db, day, worker_id, status):
    worker_id = integer_value(worker_id, "worker")
    if status not in ("present", "absent"):
        raise DomainError("Select Present or Absent.")
    with write(db):
        require_open(db, day)
        worker = db.execute("SELECT * FROM workers WHERE id = ?", (worker_id,)).fetchone()
        if worker is None:
            raise Missing("Worker not found.")
        current = db.execute(
            "SELECT status FROM attendance WHERE business_date = ? AND worker_id = ?", (day, worker_id)
        ).fetchone()
        if current and current["status"] == status:
            return
        db.execute(
            """INSERT INTO attendance (business_date, worker_id, status, daily_rate, recorded_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT (business_date, worker_id) DO UPDATE
               SET status = excluded.status, recorded_at = excluded.recorded_at""",
            (day, worker_id, status, worker["daily_rate"], timestamp()),
        )
        bump_revision(db, day)


def attendance_summary(db, day):
    rows = db.execute(
        """SELECT workers.id, workers.worker_code, workers.name,
                  COALESCE(attendance.daily_rate, workers.daily_rate) AS daily_rate,
                  attendance.status
           FROM workers LEFT JOIN attendance
             ON attendance.worker_id = workers.id AND attendance.business_date = ?
           ORDER BY workers.id""",
        (day,),
    ).fetchall()
    present = [row for row in rows if row["status"] == "present"]
    return rows, len(present), sum(row["daily_rate"] for row in present)
