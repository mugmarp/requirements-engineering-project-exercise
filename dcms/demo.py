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


def seed_history(db, end):
    """Generate five months of clearly synthetic activity into an empty database.

    Uses posting services, a context-local historical clock and documented initial
    stock. It never edits posted receipts or saved closes after their creation.
    """
    import calendar
    import json
    import random
    from datetime import date, datetime, timedelta
    from zoneinfo import ZoneInfo
    from . import services

    end = date.fromisoformat(end)
    month_index = end.year * 12 + end.month - 1 - 5
    year, month = divmod(month_index, 12)
    start = date(year, month + 1, min(end.day, calendar.monthrange(year, month + 1)[1]))
    rng = random.Random(2102)
    with write(db):
        if any(db.execute(f'SELECT 1 FROM {table} LIMIT 1').fetchone()
               for table in ('products', 'business_days', 'workers', 'non_operating_days', 'demo_metadata')):
            raise ValueError('Historical demo requires an empty database.')
        opening = []
        for sku, description, unit, price, _ in PRODUCTS[:4]:
            stock = 150_000 if sku != 'KR-G' else 30_000
            db.execute('INSERT INTO products(sku,description,unit,unit_price,stock) VALUES (?,?,?,?,?)',
                       (sku, description, unit, price, stock))
            opening.append({'sku': sku, 'quantity': stock, 'unit': unit})
        # The presentation pack is isolated to its original worked example.
        db.execute('INSERT INTO products(sku,description,unit,unit_price,stock) VALUES (?,?,?,?,?)', PRODUCTS[4])
        opening.append({'sku': PRODUCTS[4][0], 'quantity': PRODUCTS[4][4], 'unit': 'pack'})
        db.executemany('INSERT INTO demo_metadata VALUES (?,?)', [
            ('start', start.isoformat()), ('end', end.isoformat()),
            ('opening_stock', json.dumps(opening)),
            ('notice', 'Synthetic demonstration records. Prices, volumes, customers and work calendar are illustrative.'),
            ('stock_basis', 'One documented opening stock allocation; no replenishment or production history is implied.'),
            ('cash_basis', 'Independent daily opening float of UGX 50,000; prior-day custody and settlement are outside this demo.'),
        ])
    worker_names = ['Alex Kato', 'Grace Atwine', 'Peter Mugisha', 'Ruth Namara', 'David Okello',
                    'Sarah Akello', 'James Tumusiime', 'Esther Achen', 'Paul Ssemanda', 'Mary Ninsiima']
    for i, name in enumerate(worker_names):
        services.add_worker(db, f'DW-{i+1:03}', name + ' (Demo)', str(15000 + (i % 4) * 2500))
    customers = ['Kijani Building Works', 'Hillview Homes', 'West Ridge Builders', 'Lake Road Works',
                 'Sunrise Housing', 'Valley Contractors', 'Market Lane Project', 'Walk-in buyer']
    def at(day, hour, minute, operation):
        moment = datetime(day.year, day.month, day.day, hour, minute, tzinfo=ZoneInfo('Africa/Kampala'))
        token = services._recorded_time.set(moment)
        try:
            return operation()
        finally:
            services._recorded_time.reset(token)

    day = start
    index = 0
    while day <= end:
        iso = day.isoformat()
        # This schedule is a demo assumption, not an observed business calendar.
        if day not in (end, end - timedelta(days=1)) and (day.weekday() == 6 or (index > 0 and index % 47 == 0)):
            db.execute('INSERT INTO non_operating_days VALUES (?,?)',
                       (iso, 'Demo scheduled rest day' if day.weekday() == 6 else 'Demo maintenance closure'))
        else:
            services.open_day(db, iso)
            special = day == end - timedelta(days=1)
            services.set_opening_cash(db, iso, '0' if special else '50000')
            for worker in range(1, 11):
                at(day, 7, worker, lambda worker=worker: services.mark_attendance(
                    db, iso, str(worker), 'present' if rng.random() > .15 else 'absent'))
            orders = [(5, 1, 'cash'), (1, 40, 'mobile_money'), (4, 20, 'bank_deposit')] if special else None
            count = 4 if day == end else rng.randint(3, 9)
            for order in range(len(orders) if orders else count):
                if orders:
                    product, qty, channel = orders[order]
                    lines = [(str(product), str(qty))]
                else:
                    channel = 'cash' if order == 0 else rng.choices(list(services.CHANNELS), weights=[55,30,15])[0]
                    ids = rng.sample([1,2,3,4], 2 if rng.random() < .35 else 1)
                    lines = [(str(pid), str(rng.choice([20,40,60,100,150,200]) if pid != 4 else rng.choice([5,10,15,20]))) for pid in ids]
                subtotal = sum(db.execute('SELECT unit_price FROM products WHERE id=?',(pid,)).fetchone()[0]*int(qty) for pid,qty in lines)
                total = subtotal + services.calculate_vat(subtotal, services.vat_rate(db))
                received = f'{total//100}.{total%100:02d}'
                at(day, 8 + order, rng.randrange(5,55), lambda: services.post_sale(
                    db, iso, customer=customers[rng.randrange(len(customers))] + ' (Demo)',
                    channel=channel, reference='' if channel=='cash' else f'DEMO-{iso}-{order+1:02}',
                    received=received, request_key=f'history-{iso}-{order}', lines=lines))
            expenses = [('Loader lunch and local transport (Demo)', 50000)] if special else [
                (rng.choice(['Loading team lunch', 'Site transport', 'Equipment fuel']) + ' (Demo)', rng.choice([15000,20000,25000,35000]))
                for _ in range(rng.randint(0,2))]
            for i, (description, amount) in enumerate(expenses):
                at(day, 12+i, 30, lambda: services.record_expense(db,iso,description,str(amount),f'history-expense-{iso}-{i}'))
            if day < end and not special:
                _, activity = services.preview_close(db, iso)
                _, _, wages = services.attendance_summary(db, iso)
                if wages and activity['expected_cash'] >= wages:
                    at(day, 17, 45, lambda: services.record_expense(
                        db, iso, 'Daily worker wage payout (Demo)',
                        f'{wages//100}.{wages%100:02d}', f'history-wages-{iso}'))
            if day < end:
                row, activity = services.preview_close(db,iso)
                variance = -500000 if special else rng.choices([0,-100000,-200000,50000],weights=[91,4,3,2])[0]
                actual = activity['expected_cash'] + variance
                explanation = 'Demo UGX 5,000 shortage flagged for Owner review.' if special else ('Demo count difference recorded for review.' if variance else '')
                at(day,18,15,lambda: services.close_day(db,iso,actual_cash=f'{actual//100}.{actual%100:02}',explanation=explanation,revision=str(row['revision'])))
        day += timedelta(days=1)
        index += 1
