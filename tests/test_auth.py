import tempfile
import unittest
from pathlib import Path
from werkzeug.security import generate_password_hash
from dcms.db import initialize,connect
from dcms.demo import seed
from dcms.banking import add_account
from dcms.web import create_app


class AccountAccessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        password_hash=generate_password_hash('demo',method='pbkdf2:sha256:600000')
        cls.users={role:{'role':role,'name':label,'password_hash':password_hash}
                   for role,label in [('sales_manager','Sales Manager'),('ceo','CEO')]}

    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path=Path(self.folder.name)/'app.sqlite3'
        initialize(self.path)
        with connect(self.path) as db:
            seed(db)
            add_account(db,'Main account','Bank','1234')
        self.app=create_app(self.path,users=self.users,secure=True)
        self.client=self.app.test_client()

    def login(self,username='sales_manager',password='demo',next='/'):
        self.client.get('/login')
        with self.client.session_transaction() as session: token=session['csrf_token']
        return self.client.post('/login',data={'username':username,'password':password,'csrf':token,'next':next})

    def submit(self,path,**fields):
        with self.client.session_transaction() as session: token=session['csrf_token']
        return self.client.post(path,data={'csrf':token,**fields})

    def test_login_logout_csrf_and_cookie(self):
        self.assertEqual(self.client.get('/').status_code,302)
        self.assertEqual(self.client.post('/login',data={'username':'ceo','password':'demo'}).status_code,400)
        result=self.login()
        self.assertEqual(result.status_code,303)
        self.assertIn('Secure',result.headers['Set-Cookie'])
        with self.client.session_transaction() as session: self.assertEqual(session['username'],'sales_manager')
        self.assertIn(b'Sales Manager',self.client.get('/').data)
        self.assertEqual(self.submit('/logout').status_code,303)
        self.assertEqual(self.client.get('/').status_code,302)

    def test_ceo_cannot_mutate_any_post_route(self):
        self.login('ceo')
        with connect(self.path) as db: before=list(db.iterdump())
        for rule in self.app.url_map.iter_rules():
            if 'POST' not in rule.methods or rule.endpoint in ('login','logout'):continue
            path=rule.rule.replace('<day>','2026-11-10').replace('<int:worker_id>','1').replace('<int:account_id>','1').replace('<int:line_id>','1').replace('<int:match_id>','1')
            self.assertEqual(self.submit(path).status_code,403,path)
        with connect(self.path) as db:self.assertEqual(list(db.iterdump()),before)

    def test_ceo_reports_and_no_edit_controls(self):
        self.login('ceo')
        for path in ('/','/workers','/daily-records','/taxes','/banking','/days/2026-11-10/attendance','/days/2026-11-10/close'):
            response=self.client.get(path)
            self.assertEqual(response.status_code,200,path)
            text=response.get_data(as_text=True)
            self.assertIn('Read only',text)
            self.assertNotIn('data-review=',text)
        bank=self.client.get('/banking').get_data(as_text=True)
        self.assertIn('Main account',bank)
        self.assertIn('Statement transactions',bank)
        self.assertNotIn('Add bank account',bank)
        response=self.client.get('/days/2026-11-10/sales')
        self.assertTrue(response.location.endswith('/receipts'))

    def test_sales_manager_can_open_date(self):
        self.login()
        self.assertEqual(self.submit('/days',business_date='2026-11-12').status_code,303)
        with connect(self.path) as db:self.assertIsNotNone(db.execute("SELECT 1 FROM business_days WHERE business_date='2026-11-12'").fetchone())

    def test_bad_credentials_throttle_and_external_redirect(self):
        self.assertEqual(self.login(password='wrong').status_code,401)
        for _ in range(4):self.login(password='wrong')
        self.assertEqual(self.login().status_code,429)
        other=self.app.test_client()
        other.get('/login')
        with other.session_transaction() as session: token=session['csrf_token']
        result=other.post('/login',data={'csrf':token,'username':'ceo','password':'demo','next':'//evil.example'},environ_overrides={'REMOTE_ADDR':'127.0.0.2'})
        self.assertEqual(result.location,'/')


if __name__=='__main__':unittest.main()
