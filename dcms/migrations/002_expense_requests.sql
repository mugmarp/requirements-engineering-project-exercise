ALTER TABLE expenses ADD COLUMN request_key TEXT;
CREATE UNIQUE INDEX expense_request_key ON expenses (request_key);
