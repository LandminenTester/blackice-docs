# Architektur und Entwicklung

## Anfrageweg

Die HTTP-Schicht liest den signierten Umschlag und prüft Größe, Signatur, Zeitstempel, Nonce und Key-Rechte. Anschließend validieren Schema-/Query-Komponenten Namen und Werte gegen das gespeicherte Schema. Der ausgewählte Provider führt die Datenbankoperation aus. Die Antwort wird für die ursprüngliche Nonce signiert.

```text
HTTP → Authentifizierung → Berechtigung → Validierung
     → Live-Ausführung oder Write-behind-Journal → Provider
     → signierte Antwort
```

Die Komponenten sind in `src/Ldb.Api` organisiert; Tests liegen in `tests/Ldb.Tests`. Die [Quellen](../../sources.md) nennen die dokumentierte Revision.

## Datenmodell und Provider

Namespaces besitzen Tabellen und einen gespeicherten deklarativen Schema-Stand. Physische Objekte sind durch `{namespace}__{table}` getrennt. PostgreSQL, MySQL/MariaDB und MongoDB setzen denselben portablen Vertrag um, haben aber unterschiedliche Transaktions- und Typgrenzen. Diese Unterschiede müssen sichtbar bleiben; siehe [Schema](SCHEMA.md) und [HTTP-API](API.md).

## Zustand

Die dauerhaften Nutzdaten und Schema-Metadaten liegen in der Datenbank. Nonce- und Idempotenz-Caches sind instanzlokal im Speicher. Bei aktivem Write-behind kommen Warteschlange, Journal und Dead Letters hinzu. Mehrere Instanzen teilen diese nicht automatisch.

## Nebenläufigkeit und Pufferung

Schema-Sync sperrt den Namespace. Mit aktiver Schreibpufferung werden Namespace-Anfragen serialisiert, damit keine Änderung zwischen dem Leeren und einer Schemaänderung überholt. Hintergrund-Flushes verwenden zusätzlich ihre Flush-Sperre. Ein angehaltenes notwendiges Flush blockiert unmittelbare Writes, Schemaänderungen und konsistente Reads.

MongoDB-Insert-Anfragen werden nicht zu einem gemeinsamen Batch vermischt, weil Teilfehler Wiederholungen bereits angewendeter Daten verursachen könnten. Die Crash-Zustellung bleibt mindestens einmal; Anwendungsdesign muss doppelte Ausführung berücksichtigen.

## Änderungen entwickeln

HTTP-Vertrag, OpenAPI, Client, Bundle-Helper und Dokumentation zusammen prüfen. Für neue Fehlerpfade, Reihenfolge, Journal-Wiederherstellung und Provider-Verhalten aussagekräftige Tests ergänzen. Ohne Docker übersprungene Integrationstests nicht als bestanden melden. [Build und Tests](BUILD.md) erklärt den Ablauf; [Sicherheit](SECURITY.md) die Vertrauensgrenzen.
