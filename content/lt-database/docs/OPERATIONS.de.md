# Betrieb und Fehlerbehebung

## Normaler Start

API und Datenbank müssen erreichbar sein. In `cfg/server.cfg` zuerst `start lt_database`, danach die Consumer starten. Beim Start deklarieren Consumer ihre Schemas und warten auf Erfolg, bevor sie Datenzugriffe ausführen.

| Befehl | Verwendung |
| --- | --- |
| `lt-db-status` | Konfiguration und aktuellen Connector-Zustand prüfen |
| `lt-db-health` | Signierte Verbindung bis zur Datenbank testen |
| `lt-db-reload` | JSON und Secret ohne Bundle-Neustart neu laden |
| `restart lt_database` | Nach einer Manifest- oder WASM-Änderung neu starten |

Zwischen den Backends `http` und `sql` wechseln: `backend` (und die zugehörigen Felder) in `database.json` ändern, `lt-db-reload` ausführen, `lt-db-status` prüfen und die Bundles neu starten, die Schemas deklariert haben ([SQL-Backend](SQL-BACKEND.md)).

## Fehler systematisch eingrenzen

| Code oder Symptom | Prüfen und beheben |
| --- | --- |
| `not_configured` | JSON-Syntax, VFS-Freigabe, Secret-Datei und Dateirechte prüfen; Status zeigt Details. |
| `bundle_unavailable` | Connector läuft und heißt `lt_database`? Consumer-Startreihenfolge prüfen. |
| `namespace_not_allowed` | Namen in beiden Freigabelisten ergänzen; JSON neu laden. |
| `network` | API läuft? URL, Port, Firewall und `Networking.allowed` prüfen. Loopback gilt für den aufrufenden Rechner/Container. |
| `unauthorized` | Key-ID, identisches Secret, erlaubte Quelladresse und Systemuhr prüfen. |
| `bad_signature` | Secret, Proxyverhalten und Antwort prüfen; unsichere Antwort nicht verwenden. |
| `unknown_table` / `namespace_unknown` | Schema an dieser API zuerst erfolgreich synchronisieren. |
| `constraint_violation` | Eindeutige Schlüssel und Pflichtwerte prüfen; Anfrage nicht blind wiederholen. |
| `busy` / `rate_limited` | Last reduzieren, zeitversetzt versuchen und API-Limits prüfen. |
| `database_error` / `database_timeout` (Backend `sql`) | Alias fehlt oder ist falsch in der `config.toml`, die Datenbank ist nicht erreichbar oder dem Konto fehlen Rechte (einmalig `CREATE`, für den Schema-Sync DDL-Rechte). `lt-db-health`, das Serverlog (Operation, Ausnahmetyp, zugeordneter Code) und das [SQL-Backend](SQL-BACKEND.md) prüfen. |
| `conflict_retry` (Backend `sql`, SQLite) | Ein anderer Schreiber hält die einzige Schreibsperre von SQLite; den Aufruf wiederholen. |
| `unavailable` | Schutzschalter nach Transportfehlern; Ursache beheben, automatische Erholung oder Reload abwarten. |
| `write_buffer_full` | Warteschlange und Datenbank prüfen, Flush überwachen. Neue Änderung wurde nicht angenommen. |
| `write_buffer_unavailable` | Journal-Pfad, Schreibrechte und freien Speicher prüfen. |
| `write_buffer_halted` | Ältere Änderungen konnten nicht angewendet werden; Fehler im Flush-Bericht beheben. |

Ein erfolgreicher öffentlicher GET-Health-Test prüft nicht alles. `lt-db-health` prüft Signatur und Datenbank. Keine Secrets in öffentliche Logs oder Fehlermeldungen kopieren.

## Updates und Schlüsselwechsel

Vor Updates Testumgebung und [Funktionstest](../examples/smoke/README.md) verwenden. Server beziehungsweise betroffene Bundles geordnet stoppen, Laufzeitdateien aktualisieren und private VFS-Dateien behalten. Helper und gemeinsame Typen im Consumer zusammen aktualisieren und neu bauen. Nach dem Start Health und typische Datenzugriffe prüfen.

Bei Schlüsselrotation die API für alten und neuen Schlüssel vorbereiten, neues Secret im Connector installieren, `lt-db-reload` ausführen und signiert testen. Erst danach den alten Schlüssel aus der API entfernen. Das genaue `Current`-/`Next`-Verfahren steht in der [API-Sicherheit](../../lt-database-api/docs/SECURITY.md).

## Backups und Migration

Die Daten liegen in der Datenbank. VFS-Konfiguration und Secrets geschützt sichern, Datenbank-Backups sowie gegebenenfalls Write-behind-Journal und Dead-Letter-Datei sichern. Wiederherstellung regelmäßig testen. Ein Schema-Quellcode ersetzt kein Datenbackup.

Vor Migrationen Schreibzugriffe anhalten und Warteschlangen leeren; `remaining: 0`, kein `halted` und keine ungeklärten Dead Letters abwarten. Erst dann Daten übertragen und API-Adresse beziehungsweise Datenbank wechseln. Consumer-Schemas an der neuen API erneut deklarieren.

## Last und Konsistenz

Maximal 512 wartende Connector-Aufträge; `maxConcurrent` begrenzt aktive HTTP-Anfragen. Abfragen mit `limit`, geeigneten Indizes und stabiler Sortierung begrenzen. Keine blockierenden Warteschleifen im Spieltick verwenden. Bei Queue-Modus zwischen angenommenen und tatsächlich angewendeten Änderungen unterscheiden.
