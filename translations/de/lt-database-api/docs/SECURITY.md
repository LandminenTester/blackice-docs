# Sicherheit und Signaturprotokoll

Die API ist für vertrauenswürdige Serverprogramme gedacht. Sie beschränkt einen Key auf erlaubte Operationen und Namespaces; sie schützt nicht vor einem kompromittierten API-/Datenbankhost oder vor absichtlich schädlichen Aktionen innerhalb gültiger Key-Rechte. Secrets wie Datenbankpasswörter behandeln.

## Signierter Umschlag {#the-signed-envelope}

Jeder geschützte Aufruf verwendet POST mit `v`, `kid`, `ts`, `nonce`, `payload`, `sig`. `kid` ist die Key-ID, `ts` Unix-Sekunden, `nonce` ein einmaliger Wert von 8–64 Zeichen, empfohlen 16 zufällige Bytes als Base64url. `payload` ist der **exakte JSON-Text als String**, nicht ein eingebettetes Objekt.

Signatur: Base64url ohne Padding von HMAC-SHA256 mit dem Secret über diese durch `\n` getrennten UTF-8-Zeilen:

```text
v1
<request path, e.g. /v1/data/find>
<kid>
<ts>
<nonce>
<payload>
```

Der Pfad verhindert die Verwendung einer Count-Signatur für Delete. JSON nach dem Signieren nicht neu serialisieren. Die Antwort enthält `v`, `ok`, `status`, `payload`, `sig`; ihre signierten Zeilen sind:

```text
v1resp
<request nonce>
<status>
<payload>
```

Der Client muss die Antwortsignatur in konstanter Zeit vergleichen und den Status prüfen, bevor er das Ergebnis verwendet. Fehler vor Authentifizierung sind absichtlich unsigniert und allgemein gehalten. HMAC authentifiziert, verschlüsselt aber nicht; HTTPS bleibt erforderlich.

## Testvektoren {#test-vectors}

Nur für Tests: Secret `0123456789abcdef0123456789abcdef`, Pfad `/v1/data/find`, Key `main`, Zeit `1760000000`, Nonce `AAAAAAAAAAAAAAAAAAAAAA`.

| Nachricht | Nutzlast | Erwartete Signatur |
| --- | --- | --- |
| Anfrage | `{"namespace":"demo","table":"players"}` | `42zlXLbDTxoL-oJ5eJ3IuG9oGFoByqkaYeBRHtC8x7c` |
| Antwort, Status 200 | `{"count":3}` | `Uk6xxTTmVDyXYAuBqMp5aF4vxbPJQH7jjNGM2gs5MH8` |

Diese historischen Zeitwerte sind Testdaten und keine aktuell akzeptierten Live-Anfragen. Der [Python-Client](../tools/ldb_client.py) implementiert Signieren und Antwortprüfung.

## Prüfungen und Grenzen

Zuerst Adresssperre, Größenlimit und Umschlag prüfen, dann Signatur, Zeitfenster (Standard 30 Sekunden), Quellnetze und einmalige Nonce. Fehler dieser Authentifizierungsstufe liefern dieselbe 401-Antwort. Danach gelten Key-Ratenlimit, Operation, Namespace, Freigabe für unfiltrierte Writes und Idempotenzprüfung.

Nonce- und Idempotenz-Caches sind pro Instanz im Speicher. Mehrere Instanzen benötigen Sticky Routing oder einen externen gemeinsamen Mechanismus. Neustarts vergessen diese Caches. Die Zeitspanne begrenzt Replay-Risiken; die Idempotenzspeicherung gilt zehn Minuten, nicht dauerhaft.

Es gibt keine rohen SQL-/NoSQL-Abfragen. Namen werden validiert, Werte parametrisiert und Filter als feste Grammatik geparst. Updates und Deletes brauchen Filter; `all: true` braucht ein gesondertes Key-Recht. Body-, Zeilen-, Filter- und Zeitlimits begrenzen Ressourcenverbrauch.

## Datenbankrechte {#database-privileges}

Zwei Konten verwenden: Datenkonto für DML, Strukturkonto für Schema-Sync. Die [Grant-Skripte](https://github.com/LandminenTester/lt-database-api/tree/main/docker/grants) zeigen die konkreten Provider-Rechte. Datenbankport privat halten, Dateirechte einschränken und API mit einem eigenen Betriebssystemkonto ausführen.

Gemeinsame Connector-Keys sind keine harte Isolation zwischen unvertrauenswürdigen Bundles auf demselben Spielserver. Pro Spielserver getrennte Keys, Namespaces und erlaubte Quelladressen verwenden. Für Remote-TLS nur explizit konfigurierte `TrustedProxies` akzeptieren.

## Schlüsselwechsel {#key-management}

Mindestens 32 zufällige Bytes verwenden. `Current` und optional `Next` verweisen auf `env:NAME` oder `file:/pfad`. Zuerst neuen Key als akzeptierte Alternative konfigurieren und API neu starten, dann Connector-Secret austauschen, neu laden und signiert testen. Anschließend neuen Key zum aktuellen machen und alten entfernen. Geheimnisse nie in Repository oder Clientdateien speichern.

## Betrieb und Meldungen

TLS, Proxy, Firewall, Datenbackups und Wiederherstellung gehören zur Bereitstellung. Logs enthalten keine normalen Nutzlasten, Journal und Dead Letters dagegen schon: wie Datenbankdaten schützen. MySQL-Schemaänderungen können teilweise angewendet sein. Bei einem Verdacht betroffene Secrets widerrufen und über den [privaten Meldekanal](../SECURITY.md) berichten.
