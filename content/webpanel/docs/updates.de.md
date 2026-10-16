# Updates über das Dashboard

Unter **Einstellungen → Panel-Updates** prüft das Panel das neueste stabile öffentliche Release von LandminenTester/blackice-server-panel. Installierte/neue Version und Releasehinweise werden angezeigt. Prüfungen werden eine Minute zwischengespeichert; ein GitHub-Token ist nicht erforderlich. Entwürfe und Vorabversionen werden ausgeschlossen.

**Herunterladen und prüfen** lädt das passende Windows-x64-ZIP beziehungsweise Linux-x64-tar.gz. Der Supervisor prüft Paketlänge und GitHubs SHA-256-Wert, verwirft unsichere Pfade/Links und prüft Plattformdateien und VERSION. Das laufende Paket bleibt währenddessen erhalten. Fortschritt und Abbruch sind verfügbar.

Nach erfolgreicher Prüfung **Installieren und neu starten** auswählen und die Unterbrechung bestätigen. Eine Kopie des bisherigen Updaters läuft außerhalb der auszutauschenden Installation. Sie beendet den verwalteten Server, Webhost, Supervisor und das Steuerterminal, sichert Artefakte/Start/Konfiguration, tauscht das vorbereitete Paket aus und öffnet ein neues Startterminal. Für den Spielserver gilt die Autostart-Einstellung. Konfiguration, Sitzungsschlüssel, Benutzer, Spieldateien und Bundles bleiben erhalten. Updates werden nicht unbeaufsichtigt installiert.

Zum Prüfen wird **Einstellungen ändern** benötigt; Herunterladen/Installieren benötigt zusätzlich **Benutzer verwalten**. Direkte Installation ist nur für native Pakete mit geöffnetem Startterminal aktiviert. Docker- und systemd-Betrieb zeigen den Versionscheck, werden aber mit Compose beziehungsweise den Dienstwerkzeugen aktualisiert. Das Dashboard ersetzt keinen unveränderlichen Container und erhält keinen Zugriff auf den Host-Dienstmanager.

Per SSH läuft das neue Steuerterminal als tmux-Sitzung; mit `tmux list-sessions` anzeigen und an `replay-panel-<Instanzpräfix>` anhängen.

Die neue Version muss Versions- und Webbereitschaftsprüfungen bestehen. Scheitert ihr Start, wird das alte Paket automatisch wiederhergestellt. Währenddessen ist die Browserverbindung kurz unterbrochen; die Seite verbindet sich erneut und liest das gespeicherte Ergebnis. Bei Problemen Start öffnen und folgende Dateien prüfen:

- `.local/panel-update.json`: letzter Auftrag und Ergebnis.
- `.local/updates/<Auftrag>/apply.log`: Installations-/Wiederherstellungslog.
- `.local/updates/<Auftrag>/backup`: bisherige Artefakte, Start, VERSION und Konfiguration.

Sicherungen behalten, bis die neue Version funktioniert. Zur manuellen Wiederherstellung verbliebene Panelprozesse mit dem direkten Stopbefehl beenden, fehlgeschlagene Artefakte/Start zur Seite verschieben und die Sicherung zurückkopieren. panel.json nur bei gescheiterter Konfigurationsmigration zurückspielen; das Schlüsselverzeichnis behalten. Anschließend Start öffnen. Falls der Stopbefehl scheitert, vor dem Dateiaustausch Prozessidentitäten prüfen. Keine Paneldateien in den Spielserverordner kopieren.

VERSION muss beim Releasebau der Assemblyversion aus Directory.Build.props entsprechen. Die CI liefert diese Datei mit und prüft Austausch sowie Wiederherstellung unter Windows und Linux. Version 0.5.1 verwendet den alten Repositorynamen und kann umbenannte Release-Artefakte nicht prüfen. 1.0.0 einmal manuell installieren und .local erhalten; spätere native Releases lassen sich über das Dashboard installieren.

### Update-Kanäle

**Einstellungen → Updates → Update-Kanal** wählt den Release-Strom. **Stabil** (Standard) bietet nur normale Releases an. **Experimentell** bietet zusätzlich Vorabversionen mit dem Tag `vX.Y.Z-experimental.N` an; sie enthalten neue, unfertige Funktionen und können instabil sein. Ein stabiles Release, das eine Vorabversion ablöst, wird ebenfalls angeboten. Der Wechsel zurück zu Stabil führt kein Downgrade durch, es werden nur keine Vorabversionen mehr angeboten. Vorabversionen sind im Panel und auf GitHub mit **Experimentell** markiert (nie als „Latest“), nutzen dieselbe SHA-256-Prüfung samt automatischem Rollback; Docker-Nutzer wählen die genaue Image-Version selbst.
