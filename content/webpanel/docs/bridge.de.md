# LAN-Bridge und Diagnose

Standardmäßig bleibt PTY aktiv. Unter Einstellungen **LAN-Bridge** aufklappen, einen freien internen Port wählen (20774), speichern und ausdrücklich neu starten. Aktuelle offizielle Serverdateien sind erforderlich. **--mcp erzwingt sv_lan 1; der Server erscheint nicht in der öffentlichen Liste.** cfg/server.cfg wird nicht verändert. Öffentliche Server behalten PTY.

Windows/Linux verwenden nur localhost. Docker nutzt ein privates instanzeigenes Netz ohne veröffentlichten Bridge-Port. Beim bestätigten Wechsel wird der gestoppte verwaltete Spielcontainer neu erstellt; Speicher bleibt, alter Container und private Definition bleiben für Wiederherstellung erhalten.

Dashboard zeigt Verbindung, Health, Phase, Commit, Tick, letzte Antwort und Prozessende. Empfangszeit ist eine Beobachtung des Panels. Sequenznummern, Module, Quellen und erkennbare Lücken bleiben erhalten. Filter, Pause, Historie und Download beachten bestehende Rechte. Download enthält bis zu 2000 angezeigte gefilterte Zeilen. Historie bleibt lokal: standardmäßig sieben Tage / insgesamt 100 MB, konfigurierbar. Es erfolgt kein externer Versand.

Bei Verbindungsproblemen bleiben PTY und Prozessverwaltung verfügbar. Schreibbefehle werden nach Timeout nicht erneut gesendet; Zustand vor erneutem Versuch prüfen. Für öffentlichen Bridge-Betrieb muss zuerst ein offizieller Parameter unterstützt und getestet werden. Testclients sind eine spätere Erweiterung.

## Wiederherstellung

## Docker nach einer Bridge-Änderung wiederherstellen

Zuerst Supervisor und Webhost stoppen. Privates Backup `docker-before-bridge-*.json` und Instanzlabel prüfen. Der alte gestoppte Container bleibt unter einem `-previous-`-Namen erhalten. Ersatzcontainer stoppen, die alte Container-ID in der privaten `panel.json` und bei Bedarf den ursprünglichen Namen wiederherstellen, `Bridge.Enabled` deaktivieren und den Stack neu starten. Server-Mount und Zustand erhalten. Alten und neuen Container nicht gleichzeitig starten, da beide dieselben Spielports verwenden. Diese Wiederherstellung ist lokale Administratorarbeit; das Dashboard bietet keine freie Auswahl beliebiger Container.
