# Portables Schema und Synchronisierung

Ein Namespace besitzt seine vollständige Tabellenstruktur. Der Aufrufer deklariert den gewünschten Zustand, die API berechnet und speichert die Differenz. Eine unveränderte Deklaration ohne Reparaturbedarf ergibt `unchanged`. **Was du nicht mehr deklarierst, kann entfernt werden.** Pro Namespace deshalb einen klar verantwortlichen Besitzer verwenden.

## Namen und Speicherung

Muster `^[a-z][a-z0-9]*(_[a-z0-9]+)*$`; Namespace maximal 24, Tabelle 36, Spalte und Index 48 Zeichen. Physische Namen sind `{namespace}__{table}`. Interne Tabellen `_ldb_schema`, `_ldb_locks` und `_ldb_counters` sind reserviert.

## Spaltentypen

| Typ | Optionen | PostgreSQL | MySQL | MongoDB |
| --- | --- | --- | --- | --- |
| `int32` | Ganzzahl | INTEGER | INT | int/long |
| `int64` | Große Ganzzahl | BIGINT | BIGINT | long/int |
| `decimal` | Precision 1–38, Standard 18; Scale 0–Precision, Standard 0 | NUMERIC(p,s) | DECIMAL(p,s) | decimal128 |
| `float64` | Fließkomma | DOUBLE PRECISION | DOUBLE | double |
| `bool` | Wahr/falsch | BOOLEAN | TINYINT(1) | bool |
| `string` | Länge 1–4000, Standard 255 | VARCHAR(n) | VARCHAR(n) | string mit Längengrenze |
| `text` | Langer Text | TEXT | LONGTEXT | string |
| `json` | JSON-Wert | JSONB | JSON | Dokument/Liste/Wert |
| `datetime` | UTC | TIMESTAMPTZ | DATETIME(6) | date |
| `date` | Datum | DATE | DATE | Mitternacht UTC |
| `uuid` | GUID | UUID | CHAR(36) | string |
| `bytes` | Optionale Länge 1–65535 | BYTEA | VARBINARY/LONGBLOB | binData |

Weitere Optionen: `nullable` standardmäßig false, `default`, `unique`, `autoIncrement`, `renamedFrom`. Auto-Increment nur für int32/int64 und als einzige Primärschlüsselspalte. Defaults passen zum Typ; datetime erlaubt zusätzlich `"now"`.

Ein Index hat `name`, `columns`, `unique`. JSON, langer Text und unbeschränkte Bytes sind nicht indexierbar; indexierte Strings höchstens 255 Zeichen. MySQL verwendet `utf8mb4_bin`, daher sind Vergleiche wie bei den anderen Providern groß-/kleinschreibungssensitiv. MongoDB bildet einzelne Primärschlüssel auf `_id` ab, zusammengesetzte über einen eindeutigen Index.

## Ablauf

1. Deklaration prüfen, normalisieren und hashen.
2. Namespace sperren, damit Synchronisierungen nicht überlappen.
3. Vorigen Stand lesen und geordneten Änderungsplan erstellen.
4. Fehlende Tabellen, Spalten und Indizes reparieren; bereits erledigte Schritte überspringen.
5. Bei `dryRun: true` nur den Plan zurückgeben.
6. Sonst anwenden und neue Deklaration speichern.

## Umbenennen und Datenverlust steuern

Zum Umbenennen `renamedFrom` angeben, statt die alte Spalte einfach zu entfernen:

```json
{"name":"about","type":"text","nullable":true,"renamedFrom":"bio"}
```

Das gilt auch für Tabellen. Entfernen, Verkleinern, nicht rein erweiternde Typwechsel und nullable→NOT NULL gelten als destruktiv. `Schema:DestructiveMode` steuert sie:

| Modus | Verhalten |
| --- | --- |
| `Apply` | Standard: Plan anwenden |
| `Quarantine` | Entfernte Objekte nach `_dropped_<unixtime>_<name>` umbenennen; Spalten nullable machen |
| `Deny` | Destruktive Pläne mit `409 destructive_denied` verweigern |

Vor String-Verkürzung wird auf zu lange Daten geprüft (`data_does_not_fit`). Vor produktiven Änderungen Dry-Run und Backup verwenden.

## Grenzen und Provider-Unterschiede

Primärschlüsseländerung und Umschalten von Auto-Increment bestehender Spalten sind nicht unterstützt. Fremdschlüssel werden nicht definiert; Beziehungen im Programm abbilden. Manuelle Typabweichungen werden nicht vollständig erkannt; fehlende Objekte werden repariert.

PostgreSQL führt die Schemaänderung transaktional aus. MySQL/MariaDB committen DDL-Schritte einzeln; nach einem Fehler kann ein Teilzustand bleiben, den ein erneuter Sync vervollständigt. MongoDB hat ebenfalls keine DDL-Transaktion; Validatoren prüfen neue Schreibvorgänge, vorhandene Werte werden bei Typwechsel nicht automatisch konvertiert. Neue Spalten mit Default werden nachgefüllt.

Ein vollständiges Schema-Beispiel steht in der [HTTP-Referenz](API.md), C#-Builder in der [Bundle-Referenz](../../lt-database/docs/REFERENCE.md).
