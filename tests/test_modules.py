import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from dcms import services as s, banking
from dcms.db import connect,initialize
from dcms.demo import seed,seed_history
from dcms.web import create_app

HEADER='id,date,reference,description,credit,debit\n'
class ModulesTest(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(); self.addCleanup(self.folder.cleanup)
        self.path=Path(self.folder.name)/'app.sqlite3'; initialize(self.path)
        with connect(self.path) as db: seed(db)
        self.client=create_app(self.path).test_client()
        with self.client.session_transaction() as session: session['csrf_token']='token'

    def post(self,url,**data): return self.client.post(url,data={'csrf':'token',**data})

    def test_tax_summary_stored_rates_export_and_effective_dates(self):
        page=self.client.get('/taxes?month=2026-11')
        self.assertEqual(page.status_code,200)
        for text in (b'Sales VAT Summary',b'Not captured',b'2026-12-15',b'130,271.19'):
            self.assertIn(text,page.data)
        csv=self.client.get('/taxes?month=2026-11&export=csv')
        self.assertEqual(csv.mimetype,'text/csv')
        self.assertIn(b'Not a VAT return',csv.data)
        self.assertEqual(self.client.get('/taxes?month=invalid').status_code,422)
        with connect(self.path) as db:
            with self.assertRaises(s.Conflict): s.set_vat_rate(db,2000,'2026-11-10')
            s.set_vat_rate(db,2000,'2026-12-01')
            self.assertEqual(s.vat_rate(db,'2026-11-10'),1800)
            self.assertEqual(s.vat_rate(db,'2026-12-01'),2000)
            self.assertEqual(s.receipt(db,3)[0]['vat_rate'],1800)

    def test_workers_roster_history_corrections_and_stale_status(self):
        with connect(self.path) as db:
            worker=s.add_worker(db,'W-NEW','New worker','15000',start_date='2026-11-11')
            self.assertEqual(s.attendance_summary(db,'2026-11-10')[0],[])
            with self.assertRaises(s.DomainError): s.mark_attendance(db,'2026-11-10',str(worker),'present')
            s.mark_attendance(db,'2026-11-11',str(worker),'present',expected_status='',reason='')
            with self.assertRaises(s.Conflict): s.mark_attendance(db,'2026-11-11',str(worker),'absent',expected_status='',reason='Corrected register')
            with self.assertRaises(s.DomainError): s.mark_attendance(db,'2026-11-11',str(worker),'absent',expected_status='present',reason='')
            s.mark_attendance(db,'2026-11-11',str(worker),'absent',expected_status='present',reason='Marked wrong worker')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM attendance_changes').fetchone()[0],2)
            s.update_worker(db,worker,effective_from='2026-11-12',daily_rate='20000',ended_on='2026-11-12')
            self.assertEqual(s.attendance_summary(db,'2026-11-11')[0][0]['daily_rate'],1500000)
            self.assertEqual(s.attendance_summary(db,'2026-11-12')[0][0]['daily_rate'],2000000)
            self.assertEqual(s.attendance_summary(db,'2026-11-13')[0],[])
            with self.assertRaises(s.Conflict): s.update_worker(db,worker,effective_from='2026-11-11',daily_rate='30000')
        self.assertEqual(self.client.get('/workers').status_code,200)
        self.assertEqual(self.client.get(f'/workers/{worker}').status_code,200)

    def test_close_requires_unmarked_acknowledgement(self):
        with connect(self.path) as db:
            s.add_worker(db,'W-01','Unmarked worker','15000',start_date='2026-11-11')
        page=self.client.get('/days/2026-11-11/close')
        self.assertIn(b'unmarked_reviewed',page.data)
        bad=self.post('/days/2026-11-11/close',actual_cash='0',explanation='',revision='0')
        self.assertEqual(bad.status_code,409)
        good=self.post('/days/2026-11-11/close',actual_cash='0',explanation='',revision='0',unmarked_reviewed='1')
        self.assertEqual(good.status_code,303)

    def test_statement_import_atomic_retry_and_validation(self):
        with connect(self.path) as db:
            account=banking.add_account(db,'Main','Example Bank','1234')
            raw=HEADER+'A,2026-11-10,REF,Customer deposit,100000,0\n'
            self.assertEqual(banking.import_statement(db,account,raw),1)
            self.assertEqual(banking.import_statement(db,account,raw),0)
            changed=HEADER+'B,2026-11-10,R2,Other deposit,5000,0\nA,2026-11-10,REF,Customer deposit,200000,0\n'
            with self.assertRaises(s.Conflict): banking.import_statement(db,account,changed)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM bank_transactions').fetchone()[0],1)
            for bad in ('wrong,header\n',HEADER+'X,2026-11-10,R,Bad,10,10\n',HEADER+'X,2026-11-10,R,Bad,-10,0\n'):
                with self.assertRaises(s.DomainError): banking.parse_statement(bad)

    def test_bank_allocations_do_not_duplicate_sales_or_change_closed_report(self):
        with connect(self.path) as db:
            row,activity=s.preview_close(db,'2026-11-10')
            s.close_day(db,'2026-11-10',actual_cash='450000',explanation='',revision=str(row['revision']))
            before=tuple(s.close_snapshot(db,'2026-11-10'))
            account=banking.add_account(db,'Main','Example Bank','1234')
            second=banking.add_account(db,'Second','Example Bank','5678')
            banking.import_statement(db,account,HEADER+'A,2026-11-12,R1,Deposit,100000,0\nB,2026-11-13,R2,Deposit,136000,0\nC,2026-11-13,FEE,Bank charge,0,1000\n')
            banking.match(db,1,3,'100000'); banking.match(db,1,3,'100000')
            banking.match(db,2,3,'136000')
            with self.assertRaises(s.Conflict): banking.match(db,1,3,'100001')
            with self.assertRaises(s.DomainError): banking.match(db,3,3,'1000')
            with self.assertRaises(s.DomainError): banking.match(db,1,2,'1000')
            banking.import_statement(db,second,HEADER+'D,2026-11-14,REF,Wrong account,1000,0\n')
            with self.assertRaises(s.Conflict): banking.match(db,4,3,'1000')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM sales').fetchone()[0],3)
            self.assertEqual(tuple(s.close_snapshot(db,'2026-11-10')),before)
            self.assertEqual(db.execute('SELECT SUM(amount) FROM bank_matches WHERE sale_id=3').fetchone()[0],23600000)

    def test_bank_reversal_retains_history_and_restores_capacity(self):
        with connect(self.path) as db:
            account=banking.add_account(db,'Main','Example Bank','1234')
            banking.import_statement(db,account,HEADER+'A,2026-11-10,R,Deposit,236000,0\n')
            banking.match(db,1,3,'236000')
            with self.assertRaises(s.DomainError): banking.reverse(db,1,'')
            banking.reverse(db,1,'Selected wrong statement line')
            self.assertEqual(banking.summary(db,account)[1][0]['allocated'],0)
            banking.match(db,1,3,'236000')
            self.assertEqual(banking.summary(db,account)[1][0]['allocated'],23600000)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM bank_allocation_events').fetchone()[0],3)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM sales').fetchone()[0],3)

    def test_bank_delayed_retries_do_not_undo_later_corrections(self):
        with connect(self.path) as db:
            account=banking.add_account(db,'Main','Example Bank','1234')
            banking.import_statement(db,account,HEADER+'A,2026-11-10,R,Deposit,236000,0\n')
            banking.match(db,1,3,'236000',request_key='first-allocation')
            banking.reverse(db,1,'Wrong selection',request_key='first-reversal',expected_revision='0')
            banking.match(db,1,3,'236000',request_key='first-allocation')
            self.assertEqual(banking.summary(db,account)[1][0]['allocated'],0)
            banking.match(db,1,3,'236000',request_key='new-reviewed-allocation')
            banking.reverse(db,1,'Wrong selection',request_key='first-reversal',expected_revision='0')
            self.assertEqual(banking.summary(db,account)[1][0]['allocated'],23600000)
            with self.assertRaises(s.Conflict): banking.reverse(db,1,'Stale tab',request_key='stale-reversal',expected_revision='0')

    def test_banking_preview_does_not_import(self):
        account=self.post('/banking/accounts',name='Main',bank_name='Example Bank',suffix='1234')
        self.assertEqual(account.status_code,303)
        raw=HEADER+'A,2026-11-10,R,Deposit,236000,0\n'
        preview=self.post('/banking/import',account_id='1',csv=raw)
        self.assertEqual(preview.status_code,200)
        self.assertIn(b'Confirm statement import',preview.data)
        self.assertIn(b'data-navigation-url="/banking?account_id=1"',preview.data)
        with connect(self.path) as db: self.assertEqual(db.execute('SELECT COUNT(*) FROM bank_transactions').fetchone()[0],0)
        self.assertEqual(self.post('/banking/import',account_id='1',csv=raw,confirm='yes').status_code,303)
        self.assertEqual(self.client.get('/banking?account_id=1').status_code,200)

    def test_clean_history_and_no_future_timestamps(self):
        path=Path(self.folder.name)/'history.sqlite3';initialize(path)
        end=datetime.now(ZoneInfo('Africa/Kampala')).date().isoformat()
        with connect(path) as db:
            seed_history(db,end)
            for row in db.execute('SELECT posted_at FROM sales'):
                self.assertLessEqual(datetime.fromisoformat(row[0]),datetime.now(ZoneInfo('Africa/Kampala')))
            for table,column in [('workers','name'),('sales','customer'),('expenses','description'),('non_operating_days','reason')]:
                self.assertEqual(db.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} LIKE '%Demo%'").fetchone()[0],0)
            self.assertGreater(len(s.attendance_summary(db,db.execute('SELECT MIN(business_date) FROM business_days').fetchone()[0])[0]),0)
