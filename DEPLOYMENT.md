# Hosted DCMS

The deployment uses one Waitress process managed by systemd, SQLite on persistent local disk, and Caddy for HTTPS. It does not need Docker, PM2, Node.js or an additional database server.

## Current service status - 10 November 2026

Reactivated at the user request for the screenshot gallery. Both dcms and Caddy are active and enabled. The hosted site is running at https://dcms.tirallab.page. Existing data, accounts, configuration and TLS storage were reused. The earlier requested shutdown is recorded in IMPLEMENTATION_STATUS.md. Stop and resume procedures remain below. Swap settings were not changed.

## Server layout

- Host: `mark@51.107.71.47` (Ubuntu 24.04).
- Site: `https://dcms.tirallab.page`.
- Code and Python environment: `/opt/dcms` and `/opt/dcms/.venv`.
- Database: `/var/lib/dcms/dcms.sqlite3`; never replace it during an update.
- Service: `dcms.service`, dedicated unprivileged `dcms` account, `127.0.0.1:8080`, automatic restart and 256 MiB memory limit.
- Root-only runtime environment: `/etc/dcms.env`.
- Root-owned account hashes, readable by the app service group: `/etc/dcms-users.json`.
- Proxy configuration: `/etc/caddy/Caddyfile`; original retained as `Caddyfile.before-dcms`.

The initial dataset spans five months ending 10 November 2026. It contains synthetic customers and workers. Existing data is retained across restarts and updates. Swap settings were not changed.

## Accounts

Select Sales Manager or CEO on the login page and enter the requested sample password `demo`.

| Account | Internal username | Access |
|---|---|---|
| Sales Manager | `sales_manager` | Daily sales, attendance, workers, reconciliation and bank statement operations |
| CEO | `ceo` | Dashboards, reports, receipts, worker records, attendance and bank records; no operational writes |

CEO restrictions are checked on the server for every modifying route, independently of hidden editing controls. Sessions expire after eight hours, use HTTP-only secure cookies on this deployment, and rotate at sign-in. Login and logout use CSRF protection. Five login attempts per client IP per minute are allowed in the single process. Account files store salted PBKDF2 password hashes. Sample passwords are deliberately shared for presentation use. Per-change operator identity is not yet saved in business history tables.

Create the requested sample accounts once:

```bash
sudo /opt/dcms/.venv/bin/python -m dcms.auth --sample --output /etc/dcms-users.json
sudo chown root:dcms /etc/dcms-users.json
sudo chmod 640 /etc/dcms-users.json
```

The command refuses to overwrite an existing file. Add `DCMS_USERS_FILE=/etc/dcms-users.json` to `/etc/dcms.env`; keep `DCMS_SECRET_KEY` stable and `DCMS_DB_PATH=/var/lib/dcms/dcms.sqlite3`. Never commit the environment or accounts file.

## Updates and checks

```bash
sudo git -C /opt/dcms pull --ff-only origin main
sudo /opt/dcms/.venv/bin/pip install -r /opt/dcms/requirements.txt
sudo systemctl restart dcms
sudo systemctl status dcms caddy --no-pager
sudo journalctl -u dcms -u caddy -n 40 --no-pager
```

The application applies schema initialization/migrations on startup without reseeding. Before an update, create a consistent SQLite backup with Python's `sqlite3.Connection.backup()` API rather than copying an actively written database file. Store backups outside the code checkout.

Caddy proxies `dcms.tirallab.page` to `127.0.0.1:8080`; the app is not bound to a public interface. Verify the public TLS certificate, HTTP-to-HTTPS redirect, login, both account roles, and saved reports after an update. Run the regression suite locally with `.venv/bin/python -m unittest discover -s tests -v`.

## Stop and resume the site

To stop the application and prevent it returning on reboot:

```bash
sudo systemctl disable --now dcms
```

If Caddy serves only this project, it can also be stopped with `sudo systemctl disable --now caddy`. Do not stop a shared proxy. Preserve `/var/lib/dcms`, the code, account file, environment and TLS certificate storage. Swap configuration does not need to change.

To resume this dedicated deployment:

```bash
sudo systemctl enable --now dcms caddy
```

Stopping the app does not shut down or deallocate the VM. Verify the application is inactive and the public URL no longer serves DCMS.
