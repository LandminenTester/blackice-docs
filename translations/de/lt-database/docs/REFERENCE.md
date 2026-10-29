# C#-Referenz: Exporte und Builder

Diese Referenz verwendet die tatsächlichen Klassen- und Methodennamen. Den leichter lesbaren Einstieg mit Aliasen findest du unter [Nutzung](USAGE.md), ein vollständiges Programm unter [Praxisbeispiel](EXAMPLES.md).

## Exporte

| Export | Eingabe | Ergebnis |
| --- | --- | --- |
| `Call` | `DbCall(string Operation, string Json)` | `DbTicket(string Id, bool Accepted, string Error)` |
| `TakeResult` | `DbResultQuery(string Id)` | `DbResult(string Id, string State, int Status, string Code, string Json)` |

Die MessagePack-Typen liegen in `sh/Contracts.cs`. Die Exporte laufen synchron; die eigentliche Anfrage läuft im Hintergrund. Der Helper `LtDatabaseClient.Db` erledigt Ticket und Ergebnisabholung. `Accepted == false` lehnt die Anfrage sofort ab. `TakeResult` liefert `pending`, bis das Ergebnis verfügbar ist, und gibt es nur einmal aus. Unbekannte oder bereits abgeholte Tickets liefern `missing`. Nicht abgeholte Ergebnisse werden nach ungefähr zwei Minuten plus viermal Timeout verworfen.

## Helper Db

`import/LtDatabase.Server.cs` in das Server-Projekt einbinden. Methoden liefern ein `DbTicket` und rufen `done` einmal auf; eine unmittelbare Ablehnung kann den Callback sofort ausführen.

| Methode | Aufgabe |
| --- | --- |
| `Call(operation, json, done)` | Beliebige unterstützte Operation mit rohem JSON |
| `Sync(ns, schemaJson, done, dryRun = false)` | Schema deklarieren; optional nur planen |
| `Describe(ns, done)` | Gespeichertes Schema lesen |
| `Insert(ns, table, rowJson, done, immediate = false)` | Zeile anlegen; alternativ `rowsJson[]` |
| `Find(ns, table, done, filterJson, fields, sortJson, limit, offset)` | Zeilen suchen und seitenweise lesen |
| `Count(ns, table, done, filterJson)` | Treffer zählen |
| `Update(ns, table, filterJson, done, setJson, incJson, immediate = false)` | Gefilterte Zeilen ändern |
| `Upsert(ns, table, rowJson, keys, done, immediate = false)` | Über eindeutigen Schlüssel anlegen oder ändern |
| `Delete(ns, table, filterJson, done, immediate = false)` | Gefilterte Zeilen löschen |
| `Flush(ns, done)` | Wartende Änderungen jetzt anwenden |
| `Health(done)` | Signierte Dienst- und Datenbankprüfung |
| `Rows(result)` | Zeilen eines erfolgreichen Find-Ergebnisses |
| `HasMore(result)` | Weitere Seiten vorhanden? |
| `Number(result)` | Anzahl Treffer beziehungsweise betroffener Zeilen |
| `InsertedIds(result)` | Generierte Insert-Schlüssel |
| `IsQueued(result)` | Änderung bisher nur in die Warteschlange aufgenommen? |
| `ErrorMessage(result)` | Lesbare Fehlermeldung |
| `Bundle` | Connector-Ordnername; Standard `lt_database` |

Fehlt das laufende Connector-Bundle, liefert der Helper `bundle_unavailable`. Vor `Rows` oder `Number` immer den Status prüfen; leere Ergebniswerte können sonst Fehler verbergen.

## Builder

Alle Builder erzeugen JSON-Text und maskieren Werte.

| Klasse | Methoden und Bedeutung |
| --- | --- |
| `F` | Filter: `Eq Ne Gt Gte Lt Lte In NotIn IsNull StartsWith Contains And Or Not` |
| `Q` | `Row(("column", value), ...)` für Zeilen, `set` und `inc`; `Sort(("column", descending), ...)`; `Immediate(payloadJson)` |
| `S` | `Schema(tables...)`, `Table(name, primaryKey[], columns[], indexes[]?, renamedFrom?)`, `Index(name, unique, columns...)` |
| Spaltentypen in `S` | `Int32 Int64 Text LongText Bool Decimal Double Json DateTime Date Uuid Bytes` |
| `S.Column` | Alle Optionen: `name, type, length, precision, scale, nullable, unique, autoIncrement, @default, renamedFrom` |
| `JsonText` | JSON schreiben: `Quote Value Object Array Raw` |
| `MiniJson` | JSON lesen: `Parse TryParse AsObject GetString GetLong GetBool` |
| `Sha256`, `Wire`, `Ids.Next()` | Hash/HMAC, Signaturumschläge, neue Kennungen |

`MiniJson` verwendet Dictionaries, Listen, `long` oder `double`, Boolesche Werte und null. `Eq` bedeutet gleich; `Gte` größer oder gleich; weitere Kurzformen erklärt das [Verzeichnis](../../glossary.md).

## Operationen und Wiederholung

`health`, `schema.sync`, `schema.describe`, `find`, `count`, `delete`, `flush`, `insert`, `upsert`, `update`, `mutation.execute`, `mutation.receipt`. `delete` und `mutation.execute` werden nie automatisch wiederholt (`mutation.execute` wird über `mutation.receipt` wiederhergestellt). Außer Health benötigt jede Nutzlast einen erlaubten `namespace`.

Mit dem Backend `sql` laufen dieselben Operationen über `re.sql` und der Connector wiederholt nichts; die wenigen Unterschiede (kein Write-behind, keine Signatur, Destruktiv-Modus, Datenbanken) stehen im [SQL-Backend](SQL-BACKEND.md). Nur beim Backend `http` wiederholt der Connector Transportfehler und unsignierte 502/503/504-Antworten maximal dreimal mit 300 und 600 ms Abstand. Bei 401 erfolgt einmal Zeitsynchronisierung und ein weiterer Versuch. Authentische signierte API-Fehler werden nicht automatisch wiederholt. Insert, Upsert und Update benötigen für Transportwiederholungen einen `idempotencyKey`; der Helper ergänzt ihn bei Insert und Upsert.

Grenzen: Nutzlast maximal 1.000.000 Zeichen, bis zu 512 wartende Aufträge, Parallelität gemäß `maxConcurrent` beim Backend `http`; das Backend `sql` führt einen Aufruf nach dem anderen aus (siehe [Gleichzeitigkeit](SQL-BACKEND.md#gleichzeitigkeit)). Fünf Transportfehler hintereinander öffnen den Schutzschalter für 15 Sekunden.

## Zustände und Diagnose

`ok` bedeutet erfolgreich, bei Write-behind möglicherweise nur angenommen. `error` ist ein Fehler, `pending` noch nicht fertig, `missing` unbekannt oder schon abgeholt. Fehlercode, HTTP-Status und Nachricht zusammen auswerten.

Connector-Fehler: `not_configured`, `unknown_operation`, `invalid_request`, `invalid_identifier`, `namespace_not_allowed`, `payload_too_large`, `busy`, `unavailable`, `network`, `unauthorized`, `rate_limited`, `bad_signature`, `bad_response`, `internal`, `bundle_unavailable`. Die [Betriebsanleitung](OPERATIONS.md) nennt Maßnahmen. Datenbank- und Schemafehler kommen signiert aus der [HTTP-API](../../lt-database-api/docs/API.md).

| Befehl | Aufgabe |
| --- | --- |
| `lt-db-status` | Backend (`http` oder `sql`), Ziel (URL und Key-ID, oder Alias, Dialekt und Destruktiv-Modus), Namespaces, Warteschlange, aktive Anfragen und Zeitversatz; nie das Secret |
| `lt-db-health` | Signierter Verbindungstest bis zur Datenbank |
| `lt-db-reload` | Private Dateien neu laden, Schutzschalter zurücksetzen und Zeit abgleichen |

Der Connector nutzt signierte HTTP-Umschläge mit HMAC-SHA256 und prüft jede Antwort. Das exakte Protokoll und Testvektoren stehen unter [Signaturen](../../lt-database-api/docs/SECURITY.md).
