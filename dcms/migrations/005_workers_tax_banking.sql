ALTER TABLE workers ADD COLUMN started_on TEXT NOT NULL DEFAULT '0001-01-01';
ALTER TABLE workers ADD COLUMN ended_on TEXT;
UPDATE workers SET started_on = COALESCE((SELECT MIN(business_date) FROM attendance WHERE worker_id=workers.id),(SELECT MIN(business_date) FROM business_days),'0001-01-01');
CREATE TABLE worker_rates (
 worker_id INTEGER NOT NULL REFERENCES workers,
 effective_from TEXT NOT NULL,
 daily_rate INTEGER NOT NULL CHECK(daily_rate>0),
 PRIMARY KEY(worker_id,effective_from)
);
INSERT INTO worker_rates SELECT id,started_on,daily_rate FROM workers;
CREATE TABLE attendance_changes (
 id INTEGER PRIMARY KEY, worker_id INTEGER NOT NULL REFERENCES workers,
 business_date TEXT NOT NULL REFERENCES business_days, previous_status TEXT,
 new_status TEXT NOT NULL, reason TEXT NOT NULL, changed_at TEXT NOT NULL
);
CREATE TABLE vat_rates (effective_from TEXT PRIMARY KEY, basis_points INTEGER NOT NULL CHECK(basis_points BETWEEN 0 AND 10000));
INSERT INTO vat_rates SELECT '0001-01-01',value FROM settings WHERE key='vat_basis_points';
CREATE TABLE bank_accounts (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, bank_name TEXT NOT NULL,
 account_suffix TEXT NOT NULL, currency TEXT NOT NULL DEFAULT 'UGX' CHECK(currency='UGX')
);
CREATE TABLE sale_bank_accounts (sale_id INTEGER PRIMARY KEY REFERENCES sales,account_id INTEGER NOT NULL REFERENCES bank_accounts);
CREATE TABLE bank_transactions (
 id INTEGER PRIMARY KEY,account_id INTEGER NOT NULL REFERENCES bank_accounts,
 external_id TEXT NOT NULL, value_date TEXT NOT NULL, reference TEXT NOT NULL,
 description TEXT NOT NULL, credit INTEGER NOT NULL CHECK(credit>=0),debit INTEGER NOT NULL CHECK(debit>=0),
 imported_at TEXT NOT NULL, CHECK((credit>0 AND debit=0) OR (debit>0 AND credit=0)), UNIQUE(account_id,external_id)
);
CREATE TABLE bank_matches (
 id INTEGER PRIMARY KEY,transaction_id INTEGER NOT NULL REFERENCES bank_transactions,
 sale_id INTEGER NOT NULL REFERENCES sales,amount INTEGER NOT NULL CHECK(amount>0),matched_at TEXT NOT NULL,
 UNIQUE(transaction_id,sale_id)
);
