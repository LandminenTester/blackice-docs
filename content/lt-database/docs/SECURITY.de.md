# Sicherheit des Connectors

## Vertrauensgrenze

Autoritative Datenzugriffe gehören auf den Spielserver. Clientcode darf keine Secrets, beliebigen Namespaces oder ungeprüften Datenbankbefehle erhalten. Der Connector stellt Server-Exporte bereit; er isoliert nicht automatisch mehrere gegenseitig unvertrauenswürdige Server-Bundles.

Das Secret in `vfs/database.secret` authentifiziert den API-Key. Wer es lesen kann, kann dessen erlaubte Operationen ausführen. Dateirechte auf Spielserverkonto und Administratoren beschränken. Secrets weder committen noch in öffentliches Clientmaterial, Logs oder Screenshots aufnehmen.

## Netzwerk und Signaturen

`Networking.allowed` beschränkt Ziele exakt, einschließlich Weiterleitungen. HTTPS für entfernte Verbindungen verwenden. Der Connector signiert Anfragen mit HMAC-SHA256 und prüft die signierte Antwort, den Status sowie den Bezug zur Anfrage. Ungültige Antworten werden verworfen. Zeitstempel und Nonces schützen gegen Wiederverwendung; Systemuhr synchron halten.

HMAC ersetzt keine Transportverschlüsselung. `allowInsecureHttp` ist nur für vertrauenswürdige Testnetze geeignet. Loopback-Ausnahmen beziehen sich auf den tatsächlichen Rechner beziehungsweise Container des Aufrufers.

## Rechte und Eingaben

Namespaces sowohl im Connector als auch am API-Key eingrenzen. In der API Operationen, Quellnetze und Ratenlimits beschränken. Die Datenbank muss privat bleiben; ihre Konten und Passwörter kennt nur die API.

Spielerkennungen serverseitig bestimmen. Spielereingaben validieren und Werte über die JSON-Builder maskieren. Keinen rohen JSON-Filter oder frei wählbaren Namespace vom Client übernehmen. Schemaänderungen zentral verantworten; eine Deklaration kann nicht mehr genannte Tabellen oder Spalten entfernen. Vor Änderungen planen und sichern.

## Gepufferte Daten

Journal und Dead-Letter-Dateien enthalten Nutzdaten. Wie die Datenbank schützen und sichern. Ein Queue-Beleg beweist keine fertige Änderung. Für Entscheidungen über Guthaben oder Zugänge das tatsächlich angewendete Ergebnis prüfen; Fehler nicht als „kein Datensatz“ interpretieren.

Für Datenbankrechte, TLS, Schlüsselwechsel und exaktes Signaturformat die [API-Sicherheitsanleitung](../../lt-database-api/docs/SECURITY.md) lesen. Sicherheitsprobleme über den privaten Kanal des betroffenen Produkt-Repositories melden; keine Secrets oder ausnutzbaren Details öffentlich posten.
