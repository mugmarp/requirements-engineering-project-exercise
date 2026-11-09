"""SQLite connection, schema initialization and write transactions."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

MIGRATIONS = Path(__file__).with_name("migrations")


@contextmanager
def connect(path):
    db = sqlite3.connect(path, timeout=3, isolation_level=None)
    try:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        yield db
    finally:
        db.close()


@contextmanager
def write(db):
    db.execute("BEGIN IMMEDIATE")
    try:
        yield
        db.commit()
    except BaseException:
        db.rollback()
        raise


def initialize(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    migrations = sorted(MIGRATIONS.glob("*.sql"))
    with connect(path) as db:
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version > len(migrations):
            raise ValueError("This database requires a newer version of DCMS.")
        for number, migration in enumerate(migrations, 1):
            if number > version:
                db.executescript(
                    "BEGIN IMMEDIATE;\n"
                    + migration.read_text(encoding="utf-8")
                    + f"\nPRAGMA user_version = {number};\nCOMMIT;"
                )
