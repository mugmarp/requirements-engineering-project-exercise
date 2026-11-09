"""Worker records, recorded sales VAT, and bank statement review screens."""
import calendar
import csv
import io
import secrets
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from flask import request, render_template, redirect, url_for, flash, Response
from . import services as s, banking


def register(app, db):
    def today(): return datetime.now(ZoneInfo('Africa/Kampala')).date().isoformat()

    def worker_list(error=None, entry=None):
        rows=db().execute('''SELECT w.*,(SELECT daily_rate FROM worker_rates r WHERE r.worker_id=w.id AND r.effective_from<=? ORDER BY effective_from DESC LIMIT 1) AS rate_today FROM workers w ORDER BY name''',(today(),)).fetchall()
        return render_template('workers.html',active='workers',workers=rows,error=error,entry=entry or {}), error.status if error else 200

    @app.route('/workers', methods=['GET','POST'])
    def workers():
        if request.method=='POST':
            try:
                s.add_worker(db(),request.form.get('code',''),request.form.get('name',''),request.form.get('daily_rate',''),start_date=request.form.get('started_on',''))
            except s.DomainError as error: return worker_list(error,request.form)
            flash('Worker registered. Attendance and payments are recorded separately.','success')
            return redirect(url_for('workers'),303)
        return worker_list()

    @app.route('/workers/<int:worker_id>',methods=['GET','POST'])
    def worker_profile(worker_id):
        worker=db().execute('SELECT * FROM workers WHERE id=?',(worker_id,)).fetchone()
        if worker is None: raise s.Missing('Worker not found.')
        error=None; entry={}
        if request.method=='POST':
            entry=request.form
            try:
                s.update_worker(db(),worker_id,effective_from=entry.get('effective_from',''),daily_rate=entry.get('daily_rate',''),ended_on=entry.get('ended_on',''))
            except s.DomainError as problem: error=problem
            else:
                flash('Worker dates and scheduled rate saved. Existing attendance amounts remain unchanged.','success')
                return redirect(url_for('worker_profile',worker_id=worker_id),303)
        rates=db().execute('SELECT * FROM worker_rates WHERE worker_id=? ORDER BY effective_from DESC',(worker_id,)).fetchall()
        changes=db().execute('SELECT * FROM attendance_changes WHERE worker_id=? ORDER BY id DESC LIMIT 100',(worker_id,)).fetchall()
        return render_template('worker.html',active='workers',worker=worker,rates=rates,changes=changes,error=error,entry=entry,tomorrow=(date.fromisoformat(today())+timedelta(days=1)).isoformat()), error.status if error else 200

    @app.get('/taxes')
    def taxes():
        month=request.args.get('month',today()[:7])
        start=s.business_date(month+'-01')
        parsed=date.fromisoformat(start)
        if parsed.year == 9999: raise s.DomainError('Choose a reporting year before 9999.')
        end=parsed.replace(day=calendar.monthrange(parsed.year,parsed.month)[1]).isoformat()
        due=date(parsed.year+1,1,15) if parsed.month==12 else date(parsed.year,parsed.month+1,15)
        rows=db().execute('SELECT * FROM sales WHERE business_date BETWEEN ? AND ? ORDER BY business_date,id',(start,end)).fetchall()
        totals={key:sum(r[key] for r in rows) for key in ('subtotal','vat','total')}
        groups={}
        for row in rows:
            group=groups.setdefault(row['vat_rate'],dict(count=0,subtotal=0,vat=0,total=0))
            group['count']+=1
            for key in ('subtotal','vat','total'): group[key]+=row[key]
        open_dates=db().execute("SELECT business_date FROM business_days WHERE business_date BETWEEN ? AND ? AND status='open'",(start,end)).fetchall()
        rates=db().execute('SELECT * FROM vat_rates ORDER BY effective_from DESC').fetchall()
        if request.args.get('export')=='csv':
            output=io.StringIO(); writer=csv.writer(output)
            sample=db().execute('SELECT 1 FROM demo_metadata LIMIT 1').fetchone()
            writer.writerow(['Sales VAT Summary',month,'Sample data' if sample else 'Recorded sales only','Not a VAT return or EFRIS invoice'])
            writer.writerow(['Receipt','Business date','Customer','Payment channel','Sales excl VAT (UGX)','VAT rate percent','Recorded VAT (UGX)','Total incl VAT (UGX)'])
            for row in rows:
                customer=row['customer']; customer=("'"+customer) if customer.startswith(('=','+','-','@','\t','\r')) else customer
                writer.writerow([f'{row["id"]:06}',row['business_date'],customer,row['channel'],f'{row["subtotal"]/100:.2f}',f'{row["vat_rate"]/100:g}',f'{row["vat"]/100:.2f}',f'{row["total"]/100:.2f}'])
            return Response(output.getvalue(),mimetype='text/csv',headers={'Content-Disposition':f'attachment; filename="sales-vat-{month}.csv"'})
        return render_template('taxes.html',active='taxes',month=month,rows=rows,totals=totals,groups=groups,due=due.isoformat(),open_dates=open_dates,rates=rates,incomplete=today()<=end)

    def bank_page(error=None, entry=None, preview=None, selected=None):
        accounts=db().execute('SELECT * FROM bank_accounts ORDER BY name').fetchall()
        selected=selected or request.values.get('account_id') or (accounts[0]['id'] if accounts else None)
        bank=rows=receipts=matches=None
        if selected: bank,rows,receipts,matches=banking.summary(db(),selected)
        return render_template('banking.html',active='banking',accounts=accounts,bank=bank,rows=rows or [],receipts=receipts or [],matches=matches or [],error=error,entry=entry or {},preview=preview,bank_key=secrets.token_hex(16)), error.status if error else 200

    @app.get('/banking')
    def bank_home(): return bank_page()

    @app.post('/banking/accounts')
    def bank_account_create():
        try: account_id=banking.add_account(db(),request.form.get('name',''),request.form.get('bank_name',''),request.form.get('suffix',''))
        except s.DomainError as error: return bank_page(error,request.form)
        flash('Bank account registered. No online connection was made.','success')
        return redirect(url_for('bank_home',account_id=account_id),303)

    @app.post('/banking/import')
    def bank_import():
        try:
            banking.account(db(),request.form.get('account_id',''))
            if request.form.get('confirm')!='yes':
                return bank_page(entry=request.form,preview=banking.parse_statement(request.form.get('csv','')))
            added=banking.import_statement(db(),request.form.get('account_id',''),request.form.get('csv',''))
        except s.DomainError as error: return bank_page(error,request.form)
        flash(f'{added} statement rows imported. Identical transaction IDs already imported were skipped.','success')
        return redirect(url_for('bank_home',account_id=request.form['account_id']),303)

    @app.post('/banking/match')
    def bank_match():
        try:
            banking.match(db(),request.form.get('transaction_id',''),request.form.get('sale_id',''),request.form.get('amount',''),request_key=request.form.get('request_key',''))
        except s.DomainError as error: return bank_page(error,request.form)
        flash('Allocation saved. Sales totals and saved day-close reports were not changed.','success')
        return redirect(url_for('bank_home',account_id=request.form.get('account_id')),303)

    @app.post('/banking/reverse')
    def bank_reverse():
        try: banking.reverse(db(),request.form.get('match_id',''),request.form.get('reason',''),request_key=request.form.get('request_key',''),expected_revision=request.form.get('revision',''))
        except s.DomainError as error: return bank_page(error,request.form)
        flash('Allocation reversed with its reason retained. Posted receipts and day-close reports are unchanged.','success')
        return redirect(url_for('bank_home',account_id=request.form.get('account_id')),303)
