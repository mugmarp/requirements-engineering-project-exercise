"""Read-only, date-scoped dashboard queries. All monetary values are minor units."""
from datetime import date, timedelta


def overview(db, start, end, today):
    # One read transaction gives all cards and charts the same database snapshot.
    db.execute('BEGIN')
    try:
        return _overview(db, start, end, today)
    finally:
        db.rollback()


def _overview(db, start, end, today):
    bounds = (start, end)
    sales = db.execute('''SELECT COUNT(*) AS count, COALESCE(SUM(total),0) AS gross,
        COALESCE(SUM(subtotal),0) AS net, COALESCE(SUM(vat),0) AS vat
        FROM sales WHERE business_date BETWEEN ? AND ?''', bounds).fetchone()
    expenses = db.execute('SELECT COALESCE(SUM(amount),0) FROM expenses WHERE business_date BETWEEN ? AND ?', bounds).fetchone()[0]
    channels = {row['channel']: row['total'] for row in db.execute('''SELECT channel, SUM(total) AS total
        FROM sales WHERE business_date BETWEEN ? AND ? GROUP BY channel''', bounds)}
    products = db.execute('''SELECT l.product_id, l.description, l.unit, SUM(l.quantity) AS quantity,
        SUM(l.line_total) AS net FROM sale_lines l JOIN sales s ON s.id=l.sale_id
        WHERE s.business_date BETWEEN ? AND ? GROUP BY l.product_id,l.description,l.unit
        ORDER BY net DESC''', bounds).fetchall()
    days = db.execute('SELECT * FROM business_days WHERE business_date BETWEEN ? AND ? ORDER BY business_date', bounds).fetchall()
    non_operating = db.execute('SELECT * FROM non_operating_days WHERE business_date BETWEEN ? AND ? ORDER BY business_date', bounds).fetchall()
    closes = db.execute('SELECT * FROM daily_closes WHERE business_date BETWEEN ? AND ? ORDER BY business_date DESC', bounds).fetchall()
    daily = {row['business_date']: row['total'] for row in db.execute('''SELECT business_date, SUM(total) AS total
        FROM sales WHERE business_date BETWEEN ? AND ? GROUP BY business_date''', bounds)}
    # Plot recorded business dates only: unrecorded dates never become artificial zeros.
    peak = max(daily.values(), default=0) or 1
    points = [{'date': row['business_date'], 'amount': daily.get(row['business_date'], 0),
               'x': round(35 + i * 630 / max(len(days)-1, 1), 2),
               'y': round(170 - daily.get(row['business_date'], 0) * 140 / peak, 2)}
              for i, row in enumerate(days)]
    attendance = db.execute('''SELECT COUNT(*) AS present, COALESCE(SUM(daily_rate),0) AS eligible
        FROM attendance WHERE business_date=? AND status='present' ''', (today,)).fetchone()
    today_row = db.execute('SELECT * FROM business_days WHERE business_date=?', (today,)).fetchone()
    today_cash = db.execute("SELECT COALESCE(SUM(total),0) FROM sales WHERE business_date=? AND channel='cash'", (today,)).fetchone()[0]
    today_expenses = db.execute('SELECT COALESCE(SUM(amount),0) FROM expenses WHERE business_date=?', (today,)).fetchone()[0]
    recent = db.execute('''SELECT id,business_date,customer,channel,total FROM sales
        WHERE business_date BETWEEN ? AND ? ORDER BY business_date DESC,posted_at DESC,id DESC LIMIT 8''', bounds).fetchall()
    pending = db.execute("SELECT business_date FROM business_days WHERE status='open' AND business_date<=? ORDER BY business_date", (today,)).fetchall()
    known = {row['business_date'] for row in days} | {row['business_date'] for row in non_operating}
    # Future dates are not overdue missing records.
    cutoff = min(date.fromisoformat(end), date.fromisoformat(today))
    missing = []
    cursor = date.fromisoformat(start)
    while cursor <= cutoff:
        if cursor.isoformat() not in known:
            missing.append(cursor.isoformat())
        cursor += timedelta(days=1)
    metadata = {row['key']: row['value'] for row in db.execute('SELECT * FROM demo_metadata')}
    return dict(sales=sales, expenses=expenses, channels=channels, products=products,
        days=days, closes=closes, non_operating=non_operating, points=points,
        chart_peak=peak if points else 0, attendance=attendance, today_row=today_row,
        today_expected=(today_row['opening_cash'] + today_cash - today_expenses) if today_row else None,
        recent=recent, pending=pending, missing=missing, metadata=metadata,
        variance=sum(row['variance'] for row in closes))
