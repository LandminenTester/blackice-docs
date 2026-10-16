# Serverkonfiguration

**Einstellungen → Serverkonfiguration** bearbeitet die wichtigsten Schlüssel der `cfg/server.cfg`: `sv_name`, `sv_desc`, `sv_region` (ISO-3166-1-alpha-3-Ländercode, per Liste), `sv_dlc`, `sv_bindaddr`, `sv_endpoint` und `sv_lan`. Kommentare und alle anderen Zeilen bleiben unverändert, ebenso die Zeilenenden. Beim ersten Speichern entsteht `cfg/server.cfg.panel.bak`. Änderungen gelten nach einem Serverneustart. Erfordert die Berechtigung `settings.write`. Name und Beschreibung dürfen keine Anführungszeichen oder Backslashes enthalten.

## Weitere Schlüssel und Log-Archiv

Der Editor verwaltet zusätzlich `sv_voip_addr`, `sv_privacy`, `sv_ugc_automatic_restarts` sowie in `settings/server.settings.json` `channel`, `auto_update` und `restart_after_update` (Container überschreiben sie über die Umgebungsvariablen `CHANNEL`, `AUTO_UPDATE` und `RESTART_AFTER_UPDATE`). Die Region ist eine tippbare Liste mit ISO-3166-1-alpha-3-Codes. **Konsole → Log-Archiv** listet die Dateien aus `logs/` nach Tag und Serverstart, zeigt eine Datei an und lädt alle Logs als ZIP herunter (Berechtigung `logs.read`).

## Bundle-Details, Start-Log und Update-Prüfung

Die Bundle-Liste zeigt `author`, `version` und `description` aus der optionalen Tabelle `[General]` der `config.toml` jedes Bundles. **Konsole → Komplettes Log herunterladen (dieser Start)** speichert die vollständige Server-Logdatei des aktuellen (oder letzten) Serverstarts; das Log-Archiv listet ältere Starts. **Einstellungen → Allgemein → Automatisch nach Updates suchen** legt fest, ob das Panel GitHub und artifacts.replay.re selbstständig kontaktiert; ist es aus, wird nur beim Klick auf eine Prüfen-Schaltfläche geprüft.
