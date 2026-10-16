# Einrichtung

Windows 10 ab 1809, x86-64 und ConPTY verwenden. BlackICE benötigt eine CPU ab etwa 2013, mindestens 512 MB RAM nur für den Server (2 GB empfohlen) und mehrere GB Speicher.

1. Paket getrennt vom Server entpacken.
2. `Start.exe` öffnen. Das Steuerterminal bleibt offen.
3. `http://127.0.0.1:20772` öffnen, Schlüssel in `.local/supervisor.log` lesen.
4. Dashboardname, Benutzername und identische Passwörter mit mindestens 8 Zeichen festlegen.
5. Der Ordner `server` im Panel-Ordner wird automatisch angelegt; „Ordner ändern“ öffnet den System-Ordnerdialog. Vorhandene Server benötigen `REServer.exe` und `cfg/server.cfg`. Dateiformat und Schreibrechte werden geprüft.
6. Für den offiziellen Download einen leeren Ordner wählen. Der Installer arbeitet in einem temporären Verzeichnis mit Pfad- und Dateiprüfung. Abbruch und Wiederholung sind möglich; vorhandene Dateien bleiben erhalten.
7. Einrichtung abschließen und anmelden. Standardmäßig startet der Server automatisch; dies lässt sich unter Einstellungen ändern.

Beide Prozesse laufen unter demselben Konto. Start schützt `.local` für den Benutzer und SYSTEM. Private Zustandsdateien nicht veröffentlichen. Vor abgeschlossener Einrichtung erzeugt ein Supervisor-Neustart einen neuen Schlüssel.

`scripts/stop-web.ps1` beendet nur den Webhost. `scripts/control.ps1 -Action status|start|stop|restart|shutdown` bedient den Supervisor. Vor dessen Beenden den Spielserver stoppen. Für Autostart eine Aufgabe bei Benutzeranmeldung unter demselben Konto verwenden.

Windows-Adressargumente können vor der Winsock-Initialisierung scheitern. Stattdessen `sv_bindaddr "127.0.0.1:20770"` und `sv_voip_addr "127.0.0.1:20771"` in `cfg/server.cfg` eintragen.

## Direkter Terminalbetrieb

Start öffnet das Steuerterminal und für den verwalteten nativen Server ein eigenes Serverterminal. Q oder Strg+C im Startfenster beendet den gesamten Stack. Das X delegiert geordnetes Beenden an einen unabhängigen Prozess; bei Fehlern .local/controller-stop.log prüfen. Das Serverterminal per X oder mit exit zu schließen stoppt nur den Spielserver. Unter Einstellungen → Server mit dem Panel starten wird Autostart festgelegt. K lässt Dienste ausdrücklich weiterlaufen, W beendet nur den Webhost nach dessen Abschaltmodus. Für unbeaufsichtigten Betrieb Dienst-/Hintergrundstart verwenden.
