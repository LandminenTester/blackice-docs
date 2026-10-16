# Database quickstart: from installation to your first saved row

This guide connects a **BlackICE game server**, the **lt_database connector bundle**, **lt-database-api**, and a database. The panel is a separate resource and is not required.

## What runs where?

```text
Your server-side C# bundle
  → lt_database (inside the same BlackICE server)
    → lt-database-api (an HTTP service you host)
      → PostgreSQL, MySQL/MariaDB or MongoDB
```

Your game bundle knows a namespace and table names. The connector knows the API address and signing key. Only the API knows the database password. See the [glossary](glossary.md) for unfamiliar terms.

## 1. Start a local API and PostgreSQL

Use a development machine with Git, Docker and Docker Compose installed. Run the commands in a terminal; these are **not game-console commands**.

```sh
git clone https://github.com/LandminenTester/lt-database-api.git
cd lt-database-api
```

Copy `.env.example` to `.env` using your file manager, `cp .env.example .env` on Linux/macOS, or `Copy-Item .env.example .env` in PowerShell. Open `.env` in a text editor. Replace **both** example values:

- `LDB_KEY_MAIN`: a random signing secret, at least 32 characters. Keep it; the connector needs the exact same value.
- `DB_PASSWORD`: a different random password for the local database.

Then run:

```sh
docker compose --profile postgres up --build -d
docker compose --profile postgres ps
curl http://127.0.0.1:8080/v1/health
```

In PowerShell, use `curl.exe` if `curl` is an alias. The API should return JSON with `status: "ok"`. This public health check proves the HTTP service is reachable; the signed check in step 3 also checks the database. The selected Compose profile starts PostgreSQL and the API; use `mysql` or `mongodb` instead to try another provider.

This trial exposes port 8080 only on the local machine. `127.0.0.1` always means the machine **running the caller**: a game server on another machine or in a separate container cannot use this address to reach your laptop. For remote installation, follow [deployment](lt-database-api/docs/DEPLOYMENT.md) and use an HTTPS API address.

## 2. Install and configure the connector

Download the [lt_database bundle release](https://github.com/LandminenTester/lt-database/releases/latest). Extract it into `<server>/data/ugc/lt_database/`; `<server>` means the folder containing your BlackICE server installation. Do not create a second nested `lt_database` folder.

For the same-machine Compose trial, edit `config.toml`:

```toml
[Networking]
allowed = ["http://127.0.0.1:8080"]
```

Create `<server>/data/ugc/lt_database/vfs/database.json`:

```json
{
  "url": "http://127.0.0.1:8080",
  "keyId": "main",
  "secretFile": "database.secret",
  "allowedNamespaces": ["documentation_demo"]
}
```

Create `database.secret` **next to that JSON file**, containing only the `LDB_KEY_MAIN` value from `.env`, on one line. Do not include the variable name or surrounding quotes. This trial uses key ID **`main`**, as configured by `docker-compose.yml`. The separate `docker-compose.all.yml` trial uses **`gameserver`** by default; do not mix the two configurations.

The Compose trial permits every namespace at the API key. Restrict `AllowedNamespaces` on the API to your actual namespaces before using a production server. The connector's `allowedNamespaces` is an additional local check; it does not replace API permissions.

## 3. Verify the complete connection

In the **BlackICE server console**, run:

```text
start lt_database
lt-db-health
```

Look for a successful signed health result with `database: true`. If it fails, run `lt-db-status` and check the API URL, allowed host, key ID and secret. Use [troubleshooting](lt-database/docs/OPERATIONS.md) for the reported error code. A configuration edit can be reloaded with `lt-db-reload`; a manifest edit needs `restart lt_database`.

## 4. Build and run the example

Read [C# usage](lt-database/docs/USAGE.md), then follow the [player-preferences walkthrough](lt-database/docs/EXAMPLES.md). It explains every alias, the schema, callbacks, and the exact expected output. The example uses `documentation_demo`, saves one sample, reads back volume 40 and visits 1, then removes its sample row. It does not install a player settings feature.

## 5. Choose how writes are applied

Writes apply live by default. First get the live example working. Enable [optional write-behind](lt-database-api/docs/WRITE-BEHIND.md) only when delayed visibility is acceptable. A queued response means journal acceptance, not a completed database change. For fixed daily times, disable interval and threshold triggers with `FlushIntervalSeconds: 0` and `FlushThreshold: 0`, then set `FlushAt` and `TimeZone`. Manual flushes, shutdown and ordering requirements can still apply writes earlier.

## 6. Move beyond the trial

Follow production deployment for HTTPS, private database access, restricted keys and persistent backups. Keep the connector before consumers in `server.cfg`. Use the [runtime smoke test](lt-database/examples/smoke/README.md) in a disposable namespace before upgrades. Back up the database and any pending write journal, and test restoration.
