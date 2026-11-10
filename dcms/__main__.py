"""Initialize and launch the web prototype."""

import argparse
import os
import tempfile
from pathlib import Path

from .db import connect, initialize
from .demo import seed, seed_history
from .services import money_value, set_vat_rate
from .web import DEFAULT_DB, KAMPALA, create_app
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(prog="python -m dcms")
    parser.add_argument("--database", type=Path, default=Path(os.environ.get("DCMS_DB_PATH", DEFAULT_DB)))
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Initialize or migrate the database.")
    init.add_argument("--demo", action="store_true", help="Create a fresh database with sample records.")
    init.add_argument("--history", action="store_true", help="Seed five months of synthetic activity into a fresh database.")
    init.add_argument("--end-date", default=datetime.now(KAMPALA).date().isoformat(), help="Historical demo end date (YYYY-MM-DD).")
    vat = commands.add_parser("set-vat", help="Set the demo VAT percentage.")
    vat.add_argument("percent")
    vat.add_argument("--effective-from", help="Effective date after existing sales (YYYY-MM-DD).")
    server = commands.add_parser("serve", help="Run the web application with Waitress.")
    server.add_argument("--host", default="127.0.0.1")
    server.add_argument("--port", type=int, default=8080)
    server.add_argument("--secure-cookies", action="store_true", help="Require HTTPS for session cookies.")
    args = parser.parse_args()

    try:
        if args.command == "init":
            if args.demo or args.history:
                args.database.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryDirectory(dir=args.database.parent) as stage:
                    path = Path(stage) / "sample.sqlite3"
                    initialize(path)
                    with connect(path) as db:
                        if args.history:
                            seed_history(db, args.end_date)
                        else:
                            seed(db)
                    try:
                        # A completed seed is linked into place only if the target is new.
                        os.link(path, args.database)
                    except FileExistsError:
                        parser.error("Demo seed needs a new database path. Existing data was preserved.")
            else:
                initialize(args.database)
            print(f"Database ready at {args.database.resolve()}")
        elif args.command == "set-vat":
            initialize(args.database)
            with connect(args.database) as db:
                set_vat_rate(db, money_value(args.percent, "the VAT percentage"), args.effective_from)
        else:
            from waitress import serve

            password = os.environ.get("DCMS_DEMO_PASSWORD")
            if args.host not in ("127.0.0.1", "::1", "localhost") and not password and not os.environ.get("DCMS_USERS_FILE"):
                parser.error("Set DCMS_USERS_FILE or DCMS_DEMO_PASSWORD to expose the app beyond loopback.")
            initialize(args.database)
            serve(
                create_app(args.database, password=password, secure=args.secure_cookies),
                host=args.host, port=args.port,
            )
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
