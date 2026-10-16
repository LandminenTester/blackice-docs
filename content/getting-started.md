# Getting started

This is the documentation library for LandminenTester BlackICE resources. Start with the resource you want to use.
The guides cover installation, configuration, operation, building from source and API usage.

## Choose a resource

### BlackICE Server Panel

A standalone web interface for managing a BlackICE server, its console, accounts, logs and bundles.
Follow the [panel overview](webpanel/README.md) and your platform guide:
[Windows](webpanel/docs/windows.md), [Linux](webpanel/docs/linux.md) or [Docker](webpanel/docs/docker.md).

### lt_database

A server-side connector for scripts that need database persistence. It calls lt-database-api using signed HTTP requests.
Start with [bundle installation](lt-database/docs/INSTALL.md) or follow the [database pair quickstart](database-quickstart.md).

Its default folder is `lt_database`, shared C# types use `LtDatabase`, the helper uses `LtDatabaseClient`, and console
commands start with `lt-db-`. Start the connector before bundles that consume its exports.

### lt-database-api

An independently hosted HTTP service in front of PostgreSQL, MySQL/MariaDB or MongoDB. It is the backend required by
lt_database and can also serve other signed HTTP clients. Start with [deployment](lt-database-api/docs/DEPLOYMENT.md)
and the [HTTP API reference](lt-database-api/docs/API.md).

## Read a resource guide

Check its requirements, configure it for your environment, then use its documented checks before relying on it.
Use the resource's own build guide when developing from source. Use its operations and security guides for updates,
credentials, backups and troubleshooting.

## Contribute or report an issue

Each resource links to its own source repository. Report a product bug there. For documentation improvements,
see [sources and maintenance](sources.md). Sensitive findings belong in the relevant product's security reporting channel.
