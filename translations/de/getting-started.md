# Erste Schritte

Wähle zuerst die Ressource, die du verwenden möchtest. Du brauchst nicht alle Ressourcen dieser Bibliothek.

## Einen Server im Browser verwalten

Das **BlackICE Server Panel** verwaltet einen Spielserver: Start und Stop, Live-Konsole, Logs, Benutzer und Bundles. Beginne mit der [Übersicht](webpanel/README.md) und der Anleitung für [Windows](webpanel/docs/windows.md), [Linux](webpanel/docs/linux.md) oder [Docker](webpanel/docs/docker.md). Das Panel benötigt weder lt_database noch die Datenbank-API.

## Daten aus einem eigenen Bundle speichern

Verwende **lt_database** zusammen mit **lt-database-api**. Dein Server-Bundle ruft den Connector auf; dieser schickt signierte Anfragen an die API. Nur die API verbindet sich mit der eigentlichen Datenbank. Beginne mit dem [Datenbank-Schnellstart](database-quickstart.md).

Der Bundle-Ordner heißt `lt_database`, die gemeinsamen C#-Typen liegen in `LtDatabase` und der Helper in `LtDatabaseClient`. Konsolenbefehle beginnen mit `lt-db-`. Starte den Connector vor allen Bundles, die ihn verwenden.

## Nur die Datenbank-API verwenden

Die API kann auch von anderen HTTP-Clients verwendet werden. Lies [Bereitstellung](lt-database-api/docs/DEPLOYMENT.md), [HTTP-Referenz](lt-database-api/docs/API.md) und [Signaturen](lt-database-api/docs/SECURITY.md). Ein unsignierter Datenbankaufruf wird nicht akzeptiert.

## Die passende Lesereihenfolge

1. Installation und Voraussetzungen prüfen.
2. Konfiguration für deine Umgebung eintragen.
3. Den dokumentierten Verbindungstest ausführen.
4. Ein kleines Beispiel nachvollziehen und erst danach an eigene Ereignisse anbinden.
5. Referenz, Betrieb und Sicherheit für den produktiven Einsatz lesen.

Unbekannte Abkürzungen stehen im [Begriffsverzeichnis](glossary.md). Fehler am Produkt bitte im jeweiligen Repository melden; Dokumentationsänderungen sind unter [Quellen und Pflege](sources.md) beschrieben.
