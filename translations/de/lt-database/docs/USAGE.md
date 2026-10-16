# Datenbank aus einem C#-Bundle verwenden

Diese Anleitung gehört zum **Server-Projekt deines eigenen Bundles**. Der Connector sendet signierte Anfragen an die API; nur diese spricht mit der Datenbank.

## Vor dem ersten Aufruf

1. [Installation](INSTALL.md) abschließen und `lt-db-health` erfolgreich ausführen.
2. Connector vor dem Consumer starten. Consumer bedeutet nur: dein Bundle verwendet den Connector.
3. `documentation_demo` im Connector und im API-Key erlauben.
4. Gemeinsame Typen und Helper wie in der Installation ins Server-Projekt einbinden. Keine Secrets im Client speichern.

## Kurznamen verständlich machen

`S`, `F` und `Q` erstellen JSON-Text. Sie führen selbst keine Datenbankanfragen aus. Mit normalen C#-Aliasen kannst du lesbare Namen verwenden:

```csharp
using LtDatabase;
using Database = LtDatabaseClient.Db;
using Schema = LtDatabase.S;
using Filters = LtDatabase.F;
using Query = LtDatabase.Q;
```

`Schema` bedeutet Tabellen- und Spaltendefinitionen, `Filters` Auswahlbedingungen und `Query` Zeilenwerte sowie Sortierungen. `Database` sendet die Anfrage. `Filters.Eq` ist exakt dieselbe Methode wie `F.Eq`; es sind keine zusätzlichen Pakete.

| Name | Erklärung |
| --- | --- |
| Namespace (`ns`) | Gruppe von Tabellen, z. B. `documentation_demo` |
| Primärschlüssel | Eindeutige Kennung einer Zeile, z. B. `player_id` |
| Row | Einzelner Datensatz als JSON-Objekt |
| Callback (`done`) | Funktion, die das spätere Ergebnis erhält |
| Upsert | Anlegen oder anhand eines eindeutigen Schlüssels ändern |
| `setJson` / `set` | Einen Wert ersetzen |
| `incJson` / `inc` | Increment: zum vorhandenen Zahlenwert addieren |
| `immediate: true` | Live schreiben, auch bei aktivierter Schreibpufferung |

## Ein vollständiges Beispiel

Das [Praxisbeispiel](EXAMPLES.md) erklärt eine einzige Tabelle und fünf Schritte: Schema deklarieren, Beispieldatensatz speichern, ändern, lesen und entfernen. Es enthält den vollständigen kompilierten Quellcode und die erwartete Ausgabe. Es ist keine fertige Spielerfunktion; die Anbindung an Spielereignisse bleibt bei deinem Bundle.

## Asynchrone Ergebnisse richtig behandeln

Der Helper liefert sofort ein Ticket. Er holt das Ergebnis ab und ruft deinen Callback auf. Bei einer sofortigen Ablehnung kann der Callback bereits direkt laufen. Verlasse dich weder auf eine Verzögerung noch darauf, dass Code nach dem Aufruf bereits ein fertiges Datenbankergebnis sieht.

Zuerst immer `result.State` prüfen. `Rows` und `Number` liefern bei Fehlern leere Werte beziehungsweise null als Zahlwert 0; das ist kein Beweis für eine erfolgreiche Anfrage ohne Treffer.

Dieser Ausschnitt gehört in eine Methode deines Server-Bundles, nachdem das Beispiel-Schema erfolgreich synchronisiert wurde:

```csharp
Database.Find("documentation_demo", "preferences", result =>
{
    if (result.State != "ok")
    {
        Console.WriteLine($"Load failed ({result.Code}): {Database.ErrorMessage(result)}");
        return;
    }
    var rows = Database.Rows(result);
    Console.WriteLine($"Found {rows.Count} preference row(s).");
}, limit: 10);
```

## Filter und Sortierung

| Methode | Bedeutung |
| --- | --- |
| `Eq` / `Ne` | Gleich / ungleich |
| `Gt` / `Gte` | Größer als / größer oder gleich |
| `Lt` / `Lte` | Kleiner als / kleiner oder gleich |
| `In` / `NotIn` | In einer Liste / nicht in einer Liste |
| `And` / `Or` / `Not` | Bedingungen verbinden / alternativ erfüllen / umkehren |
| `IsNull` | Fehlender Wert |
| `StartsWith` / `Contains` | Text beginnt mit / enthält |

```csharp
var frequentPlayers = Filters.And(
    Filters.Gte("visits", 5),
    Filters.Lte("music_volume", 40));
var ordering = Query.Sort(("visits", true), ("player_id", false));
```

Diese JSON-Strings als `filterJson` und `sortJson` an `Find` übergeben. `true` bedeutet absteigend, `false` aufsteigend. Der zweite Sortierschlüssel stabilisiert gleiche Besuchszahlen. `limit` begrenzt die Seite; mit `offset` und `HasMore` weitere Seiten lesen. Gleichzeitige Datenänderungen können Offset-Seiten verschieben.

## Gepufferte Änderungen und Wiederholungen

Live ist der Standard. Bei Write-behind kann `State == "ok"` nur die Journal-Annahme bestätigen. `Database.IsQueued(result)` prüfen. Ein Queue-Beleg enthält keine endgültigen IDs oder betroffenen Zeilen, und Lesen sieht nur bereits angewendete Änderungen.

Mit `immediate: true` vor einer abhängigen Leseoperation live schreiben. Bei `Database.Flush` zusätzlich `halted`, `remaining` und `deadLettered` im Ergebnis prüfen; ein erfolgreicher HTTP-Aufruf allein beweist nicht, dass alle Änderungen angewendet wurden.

`inc` ist nicht beliebig wiederholbar: zweimal `+1` zählt zweimal. Insert/Upsert erhalten pro Helper-Aufruf einen neuen Idempotenzschlüssel. Ein erneuter Helper-Aufruf ist deshalb eine neue Operation. Für eine feste eigene Operationskennung `Database.Call` mit `idempotencyKey` gemäß HTTP-Referenz verwenden. Mehrere getrennte Aufrufe bilden keine gemeinsame Transaktion.

Echte Spieler-IDs serverseitig bestimmen. Namespace, Tabelle und rohe Filter nicht ungeprüft aus Spielereingaben übernehmen. Weiterführend: [C#-Referenz](REFERENCE.md), [Betrieb](OPERATIONS.md), [Sicherheit](SECURITY.md).
