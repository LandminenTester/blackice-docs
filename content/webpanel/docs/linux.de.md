# Einrichtung

Referenz: Debian 13 (trixie), x86-64. Andere glibc-Systeme benötigen eine Bibliotheksprüfung. musl/Alpine und ARM werden nicht unterstützt.

`sudo apt install ca-certificates libicu76 libssl3t64 libstdc++6 zlib1g`

Paket entpacken und `./Start` ausführen. .NET und PTY-Helfer sind enthalten. Schlüssel aus `.local/supervisor.log` lesen und localhost:20772 öffnen. Linux sowie vorhandene Installation oder leeren Zielordner wählen.

Der OCI-Installer greift direkt auf die offizielle Registry zu, wählt linux/amd64, prüft SHA-256 und extrahiert nur `/opt/replay/seed`. Ein Docker-Daemon ist nicht erforderlich. Vorhandene Server benötigen ausführbares `REServer`, `cfg/server.cfg` und Schreibrechte. `LD_LIBRARY_PATH=/srv/replay ldd /srv/replay/REServer` darf keine fehlende Bibliothek melden.

Für systemd Benutzer `replay-panel` anlegen; `/var/lib/replay-panel` und `/srv/replay` diesem Konto mit 0700 zuordnen. Paket nach `/opt/replay-panel` entpacken, Dienstdateien aus `deploy` nach `/etc/systemd/system` kopieren und die obigen systemctl-Befehle ausführen. Beide Dienste müssen dieselbe UID und denselben Laufzeitpfad nutzen. Ein Stop des Webdiensts berücksichtigt den Abschaltmodus; ein Stop des Supervisors beendet dessen Spielserver.

## Interaktive Terminals

Das Releaseverzeichnis muss beschreibbar sein. Für SSH tmux, für Desktopfenster xterm installieren. Start ist direkt ausführbar und enthält die Laufzeit. Auf dem Desktop öffnet es ein Steuerterminal; der Spielserver erhält ein weiteres Fenster über x-terminal-emulator. Per SSH bleibt die Steuerung im aktuellen Terminal, der Server läuft in einer eigenen tmux-Sitzung. C hängt diese an; Strg+B, danach D, kehrt ohne Serverstop zurück. Das Schließen des Serverterminals beziehungsweise der Sitzung fordert einen geordneten Stop an. Start schließen, Strg+C oder Q beendet den ganzen Stack. Docker öffnet kein Serverfenster.
