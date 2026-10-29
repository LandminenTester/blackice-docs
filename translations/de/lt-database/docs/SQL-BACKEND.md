# Das SQL-Backend (`re.sql`)

Seit 0.3.0 kann der Connector auf zwei Wegen mit einer Datenbank sprechen. Beide liefern Consumern **exakt dieselben Exporte, Anfragen, Ergebnisse
und Fehlercodes**. Ein Consumer-Bundle (der Helper `LtDatabaseClient.Db` oder der `LtDatabase`-Speicheradapter von lt-core) muss deshalb nie wissen,
welches Backend aktiv ist.

| | `http` (Standard) | `sql` |
|---|---|---|
| Weg | Bundle → HTTPS → [lt-database-api](https://github.com/LandminenTester/lt-database-api) → Datenbank | Bundle → `re.sql`-Provider des Hosts → Datenbank |
| Voraussetzung | laufende API, ein Key, ein erlaubter Host in `[Networking]` | BlackICE-Host mit SDK **1.3.0** oder neuer und ein `[Database.<alias>]`-Eintrag in der `config.toml` des Bundles |
| Datenbanken | PostgreSQL, MySQL/MariaDB, MongoDB | PostgreSQL, SQLite |
| Authentifizierung | HMAC-signierte Anfragen und Antworten | keine auf der Leitung; Zugriff begrenzen `allowedNamespaces` und das Datenbankkonto hinter dem Alias |
| Write-behind | optional, in der API konfiguriert | nicht verfügbar; jede Änderung wird sofort geschrieben |
| Typischer Einsatz | gemeinsame Datenbank, mehrere Spielserver, MySQL oder MongoDB | ein Spielserver, kein zusätzlicher Dienst, lokale Entwicklung, Tests |

Pro Bundle-Installation **ein** Backend wählen. Gemischter Betrieb je Namespace wird nicht unterstützt.

## Backend wählen

`vfs/database.json`:

```json
{
  "backend": "sql",
  "sqlAlias": "players",
  "sqlDialect": "auto",
  "destructiveMode": "deny",
  "allowedNamespaces": ["mygame"],
  "timeoutMs": 10000,
  "maxConcurrent": 8
}
```

| Feld | Standard | Bedeutung |
|---|---|---|
| `backend` | `"http"` | `"http"` oder `"sql"`. Eine Datei ohne dieses Feld funktioniert wie bisher. |
| `sqlAlias` | erforderlich für `sql` | Name eines `[Database.<alias>]`-Eintrags in der `config.toml` des Bundles (Buchstaben, Ziffern, `_`, `-`, höchstens 64 Zeichen). Host, Benutzer, Passwort oder Dateipfad stehen dort und sind für den Bundle-Code nie sichtbar. |
| `sqlDialect` | `"auto"` | `"auto"` (fragt die Datenbank: `sqlite_version()` antwortet bei SQLite, alles andere gilt als PostgreSQL), `"postgres"` oder `"sqlite"`. Explizit setzen, wenn keine Erkennung gewünscht ist. |
| `destructiveMode` | `"deny"` | Was `schema.sync` mit Tabellen und Spalten tun darf, die aus der Deklaration verschwunden sind: `"deny"`, `"quarantine"` oder `"apply"`, siehe [Schema-Sync](#schema-sync). |
| `allowedNamespaces`, `timeoutMs`, `maxConcurrent` | wie bei `http` | Gleiche Bedeutung. `timeoutMs` wird zum SQL-Befehlszeitlimit, auf ganze Sekunden aufgerundet und bei 30 gedeckelt (Grenze von `re.sql`). |

Mit `"backend": "sql"` werden `url`, `keyId`, `secretFile` und `allowInsecureHttp` ignoriert; `[Networking] allowed` ist nicht nötig. Jede ungültige
Kombination lässt das Bundle geladen, beantwortet aber jeden Aufruf mit `not_configured` (siehe `lt-db-status`). Eine falsche Datei fällt so nie auf
ein anderes oder halb funktionierendes Backend zurück.

Die Verbindung selbst gehört in die `config.toml`:

```toml
[Database.players]
type = "postgres"
conninfo = "host=${DB_HOST} port=5432 dbname=players user=ugc password=${DB_PASSWORD}"

[Database.stats]
type = "sqlite"
name = "stats.db"
```

`type` ist `"postgres"` oder `"sqlite"`. `conninfo` (nur PostgreSQL) ist ein libpq-Verbindungsstring, in dem `${VAR}` durch Umgebungsvariablen ersetzt
wird; er muss genau einen Host nennen. `name` (nur SQLite) legt die Datei unter `data/persistent/<bundle>/` an; jedes Bundle hat seine eigene Datei. Die
genauen Schlüssel definiert die Replay.RE-Dokumentation zu `re.sql` (SDK 1.3.0); der Connector braucht nur den Alias-Namen und liest den Eintrag nicht.
Verbindungstest: `lt-db-health` (die Antwort enthält `"database": true`, wenn `SELECT 1` funktioniert hat).

`lt-db-reload` liest `vfs/database.json` neu, verwirft alle Caches und erkennt den Dialekt erneut. Ein geänderter `[Database.<alias>]`-Eintrag erfordert
wie jede `config.toml`-Änderung einen Neustart des Bundles.

## Was identisch zur API ist

Alles, was ein Consumer beobachten kann:

* Operationen: `health`, `schema.sync`, `schema.describe`, `insert`, `find`, `count`, `update`, `upsert`, `delete`, `flush`, `mutation.execute`,
  `mutation.receipt`.
* Anfragefelder, Standardwerte und Grenzen: Filtergrammatik (8 Ebenen, 128 Bedingungen, 1000 Listeneinträge, 1024 Zeichen bei Textoperatoren), `fields`,
  `sort`, `limit` (auf 1 bis 1000 begrenzt), `offset` (0 bis 1.000.000), `set` und `inc`, `all`, Upsert-`keys` (Primärschlüssel oder Unique-Index), höchstens
  1000 Zeilen pro Insert, `dryRun`, `idempotencyKey`.
* Ergebnisformen: `{"rows":[…],"hasMore":…}`, `{"inserted":n,"ids":[…]}`, `{"affected":n}`, `{"count":n}`, das Sync-Ergebnis mit Plan,
  `schema.describe`, das Receipt-Objekt.
* Fehlercodes und HTTP-ähnliche Status (`400 invalid_filter`, `404 unknown_table`, `409 constraint_violation`, `422 idempotency_conflict`, …).
  Treibermeldungen werden nie zurückgegeben (sie können Zeilenwerte enthalten); es gibt nur einen stabilen Code und einen festen Text.
* Bezeichnerregeln, die physischen Namen (`<namespace>__<table>`, `ix_<table>_<index>`), die Verwaltungstabellen (`_ldb_schema`,
  `_ldb_mutation_receipts`) und der **Schema-Hash**. Hash, gespeicherte Definition und Receipt-Fingerprint sind byte-identisch mit denen von
  lt-database-api; Unit-Tests vergleichen sie mit Vektoren aus dem Code der API. In der Praxis kann eine über die API angelegte PostgreSQL-Datenbank vom
  SQL-Backend übernommen werden und umgekehrt.
* Idempotenz: derselbe `idempotencyKey` mit derselben Nutzlast liefert das erste Ergebnis, mit anderer Nutzlast `422 idempotency_conflict`. Der Cache lebt
  im Speicher des Bundles (10 Minuten, 5000 Einträge) und wird von `lt-db-reload`, einem Neustart oder einem Absturz geleert. Der Connector wiederholt
  Schreibvorgänge nie automatisch. Wo „genau einmal“ zählt, [Mutation-Receipts](#mutation-receipts) verwenden.

## Was anders ist (und warum)

| Thema | Verhalten mit `sql` |
|---|---|
| Authentifizierung, Signatur, Replay-Schutz, Ratenlimits | Nicht vorhanden: es gibt keinen Netzwerkweg zu schützen. Die Isolation beruht auf `allowedNamespaces` und auf dem **Datenbankkonto hinter dem Alias**, das nur anfassen darf, was das Spiel braucht (inklusive `CREATE`/`ALTER` für den Schema-Sync und bei PostgreSQL `pg_advisory_xact_lock`). |
| Rechte je Key | Die API kann ungefilterte Schreibvorgänge je Key verbieten. Im Modus `sql` ist `"all": true` immer erlaubt, weil jedes Bundle, das den Connector aufrufen kann, gleich weit vertraut wird. |
| Write-behind | Nicht implementiert. `durability` wird ignoriert, `flush` antwortet `{"flushed":0,"deadLettered":0,"remaining":0,"halted":false,"enabled":false}` und `Db.IsQueued` ist immer `false`. |
| Standard von `destructiveMode` | Hier `deny`, weil kein separater Betreiber die API konfiguriert hat. `quarantine` oder `apply` bewusst setzen. |
| `health` | `{"status":"ok","provider":"postgres"\|"sqlite","database":true\|false,"writeBuffer":{…deaktiviert…}}`; `provider` ist bei `auto` vor der ersten Verbindung `unknown`. |
| Datenbanken | Nur PostgreSQL und SQLite. MySQL, MariaDB und MongoDB bleiben beim Backend `http`. `mutation.*` gibt es auf beiden Engines. |
| Zeit- und Zahlenformate | Gleiches JSON. SQLite speichert `decimal` als `NUMERIC` und liefert eine Zahl ohne Nachkomma-Nullen (`12.5` statt `12.50`). |
| Anfragegröße | Jede Operation läuft auf einer eigenen Verbindung (je Aufruf geöffnet und geschlossen); ein Ergebnis wird vollständig in den Speicher gelesen und durch die 1000-Zeilen-Grenze begrenzt. |

### Typen

| Deklarierter Typ | PostgreSQL | SQLite |
|---|---|---|
| `int32` | `INTEGER` | `INTEGER` |
| `int64` | `BIGINT` | `INTEGER` |
| `decimal(p,s)` | `NUMERIC(p,s)` | `NUMERIC` (binäre Gleitkommazahl ab etwa 15 Stellen) |
| `float64` | `DOUBLE PRECISION` | `REAL` |
| `bool` | `BOOLEAN` | `INTEGER` 0/1 |
| `string(n)` | `VARCHAR(n)` | `TEXT`, Länge **vom Bundle erzwungen** |
| `text` | `TEXT` | `TEXT` |
| `json` | `JSONB` | `TEXT` (kompaktes JSON) |
| `datetime` | `TIMESTAMPTZ` | `TEXT`, ISO 8601 UTC mit sechs Nachkommastellen, z. B. `2026-10-28T10:00:00.000000Z` |
| `date` | `DATE` | `TEXT` `yyyy-MM-dd` |
| `uuid` | `UUID` | `TEXT`, Kleinbuchstaben |
| `bytes(n)` | `BYTEA` | `BLOB` |

`re.sql` des Hosts bindet nur primitive Werte. Der Connector sendet Datum, UUID, Dezimalzahlen und JSON deshalb als Text und lässt PostgreSQL mit einem
expliziten `CAST(… AS …)` umwandeln; er hängt nie davon ab, wie ein Treiber einen .NET-Typ abbilden würde. `datetime`-Defaults von `"now"` werden zu
`CURRENT_TIMESTAMP` (PostgreSQL) oder einem UTC-`strftime`-Ausdruck (SQLite).

## Schema-Sync

`schema.sync` verhält sich wie in der API: Die Deklaration wird geprüft und normalisiert, gehasht, mit der gespeicherten Definition verglichen, und der Plan
wird in fester Reihenfolge angewendet (Umbenennungen, Index-Löschungen, neue Spalten, geänderte Spalten, neue Tabellen, neue Indizes, entfernte Spalten,
entfernte Tabellen). Er ist **deklarativ und wiederholbar**: Eine unveränderte Deklaration liefert `status: "unchanged"`. Objekte, die existieren sollten
und in der Datenbank fehlen, werden repariert (im Plan mit dem Hinweis `repair: …`).

* Der gesamte Sync läuft in **einer Transaktion** (DDL ist auf beiden Engines transaktional); ein Fehler hinterlässt nichts Halbfertiges. Ein zweiter
  Sync desselben Namespace wartet auf eine Sperre: eine PostgreSQL-Advisory-Lock oder die einzige Schreibsperre von SQLite.
* `dryRun: true` liefert den Plan ohne Transaktion und ohne Änderung (`planned`, `unchanged` oder `denied`).
* **PostgreSQL** ändert Spalten direkt (`ALTER COLUMN … TYPE … USING`, Nullbarkeit, Defaults).
* **SQLite** kann Spalten nicht ändern. Ändern sich Typ, Nullbarkeit oder Default einer Spalte, wird die Tabelle in der Transaktion **neu aufgebaut**: neue
  Tabelle anlegen, Daten kopieren, alte löschen, neue umbenennen, Indizes neu erstellen. Spalten, die nur noch auf ihre Entfernung warten, werden (nullbar)
  mitgeführt, damit `quarantine` ihre Daten behält. Ein Neuaufbau scheitert und macht alles rückgängig, wenn vorhandene Zeilen die neue Definition
  verletzen (etwa eine `NOT NULL`-Spalte mit `NULL`).
* Neue `NOT NULL`-Spalten ohne Default erhalten für vorhandene Zeilen einen neutralen Wert (`0`, `''`, …). PostgreSQL entfernt diesen Default wieder;
  SQLite kann das nicht, der neutrale Default bleibt in der Tabellendefinition. Das Bundle verlangt trotzdem für jede neue Zeile einen Wert, weil es
  das deklarierte Schema prüft, nicht die Tabelle.
* Entfernte Tabellen und Spalten sind **destruktiv**. `deny` verweigert den Sync (`409 destructive_denied`, der Dry-Run zeigt den Plan); `quarantine`
  benennt sie in `_dropped_<Unixzeit>_<Name>` um (Spalten werden nullbar, damit sie Inserts nicht blockieren); `apply` löscht sie. Eine String-Spalte
  unter vorhandene Daten zu kürzen wird verweigert (`409 data_does_not_fit`), ebenso eine Änderung des Primärschlüssels (`409 unsupported_change`) und
  das Ein- oder Ausschalten von Auto-Increment.
* SQLite kennt kein echtes `VARCHAR(n)`; `string`-Längen erzwingt bei jedem Schreibvorgang das Bundle, nicht die Datenbank.

## Mutation-Receipts

`mutation.execute` führt genau ein `Upsert`, `Update` oder `Delete` aus und speichert **in derselben Transaktion** einen dauerhaften Beleg;
`mutation.receipt` liest ihn später, ohne etwas auszuführen. Der Vertrag entspricht dem von lt-database-api und dem Recovery-Code von lt-core:

1. Die Anfrage wird streng geprüft: nur die fünf erwarteten Textfelder, striktes UTF-8-JSON ohne doppelte Schlüssel (die Wurzel wird auch ohne
   Beachtung der Groß-/Kleinschreibung verglichen), höchstens 8192 Byte, Tiefe 16, `all` fehlt oder ist `false`, Namespace gleich dem des Belegs, und der
   Fingerprint gleich dem SHA-256 aus `effectId`, Namespace, Operation und JSON mit Längenpräfix.
2. Zuerst wird eine eindeutige Reservierung `(namespace, effectId)` eingefügt. Eine gleichzeitige Anfrage für denselben Effekt wartet, bis die erste
   Transaktion endet; derselbe Effekt mit gleichem Fingerprint liefert danach den gespeicherten Beleg, mit anderer Operation oder anderem Fingerprint
   `409 receipt_conflict`.
3. Ein Savepoint wird gesetzt, die Änderung läuft und darf **höchstens eine Zeile** betreffen (sonst `409 multiple_rows`). Ein Constraint- oder
   Wertfehler oder jede 4xx-Bedingung rollt bis zum Savepoint zurück und wird als dauerhafter Beleg `failed` mit Code gespeichert; `no_match`
   kennzeichnet ein Update oder Delete ohne Treffer.
4. Der Beleg wird abgeschlossen und die Transaktion committet. Scheitert der Commit oder geht seine Antwort verloren, wird der Fehler unverändert
   weitergereicht: erst ein späteres `mutation.receipt` zeigt, ob die Änderung stattfand. Genau das ist der Sinn des Vertrags.

Hinweise zu den Engines: PostgreSQL nutzt `READ COMMITTED` und `SELECT … FOR UPDATE` auf der Zielzeile und dem Beleg. SQLite hat einen einzigen
Schreiber; die Reservierung nimmt die Schreibsperre, ein zweiter Schreiber wartet (oder scheitert je nach Busy-Timeout des Hosts mit
`conflict_retry`). Belege für MySQL und MongoDB gibt es hier nicht (und MongoDB-Belege unterstützt auch die API nicht).

## Betrieb und Sicherheitshinweise

* Der erste Aufruf nach dem Start (oder `lt-db-reload`) legt `_ldb_schema` und `_ldb_mutation_receipts` mit `CREATE TABLE IF NOT EXISTS` an; das
  Datenbankkonto braucht dafür einmalig `CREATE`.
* SQL-Backend und API nie gleichzeitig auf dieselbe Datenbank richten, außer beide nutzen absichtlich dieselben Namespaces: Sie teilen die
  Verwaltungstabellen und sähen gegenseitig ihr Schema.
* Anweisungen entstehen nur in den SDK-freien Klassen unter `sh/Pure`; Werte reisen immer als gebundene Parameter, `NULL` wird als Literal geschrieben.
  Spalten- und Tabellennamen stammen ausschließlich aus dem gespeicherten Schema und erfüllen die Bezeichnerregeln.
* Das Log enthält nie Nutzlasten, Werte oder Treibermeldungen, nur Operation, Ausnahmetyp und zugeordneten Code.
* `lt-db-status` zeigt `backend=sql alias=… dialect=… destructive=…` und den letzten zugeordneten Fehlercode.

## Fehlerzuordnung

| Bedingung | Code | Status |
|---|---|---|
| Verletzung von Unique, Primärschlüssel, Not-null, Fremdschlüssel oder Check | `constraint_violation` | 409 |
| Deadlock, Serialisierungsfehler, gesperrte Datenbank | `conflict_retry` | 409 |
| Zeitüberschreitung | `database_timeout` | 504 |
| Von der Datenbank abgelehnter Text, Bereich oder Länge | `invalid_value` | 400 |
| Alles andere | `database_error` | 500 |

Die Einordnung betrachtet Ausnahmetyp und Meldungstext des Treibers nur auf dem Server; weil der Host keinen SQLSTATE liefert, kann eine ungewöhnliche
Meldung auf `database_error` fallen. Der Code enthält nie Treibertext.

## Prüfstatus

Automatisch geprüft (`tests/Bundle.Tests`, über 100 Tests):

* Schema-Hash, kanonisches JSON, Diff-Plan und Receipt-Fingerprint gegen Vektoren aus dem echten lt-database-api-Code;
* jede erzeugte Anweisung für beide Dialekte (Filter, Paging, Insert, Update, Upsert, Delete, DDL, Neuaufbau);
* das erzeugte SQL gegen eine **echte SQLite-Engine** (Typen, Filter, Paging, Upsert, Constraint-Fehler, Neuaufbau mit Daten und Indizes,
  Savepoint-Verhalten).

Auf einem echten BlackICE-Server (Docker, `re.sql`-Host) geprüft: Das 38-Schritte-Smoke-Bundle aus `examples/smoke` besteht mit `"backend": "sql"` auf
einem SQLite-Alias 38/38 und auf PostgreSQL 17 ebenfalls 38/38 (Parameterbindung, Transaktionen über awaitete Befehle, Schema-Sync und Neuaufbauten,
Typabbildung). SQLite-Hinweis: Die Sandbox des Hosts verweigert `pragma_table_info`; der Connector liest Spaltennamen deshalb aus `SELECT * … LIMIT 0`.

**Vom Smoke-Bundle noch nicht abgedeckt:** `mutation.execute` / `mutation.receipt` (per Unit-Test und auf echtem SQLite geprüft, aber ohne
Laufzeitszenario in einem BlackICE-Host), das Verhalten von `CommandTimeout` und gleichzeitige Schreiber. `mutation.*`-Consumer bis dahin beim Backend
`http` lassen.
