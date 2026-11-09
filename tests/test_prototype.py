import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

from dcms import services
from dcms.db import connect, initialize
from dcms.demo import DEMO_DATE, seed
from dcms.web import create_app

DAY = DEMO_DATE
NEXT_DAY = "2026-11-11"


class PrototypeTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "test.sqlite3"
        initialize(self.path)
        with connect(self.path) as db:
            seed(db)
        self.app = create_app(self.path)
        self.client = self.app.test_client()

    def sale(self, db, *, day=NEXT_DAY, request_key="test-sale", received="5310", **kwargs):
        data = {
            "customer": "Test customer", "channel": "cash", "reference": "",
            "received": received, "request_key": request_key, "lines": [("1", "1"), ("2", "1")],
        }
        data.update(kwargs)
        return services.post_sale(db, day, **data)

    def submit(self, url, **data):
        with self.client.session_transaction() as session:
            session["csrf_token"] = "test-token"
        return self.client.post(url, data={"csrf": "test-token", **data})

    def test_atomic_stock_receipt_and_retry(self):
        with connect(self.path) as db:
            before = [tuple(row) for row in db.execute("SELECT id, stock FROM products ORDER BY id")]
            with self.assertRaisesRegex(services.Conflict, "Insufficient stock"):
                self.sale(db, received="1182950", lines=[("1", "1"), ("2", "500")])
            self.assertEqual(before, [tuple(row) for row in db.execute("SELECT id, stock FROM products ORDER BY id")])
            self.assertEqual(db.execute("SELECT COUNT(*) FROM sales WHERE business_date = ?", (NEXT_DAY,)).fetchone()[0], 0)
            with self.assertRaisesRegex(services.DomainError, "must equal"):
                self.sale(db, received="5000")
            sale_id = self.sale(db)
            self.assertEqual(self.sale(db), sale_id)
            with self.assertRaisesRegex(services.Conflict, "already used"):
                self.sale(db, customer="Different customer")
            sale, lines = services.receipt(db, sale_id)
            self.assertEqual((sale["subtotal"], sale["vat"], sale["total"]), (450000, 81000, 531000))
            self.assertEqual(len(lines), 2)
            self.assertEqual(db.execute("SELECT stock FROM products WHERE id = 1").fetchone()[0], before[0][1] - 1)
            services.set_vat_rate(db, 0, "2026-11-12")
            self.assertEqual(services.receipt(db, sale_id)[0]["vat"], 81000)

    def test_two_concurrent_sales_cannot_oversell(self):
        with connect(self.path) as db:
            db.execute("UPDATE products SET stock = 1 WHERE id = 1")
        barrier = Barrier(2)

        def attempt(i):
            with connect(self.path) as db:
                barrier.wait(timeout=3)
                try:
                    return self.sale(db, request_key=f"race-{i}", lines=[("1", "1")], received="2950")
                except services.Conflict:
                    return None

        with ThreadPoolExecutor(2) as pool:
            results = list(pool.map(attempt, range(2)))
        self.assertEqual(sum(result is not None for result in results), 1)
        with connect(self.path) as db:
            self.assertEqual(db.execute("SELECT stock FROM products WHERE id = 1").fetchone()[0], 0)

    def test_close_stale_preview_and_nonzero_reason(self):
        with connect(self.path) as db:
            day, preview = services.preview_close(db, DAY)
            self.assertEqual(preview["channel_totals"], {
                "cash": 50000000, "mobile_money": 11800000, "bank_deposit": 23600000,
            })
            self.assertEqual(preview["expected_cash"], 45000000)
            self.sale(db)
            self.assertEqual(services.preview_close(db, DAY)[1]["expected_cash"], 45000000)
            for invalid in ("", "-1", "1.001"):
                with self.assertRaises(services.DomainError):
                    services.close_day(db, DAY, actual_cash=invalid, explanation="", revision=str(day["revision"]))
            with self.assertRaisesRegex(services.DomainError, "Explain"):
                services.close_day(db, DAY, actual_cash="445000", explanation="  ", revision=str(day["revision"]))
            services.set_opening_cash(db, DAY, "20000")
            with self.assertRaisesRegex(services.Conflict, "Activity changed"):
                services.close_day(db, DAY, actual_cash="445000", explanation="Sample", revision=str(day["revision"]))
            day, _ = services.preview_close(db, DAY)
            saved = services.close_day(db, DAY, actual_cash="445000", explanation="Sample", revision=str(day["revision"]))
            self.assertEqual(saved["variance"], -2500000)
            self.assertEqual(dict(saved), dict(services.close_day(db, DAY, actual_cash="", explanation="", revision="")))
            with self.assertRaises(services.Conflict):
                self.sale(db, day=DAY, request_key="after-close")
            with self.assertRaises(services.Conflict):
                services.record_expense(db, DAY, "After close", "1", "after-close-expense")
            with self.assertRaises(services.Conflict):
                services.set_opening_cash(db, DAY, "0")
            self.assertEqual(services.find_day(db, NEXT_DAY)["status"], "open")

    def test_post_racing_close_cannot_change_saved_totals(self):
        barrier = Barrier(2)

        def post():
            with connect(self.path) as db:
                barrier.wait(timeout=3)
                try:
                    self.sale(db)
                    return True
                except services.Conflict:
                    return False

        def close():
            with connect(self.path) as db:
                barrier.wait(timeout=3)
                try:
                    services.close_day(db, NEXT_DAY, actual_cash="0", explanation="", revision="0")
                    return True
                except services.Conflict:
                    return False

        with ThreadPoolExecutor(2) as pool:
            posted = pool.submit(post)
            closed = pool.submit(close)
            self.assertNotEqual(posted.result(), closed.result())
        with connect(self.path) as db:
            snapshot = services.close_snapshot(db, NEXT_DAY)
            if snapshot:
                self.assertEqual((snapshot["cash_activity"], snapshot["variance"]), (0, 0))
            else:
                day, activity = services.preview_close(db, NEXT_DAY)
                saved = services.close_day(
                    db, NEXT_DAY, actual_cash="5310", explanation="", revision=str(day["revision"])
                )
                self.assertEqual((saved["expected_cash"], saved["variance"]), (activity["expected_cash"], 0))

    def test_web_flow_and_reopen_with_new_app(self):
        response = self.client.get(f"/days/{NEXT_DAY}/sales")
        self.assertIn(b"Daily Sales", response.data)
        sale_fields = {
            "customer": "Test customer", "channel": "mobile_money", "reference": "SAMPLE-MM",
            "received": "5310", "request_key": "web-sale", "product": ["1", "2"], "quantity": ["1", "1"],
        }
        response = self.submit(f"/days/{NEXT_DAY}/sales", **sale_fields)
        self.assertEqual(response.status_code, 303)
        receipt_url = response.location
        self.assertIn(b"UGX 5,310", self.client.get(receipt_url).data)
        self.assertEqual(self.submit(f"/days/{NEXT_DAY}/sales", **sale_fields).location, receipt_url)
        self.assertEqual(self.submit(f"/days/{DAY}/close", actual_cash="445000", explanation="", revision="4").status_code, 422)
        response = self.submit(f"/days/{DAY}/close", actual_cash="445000", explanation="Sample variance", revision="4")
        self.assertEqual(response.status_code, 303)
        fresh = create_app(self.path).test_client()
        report = fresh.get(response.location).data
        for phrase in (b"450,000", b"445,000", b"UGX 5,000 deficit", b"Sample variance"):
            self.assertIn(phrase, report)
        self.assertIn(b"Test customer", fresh.get(receipt_url).data)
        self.assertIn(b"View receipt", fresh.get(f"/days/{NEXT_DAY}/receipts").data)

    def test_attendance_eligibility_and_close_snapshot(self):
        with connect(self.path) as db:
            worker = services.add_worker(db, "W-01", "Sample worker", "20000")
            other = services.add_worker(db, "W-02", "Other worker", "25000")
            self.assertEqual(services.add_worker(db, "W-01", "Sample worker", "20000"), worker)
            services.mark_attendance(db, NEXT_DAY, str(worker), "present")
            revision = services.find_day(db, NEXT_DAY)["revision"]
            services.mark_attendance(db, NEXT_DAY, str(worker), "present")
            self.assertEqual(services.find_day(db, NEXT_DAY)["revision"], revision)
            services.mark_attendance(db, NEXT_DAY, str(other), "absent")
            self.assertEqual(services.attendance_summary(db, NEXT_DAY)[1:], (1, 2000000))
            services.mark_attendance(db, DAY, str(worker), "absent")
            self.assertEqual(services.attendance_summary(db, NEXT_DAY)[1:], (1, 2000000))
            services.mark_attendance(db, NEXT_DAY, str(worker), "absent")
            self.assertEqual(services.attendance_summary(db, NEXT_DAY)[1:], (0, 0))
            services.mark_attendance(db, NEXT_DAY, str(worker), "present")
            revision = services.find_day(db, NEXT_DAY)["revision"]
            saved = services.close_day(db, NEXT_DAY, actual_cash="0", explanation="", revision=str(revision))
            self.assertEqual((saved["workers_present"], saved["payroll_eligible"]), (1, 2000000))
            with self.assertRaises(services.Conflict):
                services.mark_attendance(db, NEXT_DAY, str(worker), "absent")
            self.assertEqual(services.close_snapshot(db, NEXT_DAY)["payroll_eligible"], 2000000)

    def test_worker_and_attendance_web_entry(self):
        response = self.submit(
            f"/days/{NEXT_DAY}/workers", code="W-01", name="Sample worker", daily_rate="15000",
        )
        self.assertEqual(response.status_code, 303)
        response = self.submit(f"/days/{NEXT_DAY}/attendance", worker_id="1", status="present")
        self.assertEqual(response.status_code, 303)
        page = self.client.get(response.location)
        self.assertIn(b"UGX 15,000", page.data)
        self.assertIn(b"Present", page.data)
        self.assertEqual(self.submit(
            f"/days/{NEXT_DAY}/attendance", worker_id="1", status="half-day",
        ).status_code, 422)
        self.assertEqual(self.submit(
            f"/days/{NEXT_DAY}/workers", code="W-01", name="Different", daily_rate="20000",
        ).status_code, 409)

    def test_csrf_and_demo_password(self):
        self.assertEqual(self.client.post("/days", data={"business_date": "2026-11-12"}).status_code, 400)
        private = create_app(self.path, password="sample-pass").test_client()
        self.assertEqual(private.get("/").status_code, 401)
        self.assertEqual(private.get("/", auth=("demo", "sample-pass")).status_code, 200)

    def test_expense_retry_is_recorded_once(self):
        url = f"/days/{NEXT_DAY}/expenses"
        fields = {"description": "Sample cash expense", "amount": "123", "request_key": "expense-retry"}
        self.assertEqual(self.submit(url, **fields).status_code, 303)
        self.assertEqual(self.submit(url, **fields).status_code, 303)
        self.assertEqual(self.submit(url, **dict(fields, amount="124")).status_code, 409)
        with connect(self.path) as db:
            self.assertEqual(services.preview_close(db, NEXT_DAY)[1]["total_expenses"], 12300)


if __name__ == "__main__":
    unittest.main()
