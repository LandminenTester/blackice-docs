# Spielereinstellungen: ein vollständiges Datenbankbeispiel

## Ziel und Grenzen

Du legst eine Tabelle an, speicherst einen Datensatz, änderst ihn, liest ihn aus und entfernst ihn. Diese Grundoperationen heißen CRUD: Create, Read, Update, Delete.

Das ist eine **wegwerfbare Demonstration auf dem Server**. Sie läuft einmal beim Start des Beispiel-Bundles. Sie registriert keine Spielerereignisse und implementiert weder Ban-System noch Rangliste noch automatische Spielereinstellungen. Für ein echtes Feature verwendest du entsprechende Save-/Load-Methoden in deinen eigenen Server-Ereignissen.

## Voraussetzungen

- `lt-db-health` funktioniert und der Connector läuft vor dem Beispiel-Bundle.
- Connector und API-Key erlauben `documentation_demo`.
- Du verwendest eine Entwicklungsdatenbank. Das Beispiel überschreibt und löscht die Zeile `sample_player` in `documentation_demo.preferences`; diese Zeile nicht für echte Daten nutzen.
- Ein Quellcode-Checkout und die Build-Werkzeuge aus [Build](BUILD.md) sind vorhanden.

Im Quellcode-Ordner ausführen:

```sh
dotnet build examples/consumer/consumer.csproj -c Release
```

Die Ausgabe liegt unter `examples/consumer/bin/Release/net10.0/wasi-wasm/native/consumer.wasm`.

1. `<server>/data/ugc/preferences_demo/` anlegen.
2. Die gebaute `consumer.wasm` dorthin kopieren.
3. `examples/consumer/config.toml` **zuletzt** daneben kopieren. Dieses Manifest verweist auf `consumer.wasm`; nicht das Connector-Manifest verwenden.
4. In der Spielserver-Konsole starten:

```text
start lt_database
start preferences_demo
```

Der Consumer bleibt ein separates Bundle. Den Connector-WASM nicht ersetzen. Mit `restart preferences_demo` lässt sich der Test wiederholen.

## Die Tabelle

| Spalte | Typ | Aufgabe |
| --- | --- | --- |
| `player_id` | Text, maximal 64 Zeichen, Primärschlüssel | Eindeutige Spielerkennung |
| `music_volume` | 32-Bit-Ganzzahl | Beispielwert 25, danach 40 |
| `visits` | 32-Bit-Ganzzahl | Zähler 0, danach 1 |

## Ablauf verstehen

1. `Sync` deklariert die Tabelle. Erst bei Erfolg wird weitergearbeitet. Eine unveränderte Deklaration erstellt die Tabelle nicht erneut.
2. `Upsert` speichert `sample_player` anhand des Primärschlüssels. Jeder Demolauf setzt bewusst Lautstärke 25 und Besuche 0.
3. `Update` ersetzt mit `setJson` die Lautstärke durch 40 und addiert mit `incJson` einen Besuch. Ein wiederholtes Increment würde erneut addieren.
4. `Find` liest genau den Beispieldatensatz. Fehler und fehlende Zeile werden getrennt behandelt.
5. `Delete` löscht nur den festen Beispieldatensatz. Die Tabelle bleibt bestehen.

Jeder nächste Schritt beginnt im erfolgreichen Callback des vorigen Schritts. Alle Änderungen nutzen `immediate: true`, damit Lesen auch bei aktivem Write-behind die Änderung sieht. Die fünf Aufrufe sind keine Transaktion: Ein Fehler kann den Beispieldatensatz stehen lassen; ein erneuter Demolauf setzt ihn zurück.

## Vollständiger kompilierter Quellcode

Die englischen Bezeichner und Kommentare entsprechen exakt der Datei, die CI baut. `Database`, `Schema`, `Filters` und `Query` sind nur lesbare Aliase für `Db`, `S`, `F` und `Q`.

```csharp
using LtDatabase;
using Database = LtDatabaseClient.Db;
using Schema = LtDatabase.S;
using Filters = LtDatabase.F;
using Query = LtDatabase.Q;

namespace Examples;

/// <summary>A disposable server-side CRUD demonstration, not a player event integration.</summary>
public static class PlayerPreferences
{
    // Allow this namespace in both the connector and the API key before running.
    const string Namespace = "documentation_demo";
    const string Table = "preferences";
    const string Player = "sample_player";

    public static void Run()
    {
        var schema = Schema.Schema(Schema.Table(Table, ["player_id"],
            [Schema.Text("player_id", 64), Schema.Int32("music_volume"), Schema.Int32("visits")]));

        Database.Sync(Namespace, schema, result =>
        {
            if (!Succeeded("Create schema", result)) return;
            Save();
        });
    }

    static void Save()
    {
        var row = Query.Row(("player_id", Player), ("music_volume", 25), ("visits", 0));
        Database.Upsert(Namespace, Table, row, ["player_id"], result =>
        {
            if (!Succeeded("Save preferences", result)) return;
            Change();
        }, immediate: true);
    }

    static void Change()
    {
        Database.Update(Namespace, Table, Filters.Eq("player_id", Player), result =>
        {
            if (!Succeeded("Change preferences", result)) return;
            if (Database.Number(result) != 1)
            {
                Console.WriteLine("[preferences demo] Expected exactly one changed row; stopping.");
                return;
            }
            Read();
        }, setJson: Query.Row(("music_volume", 40)),
           incJson: Query.Row(("visits", 1)), immediate: true);
    }

    static void Read()
    {
        Database.Find(Namespace, Table, result =>
        {
            if (!Succeeded("Read preferences", result)) return;
            var rows = Database.Rows(result);
            if (rows.Count != 1)
            {
                Console.WriteLine("[preferences demo] Sample row not found; stopping.");
                return;
            }
            var row = rows[0];
            Console.WriteLine($"[preferences demo] volume={row["music_volume"]}, visits={row["visits"]}");
            RemoveSample();
        }, filterJson: Filters.Eq("player_id", Player), limit: 1);
    }

    static void RemoveSample()
    {
        Database.Delete(Namespace, Table, Filters.Eq("player_id", Player), result =>
        {
            if (!Succeeded("Remove sample row", result)) return;
            Console.WriteLine($"[preferences demo] Removed {Database.Number(result)} sample row(s). Demo complete.");
        }, immediate: true);
    }

    static bool Succeeded(string step, DbResult result)
    {
        if (result.State == "ok" && !Database.IsQueued(result)) return true;
        var message = Database.IsQueued(result)
            ? "Write is queued rather than applied; stopping this sequential demonstration."
            : $"{result.Code}: {Database.ErrorMessage(result)}";
        Console.WriteLine($"[preferences demo] {step} failed: {message}");
        return false;
    }
}
```

Einstiegspunkt des Beispielprojekts:

```csharp
public static class App
{
    public static void Start() => Examples.PlayerPreferences.Run();
}
```

## Erwartete Ausgabe

```text
[preferences demo] volume=40, visits=1
[preferences demo] Removed 1 sample row(s). Demo complete.
```

Danach ist die Beispielzeile absichtlich gelöscht. Bei Problemen nennt das Log den fehlgeschlagenen Schritt und den Fehlercode. Namespace-Rechte, Startreihenfolge und Key prüfen.

Für ein echtes Feature eigene Namespaces und stabile Spielerkennungen verwenden, beim Start das Schema deklarieren und bei passenden Serverereignissen speichern oder laden. Den Demo-Löschschritt weglassen. Dem Spieler erst dann bestätigte Speicherung melden, wenn die gewählte Live-/Queue-Semantik das tatsächlich erlaubt. Siehe [Nutzung](USAGE.md).
