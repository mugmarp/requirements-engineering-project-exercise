"""Server-side checks behind navigation and posting reviews."""
import tempfile
import unittest
from pathlib import Path

from dcms import services
from dcms.db import connect, initialize
from dcms.demo import seed
from dcms.web import create_app


class WorkflowIntegrityTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / 'test.sqlite3'
        initialize(self.path)
        with connect(self.path) as db:
            seed(db)
        self.client = create_app(self.path).test_client()
        with self.client.session_transaction() as session:
            session['csrf_token'] = 'test-token'

    def post(self, url, **fields):
        return self.client.post(url, data={'csrf': 'test-token', **fields})

    def test_worker_creation_is_locked_with_the_date(self):
        with connect(self.path) as db:
            row, activity = services.preview_close(db, '2026-11-10')
            services.close_day(db, '2026-11-10', actual_cash='450000', explanation='', revision=str(row['revision']))
        response = self.post('/days/2026-11-10/workers', code='LOCKED', name='Should not save', daily_rate='15000')
        self.assertEqual(response.status_code, 409)
        with connect(self.path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM workers').fetchone()[0], 0)

    def test_worker_errors_keep_entered_fields(self):
        response = self.post('/days/2026-11-11/workers', code='W-NEW', name='Entered name', daily_rate='bad-rate')
        self.assertEqual(response.status_code, 422)
        for value in ('W-NEW', 'Entered name', 'bad-rate'):
            self.assertIn(value.encode(), response.data)
        self.assertIn(b'data-unsaved="true"', response.data)
        with connect(self.path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM workers').fetchone()[0], 0)

    def test_float_error_keeps_attempt_without_changing_money(self):
        response = self.post('/days/2026-11-11/opening-cash', amount='bad-float')
        self.assertEqual(response.status_code, 422)
        self.assertIn(b'value="bad-float"', response.data)
        with connect(self.path) as db:
            self.assertEqual(services.find_day(db, '2026-11-11')['opening_cash'], 0)

    def test_expired_forms_and_missing_pages_have_return_navigation(self):
        response = self.client.post('/days', data={'business_date': '2026-11-12'})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'data-return-label', response.data)
        self.assertIn(b'The form expired', response.data)
        response = self.client.get('/unknown-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Breadcrumb', response.data)

    def test_review_controls_exist_and_print_is_separate(self):
        sale = self.client.get('/days/2026-11-11/sales').data
        self.assertIn(b'data-review="sale"', sale)
        self.assertIn(b'>Cancel</a>', sale)
        self.assertIn(b'id="action-dialog"', sale)
        close = self.client.get('/days/2026-11-11/close').data
        for kind in ('close', 'expense', 'opening'):
            self.assertIn(f'data-review="{kind}"'.encode(), close)
        receipt = self.client.get('/receipts/1').data
        self.assertIn(b'data-print', receipt)
        self.assertNotIn(b'data-review="sale"', receipt)
