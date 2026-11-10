"""Session authentication and roles for hosted DCMS accounts."""
import json
import os
import secrets
from datetime import timedelta
from pathlib import Path
from time import monotonic
from threading import Lock
from flask import abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def configure(app, users=None):
    path = os.environ.get('DCMS_USERS_FILE')
    if users is None and path:
        users = json.loads(Path(path).read_text())
        if not isinstance(users, dict) or not users:
            raise ValueError('The accounts file must contain at least one account.')
    users = users or {}
    for account in users.values():
        if account.get('role') not in ('sales_manager', 'ceo') or not account.get('password_hash'):
            raise ValueError('Each account needs a valid role and password hash.')
    app.config['DCMS_USERS'] = users
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    attempts = {}
    lock = Lock()
    dummy = generate_password_hash(secrets.token_hex(16), method='pbkdf2:sha256:600000') if users else ''

    @app.before_request
    def account_access():
        g.account = users.get(session.get('username')) if users else None
        if not users or request.endpoint in ('login', 'static'):
            return
        if not g.account:
            if request.method != 'GET':
                abort(401, 'Sign in before submitting this form.')
            return redirect(url_for('login', next=request.full_path.rstrip('?')))
        if g.account['role'] == 'ceo':
            if request.method not in ('GET', 'HEAD', 'OPTIONS') and request.endpoint != 'logout':
                abort(403, 'The CEO account has read-only access. Sign in as Sales Manager to record changes.')
            if request.endpoint == 'sales':
                return redirect(url_for('receipt_history', day=request.view_args['day']))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if not users:
            return redirect(url_for('home'))
        target = request.values.get('next', '/')
        if not target.startswith('/') or target.startswith('//') or '\\' in target or any(ord(c) < 32 for c in target):
            target = '/'
        error = None
        status = 200
        if request.method == 'POST':
            username = request.form.get('username', '').strip().lower()
            account = users.get(username)
            key = request.remote_addr or 'unknown'
            now = monotonic()
            with lock:
                recent = [t for t in attempts.get(key, []) if now-t < 60]
                limited = len(recent) >= 5
                if not limited:
                    if len(attempts) >= 1024 and key not in attempts:
                        attempts.clear()
                    attempts[key] = recent + [now]
            if limited:
                error, status = 'Too many attempts. Wait one minute and try again.', 429
            elif check_password_hash(account['password_hash'] if account else dummy, request.form.get('password', '')) and account:
                with lock:
                    attempts.pop(key, None)
                session.clear()
                session['username'] = username
                session['csrf_token'] = secrets.token_urlsafe(32)
                session.permanent = True
                return redirect(target, code=303)
            else:
                error, status = 'The username or password is incorrect.', 401
        return render_template('login.html', error=error, target=target), status

    @app.post('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'), code=303)

    @app.context_processor
    def account_context():
        account = getattr(g, 'account', None)
        return {'auth_enabled': bool(users), 'account': account,
                'can_manage': not users or bool(account and account['role'] == 'sales_manager')}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create the two requested sample accounts without overwriting existing accounts.')
    parser.add_argument('--sample', action='store_true', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    users = {name: {'name': label, 'role': name,
        'password_hash': generate_password_hash('demo', method='pbkdf2:sha256:600000')}
        for name, label in [('sales_manager', 'Sales Manager'), ('ceo', 'CEO')]}
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as file:
        json.dump(users, file)
    print('Created Sales Manager and CEO sample accounts.')
