# Datenbank-Schnellstart: bis zum ersten gespeicherten Datensatz

Diese Anleitung verbindet einen BlackICE-Spielserver, den Connector **lt_database**, die **lt-database-api** und eine Datenbank. Das Panel ist eine separate Ressource und wird dafür nicht benötigt.

## Was läuft wo?

```text
Dein C#-Server-Bundle
  → lt_database im selben BlackICE-Server
    → lt-database-api als selbst gehosteter HTTP-Dienst
      → PostgreSQL, MySQL/MariaDB oder MongoDB
```

Dein Bundle kennt Namespace und Tabelle, der Connector kennt API-Adresse und Signierschlüssel. Nur die API kennt das Datenbankpasswort. Unbekannte Begriffe erklärt das [Verzeichnis](glossary.md).

## 1. Lokale API mit PostgreSQL starten

Du benötigst Git, Docker und Docker Compose auf einem Entwicklungsrechner. Die folgenden Befehle gehören in ein Terminal, nicht in die Spielserver-Konsole.

```sh
git clone https://github.com/LandminenTester/lt-database-api.git
cd lt-database-api
```

Kopiere `.env.example` nach `.env`: im Dateimanager, mit `cp .env.example .env` unter Linux/macOS oder `Copy-Item .env.example .env` in PowerShell. Ersetze im Texteditor beide Beispielwerte:

- `LDB_KEY_MAIN`: zufälliges Signier-Secret mit mindestens 32 Zeichen. Der Connector benötigt später exakt denselben Wert.
- `DB_PASSWORD`: ein anderes zufälliges Passwort für die lokale Datenbank.

```sh
docker compose --profile postgres up --build -d
docker compose --profile postgres ps
curl http://127.0.0.1:8080/v1/health
```

In PowerShell bei einem gleichnamigen Alias `curl.exe` verwenden. Die API sollte JSON mit `status: "ok"` liefern. Dieser öffentliche Test prüft den HTTP-Dienst; Schritt 3 prüft zusätzlich Signatur und Datenbank. Mit dem Profil `mysql` oder `mongodb` kannst du einen anderen Anbieter ausprobieren.

Port 8080 ist nur lokal erreichbar. `127.0.0.1` bezeichnet immer den Rechner beziehungsweise Container des Aufrufers. Ein Spielserver auf einem anderen Rechner erreicht damit nicht deinen Entwicklungsrechner. Für entfernte Installationen die [Bereitstellung](lt-database-api/docs/DEPLOYMENT.md) mit HTTPS verwenden.

## 2. Connector installieren und konfigurieren

Lade das [Bundle-Release](https://github.com/LandminenTester/lt-database/releases/latest) und entpacke es nach `<server>/data/ugc/lt_database/`. `<server>` ist dein BlackICE-Installationsordner. Vermeide einen doppelt verschachtelten Bundle-Ordner.

Für den lokalen Compose-Test in `config.toml`:

```toml
[Networking]
allowed = ["http://127.0.0.1:8080"]
```

Erstelle `<server>/data/ugc/lt_database/vfs/database.json`:

```json
{
  "url": "http://127.0.0.1:8080",
  "keyId": "main",
  "secretFile": "database.secret",
  "allowedNamespaces": ["documentation_demo"]
}
```

Daneben eine Datei `database.secret` anlegen. Sie enthält nur den Wert von `LDB_KEY_MAIN` aus `.env`, ohne Variablennamen und ohne Anführungszeichen. Das hier verwendete `docker-compose.yml` nutzt die Key-ID **`main`**. Die separate Datei `docker-compose.all.yml` nutzt standardmäßig **`gameserver`**; diese Konfigurationen nicht vermischen.

Der lokale Compose-Key erlaubt alle Namespaces. Beschränke seine `AllowedNamespaces` vor einem produktiven Einsatz auf die benötigten Namen. Die lokale Connector-Liste ersetzt die API-Berechtigungen nicht.

## 3. Verbindung prüfen

In der BlackICE-Serverkonsole:

```text
start lt_database
lt-db-health
```

Erwartet wird ein erfolgreiches signiertes Ergebnis mit `database: true`. Bei Fehlern `lt-db-status` ausführen und API-Adresse, erlaubten Host, Key-ID und Secret prüfen. Die [Betriebsanleitung](lt-database/docs/OPERATIONS.md) erklärt Fehlercodes. Konfiguration mit `lt-db-reload` neu laden; nach einer Manifeständerung `restart lt_database` verwenden.

## 4. Beispiel verstehen und bauen

Lies [C#-Nutzung](lt-database/docs/USAGE.md) und das [Praxisbeispiel für Spielereinstellungen](lt-database/docs/EXAMPLES.md). Es erklärt Aliase, Tabellenstruktur und Callbacks. Im Namespace `documentation_demo` wird ein Beispieldatensatz angelegt, auf Lautstärke 40 und Besuche 1 geändert, gelesen und wieder entfernt. Es installiert kein automatisches Gameplay-Feature.

## 5. Live oder gepuffert schreiben

Standardmäßig werden Änderungen live angewendet. Teste zunächst diesen Modus. Aktiviere [Write-behind](lt-database-api/docs/WRITE-BEHIND.md) erst, wenn verzögerte Sichtbarkeit passt. `queued` bestätigt die Annahme ins Journal, nicht die fertige Datenbankänderung. Für feste Uhrzeiten `FlushIntervalSeconds: 0` und `FlushThreshold: 0` setzen und `FlushAt` sowie `TimeZone` konfigurieren. Manuelles Flush, Herunterfahren und notwendige Reihenfolgeprüfungen können trotzdem früher schreiben.

## 6. Produktiven Betrieb vorbereiten

HTTPS, private Datenbankzugriffe, eingeschränkte Keys und Backups gemäß Bereitstellungsanleitung einrichten. In `server.cfg` den Connector vor den Consumern starten. Vor Updates den [Laufzeit-Funktionstest](lt-database/examples/smoke/README.md) in einem Test-Namespace ausführen. Datenbank und wartendes Journal sichern und Wiederherstellung testen.
