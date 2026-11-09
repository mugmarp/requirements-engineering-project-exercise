CREATE TABLE workers (
    id INTEGER PRIMARY KEY,
    worker_code TEXT NOT NULL UNIQUE CHECK (length(trim(worker_code)) > 0),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    daily_rate INTEGER NOT NULL CHECK (daily_rate > 0)
);
CREATE TABLE attendance (
    business_date TEXT NOT NULL REFERENCES business_days,
    worker_id INTEGER NOT NULL REFERENCES workers,
    status TEXT NOT NULL CHECK (status IN ('present', 'absent')),
    daily_rate INTEGER NOT NULL CHECK (daily_rate > 0),
    recorded_at TEXT NOT NULL,
    PRIMARY KEY (business_date, worker_id)
);
ALTER TABLE daily_closes ADD COLUMN workers_present INTEGER;
ALTER TABLE daily_closes ADD COLUMN payroll_eligible INTEGER;
