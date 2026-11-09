ALTER TABLE bank_matches ADD COLUMN reversed_at TEXT;
ALTER TABLE bank_matches ADD COLUMN reversal_reason TEXT NOT NULL DEFAULT '';
ALTER TABLE sale_bank_accounts ADD COLUMN source TEXT NOT NULL DEFAULT 'posting';
CREATE TABLE bank_allocation_events (
 id INTEGER PRIMARY KEY,match_id INTEGER NOT NULL REFERENCES bank_matches,
 action TEXT NOT NULL CHECK(action IN ('allocate','reverse')),amount INTEGER NOT NULL,
 reason TEXT NOT NULL,recorded_at TEXT NOT NULL
);
INSERT INTO bank_allocation_events(match_id,action,amount,reason,recorded_at)
 SELECT id,'allocate',amount,'Initial allocation',matched_at FROM bank_matches;
