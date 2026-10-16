# Optionale Schreibpufferung: Write-behind

Standardmäßig ist jeder Schreibzugriff **live**: Die API wendet ihn in der Datenbank an und liefert danach IDs oder betroffene Zeilen. Write-behind ist optional. Es prüft Änderungen, schreibt sie in ein Journal und bestätigt zunächst `queued`. Die Datenbank wird später in Annahmereihenfolge aktualisiert.

## Wann passt das?

Für häufige Änderungen mit tolerierbarer Verzögerung, etwa Statistiken oder letzte Aktivität. Ungeeignet, wenn sofort eine generierte ID oder eine bestätigte Zeilenanzahl benötigt wird. Für Guthabenentscheidungen nicht allein auf einen Queue-Beleg vertrauen. Die Spielserver-Aufrufe sind bereits asynchron; Write-behind verändert vor allem Dauerhaftigkeit und Sichtbarkeit, nicht die C#-Aufrufsyntax.

## Einschalten

```json
{
  "Ldb": {
    "WriteBehind": {
      "Enabled": true,
      "Namespaces": ["mygame"],
      "Operations": ["insert", "update", "upsert", "delete"],
      "FlushIntervalSeconds": 30,
      "FlushAt": ["04:00"],
      "TimeZone": "Europe/Berlin",
      "FlushThreshold": 1000,
      "JournalPath": "/data/write-behind.journal"
    }
  }
}
```

`mygame` durch deinen Namespace ersetzen. Unter Docker `/data` als dauerhaftes beschreibbares Volume einbinden. Umgebungsvariablen folgen z. B. `LDB_Ldb__WriteBehind__Enabled=true` und `LDB_Ldb__WriteBehind__FlushAt__0=04:00`.

| Feld | Standard | Bedeutung |
| --- | --- | --- |
| `Enabled` | `false` | Hauptschalter; aus bedeutet live |
| `Namespaces` | `[]` | Betroffene Namespaces; leer bedeutet alle |
| `Operations` | alle vier | Gepufferte Schreiboperationen |
| `FlushIntervalSeconds` | `30` | Intervall in Sekunden; 0 deaktiviert es |
| `FlushAt` | `[]` | Tageszeiten als `HH:mm` im 24-Stunden-Format |
| `TimeZone` | `UTC` | Zeitzone für feste Zeiten, z. B. `Europe/Berlin` |
| `FlushThreshold` | `1000` | Früher anwenden ab dieser Menge; 0 deaktiviert |
| `MaxQueuedOperations` | `50000` | Harte Anzahlgrenze |
| `MaxQueuedBytes` | `67108864` | Harte Nutzlastgrenze |
| `JournalPath` | leer | Dauerhafte Datei; leer bedeutet nur Arbeitsspeicher |
| `JournalFsync` | `true` | Vor Bestätigung auf Datenträger schreiben |
| `OnError` | `Skip` | Dauerfehler nach Dead Letter auslagern; `Stop` hält an |
| `MaxRetries` | `5` | Versuche bei vorübergehenden Datenbankfehlern |
| `FlushBeforeRead` | `false` | Vor Find/Count den Namespace leeren |
| `ShutdownFlushSeconds` | `30` | Wartezeit für Abschluss beim geordneten Stop |

Ungültige Uhrzeit oder Zeitzone verhindert den Dienststart mit einer Fehlermeldung.

## Antwort und Sichtbarkeit

```json
{"queued": true, "id": "receipt-id", "pending": 12}
```

`id` ist ein Beleg fürs Log, keine generierte Datensatz-ID. `pending` ist die Wartemenge. Eine Queue-Antwort hat keine endgültigen Insert-IDs oder betroffenen Zeilen. Schema, Pflichtwerte, Typen und Berechtigungen werden vor Annahme geprüft; Datenbankregeln wie Eindeutigkeit können trotzdem erst beim Flush scheitern.

Lesen sieht nur bereits angewendete Daten. Für unmittelbare Sichtbarkeit `durability: "immediate"` beziehungsweise im Bundle `immediate: true` verwenden oder vorher flushen. Ältere Änderungen des Namespaces werden vor einem Live-Schreibzugriff angewendet, damit die Reihenfolge erhalten bleibt.

## Wann wird geflusht?

Intervall, feste Tageszeiten, Mengenschwelle, explizites `POST /v1/data/flush`, Schemaänderungen, unmittelbare Schreibzugriffe und geordnetes Herunterfahren lösen Verarbeitung aus. Bei `FlushBeforeRead` auch Find/Count. Für ausschließlich zeitgesteuerte reguläre Hintergrundläufe Intervall und Schwelle auf 0 setzen; die anderen notwendigen Auslöser bleiben bestehen.

Flush-Nutzlast: `{"namespace":"mygame"}`. Der Key braucht Operation `flush`. Ergebnis:

```json
{"flushed": 10, "deadLettered": 0, "remaining": 0, "halted": false, "enabled": true}
```

Nicht nur HTTP-Erfolg prüfen: `halted`, `remaining` und `deadLettered` entscheiden, ob die gewünschte Arbeit erledigt ist. Ohne aktiviertes Write-behind ist `enabled: false`. Ein fehlgeschlagenes notwendiges Flush blockiert Schemaänderung, unmittelbare Änderung oder konsistentes Lesen mit `503 write_buffer_halted`.

## Fehler und Wiederanlauf

| Situation | Verhalten |
| --- | --- |
| Datenbank nicht erreichbar | Mit Verzögerung wiederholen; danach pausieren und später erneut versuchen |
| Dauerhaft ungültige Änderung | Bei `Skip` in `<JournalPath>.dead`, bei `Stop` am Warteschlangenanfang anhalten |
| Voller Puffer | Neue Anfrage erhält `503 write_buffer_full` |
| Journal nicht schreibbar | `503 write_buffer_unavailable`; nicht angenommen |
| Prozessabsturz | Journal beim Neustart einlesen; ohne Journal gehen ausstehende Änderungen verloren |
| Geordneter Stop | Abschließendes Flush; Rest bleibt im Journal |

Die Zustellung ist **mindestens einmal**, nicht exakt einmal. Ein Absturz nach Datenbankbestätigung, aber vor Journalabschluss kann eine Änderung erneut ausführen. Stabile eindeutige Schlüssel und idempotentes Setzen/Upsert bevorzugen; `inc` kann doppelt zählen.

SQL-Provider können aufeinanderfolgende Inserts in dieselbe Tabelle bündeln. MongoDB bündelt getrennte Requests nicht, weil mehrzeilige Inserts teilweise erfolgreich sein können. Auch ein einzelner mehrzeiliger MongoDB-Request kann bei Fehlern teilweise angewendet sein.

## Überwachen und warten

Journal und Dead Letters enthalten Daten und brauchen restriktive Rechte und Backups. Signiertes Health liefert `writeBuffer` mit `enabled`, `pending`, `oldestAgeSeconds`, `halted`. Metriken: `ldb_writebehind_pending`, `ldb_writebehind_applied_total`, `ldb_writebehind_dead_lettered_total` im Meter `Ldb.Api`.

Auf wachsende Warteschlange, Stillstand und Dead Letters reagieren. Dead-Letter-Zeilen enthalten `id`, `op`, `ns`, `p`, `code`, `message`, `t`; Ursache korrigieren und die Nutzlast `p` bewusst neu senden. Vor Migration jeden Namespace flushen und `remaining: 0` abwarten. Mehrere API-Instanzen haben getrennte Reihenfolgen und Journale.

Im Bundle `Db.IsQueued(result)` verwenden, mit `Db.Flush(ns, done)` leeren und für einzelne Live-Aufrufe `immediate: true` setzen. Das [Praxisbeispiel](../../lt-database/docs/EXAMPLES.md) zeigt Live-Schreiben mit sauberer Fehlerbehandlung.
