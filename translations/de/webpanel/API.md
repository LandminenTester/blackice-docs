# Panel-HTTP-API

Die Browseroberfläche verwendet eine Cookie-authentifizierte API auf derselben Origin wie das Panel, standardmäßig `http://127.0.0.1:20772`. Es gibt keine API-Key-Anmeldung für das Panel. Diese interne Anwendungsschnittstelle kann sich zwischen Releases ändern.

Die maßgeblichen Handler stehen in [Program.cs](https://github.com/LandminenTester/blackice-server-panel/blob/main/src/Web/Program.cs) und [BundleToolsEndpoints.cs](https://github.com/LandminenTester/blackice-server-panel/blob/main/src/Web/BundleToolsEndpoints.cs). Für Integrationen die Revision in [sources.json](../sources.json) verwenden.

## Anmeldung, CSRF und Ergebnisse

`GET /api/session` liefert `authenticated`, `username`, `permissions`, `csrf` und setzt das CSRF-Cookie. **Jeder POST**, auch Login und Setup, braucht dieses Cookie und den Token im Header `X-CSRF`.

`POST /api/login` erhält `username`, `password`, `remember` und setzt das HttpOnly-Cookie `replay-panel-session`. Eine normale Sitzung endet nach vier Stunden ohne gleitende Verlängerung; „angemeldet bleiben“ verwendet ein 30-Tage-Ticket. Kontoänderungen können bestehende Sitzungen widerrufen. Logout erfolgt über `POST /api/logout`.

Viele Änderungen liefern `Reply` mit `ok`, optional `error`, `status`, `lines`; manche Datenrouten liefern direkt ausgepackte JSON-Daten. `GET /api/status` enthält einen Reply mit `status`. Nicht für alle GETs dieselbe Form voraussetzen.

| HTTP | Bedeutung |
| --- | --- |
| 200 | Anfrage erfolgreich; `ok` und gegebenenfalls Jobstatus prüfen |
| 400 | Host, CSRF oder Eingabe ungültig |
| 401 | Anmeldung fehlgeschlagen oder Sitzung fehlt/abgelaufen |
| 403 | Berechtigung fehlt |
| 404 | Ressource fehlt |
| 409 | Konflikt, deaktiviertes Feature oder Update läuft |
| 429 | Ratenlimit |

Fehler verwenden Lokalisierungsschlüssel wie `csrf.invalid` oder `bundleTools.disabled`. Remote-Zugriff benötigt die [HTTPS-/Proxy-Konfiguration](docs/operations.md).

## Browserbeispiel

Dieser Code gehört in eine Integration auf derselben Panel-Origin. Zugangsdaten gibt der Benutzer über deren Login-Oberfläche ein. Die englischen Codebezeichner bleiben identisch:

```javascript
async function session() {
  const response = await fetch('/api/session', { credentials: 'same-origin' });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
async function post(path, body) {
  const { csrf } = await session();
  const response = await fetch(path, {
    method: 'POST', credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', 'X-CSRF': csrf },
    body: JSON.stringify(body)
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  return response.json();
}
// After the user logs in:
const state = await (await fetch('/api/status')).json();
console.log(state.status);
// With console.write permission, a read-only game console command:
// await post('/api/command', { text: 'bundles' });
```

## Kernrouten

| Methode und Pfad | Eingabe / Ausgabe | Berechtigung |
|---|---|---|
| `GET /api/session` | Sitzungsstatus und CSRF-Token | Öffentlich |
| `GET /api/bootstrap` | Einrichtungsdaten | Öffentlich |
| `POST /api/login` | `{username,password,remember}` | Öffentlich, ratenbegrenzt |
| `POST /api/logout` | Leeres JSON | Angemeldet |
| `GET /api/status` | Reply mit Serverstatus, Prozess-ID und Serverordner | Angemeldet |
| `POST /api/server/{action}` | `start`, `stop`, `restart`, `force-stop` | Passendes `server.<action>` |
| `POST /api/command` | `{text}` Konsolenbefehl | `console.write` |
| `GET /api/bundles` | Bundle-Liste | `bundles.read` |
| `POST /api/bundles/{name}/{action}` | `start`, `stop`, `restart` | `bundles.read` und passendes `bundles.<action>` |
| `GET /api/logs` | Aktuelle Konsolen-/Logausgabe | `logs.read` |
| `GET /api/log-files` | `{name,size,modified,started}` Liste | `logs.read` |
| `GET /api/log-files-current` | Aktuelle Logdatei herunterladen | `logs.read` |
| `GET /api/log-files/{name}` | Letzte 2 MiB einer Logdatei | `logs.read` |
| `GET /api/log-files.zip` | ZIP-Download | `logs.read` |
| `GET /api/diagnostics` | Abfrageparameter `cursor`, `source`, `module`, `search`, `limit`, `history` | `console.read` und/oder `logs.read` abhängig von der Quelle |
| `GET /api/events` | Server-Sent Events: Status, Konsole und Rechte | Angemeldet; Konsole erfordert `console.read` |
| `GET /api/bridge` | LAN-Bridge-Status | Angemeldet |
| `POST /api/bridge/settings` | `{enabled,port,retentionDays,maxMegabytes}` | `settings.write` |
| `POST /api/settings` | `{shutdownMode,autoStartServer,locale,autoUpdateChecks,updateChannel}` | Angemeldet; alle Felder außer locale erfordern `settings.write` |
| `GET /api/server-name` | `{name}` | Angemeldet |
| `GET /api/server-config` | Bearbeitbare Serverkonfiguration | `settings.write` |
| `POST /api/server-config` | Serverkonfigurationsdokument | `settings.write` |
| `POST /api/server-path` | `{serverRoot}`; Server muss gestoppt sein | `settings.write` |
| `GET /api/users` | Kontoübersicht | `users.manage` |
| `POST /api/users/save` | `{username,password,permissions,enabled,create}` | `users.manage` |
| `POST /api/users/delete` | `{username}` | `users.manage` |

Weitere Rechte erklärt [Benutzer und Berechtigungen](docs/users.md). Vor schreibenden Integrationen den tatsächlichen Handler prüfen; neben HTTP-Rechten gelten Pfad-, Zustands- und Inhaltsprüfungen.

## Updates und Jobs

Panel: `GET /api/updates`, `POST /api/updates/{check,download,cancel,apply}`. Spielserver: `GET /api/server-updates`, `POST /api/server-updates/{check,download,apply,cancel}`, optional mit `target`. Erforderlich ist `settings.write`, für Download/Anwenden zusätzlich `users.manage`. Annahme eines Jobs ist noch kein Abschluss. Während eines Panel-Updates werden angemeldete POSTs mit `409 update.busy` abgelehnt.

## Experimentelle Bundle-Tools

Hauptschalter und Einzelrechte sind erforderlich. Builds führen vertrauenswürdigen Projektcode auf dem Host aus; vorher die [Bundle-Tools-Anleitung](docs/bundle-tools.md) lesen.

| Präfix / Route | Aktionen und Anfragehinweise | Berechtigung |
|---|---|---|
| `GET /api/bundle-tools` | Status, bereinigte Konten und erlaubte Jobs | Passendes Bundle-Recht |
| `POST /api/bundle-tools/settings` | Bundle-Tool-Einstellungen | `bundles.settings` |
| `POST /api/bundle-tools/upload` | Multipart-ZIP; `X-CSRF` erforderlich, keinen JSON-Content-Type setzen | `bundles.upload` |
| `POST /api/bundle-tools/upload/exists` | `{name}` | `bundles.upload` |
| `POST /api/bundle-tools/upload/install` | Geprüftes Upload-/Installationsdokument | `bundles.upload` |
| `/api/bundle-tools/tools` | POST `install`, `remove`; GET `latest` | `bundles.tools` |
| `GET /api/bundle-tools/projects` | Quellprojekte | `bundles.build` |
| `POST /api/bundle-tools/projects/{action}` | `create`, `import`, `pull`, `checkout`, `check`, `refs`, `build`, `rollback`, `remove` | `bundles.build`; Entfernen zusätzlich `bundles.sources.delete`; Remote-Zugriffe brauchen Kontonutzungsrechte |
| `POST /api/bundle-tools/accounts/{action}` | `save` Einstellungen/Token; `delete` oder `test` mit `{name}` | `bundles.accounts.manage` |
| `POST /api/bundle-tools/remote/{action}` | `owners`, `repositories` | `bundles.accounts.use`, ratenbegrenzt |
| `POST /api/bundle-tools/projects/workflow` | Review-/Direkt-Workflow konfigurieren | `bundles.settings` |
| `POST /api/bundle-tools/projects/compare` | Repository-Vergleich | `bundles.build`, `bundles.accounts.use` |
| `POST /api/bundle-tools/projects/{merge,review}` | Review-/Merge-Dokument | Build, Git-Schreiben, Kontonutzung und passendes Merge-/Review-Recht |
| `POST /api/bundle-tools/packages/info` | Paketmetadaten abfragen | `bundles.build` |
| `POST /api/bundle-tools/packages/review` | Paketänderung als Review | Build, Git-Schreiben, Konten, Pakete, Review |
| `GET /api/bundle-tools/jobs/{id}` | Job und Ergebnis | Recht für die Jobart |
| `GET /api/bundles/metadata` | Kategorien und Autostart | `bundles.read` |
| `POST /api/bundles/{tags,autostart}` | Metadatenänderung | `bundles.read` plus passendes Recht |
| `POST /api/bundles/delete-info` | `{name}` Löschvorschau | `bundles.read`, `bundles.delete` |
| `POST /api/bundles/delete` | Bestätigtes Löschdokument | Lesen/Löschen/Stoppen plus ausgewählte Daten-/Quellenrechte |

`projects/delivery` und `packages/set` liefern derzeit `409 bundleTools.workflow`; den konfigurierten Review-Workflow verwenden. Detaillierte Request-Typen stehen in Supervisor-Handlern und Panel-UI der dokumentierten Revision. Account-Tokens werden nie an den Browser ausgegeben.

## Ersteinrichtung

Setup benötigt den lokalen Setup-Key und ist ratenbegrenzt. POST-Routen: `/api/setup/validate`, `/install`, `/finish`, `/pick`, `/pick-status`, `/job`, `/cancel`. Das Setup-Dokument enthält `key`, `dashboardName`, `username`, `password`, `confirmation`, `locale`, `serverRoot`, `backend`; Status-/Cancel-Aufrufe verwenden `key`. Der Ordnerdialog ist nur bei direktem Loopback-Zugriff verfügbar. `GET /api/setup/console` ersetzt den Key nicht. Reihenfolge und Validierung über die [Einrichtungsanleitung](docs/windows.md) nachvollziehen.
