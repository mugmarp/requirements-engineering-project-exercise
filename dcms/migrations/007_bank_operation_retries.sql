ALTER TABLE bank_matches ADD COLUMN revision INTEGER NOT NULL DEFAULT 0;
CREATE TABLE bank_operation_requests (
 request_key TEXT PRIMARY KEY, payload TEXT NOT NULL
);
