# Einrichtung

Linux x86-64 mit Docker Engine und Compose v2. Webhost und Supervisor sind getrennt; nur der Supervisor erhält den Docker-Socket.

Zuerst das versionierte Docker-Archiv aus dem öffentlichen GitHub-Release laden und mit `gzip -dc blackice-server-panel-docker.tar.gz | docker load` importieren. Damit liegt das passende Compose-Image ohne Registryanmeldung lokal vor.

1. `deploy/compose.env.example` als private `.env` kopieren. Absolute Pfade für `PANEL_STATE`, `PANEL_RUNTIME` und `SERVER_PATH` festlegen. `DOCKER_GID` mit `stat -c %g /var/run/docker.sock` ermitteln.
2. Hostordner anlegen, UID/GID 10001 und 0700 zuordnen. Serverordner für Installation leer lassen.
3. `docker compose --env-file .env -f deploy/compose.yaml up -d` ausführen.
4. Schlüssel mit `docker compose --env-file .env -f deploy/compose.yaml logs supervisor` lesen und localhost:20772 öffnen.
5. Docker, offiziellen Download und eingebundenen Ordner `/server` wählen.

Der Supervisor lädt `ghcr.io/replayre/server` und erstellt seinen Container mit TTY/stdin, dauerhaftem Speicher, LAN-Konfiguration und deaktivierten Updates. Vor Steuerungsaktionen werden vollständige ID und Zugehörigkeitslabel geprüft. `REPLAY_PANEL_HOST_SERVER` muss dem Pfad auf dem Dockerhost entsprechen. Spiel/Voice nutzen 20770/20771 TCP und UDP.

Lokal mit `docker build -t replay-panel:local .` bauen und beide Imagefelder in einer privaten Compose-Kopie ersetzen. Feste Releaseversionen verwenden. Der Docker-Socket erlaubt dem Supervisor weitreichende Hostzugriffe; intern halten und niemals dem Webhost zuweisen. Beide Dienste verwenden UID 10001, nur der Supervisor bekommt zusätzlich die Socketgruppe.

Für keep-running nur `docker compose ... stop web` ausführen. Supervisor-Stop beendet auch den Spielserver. Host-Serverdateien und privaten Panelzustand sichern.
