# Laufzeit-Funktionstest

Das separate Smoke-Bundle registriert zwei Befehle:

* `db-smoke <label> [connector-bundle]` prüft 38 Schritte: Health, Schema und Migration, CRUD, Filter, Sortierung, Seiten, Constraints, Namespace-Isolation und Aufräumen.
* `db-smoke-mutation <label> [connector-bundle]` prüft 29 Schritte für atomare Mutation-Receipts (`mutation.execute`, `mutation.receipt`): Wiederholung, Beleg-Konflikte, Abfragen, `no_match`, `multiple_rows`, dauerhafte Fehlerbelege, abgelehnte Umschläge und zwei parallele Ausführungen.

Das optionale zweite Argument nennt das zu testende Connector-Bundle (Standard `lt_database`); so können eine `sql`- und eine `http`-Installation nebeneinander stehen. Enthält das Label `sql`, erwartet der Test das `sql`-Verhalten dort, wo es von der API abweicht (ein ungefilterter Delete wird mit `filter_required` abgelehnt; die API lehnt ihn ohne Key-Recht mit `forbidden` ab). Es prüft eine echte Installation; ein erfolgreicher C#-Build führt das Szenario nicht aus.

## Vorbereiten und bauen

Eine Entwicklungsdatenbank verwenden. Der Test entfernt und erstellt Tabellen in `smoke_test` neu; dort keine echten Daten speichern. `smoke_test` im Connector und im API-Key erlauben, `smoke_denied` im Connector weiterhin verbieten. Write-behind für `smoke_test` deaktivieren: Das Szenario erwartet Live-Ergebnisse mit IDs und Zeilenzahlen.

Im Quellcode-Ordner mit .NET 10:

```sh
dotnet build examples/smoke/sv/sv.csproj -c Release
```

`examples/smoke/sv/bin/Release/net10.0/wasi-wasm/native/sv.wasm` nach `<server>/data/ugc/db_smoke/` kopieren. Danach `examples/smoke/data/config.toml` **zuletzt** daneben kopieren. Nicht den Connector aus `dist/` als Smoke-Bundle verwenden. Bei einem abweichenden Connector-Ordner `Db.Bundle` vor dem Build in `sv/App.cs` einstellen.

## Ausführen

In der BlackICE-Serverkonsole:

```text
start lt_database
start db_smoke
db-smoke postgres
```

Erwartete letzte Zeile: `[db-smoke] RESULT postgres: 38/38 passed`. Für Receipts `db-smoke-mutation postgres` ausführen und `29/29 passed` erwarten. Effekt-IDs tragen ein Präfix pro Lauf, weil Belege dauerhaft sind.

Mit dem Backend `sql` (`"backend": "sql"` und ein `[Database.<alias>]`-Eintrag in der `config.toml` des Connectors) ein Label mit `sql` verwenden, zum Beispiel `db-smoke sql-sqlite lt_database_sqltest`. Beide Szenarien wurden so auf einem SQLite-Alias und auf PostgreSQL 17 ausgeführt. Das Label `postgres` ist nur eine Logbeschriftung und wählt keine Datenbank. Für andere Provider die API-URL des Connectors umstellen und `lt-db-reload` ausführen, dann mit passendem Label erneut testen.

Die erste FAIL-Zeile und die API-Logs lesen. Ein bestandener Live-Test bestätigt noch kein Write-behind-Verhalten; dafür gibt es die API-Integrationstests. Nach dem Test `db_smoke` stoppen und nicht mehr benötigte Testfreigaben entfernen. Keine echten VFS-Secrets veröffentlichen.

Für einen einfacheren Einstieg die [Preferences-Demo](../../docs/EXAMPLES.md) verwenden.
