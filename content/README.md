# BlackICE resources

Documentation for LandminenTester bundles, tools and resources for BlackICE servers. Browse the library to find a resource,
install it, configure it and understand its API. Each resource is documented independently.

## Resource library

| Resource | Purpose | Start here |
|---|---|---|
| BlackICE Server Panel | Independent server management interface | [Overview](webpanel/README.md), [operations](webpanel/docs/operations.md), [HTTP API](webpanel/API.md) |
| lt_database | Database connector bundle for server scripts; requires lt-database-api | [Install](lt-database/docs/INSTALL.md), [C# reference](lt-database/docs/REFERENCE.md), [explained example](lt-database/docs/EXAMPLES.md) |
| lt-database-api | Database HTTP service used by lt_database | [Deployment](lt-database-api/docs/DEPLOYMENT.md), [API reference](lt-database-api/docs/API.md), [OpenAPI](lt-database-api/docs/openapi.yaml) |

The panel is a separate resource with its own setup. The database connector and database API form a pair. Select only
the resources your server needs; this library does not prescribe a shared software stack.

## Find your starting point

Read [Getting started](getting-started.md) to choose a resource. For the database pair, use the
[database quickstart](database-quickstart.md). Each resource has build, configuration, operation and reference guides in
its own section. More BlackICE resources can be added to the library as they are published.

## Source and maintenance

These guides are public and can be read without an account. [Source revisions](sources.md) identify the upstream commits
described by the imported documentation. Report product issues in the corresponding resource repository.

New to these terms? Start with the [glossary](glossary.md). English is the default; select Deutsch in the header for German guides.
