# lt_database installieren

## Voraussetzungen

Du benötigst einen BlackICE-Spielserver mit Bundle-Unterstützung und eine erreichbare lt-database-api. Die API benötigt eine Datenbank. Ein API-Key besteht aus einer öffentlichen **Key-ID** und einem geheimen Zufallswert von mindestens 32 Zeichen. Connector und API müssen denselben Key und dieselben erlaubten Namespaces verwenden.

Wenn du noch keine API betreibst, beginne mit dem [gemeinsamen Schnellstart](../../database-quickstart.md). Für entfernte Verbindungen HTTPS verwenden.

## 1. Release herunterladen

Lade `lt_database-<version>.zip` von den [Releases](https://github.com/LandminenTester/lt-database/releases/latest). Es enthält `config.toml`, den Servercode `sv.wasm` und öffentliche Konfigurationsbeispiele. Es gibt keinen Client-Teil. Alternativ [selbst bauen](BUILD.md).

## 2. Im richtigen Ordner installieren

```text
<server>/data/ugc/lt_database/
    config.toml
    sv.wasm
    vfs/
```

`<server>` steht für deinen BlackICE-Installationsordner. Der Ordnername `lt_database` ist gleichzeitig der Laufzeitname. Beim Kopieren `sv.wasm` vor `config.toml` schreiben, damit die Dateierkennung kein unvollständiges Bundle entdeckt. Falls nötig den Server neu starten und mit `bundles` prüfen.

Ein abweichender Ordnername muss in jedem Consumer mit `LtDatabaseClient.Db.Bundle = "dein_name";` eingestellt werden. Verwende für den Einstieg den Standardnamen.

## 3. API-Host erlauben

In `config.toml` den Beispielhost ersetzen:

```toml
[Networking]
allowed = ["https://db.example.com"]
```

Das ist ein Beispielhost, den du durch deine API-Domain ersetzt. Erlaubt sind exakte Einträge `host`, `host:port`, `scheme://host` oder `scheme://host:port`; keine Wildcards. Auch Weiterleitungen werden geprüft.

## 4. Private Konfiguration erstellen

`vfs/database.json`:

```json
{
  "url": "https://db.example.com",
  "keyId": "gameserver",
  "secretFile": "database.secret",
  "allowedNamespaces": ["documentation_demo"]
}
```

`vfs/database.secret` enthält nur das zu `gameserver` gehörende API-Secret in einer Zeile. Der ID-Name ist frei wählbar, muss aber zur API passen. Beim lokalen Standard-Compose-Schnellstart lautet er stattdessen `main`.

Der VFS-Ordner wird nicht an Spieler verteilt. Betriebssystemrechte trotzdem auf das Spielserverkonto und Administratoren beschränken: Wer das Secret lesen kann, kann diesen Key verwenden. Alle Optionen stehen unter [Konfiguration](CONFIGURATION.md).

## 5. Starten und testen

In der BlackICE-Serverkonsole:

```text
start lt_database
lt-db-health
```

Ein erfolgreiches signiertes Health-Ergebnis mit `database: true` bestätigt Hostfreigabe, Key, Antwortsignatur und Datenbankverbindung. Bei Fehlern `lt-db-status` und die [Fehlerbehebung](OPERATIONS.md) verwenden.

Für automatischen Start in `cfg/server.cfg` den Connector vor deinem Bundle eintragen:

```text
start lt_database
start mygame
```

`mygame` ist hier der Ordnername deines eigenen Bundles, kein mitgeliefertes Bundle.

## 6. C#-Projekt verbinden

Die folgenden Einträge gehören in eine `<ItemGroup>` deiner Server-`.csproj`. Die relativen Pfade müssen zu deiner Ordnerstruktur passen:

```xml
<ProjectReference Include="../lt_database/sh/sh.csproj" />
<Compile Include="../lt_database/import/LtDatabase.Server.cs" Link="LtDatabase.Server.cs" />
```

Falls bereits eine andere Assembly `sh` heißt, stattdessen die gemeinsamen Quelldateien einbinden, nicht zusätzlich beide Varianten:

```xml
<Compile Include="../lt_database/sh/Contracts.cs" Link="LtDatabase/Contracts.cs" />
<Compile Include="../lt_database/sh/Pure/*.cs" Link="LtDatabase/Pure/%(Filename)%(Extension)" />
<Compile Include="../lt_database/import/LtDatabase.Server.cs" Link="LtDatabase.Server.cs" />
```

Weiter mit [Nutzung](USAGE.md) und dem [erklärten Beispiel](EXAMPLES.md). Der [Laufzeit-Funktionstest](../examples/smoke/README.md) prüft eine echte Installation in einem separaten Test-Namespace.
