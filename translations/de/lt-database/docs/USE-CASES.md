# Backend und Einstellungen wählen

lt_database erreicht eine Datenbank auf zwei Wegen: über [lt-database-api](https://github.com/LandminenTester/lt-database-api) per HTTPS
(`"backend": "http"`, der Standard) oder direkt über den `re.sql`-Provider des Hosts (`"backend": "sql"`, seit 0.3.0, siehe
[SQL-Backend](SQL-BACKEND.md)). Consumer sehen in beiden Fällen dieselben Exporte, Anfragen, Ergebnisse und Fehlercodes; es ist also eine
Betriebsentscheidung, keine Code-Entscheidung. Diese Seite hilft bei der Wahl.

## Schnellentscheidung

| Deine Situation | Verwende | Warum |
|---|---|---|
| Ein Gameserver, möglichst wenig Aufwand | `sql` + SQLite | Kein zusätzlicher Dienst, kein Key, keine Netzwerkfreigabe; die Datenbank ist eine Datei unter `data/persistent/<bundle>/` |
| Ein Gameserver, aber ein echter Datenbankserver, Backups, andere Werkzeuge sollen die Daten lesen | `sql` + PostgreSQL | Gleicher Codepfad, die Daten liegen aber in PostgreSQL |
| Mehrere Gameserver teilen Daten (Wirtschaft, Charaktere, Banns) | `http` (API vor einer Datenbank) oder `sql` + eine gemeinsame PostgreSQL | Die API liefert Keys je Server und Namespaces; mit `sql` braucht jeder Server Datenbank-Zugangsdaten |
| Du nutzt MySQL, MariaDB oder MongoDB | `http` | `re.sql` unterstützt nur PostgreSQL und SQLite |
| Viele kleine Schreibvorgänge pro Tick, die gebündelt werden sollen | `http` mit Write-behind | Write-behind gibt es nur in der API |
| Ein Effekt muss genau einmal passieren (Kauf, Auszahlung, Bestandsänderung) | beide, mit `mutation.execute` | Beide Engines speichern den Beleg in derselben Transaktion wie die Änderung |
| Lokale Entwicklung, CI, Testserver | `sql` + SQLite mit `destructiveMode: "apply"` | Schnell aufgesetzt und weggeworfen |
| Der Gameserver-Host soll keine Datenbank-Zugangsdaten halten | `http` | Das Bundle hält nur einen API-Key, begrenzt auf seine Namespaces und die Adresse des Servers |
| Wechsel zwischen beiden auf derselben PostgreSQL-Datenbank | beide, nie gleichzeitig | Schema-Hash und Receipt-Fingerprint sind identisch; nie beide gleichzeitig auf dieselben Namespaces richten |

## Die Backends im Vergleich

| | `http` + lt-database-api | `sql` (`re.sql`) |
|---|---|---|
| Beteiligte Teile | Gameserver, API-Dienst, Datenbank | Gameserver, Datenbank (SQLite: nur der Gameserver) |
| Datenbanken | PostgreSQL, MySQL/MariaDB, MongoDB | PostgreSQL, SQLite |
| Wo Geheimnisse liegen | Key-Secret im `vfs/` des Bundles, Datenbank-Zugangsdaten nur bei der API | Datenbank-Zugangsdaten in der `config.toml` des Bundles (`${VAR}` aus der Umgebung); der Bundle-Code sieht sie nie |
| Schutz auf dem Weg | HMAC-signierte Anfragen und Antworten, Replay-Schutz, Ratenlimit je Key | bei SQLite nicht nötig; bei PostgreSQL die Verbindung selbst schützen (TLS in `conninfo`) |
| Zugriffskontrolle | Rechte und Namespaces je Key an der API, plus `allowedNamespaces` im Bundle | `allowedNamespaces` plus die Rechte des Datenbankkontos hinter dem Alias |
| Write-behind | optional | nicht verfügbar, jeder Schreibvorgang ist sofort |
| Parallelität | bis zu `maxConcurrent` Aufrufe gleichzeitig | ein Aufruf nach dem anderen pro Bundle, siehe [Gleichzeitigkeit](SQL-BACKEND.md#gleichzeitigkeit) |
| Latenz | ein HTTPS-Roundtrip plus Datenbankzeit | nur Datenbankzeit |
| Exactly-once-Belege | relationale Engines der API (nicht MongoDB) | PostgreSQL, SQLite |

## Anwendungsfälle im Detail

### 1. Ein Server mit minimalem Aufwand: SQLite

`vfs/database.json`:

```json
{ "backend": "sql", "sqlAlias": "game", "destructiveMode": "quarantine", "allowedNamespaces": ["mygame"] }
```

`config.toml` des Bundles:

```toml
[Database.game]
type = "sqlite"
name = "game.db"
```

Geeignet für: Roleplay- oder Minigame-Server mit einigen hundert Spielern, Einstellungen, Statistiken, kleine Inventare.
Vorteile: nichts weiter zu installieren, Backup durch Kopieren der Datei, kein Netzwerk. Nachteile: SQLite hat einen einzigen Schreiber (ein
zweiter Schreiber kann mit `conflict_retry` beantwortet werden, dann erneut versuchen); nur dieser Server kann die Datei nutzen; kein
Werkzeug außerhalb des Hosts liest sie bequem. Sobald echte Daten existieren, `destructiveMode` auf `quarantine` oder `deny` lassen.

### 2. Ein Server auf PostgreSQL

```toml
[Database.game]
type = "postgres"
conninfo = "host=${DB_HOST} port=5432 dbname=game user=ugc password=${DB_PASSWORD}"
```

Ein eigenes Datenbankkonto anlegen. Es braucht einmalig `CREATE` (Verwaltungstabellen) und DDL-Rechte in seinem Schema, wenn `schema.sync` genutzt wird.
Geeignet für: Server, auf denen PostgreSQL ohnehin läuft, Daten, die andere Werkzeuge (Dashboards, Web-Panels, Backups) lesen sollen, einen späteren
Umstieg auf mehrere Server. `sslmode=require` in `conninfo` ergänzen, wenn die Datenbank nicht auf derselben Maschine liegt.

### 3. Mehrere Gameserver teilen Daten

Bevorzugt: lt-database-api einmal vor der Datenbank betreiben und jedem Gameserver einen eigenen Key geben, begrenzt auf die Namespaces und die
Adresse, die dieser Server braucht (`"backend": "http"`). Ein kompromittierter Server kann dann nur seine eigenen Namespaces anfassen, und ein
einzelner Key lässt sich rotieren oder sperren.

Möglich: den `sql`-Alias jedes Servers auf dieselbe PostgreSQL-Datenbank richten. Die Datenbank vermittelt zwischen den Servern (Advisory-Lock für
`schema.sync`, die eindeutige Beleg-Reservierung für `mutation.execute`), aber jeder Server hält Datenbank-Zugangsdaten, und es gibt keine
Rechteebene je Server. Das nur zwischen gleich vertrauenswürdigen Servern nutzen und `schema.sync` mit `destructiveMode` über `deny` von genau
einem Server (oder einem Deploy-Schritt) ausführen lassen.

### 4. MySQL, MariaDB oder MongoDB

Beim Backend `http` bleiben. Die API übersetzt dasselbe Schema- und Abfrageformat für diese Engines. Atomare Mutation-Receipts gibt es für
MongoDB nicht.

### 5. Schübe kleiner Schreibvorgänge

Eine Tick-Schleife, die viele winzige Zeilen schreibt (Positionen, Zähler), passt zu keinem Backend gut: Jeder Aufruf ist ein Datenbank-Roundtrip,
und mit `sql` reihen sich die Aufrufe hintereinander ein. Optionen, beste zuerst: den Zustand im Speicher halten und bei Ereignissen oder in
Intervallen schreiben; Zeilen in einem `insert` bündeln (bis 1000 Zeilen); das Backend `http` mit Write-behind nutzen, damit die API die Schreibvorgänge
journalisiert und später anwendet (`durability` je Aufruf, `immediate: true`, wenn die Antwort ein echtes Ergebnis sein muss).

### 6. Exactly-once-Effekte: Mutation-Receipts

Wenn eine Wiederholung nach verlorener Antwort einen Effekt nicht doppelt anwenden darf (Shop-Kauf, Auszahlung), `mutation.execute` mit einer
stabilen `effectId` nutzen. Die Änderung und ihr dauerhafter Beleg werden in einer Transaktion bestätigt; ein wiederholter Aufruf liefert den
gespeicherten Beleg, und eine verlorene Commit-Antwort klärt `mutation.receipt`. Der Befehl darf **höchstens eine Zeile** betreffen. Der
Recovery-Code von lt-core verlässt sich auf diesen Vertrag. `idempotencyKey` eignet sich für gewöhnliche Schreibvorgänge, bei denen der Verlust des
Caches bei einem Neustart akzeptabel ist (er liegt zehn Minuten im Speicher).

### 7. Entwicklung, Tests und CI

`sql` + SQLite mit `"destructiveMode": "apply"` liefert in Sekunden eine Wegwerf-Datenbank; zum Zurücksetzen die Datei löschen. Die Smoke-Bundles
([`examples/smoke`](../examples/smoke/README.md)) vor dem Livegang gegen die Ziel-Engine ausführen: `db-smoke` für die Operationen und
`db-smoke-mutation` für Belege.

### 8. Später wechseln

Weil Schema-Hash und Receipt-Fingerprint byte-identisch sind, kann eine über die API angelegte PostgreSQL-Datenbank vom Backend `sql` übernommen
werden und zurück. Zuerst die andere Seite stoppen, `backend` in `database.json` ändern, `lt-db-reload` ausführen, `lt-db-status` prüfen und die
Consumer-Bundles neu starten.

## Einstellungen und ihre Wirkung

| Einstellung (`vfs/database.json`) | Werte | Wirkung und wann ändern |
|---|---|---|
| `backend` | `http`, `sql` | Wählt den Weg. Ohne die Angabe bleibt es `http`. Eine ungültige Kombination beantwortet jeden Aufruf mit `not_configured` und fällt nie auf ein anderes Backend zurück. |
| `sqlAlias` | Name aus `config.toml` | Welchen `[Database.<alias>]`-Eintrag der Connector nutzt. Ein Alias pro Bundle-Installation. |
| `sqlDialect` | `auto`, `postgres`, `sqlite` | `auto` fragt die Engine beim ersten Aufruf. Explizit setzen, wenn der erste Aufruf ohne Erkennung auskommen soll oder ein Proxy die Engine verbirgt. |
| `destructiveMode` | `deny`, `quarantine`, `apply` | Was `schema.sync` mit Tabellen und Spalten tut, die du aus der Deklaration entfernt hast. `deny` (Standard): ablehnen und den Plan zeigen, die sichere Wahl für Produktion. `quarantine`: in `_dropped_<Zeit>_<Name>` umbenennen, damit Daten wiederherstellbar bleiben; gut, solange sich das Schema noch bewegt. `apply`: wirklich löschen, für Tests und Wegwerf-Datenbanken. |
| `allowedNamespaces` | Liste oder `"*"` | Welche Namespaces der Connector sendet. Jede Consumer-Familie bekommt einen eigenen Namespace, nur diese eintragen; `"*"` ist für die Entwicklung. |
| `timeoutMs` | 1000 bis 120000 | `http`: Zeit, die eine Anfrage dauern darf. `sql`: SQL-Befehlszeitlimit, auf ganze Sekunden aufgerundet, bei 30 gedeckelt. Für große `schema.sync`-Neuaufbauten erhöhen, zum schnellen Scheitern senken. |
| `maxConcurrent` | 1 bis 64 | `http`: gleichzeitige Aufrufe (erhöhen bei vielen unabhängigen Aufrufern und schneller API). `sql`: keine Wirkung über 1, Aufrufe laufen nacheinander. |
| `url`, `keyId`, `secretFile`, `allowInsecureHttp` | | Nur `http`; mit `sql` ignoriert. Reines `http://` zu einem entfernten Host nur in einem Netz, dem du voll vertraust. |

Je Aufruf, unabhängig vom Backend:

| Option | Wirkung |
|---|---|
| `idempotencyKey` | Derselbe Key mit gleicher Nutzlast liefert das erste Ergebnis (10 Minuten, im Speicher); andere Nutzlast ergibt `422 idempotency_conflict`. |
| `dryRun` (`schema.sync`) | Zeigt den Plan, ohne ihn anzuwenden. Vor jedem Produktions-Deployment ausführen. |
| `durability` / `immediate` | Nur Write-behind (`http`). Mit `sql` ignoriert, dort ist jeder Schreibvorgang sofort. |
| `limit`, `offset`, `fields`, `sort` | `limit` klein halten und auf indizierte Spalten filtern; mit `sql` verzögert eine langsame Abfrage die dahinter wartenden Aufrufe. |

## Häufige Fehler

* Das Backend `sql` und eine API gleichzeitig auf dieselbe Datenbank und dieselben Namespaces richten: Sie teilen die Verwaltungstabellen.
* `destructiveMode` nach der Entwicklung auf `apply` lassen.
* Write-behind oder parallele Aufrufe mit `sql` erwarten.
* Einen einzigen Namespace (oder `"*"`) für alles verwenden: Die Trennung zwischen Bundles geht verloren.
* `idempotencyKey` für dauerhaft halten. Nach einem Neustart ist der Cache weg; wo es zählt, Mutation-Receipts nutzen.
* Datenbank-Passwörter in `database.json` oder ins Repository schreiben: `${VAR}` in `conninfo` und die Umgebung des Servers verwenden.
