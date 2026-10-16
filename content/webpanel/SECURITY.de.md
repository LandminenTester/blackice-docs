# Security policy

Überwiegend KI-gestützt entwickelt, menschlich geprüft und getestet; keine unabhängige Sicherheitsprüfung. Betreiber beurteilen den Einsatz selbst. Schwachstellen über den privaten GitHub-Link oben melden: Versionen, Plattform, minimale Reproduktion, Auswirkungen und bereinigte Nachweise angeben. Keine Zugangsdaten oder ausnutzbaren Details öffentlich posten. Die neueste stabile Version wird unterstützt; es gibt keine garantierte Reaktionszeit. Reviews und gemeinsame Behebung sind willkommen.

### Härtung

- **Setup-Key.** Bis der erste Administrator existiert, schützt ein zufälliger 8-stelliger Key `/api/setup/*`; er steht nur in der Supervisor-Konsole und in `.local/supervisor.log`. Das Browser-Terminal zeigt ihn **nur, wenn das Panel auf demselben Computer geöffnet wird** (Loopback, keine Proxy-Header, Host `localhost`/`127.0.0.1`); Fernzugriff muss ihn in der Konsole lesen. Fünf falsche Keys machen ihn ungültig und erzeugen einen neuen; die Setup-Endpunkte sind zusätzlich ratenbegrenzt. Setup abschließen, bevor der Port erreichbar gemacht wird.
- **Docker-Socket.** Der Docker-Modus gibt dem **Supervisor** Zugriff auf `/var/run/docker.sock`, was auf dem Host Root-Rechten entspricht. Der Code berührt nur selbst angelegte, mit der Instanz-ID markierte Container und Netzwerke, ein kompromittierter Supervisor könnte den Socket aber missbrauchen. Panel nur auf vertrauenswürdigen Hosts betreiben, den Supervisor nie veröffentlichen und für eine strengere Grenze einen filternden Proxy wie [`tecnativa/docker-socket-proxy`](https://github.com/Tecnativa/docker-socket-proxy) vor den Socket setzen (nur Container-, Netzwerk- und Image-Endpunkte erlauben) oder Rootless-Docker/Podman nutzen. Ein eingebauter Filter wäre wirkungslos, weil jede Komponente im Supervisor denselben Zugriff bereits besitzt.
- **Server-Binary.** Unter Linux führt die Prüfung `ldd` auf der gewählten `REServer`-Datei aus, nachdem sie als nicht gruppen-/weltbeschreibbar bestätigt wurde. Das Panel startet diese Datei ohnehin; nur vertrauenswürdige Dateien auswählen.
- **Updates.** Panel- und Server-Updates werden gegen SHA-256-Prüfsummen geprüft (Integrität), nicht gegen eine Herausgeber-Signatur. Release-Dateien enthalten `SHA256SUMS.txt` und eine GitHub-Build-Provenance-Attestierung; prüfen mit `gh attestation verify <Datei> --repo LandminenTester/blackice-server-panel`. Automatische Update-Prüfungen (GitHub, artifacts.replay.re) lassen sich unter **Einstellungen → Allgemein** abschalten.
- **Konsolenzugriff.** Wer *Konsole schreiben* hat, kann beliebige REServer-Befehle senden; nur an vertrauenswürdige Betreiber vergeben.

## Bundle-Tools (experimentell) {#bundle-tools-experimental}

Bundle-Tools sind standardmäßig aus. **Ein Build führt Code aus und ist keine Sandbox.** MSBuild, Analyzer und Web-Builds laufen mit den Rechten des Panel-Betriebssystemkontos. Fremder Projektcode kann dessen erreichbare Dateien einschließlich Panelzustand und Token-Schlüsseln lesen. Buildrechte nur vertrauenswürdigen Entwicklern geben, Tokens eng begrenzen, das Panel mit einem eingeschränkten Betriebssystemkonto betreiben und Entwicklung vom Live-Server trennen.

Git-Konten gehören zur **Serverinstallation**, nicht einzelnen Panelbenutzern. Tokens werden verschlüsselt gespeichert, nicht an den Browser zurückgegeben und in Joblogs geschwärzt. Verwaltung, Nutzung und Repository-Schreibzugriff sind getrennte Berechtigungen. Das verhindert keinen Zugriff durch privilegierte Betriebssystembenutzer oder bösartigen Buildcode. Zustand und Schlüssel gemeinsam geschützt sichern; bei Verdacht Tokens widerrufen und privat melden. Details in [Bundle-Tools](docs/bundle-tools.md) und [Berechtigungen](docs/users.md).


## Remote-Aktionen und Bundle-Lebenszyklus

Direktes Zusammenführen, Review-Anfragen, Paketvorschläge, Autostart, Kategorien und Löschen haben getrennte serverseitige Rechte. Nach unklaren Fehlern werden Remote-Schreibvorgänge nicht automatisch wiederholt. Beim Löschen bleiben Daten standardmäßig erhalten; optionale Datenlöschung ist auf den verifizierten exklusiven lokalen VFS-Ordner ohne Verknüpfungen begrenzt. Vor nicht umkehrbaren Aktionen Backups anlegen. Neue APIs behalten Origin-Prüfung, Zielkontrolle, CSRF und bereinigte Klartextlogs bei.
