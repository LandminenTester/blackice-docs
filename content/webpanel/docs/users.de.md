# Benutzer und Berechtigungen

Berechtigungen bestimmen, welche Aktionen ein Konto im Panel ausführen darf. Verwende eigene Konten pro Person, damit du einzelne Zugänge ändern oder sperren kannst. Die Rechte begrenzen nicht das Betriebssystemkonto oder die native Spielserver-Konsole.

## Konto anlegen

1. Mit einem Konto anmelden, das **Benutzer verwalten** darf.
2. **Benutzer** öffnen und ein Konto anlegen.
3. Benutzername mit 3–32 Buchstaben, Zahlen, Punkten, Unterstrichen oder Bindestrichen wählen; das erste Zeichen muss ein Buchstabe oder eine Zahl sein.
4. Passwort mit 8–256 Zeichen vergeben.
5. Nur die benötigten Berechtigungen auswählen und speichern.

Bestehende Konten lassen sich bearbeiten oder deaktivieren. Ein leeres Passwortfeld behält das bisherige Passwort. Löschen erfordert eine Bestätigung. Mindestens ein aktives Konto muss **Benutzer verwalten** behalten.

## Administratoren

Der ursprüngliche Administrator behält alle Rechte. **Super-Admin** wählt im Editor sämtliche Berechtigungen aus und sperrt die einzelnen Schalter. Das ist vollständiger Zugriff, keine eingeschränkte Betreiberrolle.

Kontoänderungen beenden bestehende Sitzungen und offene Eventstreams dieses Kontos. Ältere Installationen übernehmen beim ersten Bearbeiten die ursprünglichen gesalzenen Passwort-Hashes. Nach älteren Versionsupdates erneut anmelden. Passwort-Hashes werden nicht an den Browser ausgegeben. Private Konfiguration und Verschlüsselungsschlüssel gemeinsam sichern.

## Grundberechtigungen

| Berechtigung | Erlaubt |
| --- | --- |
| Server starten / stoppen / neustarten / erzwungen stoppen | Jede Aktion getrennt |
| Konsole lesen / schreiben | Ausgabe sehen / rohe Spielserverbefehle ausführen |
| Logs lesen | Logdateien ansehen und herunterladen |
| Bundles sehen | Installierte und geladene Bundles auflisten |
| Bundles starten / stoppen / neustarten | Jeweilige Aktion; zusätzlich Bundles sehen erforderlich |
| Einstellungen ändern | Start-, Abschalt- und allgemeine Panel-Einstellungen |
| Benutzer verwalten | Konten und deren Berechtigungen verwalten |

**Konsole schreiben ist weitreichend.** BlackICE-Befehle können Bundles und Spielzustände verändern. Wer nur Bundles neu starten soll, erhält Bundle-Rechte ohne Konsolenschreibzugriff. Jeder angemeldete Benutzer sieht den Prozessstatus und darf die eigene Oberflächensprache ändern.

## Entwickler- und Bundle-Tool-Rechte

Der Editor gruppiert die Rechte nach Server, Konsole/Logs, Bundle-Betrieb, Projekte/Git, Werkzeuge/Konten und Administration. Experimentelle Bundle-Tools benötigen zusätzlich den Feature-Hauptschalter.

| Berechtigungs-ID | Aktion |
| --- | --- |
| `bundles.upload` | Kompiliertes Bundle-ZIP prüfen und installieren |
| `bundles.build` | Quellen verwalten, vertrauenswürdige Builds ausführen und Buildlogs lesen |
| `bundles.settings` | Feature-/Build-Einstellungen und Projekt-Workflow ändern |
| `bundles.tools` | Panelverwaltete Build-Werkzeuge prüfen, installieren und entfernen |
| `bundles.accounts.manage` | Gemeinsame Git-Zugangsdaten anlegen, ersetzen, testen und entfernen |
| `bundles.accounts.use` | Gemeinsame Zugangsdaten für erlaubte Repository-Aktionen nutzen |
| `bundles.git.write` | Remote-Repositories erstellen und beschreiben |
| `bundles.review` | Review-Anfragen beim Anbieter erstellen |
| `bundles.merge` | Explizit direkt auf dem Remote zusammenführen |
| `bundles.packages` | Isolierte Paketänderungen vorschlagen |
| `bundles.autostart` | Verwaltete Start-Einträge ändern |
| `bundles.tags` | Serverweite Kategorien ändern |
| `bundles.delete` | Bundle-Laufzeitdateien und ausgewählte Backups löschen |
| `bundles.sources.delete` | Lokale Projektquellen löschen |
| `bundles.data.delete` | Geprüfte exklusive lokale Bundle-Daten löschen |

Remote-Erstellung und Auslieferung brauchen **Build + Kontonutzung + Git-Schreiben** zusammen. Remote-Git-Aktionen benötigen zusätzlich das konkrete Aktionsrecht. Paketvorschläge brauchen außerdem **Pakete + Review**. Löschen erfordert Lesen, Löschen und Stoppen sowie bei erweitertem Umfang Quellen-/Datenlöschrechte. Normale Git-Schreibrechte vergeben Merge und Löschen nicht automatisch.

## Gemeinsame Konten und Vertrauen

Git-Konten gehören zur Serverinstallation. Ein bekannter Kontoname gewährt keinen Zugriff; Verwaltung und Nutzung werden getrennt geprüft. Tokens sind verschlüsselt gespeichert und werden nie von der API an den Browser geliefert. Benutzerverwaltung kann diese Rechte vergeben und ist selbst eine Vertrauensposition.

Buildrechte führen Projektcode mit den Rechten des Panel-Betriebssystemkontos aus. Sie sind für vertrauenswürdige Entwickler gedacht. Vor Aktivierung die [Sicherheitsgrenze](../SECURITY.md#bundle-tools-experimental) lesen.
