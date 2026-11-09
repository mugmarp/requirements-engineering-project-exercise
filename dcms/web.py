"""Flask adapter for the DCMS prototype."""

import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, date
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, Response, abort, g, redirect, render_template, request, session, url_for, flash

from . import services
from .analytics import overview
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
        MAX_CONTENT_LENGTH=262_144,
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
        today = datetime.now(KAMPALA).date().isoformat()
        if selected_day:
            session['business_date'] = selected_day
        nav_day = selected_day or session.get('business_date') or today
        day_status = None
        if nav_day:
            row = db().execute(
                "SELECT status FROM business_days WHERE business_date = ?", (nav_day,),
            ).fetchone()
            if row:
                day_status = row["status"]
        navigation_url = ''
        if request.method == 'POST':
            if request.endpoint in ('create_worker',):
                navigation_url=url_for('attendance',day=selected_day)
            elif request.endpoint in ('opening_cash','expense','finalize_close'):
                navigation_url=url_for('reconciliation',day=selected_day)
            elif request.endpoint in ('bank_import','bank_match','bank_account_create','bank_reverse'):
                navigation_url=url_for('bank_home',account_id=request.form.get('account_id') or None)
        return {
            "navigation_url": navigation_url,
            "csrf_token": session["csrf_token"], "channels": services.CHANNELS,
            "day_status": day_status, "nav_day": nav_day if day_status else None,
            "today": today, "is_sample": bool(db().execute("SELECT 1 FROM demo_metadata LIMIT 1").fetchone()),

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

    @app.errorhandler(400)
    @app.errorhandler(404)
    def request_error(error):
        return render_template('error.html', message=error.description), error.code

    @app.errorhandler(services.DomainError)
    def domain_error(error):
        return render_template("error.html", message=str(error)), error.status

    @app.errorhandler(sqlite3.OperationalError)
    def database_error(error):
        if getattr(error, "sqlite_errorcode", None) in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
            return render_template("error.html", message="The database is busy. Retry in a moment."), 503
        app.logger.exception("Database error")
        return render_template("error.html", message="Could not access the DCMS database."), 500

    WORKFLOWS = {"sales": "sales", "attendance": "attendance", "close": "reconciliation", "receipts": "receipt_history"}

    @app.get("/")
    def home():
        today = datetime.now(KAMPALA).date()
        period = request.args.get('period', '30')
        first = db().execute('SELECT MIN(business_date) FROM (SELECT business_date FROM business_days UNION ALL SELECT business_date FROM non_operating_days)').fetchone()[0]
        if period == 'custom':
            start, end = request.args.get('start', ''), request.args.get('end', '')
        elif period == 'history':
            start, end = first or today.isoformat(), today.isoformat()
        elif period in ('today', '7', '30'):
            length = 1 if period == 'today' else int(period)
            start, end = (today-timedelta(days=length-1)).isoformat(), today.isoformat()
        else:
            raise services.DomainError('Choose a valid reporting period.')
        services.business_date(start)
        services.business_date(end)
        if start > end or (date.fromisoformat(end)-date.fromisoformat(start)).days > 3660:
            raise services.DomainError('Choose a reporting period of up to ten years with the start before the end.')
        data = overview(db(), start, end, today.isoformat())
        return render_template('dashboard.html', active='dashboard', data=data, start=start,
                               end=end, period=period)

    @app.get('/daily-records')
    def daily_records():
        days = db().execute("SELECT * FROM business_days ORDER BY business_date DESC").fetchall()
        non_operating = db().execute('SELECT * FROM non_operating_days ORDER BY business_date DESC').fetchall()
        target = request.args.get('next', 'close')
        if target not in WORKFLOWS:
            target = 'close'
        return render_template('home.html', active='records', days=days,
                               non_operating=non_operating, target=target)

    @app.get('/work/<workflow>')
    def start_workflow(workflow):
        if workflow not in WORKFLOWS:
            abort(404)
        selected = request.args.get('day') or datetime.now(KAMPALA).date().isoformat()
        row = db().execute('SELECT status FROM business_days WHERE business_date=?', (selected,)).fetchone()
        if row:
            endpoint = 'receipt_history' if workflow == 'sales' and row['status'] == 'closed' else WORKFLOWS[workflow]
            return redirect(url_for(endpoint, day=selected))
        return redirect(url_for('daily_records', next=workflow))

    @app.post("/days")
    def create_day():
        day = request.form.get("business_date", "")
        services.open_day(db(), day)
        target = WORKFLOWS.get(request.form.get('next', 'close'), 'reconciliation')
        if target == 'sales' and services.find_day(db(), day)['status'] == 'closed':
            target = 'receipt_history'
        return redirect(url_for(target, day=day), code=303)

    def sale_form(day, *, error=None, status=200, posted=None, lines=None):
        row = services.find_day(db(), day)
        if row["status"] == "closed":
            if error:
                return domain_error(error)
            return redirect(url_for("reconciliation", day=day))
        products = db().execute("SELECT * FROM products WHERE active = 1 ORDER BY id").fetchall()
        return render_template(
            "sales.html", active="sales", day=day, products=products, rate=services.vat_rate(db(), day),
            bank_accounts=db().execute("SELECT * FROM bank_accounts ORDER BY name").fetchall(),
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
                request_key=posted.get("request_key", ""), lines=lines, bank_account_id=posted.get("bank_account_id") or None,
            )
        except services.DomainError as error:
            return sale_form(day, error=error, status=error.status, posted=posted, lines=lines)
        return redirect(url_for("receipt_page", sale_id=sale_id), code=303)

    @app.get("/receipts/<int:sale_id>")
    def receipt_page(sale_id):
        sale, lines = services.receipt(db(), sale_id)
        bank_account = db().execute('SELECT b.* FROM bank_accounts b JOIN sale_bank_accounts a ON a.account_id=b.id WHERE a.sale_id=?',(sale_id,)).fetchone()
        return render_template("receipt.html", active="history", day=sale["business_date"], sale=sale, lines=lines, bank_account=bank_account)

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
        return attendance_page(day)

    def attendance_page(day, *, worker_entry=None, worker_error=None):
        error = worker_error
        status = error.status if error else 200
        if request.method == "POST" and worker_entry is None:
            try:
                services.mark_attendance(
                    db(), day, request.form.get("worker_id", ""), request.form.get("status", ""),
                    expected_status=request.form.get("expected_status", ""), reason=request.form.get("reason", ""),
                )
            except services.DomainError as problem:
                error, status = problem, problem.status
            else:
                flash("Attendance saved.", "success")
                return redirect(url_for("attendance", day=day), code=303)
        row = services.find_day(db(), day)
        workers, count, total = services.attendance_summary(db(), day)
        return render_template(
            "attendance.html", active="attendance", day=day, row=row, workers=workers,
            count=count, total=total, error=error, worker_entry=worker_entry or {},
        ), status

    @app.post("/days/<day>/workers")
    def create_worker(day):
        try:
            services.add_worker(
                db(), request.form.get("code", ""), request.form.get("name", ""),
                request.form.get("daily_rate", ""), day=day,
            )
        except services.DomainError as error:
            return attendance_page(day, worker_entry=request.form, worker_error=error)
        flash("Worker saved. Mark attendance separately.", "success")
        return redirect(url_for("attendance", day=day), code=303)

    def close_form(day, *, error=None, status=200, posted=None, expense_entry=None, opening_entry=None):
        row, activity = services.preview_close(db(), day)
        if row["status"] == "closed":
            return render_template(
                "close.html", active="close", day=day, saved=services.close_snapshot(db(), day),
                error=error,
            ), status
        return render_template(
            "close.html", active="close", day=day, saved=None, row=row, activity=activity,
            posted=posted or {}, error=error, expense_entry=expense_entry or {}, opening_entry=opening_entry or {},
            expense_key=(expense_entry or {}).get("request_key") or secrets.token_hex(16),
            unmarked=sum(1 for w in services.attendance_summary(db(),day)[0] if w["status"] is None),
        ), status

    @app.get("/days/<day>/close")
    def reconciliation(day):
        return close_form(day)

    @app.post("/days/<day>/opening-cash")
    def opening_cash(day):
        try:
            services.set_opening_cash(db(), day, request.form.get("amount", ""))
        except services.DomainError as error:
            return close_form(day, error=error, status=error.status, opening_entry=request.form)
        flash("Opening cash saved.", "success")
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
        flash("Cash expense recorded.", "success")
        return redirect(url_for("reconciliation", day=day), code=303)

    @app.post("/days/<day>/close")
    def finalize_close(day):
        try:
            services.close_day(
                db(), day, actual_cash=request.form.get("actual_cash", ""),
                explanation=request.form.get("explanation", ""), revision=request.form.get("revision", ""),
                expected_unmarked=request.form.get("unmarked_reviewed", "0"),
            )
        except services.DomainError as error:
            return close_form(day, error=error, status=error.status, posted=request.form)
        return redirect(url_for("reconciliation", day=day), code=303)

    from .modules import register
    register(app, db)
    return app
