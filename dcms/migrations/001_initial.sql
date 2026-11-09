CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value INTEGER NOT NULL CHECK (value BETWEEN 0 AND 10000)
);
INSERT INTO settings VALUES ('vat_basis_points', 1800);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    unit TEXT NOT NULL,
    unit_price INTEGER NOT NULL CHECK (unit_price > 0),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);

CREATE TABLE business_days (
    business_date TEXT PRIMARY KEY,
    opening_cash INTEGER NOT NULL DEFAULT 0 CHECK (opening_cash >= 0),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    revision INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    business_date TEXT NOT NULL REFERENCES business_days,
    posted_at TEXT NOT NULL,
    customer TEXT NOT NULL CHECK (length(trim(customer)) > 0),
    channel TEXT NOT NULL CHECK (channel IN ('cash', 'mobile_money', 'bank_deposit')),
    payment_reference TEXT NOT NULL DEFAULT '',
    subtotal INTEGER NOT NULL CHECK (subtotal > 0),
    vat_rate INTEGER NOT NULL CHECK (vat_rate BETWEEN 0 AND 10000),
    vat INTEGER NOT NULL CHECK (vat >= 0),
    total INTEGER NOT NULL CHECK (total = subtotal + vat),
    received INTEGER NOT NULL CHECK (received = total),
    request_key TEXT NOT NULL UNIQUE,
    request_hash TEXT NOT NULL
);
CREATE INDEX sales_business_date ON sales (business_date, channel);

CREATE TABLE sale_lines (
    sale_id INTEGER NOT NULL REFERENCES sales,
    product_id INTEGER NOT NULL REFERENCES products,
    description TEXT NOT NULL,
    unit TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price INTEGER NOT NULL CHECK (unit_price > 0),
    line_total INTEGER NOT NULL CHECK (line_total = quantity * unit_price),
    PRIMARY KEY (sale_id, product_id)
);

CREATE TABLE expenses (
    id INTEGER PRIMARY KEY,
    business_date TEXT NOT NULL REFERENCES business_days,
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    amount INTEGER NOT NULL CHECK (amount > 0),
    recorded_at TEXT NOT NULL
);
CREATE INDEX expenses_business_date ON expenses (business_date);

CREATE TABLE daily_closes (
    business_date TEXT PRIMARY KEY REFERENCES business_days,
    opening_cash INTEGER NOT NULL CHECK (opening_cash >= 0),
    cash_activity INTEGER NOT NULL CHECK (cash_activity >= 0),
    mobile_money_activity INTEGER NOT NULL CHECK (mobile_money_activity >= 0),
    bank_activity INTEGER NOT NULL CHECK (bank_activity >= 0),
    expenses INTEGER NOT NULL CHECK (expenses >= 0),
    expected_cash INTEGER NOT NULL CHECK (expected_cash = opening_cash + cash_activity - expenses),
    actual_cash INTEGER NOT NULL CHECK (actual_cash >= 0),
    variance INTEGER NOT NULL CHECK (variance = actual_cash - expected_cash),
    explanation TEXT NOT NULL CHECK (variance = 0 OR length(trim(explanation)) > 0),
    closed_at TEXT NOT NULL
);
