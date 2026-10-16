# Begriffe und Abkürzungen

Code und Konfiguration behalten ihre englischen Namen, damit sie genau zur Software passen.

| Begriff | Bedeutung |
| --- | --- |
| BlackICE / REServer | Die Spielserver-Software, auf der deine Server-Bundles laufen. |
| Ressource | Ein eigenständig installierbares Werkzeug, Bundle oder ein Dienst dieser Bibliothek. |
| Bundle / UGC | Spielerweiterung; UGC bedeutet „User-Generated Content“. Ein Bundle kann Server-, Client- und gemeinsame Teile enthalten. |
| Consumer | Dein eigenes Bundle, das exportierte Funktionen eines anderen Bundles aufruft. |
| Server / Client realm | Code auf dem Spielserver / auf dem Computer des Spielers. Datenbank-Secrets gehören ausschließlich auf den Server. |
| API / HTTP / Endpoint | Programmierschnittstelle / Netzwerkprotokoll / Kombination aus HTTP-Methode und Pfad, z. B. `POST /v1/data/find`. |
| JSON | Textformat für Objekte, Listen und Werte in Konfigurationen und Nachrichten. |
| Namespace (`ns`) | Benannte Gruppe von Tabellen; Connector und API-Key müssen sie beide erlauben. |
| Schema / Tabelle / Zeile / Spalte | Datenstruktur / Sammlung von Datensätzen / einzelner Datensatz / benannter Wert eines Datensatzes. |
| Primary key | Primärschlüssel: Spalte(n), die einen Datensatz eindeutig identifizieren. |
| Index / unique | Suchindex / Eindeutigkeitsregel, die doppelte Werte verhindert. |
| Nullable / null | Erlaubt einen fehlenden Wert / die Darstellung dieses fehlenden Werts. |
| CRUD | Create, Read, Update, Delete: Anlegen, Lesen, Ändern und Löschen. |
| Upsert | Datensatz anlegen, falls der eindeutige Schlüssel fehlt; sonst diesen Datensatz ändern. |
| `Db` | Der C#-Helper `LtDatabaseClient.Db`, der Connector-Anfragen ausführt. |
| `S` / `F` / `Q` | Schema-Builder / Filter-Builder / Builder für Zeilen und Sortierungen. In der Nutzungsanleitung heißen die lesbaren Aliase `Schema`, `Filters` und `Query`. |
| `Eq` / `Ne` | Equal / Not equal: gleich / ungleich. |
| `Gt` / `Gte` | Greater than / greater than or equal: größer als / größer oder gleich. |
| `Lt` / `Lte` | Less than / less than or equal: kleiner als / kleiner oder gleich. |
| `inc` / `incJson` | Increment: eine Zahl zum vorhandenen Wert addieren; `-5` zieht fünf ab. |
| `set` / `setJson` | Vorhandenen Wert durch den angegebenen Wert ersetzen. |
| Callback / asynchron | Eine Funktion erhält das Ergebnis, sobald es vorliegt; der ursprüngliche Aufruf wartet nicht auf die Datenbank. |
| Ticket | Kennung eines angenommenen Auftrags; noch kein fertiges Datenbankergebnis. |
| Idempotent | Wiederholungen haben denselben Effekt wie eine einmalige Ausführung. Fest auf 40 setzen kann idempotent sein; 1 addieren ist es nicht. |
| Idempotency key | Kennung einer Operation, mit der Wiederholungen innerhalb des Zeitfensters dasselbe Ergebnis erhalten. |
| Write-behind / queued | Optionale Schreibpufferung / angenommen, aber noch nicht in der Datenbank angewendet. |
| Flush | Wartende Änderungen jetzt anwenden; Bericht auf Restmenge, Fehler und angehaltene Verarbeitung prüfen. |
| Journal / dead letter | Dauerhafte Warteschlangendatei / nicht anwendbare Änderung zur Fehleranalyse. |
| Live / immediate | Änderung wird vor der Ergebnisantwort in der Datenbank ausgeführt. |
| DDL / DML | Data Definition Language für Schemaänderungen / Data Manipulation Language für Datenzugriffe. Getrennte Datenbankkonten können Rechte begrenzen. |
| HMAC / SHA-256 | Schlüsselbasierte Nachrichtenauthentifizierung / verwendeter Hash-Algorithmus. |
| TLS / HTTPS | Verschlüsselte, authentifizierte Verbindung / HTTP über TLS. |
| Key ID / secret | Öffentliche Kennung des Signierschlüssels / geheimer Zufallswert. Die ID ist kein Passwort. |
| Nonce / UTC | Einmaliger Zufallswert einer Anfrage / koordinierte Weltzeit für Zeitstempel. |
| VFS | Virtuelles Dateisystem; privater Konfigurationsordner eines Bundles. |
| WASM / WASI | WebAssembly-Dateiformat / Systemschnittstelle für den kompilierten Servercode. |
| SDK / .NET | Software Development Kit / Laufzeit und Build-Werkzeuge der C#-Projekte. |
| CI | Continuous Integration: automatische Prüfungen durch GitHub Actions. |
| Supervisor / Webhost | Prozesssteuerung des Panels / Komponente für die Browseroberfläche. |
| Reverse Proxy | Vorgeschalteter Server, der HTTPS bereitstellen und Anfragen weiterleiten kann. |
| CIDR / ACL | Schreibweise für Netzwerkbereiche / Dateizugriffsrechte des Betriebssystems. |
| CSRF / SSE | Cross-Site Request Forgery / Server-Sent Events für Live-Aktualisierungen. |

Weiter mit den [ersten Schritten](getting-started.md) oder der [C#-Nutzungsanleitung](lt-database/docs/USAGE.md).
