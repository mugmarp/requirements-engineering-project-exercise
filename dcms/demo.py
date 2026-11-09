"""Repeatable sample data for the presentation."""

from .db import write
from .services import open_day, post_sale, record_expense

DEMO_DATE = "2026-11-10"
PRODUCTS = (
    ("SB-6", "Solid concrete block 6 × 8 × 16", "piece", 250_000, 600),
    ("HB-4", "Hollow concrete block 4 × 8 × 16", "piece", 200_000, 480),
    ("PV-60", "Interlocking paver 60 mm", "piece", 125_000, 960),
    ("KR-G", "Garden kerb", "piece", 1_000_000, 160),
    ("PV-PACK", "Paver project pack", "pack", 42_372_881, 8),
)


def seed(db):
    # A demo initialization is intentionally restricted to an empty database.
    with write(db):
        if db.execute("SELECT 1 FROM business_days LIMIT 1").fetchone():
            raise ValueError("Demo seed requires a fresh database. Choose a new database path.")
        db.executemany(
            "INSERT INTO products (sku, description, unit, unit_price, stock) VALUES (?, ?, ?, ?, ?)",
            PRODUCTS,
        )
    open_day(db, DEMO_DATE)
    open_day(db, "2026-11-11")
    for product, quantity, channel, received in (
        (5, 1, "cash", "500000"),
        (1, 40, "mobile_money", "118000"),
        (4, 20, "bank_deposit", "236000"),
    ):
        post_sale(
            db, DEMO_DATE, customer="Sample customer", channel=channel,
            reference="" if channel == "cash" else f"DEMO-{product}",
            received=received, request_key=f"seed-{product}",
            lines=[(str(product), str(quantity))],
        )
    record_expense(db, DEMO_DATE, "Sample loading and transport expense", "50000", "seed-expense")
