# Client- und Bundle-Anbindung

## Eigener HTTP-Client

Ein Client braucht HTTP POST, HMAC-SHA256 und sichere zufällige Nonces. Er erstellt eine JSON-Nutzlast, signiert die exakten Bytes mit Pfad, Key-ID, Zeitstempel und Nonce und sendet den Umschlag. Die Antwort wird vor der JSON-Auswertung signaturgeprüft. Das genaue Format und feste Testvektoren stehen unter [Sicherheit](SECURITY.md).

Der öffentliche [Python-Referenzclient](../tools/ldb_client.py) zeigt den vollständigen Ablauf. Mit `GET /v1/health` kann der Client die API-Zeit für einen Zeitversatz ermitteln. Diese öffentliche Antwort ist kein signierter Datenbanknachweis.

Bei einem Timeout für dieselbe logische Schreiboperation dieselbe Nutzlast und denselben `idempotencyKey` verwenden, aber einen neuen Umschlag mit neuer Nonce signieren. Das gilt nur innerhalb des dokumentierten Aufbewahrungsfensters.

## BlackICE-Bundles

Server-Bundles laufen in einer Sandbox. SDK 1.1.0 bietet ausgehendes GET und POST über `re.net.Http`; deshalb sind auch Update und Delete hier POST-Operationen. Ziele müssen im Manifest erlaubt sein:

```toml
[Networking]
allowed = ["https://db.example.com"]
```

Der private VFS-Ordner wird nicht an Spieler gestreamt, bleibt aber durch Betriebssystemrechte zu schützen.

Verwende normalerweise den [lt_database-Connector](../../lt-database/README.md), statt Signatur und HTTP selbst in jedem Bundle zu implementieren. Dein Consumer bindet gemeinsame Typen und Helper ein und ruft `Db.Sync`, `Insert`, `Find`, `Update`, `Upsert`, `Delete`, `Count` oder `Flush` auf. Die tatsächlichen Connector-Exporte heißen `Call` und `TakeResult`; der Helper abstrahiert sie.

### API oder `re.sql`: welches?

Seit Version 0.3.0 kann das Bundle **lt_database** PostgreSQL oder SQLite auch direkt über den `re.sql`-Provider des Hosts ansprechen (`"backend": "sql"` in seiner `vfs/database.json`, SDK 1.3.0 oder neuer), ganz ohne diese API. Consumer sehen dieselben Exporte, Anfragen, Ergebnisse und Fehlercodes; Schema-Hash und Receipt-Fingerprint sind identisch. Eine über diese API angelegte Datenbank lässt sich deshalb vom Backend `sql` übernehmen und umgekehrt (nie beide gleichzeitig auf denselben Namespaces).

Nimm **diese API**, wenn mehrere Gameserver eine Datenbank teilen, du MySQL, MariaDB oder MongoDB nutzt, Write-behind brauchst oder der Gameserver-Host keine Datenbank-Zugangsdaten halten soll (das Bundle hält nur einen Key, der auf seine Namespaces und Adresse beschränkt ist). Nimm **`re.sql`**, wenn ein Gameserver genügt, nichts weiter laufen soll (SQLite ist eine Datei) oder du entwickelst und testest. Der Leitfaden [Backend und Einstellungen wählen](../../lt-database/docs/USE-CASES.md) vergleicht beide mit Anwendungsfällen, [SQL-Backend](../../lt-database/docs/SQL-BACKEND.md) nennt jeden Unterschied.

## Reihenfolge

1. API mit Key und eingeschränkten Namespaces betreiben.
2. API-Host im Connector-Manifest erlauben.
3. URL, Key-ID und Secret im privaten VFS eintragen.
4. Connector starten und `lt-db-health` prüfen.
5. Consumer starten, Schema deklarieren und auf erfolgreichen Callback warten.

Das [erklärte C#-Beispiel](../../lt-database/docs/EXAMPLES.md) zeigt alle Schritte innerhalb des Consumers. Für die gemeinsame Installation den [Schnellstart](../../database-quickstart.md) lesen.

Bei Write-behind `Db.IsQueued(result)` prüfen. `Db.Flush` liefert einen Bericht; `halted`, `remaining` und `deadLettered` auswerten. Mit `immediate: true` einzelne Änderungen vor einer davon abhängigen Aktion live anwenden.
