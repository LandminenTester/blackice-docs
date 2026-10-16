# HTTP-API-Referenz

## Zuerst verstehen: Nutzlast und Umschlag

Die folgenden Beispiele beschreiben die **Nutzlast** einer Operation. Für einen echten HTTP-Aufruf wird sie als JSON-String in einen signierten Umschlag eingebettet. Ein einfaches `curl` mit nur `namespace` und `table` genügt deshalb nicht. Für den Einstieg den [Referenzclient](BUNDLE-INTEGRATION.md) oder den Bundle-Helper verwenden. Das Signaturformat steht unter [Sicherheit](SECURITY.md).

JSON ist UTF-8 mit `camelCase`-Feldern. Unbekannte Nutzlastfelder werden ignoriert, falsche Typen abgelehnt. Außer Health benötigt jede Nutzlast einen `namespace`. Gültige Namen folgen `^[a-z][a-z0-9]*(_[a-z0-9]+)*$`; Namespace maximal 24, Tabelle 36, Spalte 48 Zeichen.

## Endpoints

| Methode und Pfad | Operation für `AllowedOperations` | Aufgabe |
| --- | --- | --- |
| `GET /v1/health` | öffentlich | Status und Unix-Zeit, kein Datenbanktest |
| `GET /healthz`, `GET /readyz` | öffentlich | Prozess- beziehungsweise Datenbankbereitschaft |
| `POST /v1/health` | `health` | Signierter Provider-/Datenbanktest |
| `POST /v1/schema/sync` | `schema.sync` | Vollständiges Schema deklarieren |
| `POST /v1/schema/describe` | `schema.describe` | Gespeichertes Schema lesen |
| `POST /v1/data/insert` | `insert` | Zeilen anlegen |
| `POST /v1/data/find` | `find` | Zeilen suchen |
| `POST /v1/data/update` | `update` | Zeilen ändern |
| `POST /v1/data/upsert` | `upsert` | Über eindeutigen Schlüssel anlegen/ändern |
| `POST /v1/data/delete` | `delete` | Zeilen löschen |
| `POST /v1/data/count` | `count` | Zeilen zählen |
| `POST /v1/data/flush` | `flush` | Wartende Änderungen anwenden |

## Durchgängiges Datenmodell

Das folgende Schema zuerst mit `schema.sync` deklarieren. Es entspricht einem einfachen Preferences-Beispiel:

```json
{
  "namespace": "documentation_demo",
  "dryRun": false,
  "schema": {
    "tables": [{
      "name": "preferences",
      "primaryKey": ["player_id"],
      "columns": [
        {"name": "player_id", "type": "string", "length": 64},
        {"name": "music_volume", "type": "int32"},
        {"name": "visits", "type": "int32"}
      ]
    }]
  }
}
```

Die Antwort nennt `namespace`, `hash`, `changed`, `dryRun`, `status` und `plan`. Status: `unchanged`, `planned`, `applied` oder bei verweigertem Dry-Run `denied`. Nicht mehr deklarierte Objekte können entfernt werden; [Schema-Regeln](SCHEMA.md) vorher lesen. `schema.describe` bekommt nur `namespace` und liefert `namespace`, `hash`, `schema`, `updatedAt`; vor dem ersten Sync ist `schema` null.

## Schreiben

Ein **Upsert** speichert eine Zeile anhand eines Primärschlüssels oder exakt passenden eindeutigen Indexes:

```json
{
  "namespace": "documentation_demo",
  "table": "preferences",
  "row": {"player_id": "sample_player", "music_volume": 25, "visits": 0},
  "keys": ["player_id"],
  "durability": "immediate",
  "idempotencyKey": "preferences-demo-save-001"
}
```

`insert` verwendet stattdessen `rows: [{...}]` und liefert `inserted` sowie `ids`. Fehlende Werte verwenden Default oder Auto-Increment; Pflichtwerte ohne Default führen zu `missing_value`. Maximal `MaxInsertRows`, standardmäßig 1000. SQL-Provider führen einen Insert-Request transaktional aus; MongoDB kann bei mehrzeiligen Inserts teilweise erfolgreich sein.

Ein **Update** wählt Zeilen mit `filter`, ersetzt Werte durch `set` und addiert Zahlen durch `inc`:

```json
{
  "namespace": "documentation_demo",
  "table": "preferences",
  "filter": {"field": "player_id", "op": "eq", "value": "sample_player"},
  "set": {"music_volume": 40},
  "inc": {"visits": 1},
  "durability": "immediate"
}
```

Update und Upsert liefern `affected`. Primärschlüssel sind nicht änderbar. `set` und/oder `inc` sind erforderlich. `inc` bedeutet Increment; wiederholtes `+1` zählt erneut.

`delete` benötigt `namespace`, `table` und `filter` und liefert `affected`. Ohne Filter sind Update/Delete verboten. `all: true` ersetzt den Filter nur mit `AllowUnfilteredWrites`-Berechtigung.

## Lesen und Zählen

```json
{
  "namespace": "documentation_demo",
  "table": "preferences",
  "filter": {"field": "visits", "op": "gte", "value": 1},
  "fields": ["player_id", "music_volume", "visits"],
  "sort": [{"field": "visits", "dir": "desc"}, {"field": "player_id", "dir": "asc"}],
  "limit": 50,
  "offset": 0
}
```

Find liefert `rows` und `hasMore`. `limit` ist durch `MaxRows` begrenzt, standardmäßig 1000. Ohne Sortierung wird nach Primärschlüssel sortiert. JSON-Spalten sind nicht sortierbar, unter MongoDB auch nicht filterbar. `count` verwendet `namespace`, `table`, optional `filter` und liefert `count`.

## Filter

Ein Vergleich hat `field`, `op`, `value`. Bedingungen lassen sich mit `{"and":[...]}`, `{"or":[...]}` und `{"not":...}` verbinden. Maximal 8 Ebenen und 128 Bedingungen.

| Operator | Bedeutung | Wert |
| --- | --- | --- |
| `eq`, `ne` | Gleich, ungleich | Einzelwert; `eq` mit null prüft fehlenden Wert |
| `gt`, `gte`, `lt`, `lte` | Größer, größer/gleich, kleiner, kleiner/gleich | Nicht-null Einzelwert |
| `in`, `nin` | In Liste, nicht in Liste | 1 bis 1000 Einzelwerte |
| `isNull` | Ist null; `false` bedeutet nicht null | Boolesch, Standard true |
| `startsWith`, `contains` | Textanfang, enthaltener Text | Nichtleerer Text; Groß-/Kleinschreibung relevant |

`ne` und Größenvergleiche treffen wie in SQL keine null-Werte. Text-Wildcards werden maskiert.

## Datentypen

Ganzzahlen und Fließkommazahlen als JSON-Zahl, Decimal als Zahl oder numerischer String, Bool als true/false, Text als String. JSON-Spalten nehmen beliebige JSON-Werte. Datum/Zeit als ISO-8601-UTC-String, Datum als `yyyy-MM-dd`, UUID als GUID-String und Bytes als Base64. Nullable-Spalten erlauben null. Weitere Grenzen stehen im [Schema](SCHEMA.md).

## Idempotenz und Schreibpufferung

Schreibvorgänge dürfen einen stabilen `idempotencyKey` tragen. Gleicher Key und identische Nutzlast geben für zehn Minuten das ursprüngliche Ergebnis zurück; abweichende Nutzlast führt zu `422 idempotency_conflict`. Für einen Retry einen neuen Umschlag mit neuer Nonce, aber identischer Nutzlast signieren.

Bei aktiviertem Write-behind kann die Antwort statt Zähler/IDs `{"queued":true,"id":"...","pending":12}` sein. `durability: "immediate"` fordert Live-Ausführung an. Flush mit `{"namespace":"documentation_demo"}` liefert `flushed`, `deadLettered`, `remaining`, `halted`, `enabled`. Auch bei HTTP 200 diesen Bericht prüfen. Details: [Write-behind](WRITE-BEHIND.md).

## Fehler

Erfolg: HTTP 200 und `ok: true` im Umschlag. Fehlernutzlast: `{"error":{"code":"...","message":"..."}}`.

| HTTP | Codes | Bedeutung |
| --- | --- | --- |
| 400 | `invalid_request`, `invalid_identifier`, `invalid_schema`, `invalid_filter`, `invalid_sort` | Aufbau oder Namen ungültig |
| 400 | `unknown_column`, `missing_value`, `invalid_value`, `value_too_long`, `filter_required` | Nutzdaten oder Filter korrigieren |
| 401 | `unauthorized` | Key, Signatur, Zeitstempel oder Nonce ungültig |
| 403 | `forbidden` | Namespace, Operation, Quelle oder unfiltrierte Änderung nicht erlaubt |
| 404 | `unknown_table`, `namespace_unknown` | Schema noch nicht vorhanden |
| 409 | `constraint_violation` | Eindeutigkeit oder andere Datenregel verletzt |
| 409 | `destructive_denied`, `data_does_not_fit`, `unsupported_change`, `sync_in_progress`, `conflict_retry` | Schemaänderung verweigert oder Konflikt |
| 413 | `payload_too_large`, `too_many_rows` | Größenlimit überschritten |
| 422 | `idempotency_conflict` | Gleicher Operationsschlüssel mit anderen Daten |
| 429 | `rate_limited` | Ratenlimit oder temporäre Sperre |
| 503 | `write_buffer_full`, `write_buffer_unavailable` | Änderung nicht angenommen |
| 503 | `write_buffer_halted` | Notwendiges Flush konnte ältere Änderungen nicht abschließen |
| 500/504 | `database_error`, `internal_error`, `database_timeout`, `timeout` | Details im Dienstlog prüfen |

Maschinenlesbare Referenz: [openapi.yaml](openapi.yaml). Mehrere HTTP-Aufrufe sind keine gemeinsame Transaktion.
