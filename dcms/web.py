"""Flask adapter for the DCMS prototype."""

import hmac
import os
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, Response, abort, g, redirect, render_template, request, session, url_for

from . import services
from .db import connect

DEFAULT_DB = Path(__file__).resolve().parents[1] / "instance" / "dcms.sqlite3"
KAMPALA = ZoneInfo("Africa/Kampala")


def create_app(database=DEFAULT_DB, *, password=None, secure=False):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("DCMS_SECRET_KEY") or secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=secure,
        MAX_CONTENT_LENGTH=32_768,
    )

    def db():
        if "db" not in g:
            g.connection = connect(database)
            g.db = g.connection.__enter__()
        return g.db

    @app.teardown_appcontext
    def close_connection(_error):
        if "connection" in g:
            g.connection.__exit__(None, None, None)

    @app.before_request
    def protect():
        if password:
            credentials = request.authorization
            if (
                not credentials or credentials.type != "basic" or credentials.username != "demo"
                or not hmac.compare_digest((credentials.password or "").encode(), password.encode())
            ):
                return Response("Sign in to open the DCMS demo.", 401, {
                    "WWW-Authenticate": 'Basic realm="DCMS demo"',
                })
        if request.method == "POST":
            expected = session.get("csrf_token")
            submitted = request.form.get("csrf", "")
            if not expected or not hmac.compare_digest(expected.encode(), submitted.encode()):
                abort(400, "The form expired. Reload the page and try again.")

    @app.after_request
    def headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        return response

    @app.context_processor
    def context():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        selected_day = (request.view_args or {}).get("day")
        sale_id = (request.view_args or {}).get("sale_id")
        if sale_id:
            sale = db().execute("SELECT business_date FROM sales WHERE id = ?", (sale_id,)).fetchone()
            if sale:
                selected_day = sale["business_date"]
        day_status = None
        if selected_day:
            row = db().execute(
                "SELECT status FROM business_days WHERE business_date = ?", (selected_day,),
            ).fetchone()
            if row:
                day_status = row["status"]
        return {
            "csrf_token": session["csrf_token"], "channels": services.CHANNELS,
            "day_status": day_status,
        }

    @app.template_filter("money")
    def money(amount):
        sign = "−" if amount < 0 else ""
        whole, minor = divmod(abs(amount), 100)
        return f"{sign}{whole:,}" if minor == 0 else f"{sign}{whole:,}.{minor:02d}"

    @app.template_filter("amount")
    def amount_field(amount):
        whole, minor = divmod(amount, 100)
        return f"{whole}.{minor:02d}" if minor else str(whole)

    @app.template_filter("local_time")
    def local_time(value):
        return datetime.fromisoformat(value).astimezone(KAMPALA).strftime("%d %b %Y, %H:%M EAT")

    @app.errorhandler(services.DomainError)
    def domain_error(error):
        return render_template("error.html", message=str(error)), error.status

    @app.errorhandler(sqlite3.OperationalError)
    def database_error(error):
        if getattr(error, "sqlite_errorcode", None) in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
            return render_template("error.html", message="The database is busy. Retry in a moment."), 503
        app.logger.exception("Database error")
        return render_template("error.html", message="Could not access the DCMS database."), 500

    @app.get("/")
    def home():
        days = db().execute("SELECT * FROM business_days ORDER BY business_date DESC").fetchall()
        return render_template("home.html", days=days, today=datetime.now(KAMPALA).date().isoformat())

    @app.post("/days")
    def create_day():
        day = request.form.get("business_date", "")
        services.open_day(db(), day)
        return redirect(url_for("reconciliation", day=day), code=303)

    def sale_form(day, *, error=None, status=200, posted=None, lines=None):
        row = services.find_day(db(), day)
        if row["status"] == "closed":
            if error:
                return domain_error(error)
            return redirect(url_for("reconciliation", day=day))
        products = db().execute("SELECT * FROM products WHERE active = 1 ORDER BY id").fetchall()
        return render_template(
            "sales.html", active="sales", day=day, products=products, rate=services.vat_rate(db()),
            posted=posted or {}, lines=lines or [("", "1")], error=error,
            request_key=(posted or {}).get("request_key") or secrets.token_hex(16),
        ), status

    @app.route("/days/<day>/sales", methods=["GET", "POST"])
    def sales(day):
        if request.method == "GET":
            return sale_form(day)
        posted = request.form
        lines = list(zip(posted.getlist("product"), posted.getlist("quantity")))
        try:
            if len(lines) != len(posted.getlist("product")) or len(lines) != len(posted.getlist("quantity")):
                raise services.DomainError("Each product needs a quantity.")
            sale_id = services.post_sale(
                db(), day, customer=posted.get("customer", ""), channel=posted.get("channel", ""),
                reference=posted.get("reference", ""), received=posted.get("received", ""),
                request_key=posted.get("request_key", ""), lines=lines,
            )
        except services.DomainError as error:
            return sale_form(day, error=error, status=error.status, posted=posted, lines=lines)
        return redirect(url_for("receipt_page", sale_id=sale_id), code=303)

    @app.get("/receipts/<int:sale_id>")
    def receipt_page(sale_id):
        sale, lines = services.receipt(db(), sale_id)
        return render_template("receipt.html", active="sales", day=sale["business_date"], sale=sale, lines=lines)

    @app.get("/days/<day>/receipts")
    def receipt_history(day):
        services.find_day(db(), day)
        sales = db().execute(
            "SELECT id, customer, channel, total FROM sales WHERE business_date = ? ORDER BY id DESC",
            (day,),
        ).fetchall()
        return render_template("history.html", active="history", day=day, sales=sales)

    @app.route("/days/<day>/attendance", methods=["GET", "POST"])
    def attendance(day):
        error = None
        status = 200
        if request.method == "POST":
            try:
                services.mark_attendance(
                    db(), day, request.form.get("worker_id", ""), request.form.get("status", ""),
                )
            except services.DomainError as problem:
                error, status = problem, problem.status
            else:
                return redirect(url_for("attendance", day=day), code=303)
        row = services.find_day(db(), day)
        workers, count, total = services.attendance_summary(db(), day)
        return render_template(
            "attendance.html", active="attendance", day=day, row=row, workers=workers,
            count=count, total=total, error=error,
        ), status

    @app.post("/days/<day>/workers")
    def create_worker(day):
        services.find_day(db(), day)
        services.add_worker(
            db(), request.form.get("code", ""), request.form.get("name", ""),
            request.form.get("daily_rate", ""),
        )
        return redirect(url_for("attendance", day=day), code=303)

    def close_form(day, *, error=None, status=200, posted=None, expense_entry=None):
        row, activity = services.preview_close(db(), day)
        if row["status"] == "closed":
            return render_template(
                "close.html", active="close", day=day, saved=services.close_snapshot(db(), day),
                error=error,
            ), status
        return render_template(
            "close.html", active="close", day=day, saved=None, row=row, activity=activity,
            posted=posted or {}, error=error, expense_entry=expense_entry or {},
            expense_key=(expense_entry or {}).get("request_key") or secrets.token_hex(16),
        ), status

    @app.get("/days/<day>/close")
    def reconciliation(day):
        return close_form(day)

    @app.post("/days/<day>/opening-cash")
    def opening_cash(day):
        try:
            services.set_opening_cash(db(), day, request.form.get("amount", ""))
        except services.DomainError as error:
            return close_form(day, error=error, status=error.status)
        return redirect(url_for("reconciliation", day=day), code=303)

    @app.post("/days/<day>/expenses")
    def expense(day):
        try:
            services.record_expense(
                db(), day, request.form.get("description", ""), request.form.get("amount", ""),
                request.form.get("request_key", ""),
            )
        except services.DomainError as error:
            return close_form(day, error=error, status=error.status, expense_entry=request.form)
        return redirect(url_for("reconciliation", day=day), code=303)

    @app.post("/days/<day>/close")
    def finalize_close(day):
        try:
            services.close_day(
                db(), day, actual_cash=request.form.get("actual_cash", ""),
                explanation=request.form.get("explanation", ""), revision=request.form.get("revision", ""),
            )
        except services.DomainError as error:
            return close_form(day, error=error, status=error.status, posted=request.form)
        return redirect(url_for("reconciliation", day=day), code=303)

    return app
