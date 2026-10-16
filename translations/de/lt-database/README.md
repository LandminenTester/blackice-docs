# lt_database

`lt_database` verbindet deine BlackICE-Server-Bundles mit der **lt-database-api**. Die API speichert Daten in PostgreSQL, MySQL/MariaDB oder MongoDB. Das Panel ist eine eigenständige Ressource und wird dafür nicht benötigt.

## Was du damit machen kannst

Tabellen deklarieren, Datensätze anlegen, suchen, zählen, ändern und löschen. Dein Bundle arbeitet mit einer gemeinsamen JSON-Schnittstelle, während die API die konkrete Datenbank anspricht. SQL und Zugangsdaten zur Datenbank gehören nicht in dein Spiel-Bundle.

```text
Eigenes Server-Bundle → lt_database → lt-database-api → Datenbank
```

## Der Einstieg

1. [Schnellstart](../database-quickstart.md): API und Connector gemeinsam ausprobieren.
2. [Installation](docs/INSTALL.md): Bundle-Ordner, Hostfreigabe und Secret einrichten.
3. [Konfiguration](docs/CONFIGURATION.md): alle Einstellungen und ihre Zuständigkeiten.
4. [Nutzung](docs/USAGE.md): Kurzbegriffe, Callbacks und Fehler verstehen.
5. [Praxisbeispiel](docs/EXAMPLES.md): einen Datensatz anlegen, ändern, lesen und entfernen.

Das Beispiel ist eine Datenbank-Demonstration, keine fertige Spielerfunktion. Die Anbindung an reale Spielerereignisse schreibst du in deinem eigenen Server-Bundle.

## Namen im Projekt

| Name | Bedeutung |
| --- | --- |
| GitHub-Repository `lt-database` | Quellcode und Downloads |
| Bundle-Ordner `lt_database` | Laufzeitname und Ziel der Export-Aufrufe |
| `LtDatabase` | Gemeinsame C#-Typen und JSON-Builder |
| `LtDatabaseClient.Db` | Helper zum Aufrufen des Connectors |
| `lt-db-status`, `lt-db-health`, `lt-db-reload` | Server-Konsolenbefehle |

## Live und gepuffert

Standardmäßig schreibt die API live. Optional nimmt sie Änderungen zuerst in ein Journal auf und wendet sie später an. Eine `queued`-Antwort ist dann noch kein Datenbankergebnis. Prüfe `Db.IsQueued`, verwende bei Bedarf `immediate: true` und lies die [Write-behind-Anleitung](../lt-database-api/docs/WRITE-BEHIND.md).

Weitere Details: [C#-Referenz](docs/REFERENCE.md), [Betrieb](docs/OPERATIONS.md), [Sicherheit](docs/SECURITY.md), [Build](docs/BUILD.md), [Laufzeit-Funktionstest](examples/smoke/README.md). Quellcode und Releases stehen im [Repository](https://github.com/LandminenTester/lt-database). Die ursprüngliche Lizenz und Hinweise gelten weiterhin.
