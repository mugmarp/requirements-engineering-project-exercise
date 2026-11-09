"""Statement imports and allocations. Matching never creates revenue or edits closes."""
import csv
import io
import json
from . import services as s
from .db import write


def account(db, account_id):
    account_id=s.integer_value(str(account_id),'bank account')
    row=db.execute('SELECT * FROM bank_accounts WHERE id=?',(account_id,)).fetchone()
    if row is None: raise s.Missing('Bank account not found.')
    return row


def add_account(db,name,bank,suffix):
    name=s.text_value(name,'an account label',80)
    bank=s.text_value(bank,'a bank name',80)
    suffix=s.text_value(suffix,'the last four account digits',4)
    if not suffix.isascii() or not suffix.isdigit() or len(suffix)!=4:
        raise s.DomainError('Enter exactly the last four account digits. Do not enter banking passwords.')
    with write(db):
        existing=db.execute('SELECT * FROM bank_accounts WHERE name=?',(name,)).fetchone()
        if existing:
            if (existing['bank_name'],existing['account_suffix'])!=(bank,suffix):
                raise s.Conflict('That account label already exists with different details.')
            return existing['id']
        return db.execute('INSERT INTO bank_accounts(name,bank_name,account_suffix) VALUES (?,?,?)',(name,bank,suffix)).lastrowid


def parse_statement(raw):
    if len(raw)>180000: raise s.DomainError('Import at most 180 KB of CSV at a time.')
    reader=csv.DictReader(io.StringIO(raw.lstrip('\ufeff')))
    if reader.fieldnames!=['id','date','reference','description','credit','debit']:
        raise s.DomainError('CSV columns must be: id,date,reference,description,credit,debit')
    result=[]; ids=set()
    for index,row in enumerate(reader,2):
        if len(result)>=500: raise s.DomainError('Import at most 500 statement rows at a time.')
        if None in row or any(value is None for value in row.values()):
            raise s.DomainError(f'Row {index}: incorrect number of CSV columns.')
        try:
            external=s.text_value(row['id'],'a unique statement transaction ID',100)
            day=s.business_date(row['date'].strip())
            reference=s.text_value(row['reference'],'a reference',100,required=False)
            description=s.text_value(row['description'],'a description',180)
            credit=s.money_value(row['credit'] or '0','credit')
            debit=s.money_value(row['debit'] or '0','debit')
            if (credit>0)==(debit>0): raise s.DomainError('Enter either a positive credit or a positive debit, not both.')
            if external in ids: raise s.DomainError('Transaction ID occurs twice in this import.')
        except s.DomainError as error:
            raise s.DomainError(f'Row {index}: {error}') from error
        ids.add(external); result.append((external,day,reference,description,credit,debit))
    if not result: raise s.DomainError('The statement has no data rows.')
    return result


def import_statement(db,account_id,raw):
    bank=account(db,account_id); rows=parse_statement(raw); added=0
    with write(db):
        for row in rows:
            existing=db.execute('SELECT external_id,value_date,reference,description,credit,debit FROM bank_transactions WHERE account_id=? AND external_id=?',(bank['id'],row[0])).fetchone()
            if existing:
                if tuple(existing)!=row: raise s.Conflict('A statement ID was previously imported with different values. No rows were imported.')
                continue
            db.execute('INSERT INTO bank_transactions(account_id,external_id,value_date,reference,description,credit,debit,imported_at) VALUES (?,?,?,?,?,?,?,?)',(bank['id'],*row,s.timestamp()))
            added+=1
    return added


def match(db,transaction_id,sale_id,amount, *, request_key=None):
    transaction_id=s.integer_value(str(transaction_id),'statement transaction')
    sale_id=s.integer_value(str(sale_id),'receipt')
    amount=s.money_value(amount,'allocation amount',positive=True)
    with write(db):
        if _retry(db,request_key,['allocate',transaction_id,sale_id,amount]): return
        tx=db.execute('SELECT * FROM bank_transactions WHERE id=?',(transaction_id,)).fetchone()
        sale=db.execute('SELECT * FROM sales WHERE id=?',(sale_id,)).fetchone()
        if tx is None or sale is None: raise s.Missing('Statement transaction or receipt not found.')
        if not tx['credit'] or sale['channel']!='bank_deposit':
            raise s.DomainError('Only statement credits can match Bank Deposit receipts. Debits and transfers are reviewed separately.')
        existing=db.execute('SELECT id,amount,reversed_at FROM bank_matches WHERE transaction_id=? AND sale_id=?',(transaction_id,sale_id)).fetchone()
        if existing and existing['reversed_at'] is None:
            if existing['amount']!=amount: raise s.Conflict('That allocation already exists with a different amount.')
            return
        assigned=db.execute('SELECT account_id FROM sale_bank_accounts WHERE sale_id=?',(sale_id,)).fetchone()
        if assigned and assigned['account_id']!=tx['account_id']: raise s.Conflict('Receipt belongs to a different bank account.')
        tx_used=db.execute('SELECT COALESCE(SUM(amount),0) FROM bank_matches WHERE transaction_id=? AND reversed_at IS NULL',(transaction_id,)).fetchone()[0]
        sale_used=db.execute('SELECT COALESCE(SUM(amount),0) FROM bank_matches WHERE sale_id=? AND reversed_at IS NULL',(sale_id,)).fetchone()[0]
        if amount>tx['credit']-tx_used or amount>sale['total']-sale_used:
            raise s.Conflict('Allocation exceeds the unmatched statement credit or receipt amount.')
        if assigned is None: db.execute("INSERT INTO sale_bank_accounts(sale_id,account_id,source) VALUES (?,?,'matching')",(sale_id,tx['account_id']))
        if existing:
            match_id=existing['id']
            db.execute("UPDATE bank_matches SET amount=?,matched_at=?,reversed_at=NULL,reversal_reason='',revision=revision+1 WHERE id=?",(amount,s.timestamp(),match_id))
        else:
            match_id=db.execute('INSERT INTO bank_matches(transaction_id,sale_id,amount,matched_at) VALUES (?,?,?,?)',(transaction_id,sale_id,amount,s.timestamp())).lastrowid
        db.execute("INSERT INTO bank_allocation_events(match_id,action,amount,reason,recorded_at) VALUES (?,'allocate',?,'Reviewed allocation',?)",(match_id,amount,s.timestamp()))


def summary(db,account_id):
    bank=account(db,account_id)
    rows=db.execute('''SELECT t.*,COALESCE((SELECT SUM(amount) FROM bank_matches m WHERE m.transaction_id=t.id AND m.reversed_at IS NULL),0) AS allocated
        FROM bank_transactions t WHERE account_id=? ORDER BY value_date DESC,id DESC''',(bank['id'],)).fetchall()
    receipts=db.execute('''SELECT s.id,s.business_date,s.customer,s.payment_reference,s.total,
        COALESCE((SELECT SUM(amount) FROM bank_matches m WHERE m.sale_id=s.id AND m.reversed_at IS NULL),0) AS allocated,
        b.account_id FROM sales s LEFT JOIN sale_bank_accounts b ON b.sale_id=s.id
        WHERE s.channel='bank_deposit' AND (b.account_id=? OR b.account_id IS NULL)
        ORDER BY s.business_date DESC,s.id DESC''',(bank['id'],)).fetchall()
    matches=db.execute('''SELECT m.*,s.business_date,t.external_id FROM bank_matches m JOIN sales s ON s.id=m.sale_id
        JOIN bank_transactions t ON t.id=m.transaction_id WHERE t.account_id=? ORDER BY m.id DESC''',(bank['id'],)).fetchall()
    return bank,rows,[r for r in receipts if r['allocated']<r['total']],matches


def reverse(db,match_id,reason, *, request_key=None, expected_revision=None):
    match_id=s.integer_value(str(match_id),'allocation')
    reason=s.text_value(reason,'a reason for reversing this allocation',250)
    with write(db):
        if _retry(db,request_key,['reverse',match_id,reason,expected_revision]): return
        row=db.execute('SELECT * FROM bank_matches WHERE id=?',(match_id,)).fetchone()
        if row is None: raise s.Missing('Allocation not found.')
        if row['reversed_at']: return
        if expected_revision is not None and str(expected_revision)!=str(row['revision']):
            raise s.Conflict('Allocation changed. Review its current state before reversing it.')
        db.execute('UPDATE bank_matches SET reversed_at=?,reversal_reason=?,revision=revision+1 WHERE id=?',(s.timestamp(),reason,match_id))
        db.execute("INSERT INTO bank_allocation_events(match_id,action,amount,reason,recorded_at) VALUES (?,'reverse',?,?,?)",(match_id,row['amount'],reason,s.timestamp()))
        if not db.execute('SELECT 1 FROM bank_matches WHERE sale_id=? AND reversed_at IS NULL',(row['sale_id'],)).fetchone():
            db.execute("DELETE FROM sale_bank_accounts WHERE sale_id=? AND source='matching'",(row['sale_id'],))


def _retry(db,key,payload):
    if key is None: return False
    key=s.text_value(key,'a bank operation request key',64)
    payload=json.dumps(payload)
    previous=db.execute('SELECT payload FROM bank_operation_requests WHERE request_key=?',(key,)).fetchone()
    if previous:
        if previous['payload']!=payload: raise s.Conflict('This bank request key was used for different details. Reload and review again.')
        return True
    db.execute('INSERT INTO bank_operation_requests VALUES (?,?)',(key,payload))
    return False
