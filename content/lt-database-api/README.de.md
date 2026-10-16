# lt-database-api

Die API ist ein selbst gehosteter HTTP-Dienst vor PostgreSQL, MySQL/MariaDB oder MongoDB. Sie prüft signierte Anfragen, Berechtigungen und Datenstrukturen und führt danach Datenbankoperationen aus. Der BlackICE-Connector **lt_database** nutzt diese Schnittstelle. Andere Clients können das dokumentierte Signaturprotokoll ebenfalls implementieren. Das Server Panel ist eine separate Ressource.

## Schnell beginnen

Für den ersten Versuch den [gemeinsamen Schnellstart](../database-quickstart.md) verwenden. Er erklärt, welche Programme auf welchem Rechner laufen, welche Dateien angelegt werden und welche Ausgabe Erfolg bestätigt.

```sh
git clone https://github.com/LandminenTester/lt-database-api.git
cd lt-database-api
```

`.env.example` nach `.env` kopieren, `LDB_KEY_MAIN` und `DB_PASSWORD` durch unterschiedliche Zufallswerte ersetzen, dann:

```sh
docker compose --profile postgres up --build -d
curl http://127.0.0.1:8080/v1/health
```

Das ist eine lokale Entwicklungsinstallation auf Port 8080 mit Key-ID `main`; keine fertige Produktivkonfiguration. Für Produktion [Bereitstellung](docs/DEPLOYMENT.md) und [Sicherheit](docs/SECURITY.md) lesen.

## Funktionen und Grenzen

- Deklarative Schema-Synchronisierung mit Planung, Umbenennungen und steuerbarem Umgang mit destruktiven Änderungen.
- CRUD: Datensätze anlegen, lesen, ändern und löschen; zusätzlich Upsert, Zählen, Filter und Sortierung.
- HMAC-signierte Nachrichten, Nonces, Zeitfenster, Namespace-Rechte und Ratenlimits.
- Live-Schreiben als Standard; optionales [Write-behind](docs/WRITE-BEHIND.md) mit Journal und Zeitplan.
- Native Releases für Linux x64/ARM64 und Windows x64 sowie ein Container-Image.

Die API bietet keine frei formulierten SQL-Abfragen, keine Fremdschlüsseldefinitionen und keine gemeinsame Transaktion über mehrere HTTP-Aufrufe. Wiederholbarkeit und Provider-Grenzen stehen in der [Referenz](docs/API.md) und im [Schema-Leitfaden](docs/SCHEMA.md).

## Weiterführend

[Konfiguration und Betrieb](docs/DEPLOYMENT.md), [HTTP-API](docs/API.md), [OpenAPI](docs/openapi.yaml), [Signaturen](docs/SECURITY.md), [Client-Anbindung](docs/BUNDLE-INTEGRATION.md), [Architektur](docs/ARCHITECTURE.md), [Build und Tests](docs/BUILD.md). Quellcode und Downloads: [Repository](https://github.com/LandminenTester/lt-database-api).
