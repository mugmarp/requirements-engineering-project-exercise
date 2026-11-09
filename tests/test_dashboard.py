"""Historical demo integrity and dashboard/navigation acceptance checks."""
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from dcms import services
from dcms.analytics import overview
from dcms.db import connect, initialize
from dcms.demo import seed_history
from dcms.web import create_app


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href.startswith('/'):
                self.urls.add(href)


class DashboardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        cls.path = Path(cls.folder.name) / 'history.sqlite3'
        initialize(cls.path)
        with connect(cls.path) as db:
            seed_history(db, '2026-11-10')

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def test_history_closes_attendance_stock_and_timestamps_agree(self):
        with connect(self.path) as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            days = db.execute('SELECT * FROM business_days').fetchall()
            self.assertGreater(len(days), 100)
            self.assertEqual([r['business_date'] for r in days if r['status']=='open'], ['2026-11-10'])
            for row in db.execute('SELECT * FROM sales'):
                self.assertEqual(row['posted_at'][:10], row['business_date'])
                self.assertEqual(row['received'], row['total'])
                subtotal = db.execute('SELECT SUM(line_total) FROM sale_lines WHERE sale_id=?', (row['id'],)).fetchone()[0]
                self.assertEqual(row['subtotal'], subtotal)
                self.assertEqual(row['vat'], services.calculate_vat(subtotal, row['vat_rate']))
            for close in db.execute('SELECT * FROM daily_closes'):
                _, activity = services.preview_close(db, close['business_date'])
                self.assertEqual(close['expected_cash'], activity['expected_cash'])
                self.assertEqual(close['expenses'], activity['total_expenses'])
                self.assertEqual(close['cash_activity'], activity['channel_totals']['cash'])
                self.assertEqual(close['mobile_money_activity'], activity['channel_totals']['mobile_money'])
                self.assertEqual(close['bank_activity'], activity['channel_totals']['bank_deposit'])
                self.assertEqual(close['variance'], close['actual_cash']-close['expected_cash'])
                _, present, eligible = services.attendance_summary(db, close['business_date'])
                self.assertEqual((close['workers_present'],close['payroll_eligible']), (present,eligible))
                latest = db.execute('SELECT MAX(posted_at) FROM sales WHERE business_date=?', (close['business_date'],)).fetchone()[0]
                self.assertGreater(close['closed_at'],latest)
            baseline = json.loads(db.execute("SELECT value FROM demo_metadata WHERE key='opening_stock'").fetchone()[0])
            for product in baseline:
                current = db.execute('SELECT * FROM products WHERE sku=?',(product['sku'],)).fetchone()
                sold = db.execute('SELECT COALESCE(SUM(quantity),0) FROM sale_lines WHERE product_id=?',(current['id'],)).fetchone()[0]
                self.assertEqual(product['quantity']-sold,current['stock'])
                self.assertGreaterEqual(current['stock'],0)
            special = services.close_snapshot(db, '2026-11-09')
            self.assertEqual((special['expected_cash'],special['actual_cash'],special['variance']), (45000000,44500000,-500000))
            self.assertIsNone(services._recorded_time.get())

    def test_dashboard_aggregations_and_calendar_coverage(self):
        with connect(self.path) as db:
            data=overview(db,'2026-06-10','2026-11-10','2026-11-10')
            self.assertEqual(data['missing'],[])
            self.assertGreater(len(data['non_operating']),15)
            self.assertEqual(data['sales']['gross'],sum(data['channels'].values()))
            self.assertEqual(data['sales']['net'],sum(p['net'] for p in data['products']))
            self.assertEqual(data['sales']['gross'],sum(p['amount'] for p in data['points']))
            self.assertEqual(data['sales']['gross'],data['sales']['net']+data['sales']['vat'])
            for day in ('2026-06-10','2026-11-09','2026-11-10'):
                data=overview(db,day,day,'2026-11-10')
                expected=db.execute('SELECT COALESCE(SUM(total),0) FROM sales WHERE business_date=?',(day,)).fetchone()[0]
                self.assertEqual(data['sales']['gross'],expected)
            empty=overview(db,'2026-01-01','2026-01-02','2026-11-10')
            self.assertEqual(empty['sales']['gross'],0)
            self.assertEqual(len(empty['missing']),2)
            self.assertEqual(empty['points'],[])

    def test_dashboard_and_linked_pages_render(self):
        client=create_app(self.path).test_client()
        for route in ('/?period=history','/?period=custom&start=2026-06-10&end=2026-06-30',
                      '/daily-records','/days/2026-11-10/sales','/days/2026-11-10/attendance'):
            page=client.get(route)
            self.assertEqual(page.status_code,200,route)
            links=Links(); links.feed(page.get_data(as_text=True))
            for url in links.urls:
                self.assertEqual(client.get(url,follow_redirects=True).status_code,200,url)
        self.assertEqual(client.get('/?period=custom&start=bad&end=2026-06-30').status_code,422)
        self.assertEqual(client.get('/?period=custom&start=2026-07-01&end=2026-06-30').status_code,422)
        self.assertIn(b'next=sales',client.get('/days/2026-11-10/sales').data)
        self.assertIn(b'/work/attendance?day=2026-11-09',client.get('/daily-records?next=attendance').data)
        result=client.get('/work/sales?day=2026-11-09')
        self.assertTrue(result.location.endswith('/days/2026-11-09/receipts'))

    def test_empty_dashboard_and_start_preserves_workflow(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'empty.sqlite3'; initialize(path)
            client=create_app(path).test_client()
            self.assertIn(b"Start today's operations",client.get('/').data)
            with connect(path) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM business_days').fetchone()[0],0)
            self.assertIn('next=attendance',client.get('/work/attendance?day=2026-11-10').location)
            with client.session_transaction() as session:
                session['csrf_token']='test-token'
            response=client.post('/days',data={'csrf':'test-token','business_date':'2026-11-10','next':'attendance'})
            self.assertTrue(response.location.endswith('/days/2026-11-10/attendance'))

    def test_demo_cannot_overwrite_records_or_open_closures(self):
        with connect(self.path) as db:
            before=db.execute('SELECT COUNT(*) FROM sales').fetchone()[0]
            with self.assertRaises(ValueError):
                seed_history(db,'2026-11-10')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM sales').fetchone()[0],before)
            rest=db.execute('SELECT business_date FROM non_operating_days LIMIT 1').fetchone()[0]
            with self.assertRaises(services.Conflict):
                services.open_day(db,rest)
