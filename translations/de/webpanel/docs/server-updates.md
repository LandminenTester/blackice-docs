# REServer-Updates

Unter Einstellungen → REServer-Updates die offizielle Alpha-Version prüfen, Dateien vorbereiten und anschließend mit Bestätigung installieren. SHA-256-Prüfung, geordneter Stop, Sicherung und Wiederherstellung bei Startfehlern sind enthalten. Ein zuvor laufender Spielserver startet wieder; ein gestoppter bleibt gestoppt. Das Panel bleibt erreichbar.

Gezielte Auswahl: aktuelles offizielles Alpha und frühere vom Panel gesicherte Builds. Beliebige historische Commits werden nicht als herunterladbar dargestellt, da dafür kein offizieller Katalog bestätigt wurde. Ein alter Windows-ZIP-Seed kann zunächst aktualisiert werden, um die Bridge-Module zu erhalten.

Spielkonfiguration, Einstellungen, Bundles/VFS und Logs bleiben erhalten. Das gilt auch für Dateien im dauerhaften Docker-Servermount. Prüfen benötigt settings.write; Vorbereitung und Installation zusätzlich users.manage. Schreibaktionen werden während der Installation gesperrt. Vor dem Installieren kann der Download abgebrochen werden.

Sicherungen unter privatem state/server-updates bleiben für gezielte Wiederherstellung erhalten; genügend Speicher für Stage und Backup vorsehen. Unterbrochene Vorgänge prüfen. Bei fehlgeschlagener Wiederherstellung Stack stoppen und verwaltete Laufzeitdateien aus dem Backup zurückkopieren; keine privaten Spielverzeichnisse überschreiben.
