# Bundle-Tools (Experimentell)

Optional, **standardmäßig aus**, nur im experimentellen Update-Kanal (Einstellungen → Updates). Aktivierung unter Einstellungen → Bundle-Tools oder im Setup-Assistenten.

- **Upload**: fertiges Bundle-ZIP hochladen, nur Strukturprüfung, Backup der alten Version.
- **Toolchain**: erkannte Host-Installationen von Git, .NET SDK 10 und Node.js mit npm können direkt verwendet werden. Die Anzeige unterscheidet Systemwerkzeuge und Panel-Kopien. Optionale private Kopien liegen unter `<state>/toolchain` und haben Vorrang; ihr Entfernen erhält die Systeminstallation. Ein vorhandenes WASI SDK wird aus `WASI_SDK_PATH` oder dem `.wasi-sdk`-Cache des Benutzers wiederverwendet, andernfalls beim ersten Build heruntergeladen.
- **Projekte**: neues Projekt aus Vorlage (optional ReUi mit Svelte, Vue oder React) oder Git-Repository importieren (GitHub, GitLab, Gitea/Forgejo/Codeberg), optional Remote-Repo anlegen.
- **Build**: Pull, Build, Pull & Build. Ausgabe in `<server>/data/ugc/<bundle>`, Quellen in `<server>/panel_src/<bundle>`. Rollback möglich.
- **Pakete**: installierte und verfügbare `replay.blackice.*`-Versionen prüfen; Updates über einen isolierten Änderungsbranch und eine Review-Anfrage vorschlagen.

## Arbeitsbereich

Projekte erscheinen als durchsuchbare kompakte Zeilen mit letztem Build, Branch-/Commit-Stand und einheitlichen UI-Badges. **Details** öffnet den zweispaltigen Bereich für Git-Refs, Paketversionen, Quellen und Branch-Merges. Erstellen und Importieren trennen Projektoptionen von Web-Paketen beziehungsweise Remotesuche. Optionale Vorlagenpakete: Zod, Lucide, TanStack Query, clsx, Day.js, Floating UI, Vitest und Prettier; fest gebundene Auswahl statt beliebiger Paketinstallation.

Import über gespeichertes Konto, Eigentümer und seitenweise Repositorysuche oder direkte HTTPS-Clone-Adresse. Beim Erstellen lässt sich ein persönlicher/Organisations-/Gruppeneigentümer wählen, soweit Provider und Token das erlauben. Upload trennt Metadaten und Installation von Strukturprüfungen. Jobausgabe bietet Suche, Folgen, Pause/Fortsetzen und Logdownload. Pause hält nur die Ansicht an; Builds laufen weiter. Originalausgabe bleibt reiner Text.

## Gemeinsame Git-Konten und Berechtigungen

Git-Konten gelten für die Serverinstallation. Eigene, eng auf die benötigten Repositories begrenzte Tokens verwenden. Tokens lassen sich im Dashboard weder anzeigen noch herunterladen. Verwaltung, Verwendung und Remote-Schreibzugriff sind getrennte Rechte; siehe [Berechtigungen](users.md).

Providerzugriff verwendet HTTPS. Tokens sind an die konfigurierte Provider-Adresse samt Pfad gebunden; bei einer Änderung des Ziels ist ein neuer Token nötig. Authentifizierte Provideraufrufe und Git folgen keinen Weiterleitungen. Verfügbare Organisationen/Gruppen und Repositories hängen von Mitgliedschaft, Provider und Tokenrechten ab; die endgültige Schreibberechtigung prüft der Provider.

## Branches zusammenführen und Paketupdates

Entwickler arbeiten auf ihren Rechnern und pushen Änderungen zum Git-Anbieter. Auf dem Entwicklungsserver wird der konfigurierte Branch mit **Pull & Build** aktualisiert; der Hauptserver nutzt seinen Produktionsbranch und wird separat bereitgestellt.

**Branches zusammenführen** bietet Quell- und Zielbranch aus der Remote-Auswahl. Vor der Aktion erscheinen Commit-Stände und Änderungen. Global gilt zunächst **Review-Anfrage**; **Direkter Merge** kann global oder pro Projekt erlaubt werden. Die alte Regel **Nur Branches** bleibt ohne Merge-Erlaubnis erhalten. Direkte Merges benötigen ein eigenes Recht und eine Bestätigung; der Anbieter prüft Branchschutz, Reviews und CI. Konflikte werden außerhalb des Panels gelöst. Kein Force-Push, automatischer Wiederholungsversuch, Branchlöschen oder Deployment. Eine abgelehnte Merge-Aktion kann eine offene Anfrage beim Anbieter hinterlassen.

Der Paketdialog prüft installierte und neueste gemeinsame Versionen. Aktuelle oder bestimmte Version samt Remote-Branch auswählen. Das Panel erstellt in einem temporären Checkout einen Änderungsbranch und eine Review-Anfrage; aktive Quellen und Bundle-Dateien bleiben unverändert. Ohne Remote und passenden Zugang ist die Prüfung nur lesend. Bei einem Fehler nach dem Push kann der Änderungsbranch beim Anbieter verbleiben.

Zustandsverwaltung: React ohne Zusatzbibliothek/Zustand/Jotai/Nano Stores; Vue ohne Zusatzbibliothek/Pinia/Nano Stores; Svelte lokale Runes/gemeinsamer Runes-Store/Nano Stores. Beispiele und Abhängigkeiten sind fest gebunden. Vue mit Nano Stores überspringt per `skipLibCheck` inkompatible Bibliotheksdeklarationen unter TypeScript 6; eigener Anwendungscode wird weiterhin geprüft.

## Kategorien, Autostart und Löschen

Bundle-Suche und Kategorienfilter teilen sich eine Werkzeugleiste mit dem Prüfzeitpunkt. Kategorien werden im Panelzustand gespeichert und überstehen Bundle-Updates.

**Autostart deaktivieren** erhält Dateien und laufenden Zustand. Manuelles Starten bleibt möglich. Exakte `start <bundle>`-Zeilen in der Startkonfiguration und statischen Includes werden gesichert und mit wiederherstellbaren Markierungen deaktiviert. Beim erneuten Aktivieren bleiben Text und Reihenfolge erhalten. Neue Startzeilen werden vor dem verwalteten Serverstart geprüft; deaktivierte Bundles werden nach einem Build nicht automatisch gestartet. Unklare, dynamische, externe oder verlinkte Konfigurationen werden abgelehnt. Konsolenberechtigte und externe Dateiänderungen können diese Regeln weiterhin außerhalb des Panels beeinflussen.

**Bundle löschen** verlangt eine ausdrückliche Umfangswahl und ein bestätigtes Stoppen. Standardmäßig verschwinden nur Laufzeitdateien; Projektquellen, Backups und persistente Daten bleiben. Quellen und eindeutig zugeordnete Backups lassen sich zusätzlich wählen. Datenlöschung wird nur für das exklusive lokale, nicht verlinkte Bundle-VFS angeboten; externe Mounts werden nicht entfernt. Gelöschte Dateien sind nicht über das Panel wiederherstellbar.

ZIP-Uploads prüfen den endgültigen Zielnamen erneut und fragen bei Kollisionen **Überschreiben oder Abbrechen**. Der Austausch stoppt das Bundle, sichert Laufzeitdateien und erhält Daten. Strukturprüfung bedeutet keine Sicherheitsprüfung des enthaltenen Codes.

Es wird nichts automatisch aktualisiert. Docker wird vollständig unterstützt (`git` im Image, Toolchain im `/state`-Volume). Builds führen Projektcode auf dem Host aus, siehe SECURITY.md.

Einstellungen → Bundle-Tools enthält drei Untertabs: **Allgemein** für Funktions- und Build-Einstellungen, **Build-Werkzeuge** für Erkennung und private Werkzeugkopien sowie **Git-Konten** für Repository-Zugänge. Der Schalter für die experimentelle Funktion bleibt darüber sichtbar. Die Untertabs unterstützen Links/Rechts sowie Pos1/Ende auf der Tastatur.

Die Erkennung läuft auf dem **Panel-Host** unter dessen Benutzerkonto, nicht im Browser. Docker erkennt Werkzeuge im Container, nicht auf dem Docker-Host. Ein Dienstkonto kann deshalb einen anderen PATH und WASI-Cache als das Desktop-Konto sehen. Die Erkennung wird bis zu 30 Sekunden zwischengespeichert; nach einer Installation den Untertab Build-Werkzeuge erneut öffnen. Eine .NET-Runtime ohne SDK 10 beziehungsweise Node.js ohne auffindbare npm-CLI reichen für Bundle-Builds nicht aus. Builds verwenden weiterhin eigene Home- und Paketcache-Verzeichnisse, auch mit Systemprogrammen.
