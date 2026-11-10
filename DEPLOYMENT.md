# Server deployment and operation

Verified over SSH on 10 November 2026. The site is running at <https://dcms.tirallab.page>. Both `dcms` and Caddy are active and enabled after the requested screenshot capture. This document does not itself stop or reconfigure them. Local web-preview instructions are in [RUNNING.md](RUNNING.md); component boundaries are in [ARCHITECTURE.md](ARCHITECTURE.md).

## Installed layout

| Item | Current value |
|---|---|
| SSH | `mark@51.107.71.47`, Ubuntu 24.04 |
| Code and virtual environment | `/opt/dcms`, `/opt/dcms/.venv` |
| Data | `/var/lib/dcms/dcms.sqlite3` |
| Service account | Unprivileged `dcms` user and group |
| App listener | `127.0.0.1:8080`, one Waitress process |
| Environment | `/etc/dcms.env`, `root:root`, mode `600` |
| Account hashes | `/etc/dcms-users.json`, `root:dcms`, mode `640` |
| Data directory | `/var/lib/dcms`, `dcms:dcms`, mode `750` |
| HTTPS proxy | Caddy; `/etc/caddy/Caddyfile` |
| Service unit | `/etc/systemd/system/dcms.service` |

The VM has approximately 1 GB RAM. The application has a 256 MiB systemd memory ceiling. No Docker, PM2, Node application runtime, external database or swap change was introduced. This setup has not been load-tested for production capacity.

The server code revision observed during this documentation review was `9445df0`; later repository commits contain documentation and screenshots. Pushing to GitHub does not automatically update `/opt/dcms`. The installed dataset is synthetic and spans five months ending 10 November 2026. Updates and restarts retain it.

## Connect

From the computer holding the private key:

```bash
ssh -i /home/mark/Documents/ChatGPT/DCMS/last_key.pem mark@51.107.71.47
```

Run the remaining server commands in that SSH session. Keep the key private and outside Git. The account has sudo access. SSH requires TCP 22, and the public site requires TCP 80/443 through the VM/network firewall. Port 8080 stays private on loopback. The domain must resolve to the server for public HTTPS.

## Runtime configuration and accounts

The protected environment file contains these variables; placeholder text below is descriptive, not a working secret:

```text
DCMS_DB_PATH=/var/lib/dcms/dcms.sqlite3
DCMS_USERS_FILE=/etc/dcms-users.json
DCMS_SECRET_KEY=<stable randomly generated secret>
```

Keep the existing secret stable during ordinary updates. The legacy `DCMS_DEMO_PASSWORD` setting is unnecessary for account-file login. systemd loads the environment file; the app does not automatically load a repository `.env` file.

| Login selection | Username | Requested presentation password | Access |
|---|---|---|---|
| Sales Manager | `sales_manager` | `demo` | Daily operations and reports |
| CEO | `ceo` | `demo` | Read-only oversight |

Passwords are stored as salted PBKDF2 hashes. Sessions last eight hours, with secure HTTP-only cookies, CSRF protection and server-side role enforcement. There is a five-attempt per-client-IP per-minute login limit in the single app process. These are shared presentation credentials, not private operator identities. General per-change actor attribution remains pending.

The account file already exists on this server. For a fresh installation only, create it from the checkout working directory, then set ownership:

```bash
cd /opt/dcms
sudo .venv/bin/python -m dcms.auth --sample --output /etc/dcms-users.json
sudo chown root:dcms /etc/dcms-users.json
sudo chmod 640 /etc/dcms-users.json
```

Creation refuses to overwrite an existing account file. Never commit or print account hashes or runtime secrets.

## Installed service definitions

The systemd unit is:

```ini
[Unit]
Description=Deniz Construction web application
After=network.target

[Service]
User=dcms
Group=dcms
WorkingDirectory=/opt/dcms
EnvironmentFile=/etc/dcms.env
Environment=PYTHONDONTWRITEBYTECODE=1
ExecStart=/opt/dcms/.venv/bin/python -m dcms serve --host 127.0.0.1 --port 8080 --secure-cookies
Restart=on-failure
RestartSec=3
UMask=0027
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/dcms
MemoryMax=256M
TasksMax=32

[Install]
WantedBy=multi-user.target
```

Caddy configuration:

```caddyfile
dcms.tirallab.page {
    encode gzip
    reverse_proxy 127.0.0.1:8080
}
```

Caddy manages TLS and redirects HTTP to HTTPS. Waitress accepts proxy headers from loopback. The original Caddy configuration was retained as `/etc/caddy/Caddyfile.before-dcms`. Existing Caddy certificate storage must survive restarts and updates.

For a **new server**, provision Python 3/venv, Git and Caddy; create the unprivileged service account and data directory with the ownership above; clone the repository into `/opt/dcms`; create its virtual environment and install `requirements.txt`. Create a protected environment file with a fresh random secret and the account file, then install the unit and proxy definitions above. Initialize the selected database as `dcms`. Use `init --history --end-date 2026-11-10` only for a fresh presentation database; use plain `init` for an empty database. Do not seed over an existing installation. Finish with `systemctl daemon-reload`, Caddy validation, and `systemctl enable --now dcms caddy`, then perform the verification below. This describes rebuilding the installed topology; it is not an automated provisioning script.

## Start, stop and restart

| Intention | Server command | Result |
|---|---|---|
| Start application now | `sudo systemctl start dcms` | Opens the existing database; does not change boot policy |
| Restart application | `sudo systemctl restart dcms` | Brief interruption; retains records and applies outstanding migrations |
| Stop temporarily | `sudo systemctl stop dcms` | Stops the app now; an enabled service returns after reboot |
| Stop across reboots | `sudo systemctl disable --now dcms` | Stops now and removes automatic boot startup |
| Resume this dedicated site | `sudo systemctl enable --now dcms caddy` | Starts both services and enables startup after reboot |

Caddy serves only this project on the current VM. For a complete site shutdown also run `sudo systemctl disable --now caddy`. On a shared server, leave the shared proxy running and remove or disable only this site's configuration. An active proxy with a stopped backend may return 502; that does not mean DCMS is still running.

Check actual state with `systemctl is-active dcms caddy`, `systemctl is-enabled dcms caddy`, and `sudo ss -ltnp`. State commands return nonzero when a service is inactive or disabled. A full shutdown should leave no DCMS application listener and no public DCMS page. Preserve code, database, configuration, accounts and certificates. Stopping the site does not stop or deallocate the Azure VM or end its compute charges.

## Consistent database backup

There is no scheduled off-machine backup job. Create a backup before updates and before any recovery operation. This command uses SQLite's backup API and can run while the app is active. It creates a root-only backup outside the code checkout:

```bash
sudo install -d -m 700 -o root -g root /var/backups/dcms
sudo python3 - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
path = Path('/var/backups/dcms') / f'dcms-{stamp}.sqlite3'
with sqlite3.connect('file:/var/lib/dcms/dcms.sqlite3?mode=ro', uri=True) as source:
    with sqlite3.connect(path) as target:
        source.backup(target)
        assert target.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
path.chmod(0o600)
print(path)
PY
```

Retain the printed path and the matching code revision. An on-VM backup is not protection from VM loss. Keep protected copies off the VM, together with separately protected configuration/accounts and recovery instructions. Do not copy an actively written SQLite database with ordinary `cp`.

## Update an existing deployment

Perform a planned interruption so the pre-update backup includes all accepted writes. First stop DCMS, run the backup command above and record the installed revision:

```bash
sudo systemctl stop dcms
sudo git -C /opt/dcms rev-parse HEAD
sudo git -C /opt/dcms status --short
```

After the backup succeeds, inspect any local changes, then update:

```bash
sudo git -C /opt/dcms pull --ff-only origin main
sudo /opt/dcms/.venv/bin/python -m pip install -r /opt/dcms/requirements.txt
sudo systemctl start dcms
sudo systemctl status dcms caddy --no-pager
sudo journalctl -u dcms -n 40 --no-pager
```

Do not continue past a failed pull or dependency installation. Startup applies migrations without reseeding. A failed startup needs log review and recovery; blindly starting old code against a newer schema is not a rollback plan. Do not run the test suite against the hosted database; run it locally before deployment.

For unit changes run `sudo systemctl daemon-reload` before restarting the app. For proxy changes validate before reloading:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Ordinary code/documentation updates do not require changing or restarting Caddy.

## Verify and troubleshoot

```bash
sudo systemctl status dcms caddy --no-pager
sudo journalctl -u dcms -u caddy -n 40 --no-pager
curl -I http://127.0.0.1:8080/
curl -I https://dcms.tirallab.page/
```

With account login enabled, an unauthenticated root request redirects to login; this is expected. Verify HTTP redirects to HTTPS, login works for both roles, existing receipts and close reports reopen, CEO cannot write, and Sales Manager can reach the operational forms. Avoid creating transactions simply to check an existing presentation dataset. Check database integrity using a read-only SQLite connection when investigating storage issues.

A 502 points first to the backend service/listener. An unreachable domain needs DNS, VM, firewall and Caddy checks. Login/form failures need account-file permissions, secure-cookie/HTTPS configuration, stable secret and proxy checks. Inspect logs rather than replacing the database to fix startup errors.

## Restore or roll back

Restore is a deliberate recovery operation that can discard records created after the chosen backup. Stop DCMS first and take a separate backup of its current database. Validate the selected recovery file with SQLite `PRAGMA integrity_check` and establish the matching code/schema version before replacing data.

With the service stopped, restore a copy into `/var/lib/dcms/dcms.sqlite3`, owned by `dcms:dcms` with mode `640`. Keep the original failed database and a record of which backup and code revision were used. Restore the matching code and dependencies if needed, then start DCMS and verify saved reports and roles. Do not merge files, reseed, or run an older release against a database its migration version rejects. Automatic rollback, restore UI and tested off-machine disaster recovery are still pending work.
