-- Explicit non-operating dates distinguish planned closures from missing records.
CREATE TABLE non_operating_days (
    business_date TEXT PRIMARY KEY,
    reason TEXT NOT NULL
);
-- Demo provenance and opening stock assumptions are kept with the dataset.
CREATE TABLE demo_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
