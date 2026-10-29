# Connector konfigurieren

Die Konfiguration besteht aus dem Manifest `config.toml` und zwei privaten Dateien im VFS-Ordner. Nach Änderungen an JSON oder Secret `lt-db-reload` ausführen. Änderungen am Manifest brauchen `restart lt_database`.

## Welche Einstellung gehört wohin?

| Einstellung | Datei beziehungsweise Dienst |
| --- | --- |
| Erlaubte Netzwerkziele | `config.toml`, Abschnitt `Networking.allowed` |
| API-Adresse, Key-ID und Namespaces | `vfs/database.json` |
| Signier-Secret | `vfs/database.secret` |
| Datenbankpasswort | Nur in der API-Konfiguration |
| API-Rechte, Ratenlimits, Schreibpufferung | lt-database-api |

## Manifest

```toml
[General]
description = "lt_database connector"
author = "LandminenTester"
version = "0.3.0"

[Scripting]
server_blob = "sv.wasm"
enable_vfs = true

[Networking]
allowed = ["https://db.example.com"]

[Meta]
config_version = "alpha_playtest"
```

`enable_vfs = true` ist erforderlich, damit das Bundle seine privaten Dateien lesen kann. `server_blob` muss auf die tatsächlich installierte WASM-Datei zeigen. Den Beispielhost ersetzen; Hostfreigaben werden exakt und ohne Wildcards geprüft, auch nach Weiterleitungen.

## database.json

Der Connector hat zwei Backends, gewählt über `"backend"`: `"http"` (Standard; dieser Abschnitt) spricht mit lt-database-api, `"sql"` nutzt den `re.sql`-Provider des Hosts mit PostgreSQL oder SQLite und braucht keine API ([SQL-Backend](SQL-BACKEND.md), dort auch die zusätzlichen Felder `sqlAlias`, `sqlDialect` und `destructiveMode`).

```json
{
  "url": "https://db.example.com",
  "keyId": "gameserver",
  "secretFile": "database.secret",
  "allowedNamespaces": ["documentation_demo"],
  "timeoutMs": 15000,
  "maxConcurrent": 8,
  "allowInsecureHttp": false
}
```

| Feld | Standard | Bedeutung |
| --- | --- | --- |
| `url` | erforderlich | Basisadresse ohne API-Pfad. HTTPS, außer für Loopback-Tests. |
| `keyId` | erforderlich | API-Key-ID, höchstens 64 Zeichen; muss zur API passen. |
| `secretFile` | `database.secret` | Datei innerhalb des VFS; absolute Pfade und `..` sind verboten. |
| `allowedNamespaces` | erforderlich | Mindestens ein Namespace; `"*"` erlaubt lokal alle. Die API-Rechte gelten zusätzlich. |
| `timeoutMs` | `15000` | Zeitlimit pro Anfrage in Millisekunden; 1000 bis 120000. |
| `maxConcurrent` | `8` | Gleichzeitige Anfragen; 1 bis 64. Weitere warten im Connector. |
| `allowInsecureHttp` | `false` | Erlaubt HTTP zu entfernten Hosts; nur für vollständig vertrauenswürdige Testnetze. |
| `backend` | `"http"` | `"http"` oder `"sql"`. Mit `"sql"` werden `url`, `keyId`, `secretFile` und `allowInsecureHttp` ignoriert. |

SQL-Variante (siehe [SQL-Backend](SQL-BACKEND.md)):

```json
{ "backend": "sql", "sqlAlias": "players", "sqlDialect": "auto", "destructiveMode": "deny", "allowedNamespaces": ["mygame"] }
```

Eine fehlende oder ungültige Datei lässt das Bundle geladen, aber Aufrufe scheitern mit `not_configured`. `lt-db-status` nennt den Grund.

## Namespaces und Namen

Ein Namespace gruppiert Tabellen einer Funktion oder eines Bundles. Namespaces, Tabellen, Spalten und Indizes folgen `^[a-z][a-z0-9]*(_[a-z0-9]+)*$`. Maximale Längen: Namespace 24, Tabelle 36, Spalte 48 Zeichen. `player_prefs` ist gültig; `Player`, `a__b`, `1st` und `a-b` sind ungültig.

Sowohl die Connector-Liste `allowedNamespaces` als auch `AllowedNamespaces` des API-Keys müssen den Namen erlauben. Nur die API entscheidet verbindlich über die Berechtigungen.

## Secret und Umgebungen

`database.secret` enthält eine Zeile mit mindestens 32 zufälligen Zeichen, beispielsweise erzeugt mit `openssl rand -base64 48`. Leerraum am Rand wird entfernt. Es muss exakt zum API-Secret passen.

Für Test und Produktion getrennte URLs, Keys und Secrets verwenden. Die Bereitstellung kopiert jeweils die passenden privaten Dateien. Beim Wechsel der API mit `lt-db-reload` müssen Consumer ihre Schemas an der neuen API erneut deklarieren, etwa durch einen Consumer-Neustart. Vor einem Wechsel ausstehende Schreibvorgänge berücksichtigen.
