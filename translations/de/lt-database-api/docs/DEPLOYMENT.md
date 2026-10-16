# Bereitstellung und Konfiguration

## Voraussetzungen und Lesereihenfolge

Die API braucht eine erreichbare PostgreSQL-, MySQL/MariaDB- oder MongoDB-Datenbank, einen Signierschlüssel pro Aufrufer und HTTPS für entfernte Verbindungen. Für einen ersten lokalen Versuch den [Schnellstart](../../database-quickstart.md) verwenden. Hier geht es um den dauerhaft betriebenen Dienst.

Nur die API benötigt Datenbankpasswörter. Der Connector bekommt URL, Key-ID und Signier-Secret. Zwei Datenbankkonten können Rechte trennen: DML für Datenzugriff, DDL für Strukturänderungen. Fertige Berechtigungsskripte stehen im [Quellcode](https://github.com/LandminenTester/lt-database-api/tree/main/docker/grants).

## Wo Einstellungen herkommen

Die API liest `appsettings.json`, `appsettings.<Environment>.json` und Umgebungsvariablen. Variablen gewinnen. Der Präfix lautet `LDB_`; Doppelpunkte einer Einstellung werden als doppelte Unterstriche geschrieben:

```text
LDB_Ldb__Database__Provider=postgres
LDB_Ldb__Security__Keys__0__KeyId=main
LDB_Ldb__Security__Keys__0__Current=env:LDB_KEY_MAIN
LDB_Ldb__Security__Keys__0__AllowedNamespaces__0=documentation_demo
```

`0` ist der erste Listeneintrag. `Current=env:LDB_KEY_MAIN` ist ein Verweis auf eine andere Umgebungsvariable, nicht das Secret selbst. Alternativ `file:/geschuetzter/pfad` verwenden.

## Alle wesentlichen Einstellungen

| Einstellung unter `Ldb` | Standard | Bedeutung |
| --- | --- | --- |
| `Database:Provider` | `postgres` | `postgres`, `mysql` oder `mongodb` |
| `Database:DmlConnectionString` | erforderlich | Verbindung für Datenzugriffe |
| `Database:DdlConnectionString` | DML-Verbindung | Verbindung ausschließlich für Schema-Sync |
| `Database:MongoDatabase` | `ldb` | MongoDB-Datenbankname |
| `Database:CommandTimeoutSeconds` | `15` | Zeitlimit je Datenbankbefehl; Operationen werden nach dem Vierfachen abgebrochen |
| `Security:AllowInsecureHttp` | `false` | Entferntes HTTP nur für lokale Testnetze erlauben |
| `Security:TimestampToleranceSeconds` | `30` | Erlaubter Zeitversatz in Sekunden |
| `Security:MaxBodyBytes` | `1048576` | Maximale Anfragegröße |
| `Security:FailedAuthPerMinute` | `10` | Fehlversuche je Adresse vor Sperre |
| `Security:TrustedProxies` | `[]` | Nur deren Forwarded-Headern vertrauen |
| `Security:Keys[n]:KeyId` | erforderlich | Schlüsselkennung, höchstens 64 Zeichen |
| `Security:Keys[n]:Current` / `Next` | erforderlich / optional | Secret-Verweise `env:NAME` oder `file:/pfad`, mindestens 32 Bytes |
| `Security:Keys[n]:AllowedNamespaces` | erforderlich | Namespace-Freigaben; `"*"` bedeutet alle |
| `Security:Keys[n]:AllowedOperations` | alle | Optional z. B. `find`, `count`, `insert` einschränken |
| `Security:Keys[n]:AllowedCidrs` | alle Quellen | Erlaubte Netzwerkbereiche |
| `Security:Keys[n]:RequestsPerMinute` | `600` | Ratenlimit pro Key |
| `Security:Keys[n]:AllowUnfilteredWrites` | `false` | `all: true` bei Update/Delete erlauben |
| `Schema:DestructiveMode` | `Apply` | `Apply`, `Quarantine` oder `Deny` |
| `Schema:MaxTables` | `64` | Tabellen pro Namespace |
| `Limits:MaxRows` | `1000` | Zeilen pro Find-Antwort |
| `Limits:MaxInsertRows` | `1000` | Zeilen pro Insert |
| `WriteBehind:*` | deaktiviert | Alle Felder unter [Schreibpufferung](WRITE-BEHIND.md) |

## Verbindung zur Datenbank

Platzhalter in den folgenden Beispielen durch deine Werte ersetzen:

```text
postgres: Host=db.internal;Port=5432;Database=ldb;Username=ldb_data;Password=SECRET;SSL Mode=Require
mysql: Server=db.internal;Port=3306;Database=ldb;User ID=ldb_data;Password=SECRET;SslMode=Required
mongodb: mongodb://ldb_data:SECRET@db.internal:27017/ldb?authSource=ldb&tls=true
```

Passwörter über geschützte Umgebungsvariablen oder eine nur für das Dienstkonto lesbare Produktionskonfiguration bereitstellen. Nicht committen.

## Container und HTTPS

Das veröffentlichte Image `ghcr.io/landminentester/lt-database-api` läuft ohne Rootrechte und ohne Shell. Für reproduzierbare Deployments einen Versions-Tag statt `latest` wählen. Die Compose-Datei startet dagegen Testdatenbanken und erlaubt HTTP; sie ist für lokale Entwicklung gedacht.

Für Produktion nur den API-Port an Loopback binden und einen Reverse Proxy mit TLS davorsetzen. Den tatsächlichen Proxy in `TrustedProxies` eintragen, damit HTTPS und Quelladressen korrekt ausgewertet werden. Beispiel Caddy:

```text
db.example.com {
    request_body { max_size 2MB }
    reverse_proxy 127.0.0.1:8080
}
```

Alternativ kann Kestrel selbst ein Zertifikat verwenden. Die englische Fassung enthält vollständige Docker-, nginx- und Kestrel-Beispiele mit denselben Einstellungen. Bei Journalbetrieb ein dauerhaftes, für den App-Benutzer beschreibbares Volume nach `/data` mounten; das übrige Dateisystem kann schreibgeschützt bleiben.

## Linux und Windows als Dienst

Native Archive von den [Releases](https://github.com/LandminenTester/lt-database-api/releases/latest) herunterladen und die Prüfsummen prüfen. Sie benötigen kein installiertes SDK.

Unter Linux als eigenes eingeschränktes Konto betreiben, z. B. mit systemd: Arbeitsverzeichnis `/opt/ldb`, `ExecStart=/opt/ldb/Ldb.Api`, geschützte `EnvironmentFile=/etc/ldb/ldb.env`, `Restart=on-failure`, `NoNewPrivileges=true`. Für einen gepufferten Betrieb den Journal-Pfad ausdrücklich beschreibbar machen.

Unter Windows das Archiv beispielsweise nach `C:\ldb` entpacken. `Ldb.Api.exe` als Dienst mit eigenem Konto einrichten; Konfiguration und Zertifikat nur diesem Konto und Administratoren lesbar machen. In beiden Fällen zuerst Konfiguration und TLS prüfen, danach automatischen Start aktivieren.

## Betrieb

- `GET /healthz`: Prozess lebt. `GET /readyz`: Datenbank erreichbar, sonst 503.
- `POST /v1/health`: signierte Prüfung einschließlich Provider und Pufferzustand.
- Logs sind JSON-Zeilen auf stdout. Fehlerdetails stehen im Dienstlog, nicht im öffentlichen API-Fehler.
- Datenbank sowie ausstehendes Journal und Dead Letters sichern. Konfiguration und Secrets geschützt außerhalb austauschbarer Release-Ordner speichern.
- Beim Update binäre Dateien beziehungsweise Image ersetzen und geordnet neu starten. Vorher Warteschlangen prüfen und Wiederherstellung testen.
- Mehrere Instanzen haben getrennte Nonce-/Idempotenz-Caches und Journale. Sticky Routing je Key verwenden; globale Reihenfolge ist nicht enthalten.

Schlüsselwechsel und Rechte stehen unter [Sicherheit](SECURITY.md), Warteschlangenbetrieb unter [Write-behind](WRITE-BEHIND.md).
