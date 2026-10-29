# Build und Release

Diese Anleitung baut den Connector aus Quellcode. Für eine reine Installation reicht das fertige [Release](https://github.com/LandminenTester/lt-database/releases/latest).

## Voraussetzungen

.NET 10 SDK und die im Projekt gepinnten BlackICE-/WASM-Build-Abhängigkeiten installieren. `sv` enthält den Servercode, `sh` die gemeinsamen Typen und reinen JSON-/Kryptografie-Helfer. Es gibt keinen Client-WASM. Die genauen Paketversionen stehen in den Projektdateien; nicht unabhängig voneinander aktualisieren. `replay.blackice` SDK 1.3.0 liefert `re.sql`, das das SQL-Backend benötigt.

## Bauen

Im Repository-Ordner:

```sh
dotnet restore sv/sv.csproj
dotnet build sv/sv.csproj -c Release
dotnet build examples/consumer/consumer.csproj -c Release
```

Der BlackICE-Build erzeugt nativen WASM-Code, nicht nur eine Desktop-DLL. Die generierte Datei `sv/bin/Release/net10.0/wasi-wasm/native/sv.wasm` als `sv.wasm` in ein Laufzeitpaket übernehmen; der Name muss zu `server_blob` im Manifest passen. Den Consumer separat halten: Er ist das Beispiel, nicht der Connector.

## Prüfen

`dotnet test tests/Bundle.Tests` ausführen (über 100 Tests: SQL-Erzeugung, Schema-Hash, Diff und Receipts, verglichen mit Vektoren aus dem echten lt-database-api-Code und ausgeführt auf einer SQLite-Engine im Speicher) und das veröffentlichte Paket in einer Testinstallation mit `lt-db-health` sowie dem [Funktionstest](../examples/smoke/README.md) prüfen. Ein erfolgreicher Build beweist noch keinen Laufzeittest gegen eine Datenbank. Das [Praxisbeispiel](EXAMPLES.md) muss exakt zum kompilierten `examples/consumer/PlayerPreferences.cs` passen.

## Paket erstellen

Manifest, Server-WASM, Konfigurationsbeispiele, Helper, gemeinsame Quellen, Lizenz und Dokumentation nach dem vorhandenen Release-Workflow verpacken. Private `database.json`-/Secret-Dateien, Datenbanken, Journaldateien, `bin/` und `obj/` nicht ungeprüft einpacken. Versionsnummern, Archivname und Prüfsummen müssen zusammenpassen.

Vor Veröffentlichung Quellcode, Beispiele und Dokumentation committen, CI prüfen, Versions-Tag erstellen und Release-Workflow verwenden. Nach dem Download Prüfsumme und Paketinhalt kontrollieren. Betrieb und Wiederherstellung stehen unter [Betrieb](OPERATIONS.md).
