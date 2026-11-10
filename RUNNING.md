# Run DCMS locally

These commands run the current web application from the repository root on Linux or a compatible shell. The Windows standalone installer and Debian package are planned separately; they are not required for this local web preview. Hosting instructions are in [DEPLOYMENT.md](DEPLOYMENT.md).

## First setup

Install Python 3 with its `venv` support and Git. Clone the repository if it is not already present, then enter it:

```bash
git clone https://github.com/mugmarp/requirements-engineering-project-exercise.git
cd requirements-engineering-project-exercise
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m dcms --database instance/local.sqlite3 init --history
.venv/bin/python -m dcms --database instance/local.sqlite3 serve --host 127.0.0.1 --port 8081
```

Open <http://127.0.0.1:8081>. Keep the terminal open while using the application. Dependencies must be installed before a disconnected local preview; the browser and Python process then run on the same computer. This preview is separate from standalone desktop delivery.

`init --history` creates five months of synthetic activity ending on the current Kampala date. For the presentation fixture add `--end-date 2026-11-10` to the initialization command. That fixture includes the saved 9 November UGX 5,000 deficit report and leaves 10 November open. `init --demo` creates the older, small worked example instead. Both seed options require a new database path and refuse to replace an existing database.

For a new empty database use `init` without seed options. No database or credentials are stored in Git.

## Stop and start again

Press **Ctrl+C** in the serving terminal. Closing the browser alone does not stop the Python process. Stopping the process does not delete the database.

To resume, enter the same repository and use the same database path:

```bash
.venv/bin/python -m dcms --database instance/local.sqlite3 serve --host 127.0.0.1 --port 8081
```

Do not repeat seeding to resume. The `serve` command applies outstanding migrations and opens saved data. A relative database path is resolved from the working directory; using the wrong directory or filename can open a different database.

## Optional account login

An isolated loopback preview without authentication variables opens directly into the application. To review the actual login and role behaviour, create the two sample accounts once:

```bash
.venv/bin/python -m dcms.auth --sample --output instance/local-users.json
export DCMS_USERS_FILE="$PWD/instance/local-users.json"
.venv/bin/python -m dcms --database instance/local.sqlite3 serve --port 8081
```

Select **Sales Manager** or **CEO** and enter `demo`, as requested for the presentation. CEO is read-only. The account command refuses to overwrite an existing file. Repeat the `export` when opening another terminal, but reuse the account file.

Without a configured `DCMS_SECRET_KEY`, restarting the app generates a new session secret and requires users to sign in again. The hosted service supplies a stable secret from a protected environment file. `DCMS_DB_PATH` supplies the default database path; explicit `--database` overrides it. A configured `DCMS_USERS_FILE` enables account login; the older `DCMS_DEMO_PASSWORD` Basic-auth fallback applies when no account file is configured.

Keep this preview bound to loopback. For hosted access use the documented HTTPS proxy and protected configuration. Do not use `--secure-cookies` for a direct HTTP preview: the browser will not return secure session cookies over ordinary HTTP.

## Update and verify

Stop the local process and back up the database before an update that may include migrations. With the process stopped, copying the database is sufficient for the current setup; the server guide also provides an SQLite backup command that works for a running database.

```bash
cp instance/local.sqlite3 "instance/local-before-update-$(date -u +%Y%m%dT%H%M%SZ).sqlite3"
git status --short
git pull --ff-only origin main
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m dcms --database instance/local.sqlite3 serve --port 8081
```

Review or preserve local changes before pulling; do not discard work to force an update. Reopen the dashboard, a saved receipt and a reconciliation report. To reset sample history, seed a different filename and explicitly serve that file; keep the original if it contains work you need.

## Troubleshooting

| Symptom | Check |
|---|---|
| Address already in use | Another process may own the port. Stop your existing DCMS terminal or select another `--port`; do not kill all Python processes. |
| Missing dependencies | Use `.venv/bin/python`, and install the repository's `requirements.txt` into that environment. |
| Seed refuses an existing path | Resume with `serve`, or select a new path for a new dataset. |
| Unexpected empty history | Check the working directory, `--database` and `DCMS_DB_PATH`. |
| Login or form keeps failing | Check the account file, HTTP versus secure-cookie setting, and whether the process restarted between requests. Reload and sign in again. |
| Old presentation date is closed | View its saved report. Create transactions on an open business date. |

For schema, transactions and deployment boundaries see [ARCHITECTURE.md](ARCHITECTURE.md).
