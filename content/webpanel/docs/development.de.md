# Entwicklung

Voraussetzungen: Git, .NET SDK 10.0.401 aus global.json, Node 24.19.0 und npm. Linux benötigt zusätzlich cc, libc-Header und libutil. VS Code mit C#- und Svelte-Erweiterung eignet sich als Editor.

Die einzelnen Windows-/Linux-Befehle aus [Builden](building.md) im offenen Terminal ausführen. Buildskripte sind optionale Hilfen. Paketversionen mit `npm --prefix ui ci` wiederherstellen; .NET-Lockdateien sind versioniert. Vor dem Build `npm --prefix ui run check` ausführen.

`IServerBackend` definiert Status, Start, Stop/Force, Befehl, Konsole und Logs. Plattformintegration gehört in den Supervisor. Der Webhost greift weder auf Spieldateien noch auf Docker Engine zu. BundleManager serialisiert Abfragen und Aktionen, begrenzt Antworten durch Echo-Marker und wartet auf echte Lebenszyklusereignisse. Geladene Bundles können gestoppt sein.

Die interne Verbindung nutzt JSON-Zeilen, Benutzer-Pipes unter Windows und Unix-Sockets mit 0600 unter Linux. Der Supervisor besitzt Einrichtungsschlüssel, Passwort-Hashes, Dateiprüfung und Installationsaufträge.

`ui/src/locales.ts` definiert englische Schlüssel und erzwingt die vollständige deutsche Übersetzung. Jeder neue Fehlercode muss in beiden Katalogen stehen. BlackICE-Logs, Benutzer- und Bundlenamen werden nicht übersetzt. Komponenten in `ui/src/components` müssen Tastaturbedienung, Fokus und reduzierte Bewegung erhalten.

Die oben aufgeführten Tests verwenden eigene Ports, Prozesse und Ordner. Niemals Produktionsverzeichnisse an Fixturetests übergeben. Offizielle Downloads hängen von der Anbietererreichbarkeit ab. Releases enthalten Windows-/Linux-Laufzeit, PTY-Helfer, Dokumentation und Skripte; Docker verwendet getrennte Dienste und ein versioniertes Image.
