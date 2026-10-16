# API bauen, testen und veröffentlichen

## Werkzeuge

.NET 10 SDK und Git installieren. Für echte Datenbanktests wird eine Docker-Laufzeit mit Linux-Containern benötigt. Fertige native Release-Archive brauchen kein SDK auf dem Zielsystem.

```sh
git clone https://github.com/LandminenTester/lt-database-api.git
cd lt-database-api
dotnet restore
dotnet build -c Release
dotnet test -c Release
```

Die Tests prüfen Signaturen, Sicherheit, Request-Verarbeitung, Schema und Abfragen, Zeitpläne, Journal-Wiederherstellung und Provider-Verträge. PostgreSQL 17, MySQL 8.4 und MongoDB 8 werden automatisch in Containern gestartet. Ohne Docker werden diese Tests übersprungen. `LDB_SKIP_DOCKER=1` wählt ausdrücklich nur die Tests ohne Container. Linux-CI prüft die Datenbanken, Windows-CI die Unit-Tests.

## Lokal entwickeln

Entwicklungs-Keys auf Test-Namespaces beschränken. Alle drei Provider gleichzeitig mit `docker compose -f docker-compose.all.yml up -d --build` nach Einrichtung von `.env` starten. Die Endpunkte liegen dann auf 8081, 8082 und 8083; Key-ID ist standardmäßig `gameserver`. Das normale Profil-Compose verwendet dagegen Port 8080 und Key `main`.

Den [Python-Client](../tools/ldb_client.py) zum Signaturtest verwenden. `.env`, Produktionskonfiguration, Secrets, Journale und Datenbankinhalte nicht committen.

## Native Anwendung

```sh
dotnet publish src/Ldb.Api -c Release -r linux-x64 --self-contained -p:PublishSingleFile=true -p:DebugType=None -o out/linux-x64
```

Alternativ `linux-arm64` oder `win-x64`. Gesamten Publish-Ordner einschließlich `appsettings.json`, README und Lizenz verpacken. Programmname: `Ldb.Api`, unter Windows `Ldb.Api.exe`. Private Konfiguration und Journal außerhalb ersetzbarer Release-Ordner halten.

## Container

```sh
docker build -f docker/Dockerfile -t lt-database-api:local .
```

Der Container läuft ohne Rootrechte. Secrets zur Laufzeit bereitstellen; bei Journalbetrieb `/data` dauerhaft und beschreibbar mounten. [Bereitstellung](DEPLOYMENT.md) beschreibt Netzwerk und TLS.

## Release

1. Geprüften Code und Dokumentation committen.
2. Vollständige grüne CI inklusive Linux-Datenbanktests abwarten.
3. Neuen Versions-Tag `v<version>` pushen; vorhandene Tags nicht überschreiben.
4. Release-Workflow erzeugt drei native Archive, Prüfsummen und versioniertes GHCR-Image plus `latest`.
5. Jobs, heruntergeladene Pakete und Prüfsummen kontrollieren. Ein Tag allein ist kein fertiges Release.
6. Dokumentation aus den neuen Quellrevisionen synchronisieren.

Bei Pufferänderungen insbesondere Reihenfolge, angehaltene Flushes, erneute Schema-Validierung und MongoDB-Teilfehler testen. Siehe [Write-behind](WRITE-BEHIND.md).
