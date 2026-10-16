# Quellen und Pflege

Diese Dokumentation liegt in [LandminenTester/blackice-docs](https://github.com/LandminenTester/blackice-docs). Die Brewery-Skriptdokumentation bleibt separat in [LandminenTester/docs](https://github.com/LandminenTester/docs).

## Zuständigkeiten

Die englischen Produktanleitungen werden in den jeweiligen Produkt-Repositories gepflegt. [sources.json](sources.json) nennt die importierten Commit-Versionen. Der Importer akzeptiert nur unveränderte, bereits commitete Quellen und übernimmt ausschließlich freigegebene öffentliche Dateien.

Gemeinsame Einstiegsseiten werden hier bearbeitet. Geprüfte deutsche Übersetzungen liegen in `translations/de/` und werden nach dem Import als `content/*.de.md` eingesetzt. Vorhandene zweisprachige Panel-Seiten werden in getrennte Sprachdateien zerlegt. Bezeichner in Code und Konfiguration werden nicht übersetzt.

## Sprachen

Englisch liegt unter `/` und ist immer die Standardsprache. Deutsch liegt unter `/de/`. Die Sprachauswahl führt zur entsprechenden Seite; die Browsersprache löst keine automatische Umleitung aus. Die Suche zeigt Ergebnisse in der ausgewählten Sprache. Navigation, Schaltflächen und Fehlermeldungen verwenden einen eigenen Übersetzungskatalog.

Alle Seiten der Navigation haben eine deutsche Fassung. Fehlt bei einer zukünftigen Seite die Übersetzung, zeigt ein Hinweis ausdrücklich die englische Referenz an. Bei Änderungen beide Fassungen und verlinkte Anker prüfen.

## Prüfen und veröffentlichen

Die [Repository-Anleitung](https://github.com/LandminenTester/blackice-docs#build-and-preview) erklärt den lokalen Build. GitHub Actions prüft Links, Sprachabdeckung und die Übereinstimmung des Beispiels mit dem kompilierten Quellcode und veröffentlicht `main` auf GitHub Pages. Die Domain lautet `blackice.landminentester.de`.

Für GitBook lassen sich getrennte englische und deutsche Inhaltsbäume exportieren. GitBook übernimmt Markdown und Navigation; das Cyberpunk-Theme dieser Website wird durch MkDocs auf GitHub Pages gerendert. GitBook-eigene Gestaltung und Domains werden dort eingestellt.

Importierte Texte behalten ihre ursprünglichen Lizenzen. Produktfehler gehören in das jeweilige Repository, Sicherheitsmeldungen in dessen privaten Meldekanal.
