# Terms and abbreviations

Start here when a name in a guide is unfamiliar. Names inside code and configuration stay in English so they match the actual software.

| Term | Explanation |
| --- | --- |
| BlackICE / REServer | The game-server software on which server bundles run. |
| Resource | A separately installed tool, service or bundle in this library. |
| Bundle / UGC | A game extension; UGC means user-generated content. A bundle can contain server, client and shared code. |
| Consumer | Your own bundle that uses another bundle's exported functions. |
| Server realm | Code running on the game server, where authoritative database access belongs. |
| Client realm | Code running on a player's computer; never store database secrets here. |
| API / HTTP | Application Programming Interface; HTTP is the network protocol used by the database service and panel interfaces. |
| Endpoint | A specific HTTP method and path, such as `POST /v1/data/find`. |
| JSON | A text format for objects, arrays and values; used for settings and API messages. |
| Namespace (`ns`) | A named collection of tables. Both the connector and API key must allow it. |
| Schema / table / row / column | The data definition; a collection of records; one record; one named value in a record. |
| Primary key | Column(s) uniquely identifying a record. |
| Index / unique | An index helps lookups; a unique index also rejects duplicate values. |
| Nullable / null | A nullable column permits an absent value represented by `null`. |
| CRUD | Create, Read, Update, Delete: the four basic data operations. |
| Upsert | Insert a row if its key is missing, otherwise update the matching row. |
| `Db` | The `LtDatabaseClient.Db` C# helper that sends connector requests. |
| `S` / `F` / `Q` | Schema builder / filter builder / row-and-sort builder in `LtDatabase`. Readable aliases are shown in the usage guide. |
| `Eq` / `Ne` | Equal / not equal. |
| `Gt` / `Gte` / `Lt` / `Lte` | Greater than / greater than or equal / less than / less than or equal. |
| `inc` / `incJson` | Increment: add the supplied number to the existing numeric value. `-5` subtracts five. |
| `set` / `setJson` | Replace a value with the supplied value. |
| Callback / asynchronous | A function receives the result when it is available; the call does not wait for the database to finish. |
| Ticket | An identifier returned when the connector accepts work. It is not the final database result. |
| Idempotent | Repeating an operation has the same effect as applying it once. Setting a fixed value can be idempotent; adding one is not. |
| Idempotency key | Identifies one operation so retries can return its existing result within the API's retention window. |
| Write-behind / queued | Optional write buffering: accepted writes enter a journal and reach the database later. |
| Flush | Apply pending writes now. Check the report for remaining, rejected or halted operations. |
| Journal / dead letter | Durable pending-write log / a write that could not be applied and needs investigation. |
| Live / immediate | The request applies to the database before reporting its write result. |
| DDL / DML | Data Definition Language (schema changes) / Data Manipulation Language (read and write rows). Separate database accounts can limit their privileges. |
| HMAC / SHA-256 | Keyed message authentication / the hash algorithm used by the signing protocol. HMAC authenticates messages; TLS protects the connection. |
| TLS / HTTPS | Encrypted, authenticated transport. HTTPS is HTTP over TLS. |
| Key ID / secret | Public identifier of a signing key / private random value used to sign requests. The ID is not a password. |
| Nonce / UTC | A one-use random request value / Coordinated Universal Time, used for timestamps. |
| VFS | Virtual file system: the bundle's private settings directory. |
| WASM / WASI | WebAssembly executable format / the system interface used by compiled server code. |
| SDK / .NET | Software Development Kit / the runtime and build tools used by these C# projects. |
| CI | Continuous Integration: automated checks run by GitHub Actions. |
| Supervisor / Webhost | The panel's process controller / the component serving the browser interface. |
| Reverse proxy | A server in front of an application that can provide HTTPS and forward requests. |
| CIDR / ACL | Network range notation / operating-system access control list. |
| CSRF / SSE | Cross-Site Request Forgery / Server-Sent Events, used for live browser updates. |

Next: [choose a resource](getting-started.md), [database quickstart](database-quickstart.md), or [C# usage](lt-database/docs/USAGE.md).
