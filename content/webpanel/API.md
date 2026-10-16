# Panel HTTP API

The panel's browser uses a same-origin, cookie-authenticated HTTP API on the panel URL (default
`http://127.0.0.1:20772`). This is the panel's internal application API and can change between panel releases.
There is no panel API-key authentication.

The source of truth is
[`src/Web/Program.cs`](https://github.com/LandminenTester/blackice-server-panel/blob/main/src/Web/Program.cs) and
[`BundleToolsEndpoints.cs`](https://github.com/LandminenTester/blackice-server-panel/blob/main/src/Web/BundleToolsEndpoints.cs).
Request records live in those files and
[`src/Shared`](https://github.com/LandminenTester/blackice-server-panel/tree/main/src/Shared).
Match the source revision in [sources.json](../sources.json) when developing an integration.

## Sessions, CSRF and response shapes

`GET /api/session` returns `{authenticated, username, permissions, csrf}` and issues the CSRF cookie.
**Every POST**, including login and setup, requires the returned token in `X-CSRF` together with its cookie.
`POST /api/login` takes `{username, password, remember}` and creates the `replay-panel-session` HttpOnly cookie.
`POST /api/logout` ends it. A normal session expires after four hours without sliding renewal; remember-me uses a
30-day persistent authentication ticket. Account changes can revoke a session through its security stamp.

Most mutations return a `Reply`: `{ok, error?, status?, lines?}`. Some data routes unwrap JSON from `lines[0]` and
return that data directly. `GET /api/status` returns a Reply containing `status`; do not assume every GET has that shape.

| Status | Meaning |
|---|---|
| 200 | Success; inspect `ok` and any asynchronous job state |
| 400 | Invalid host, CSRF or malformed input |
| 401 | Login failed or session missing/expired |
| 403 | Required account permission is missing |
| 404 | Requested file/resource does not exist |
| 409 | Application conflict, disabled feature, refused operation or update applying |
| 429 | Login/setup/provider discovery rate limit |

Errors use localization keys such as `csrf.invalid`, `update.busy` or `bundleTools.disabled`; display them through the
panel's translation layer. HTTPS remote access requires the [proxy configuration](docs/operations.md). Do not expose
the loopback service by changing a bind address without configuring trusted proxies and allowed hosts.

## Browser example

Run this from a same-origin panel integration. The user supplies their own credentials through its login UI.

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

## Core route reference

| Method and path | Input / output | Permission |
|---|---|---|
| `GET /api/session` | Session state and CSRF token | Public |
| `GET /api/bootstrap` | Setup/bootstrap data | Public |
| `POST /api/login` | `{username,password,remember}` | Public, rate limited |
| `POST /api/logout` | Empty JSON | Authenticated |
| `GET /api/status` | Reply with server state/PID/configured root | Authenticated |
| `POST /api/server/{action}` | `start`, `stop`, `restart`, `force-stop` | Matching `server.<action>` |
| `POST /api/command` | `{text}` console command | `console.write` |
| `GET /api/bundles` | Bundle list | `bundles.read` |
| `POST /api/bundles/{name}/{action}` | `start`, `stop`, `restart` | `bundles.read` and matching `bundles.<action>` |
| `GET /api/logs` | Recent console/log reply | `logs.read` |
| `GET /api/log-files` | `{name,size,modified,started}` array | `logs.read` |
| `GET /api/log-files-current` | Current log text download | `logs.read` |
| `GET /api/log-files/{name}` | Last 2 MiB of one log | `logs.read` |
| `GET /api/log-files.zip` | Streaming ZIP archive | `logs.read` |
| `GET /api/diagnostics` | Query `cursor`, `source`, `module`, `search`, `limit`, `history` | `console.read` and/or `logs.read` according to source |
| `GET /api/events` | Server-Sent Events; status, console and permissions | Authenticated; console requires `console.read` |
| `GET /api/bridge` | LAN bridge status | Authenticated |
| `POST /api/bridge/settings` | `{enabled,port,retentionDays,maxMegabytes}` | `settings.write` |
| `POST /api/settings` | `{shutdownMode,autoStartServer,locale,autoUpdateChecks,updateChannel}` | Authenticated; any field other than locale requires `settings.write` |
| `GET /api/server-name` | `{name}` | Authenticated |
| `GET /api/server-config` | Editable server configuration | `settings.write` |
| `POST /api/server-config` | Server configuration document | `settings.write` |
| `POST /api/server-path` | `{serverRoot}`; server must be stopped | `settings.write` |
| `GET /api/users` | Account views | `users.manage` |
| `POST /api/users/save` | `{username,password,permissions,enabled,create}` | `users.manage` |
| `POST /api/users/delete` | `{username}` | `users.manage` |

Use [users and permissions](docs/users.md) for the complete permission model and administrator safeguards.
Read the exact route handler before implementing a mutating integration; server configuration, path validation and
permission rules include checks beyond HTTP authorization.

## Updates and asynchronous jobs

Panel update routes are `GET /api/updates` and `POST /api/updates/{check,download,cancel,apply}`.
Server updates use `GET /api/server-updates` and `POST /api/server-updates/{check,download,apply,cancel}` with an optional
`{target}`. They require `settings.write`; download/apply also require `users.manage`.
Inspect returned job status rather than treating acceptance as completion. While a panel update is applying,
authenticated POST operations are refused with `409 update.busy`.
See [updates](docs/updates.md) and [server updates](docs/server-updates.md) for backups and rollback.

## Experimental bundle tools

These routes require the feature master switch and individual permissions. Source builds execute trusted project
code on the host. See [Bundle Tools](docs/bundle-tools.md) before enabling them.

| Prefix / route | Actions and request notes | Permission |
|---|---|---|
| `GET /api/bundle-tools` | Status, redacted accounts and authorized jobs | Relevant bundle permission |
| `POST /api/bundle-tools/settings` | BundleTools settings document | `bundles.settings` |
| `POST /api/bundle-tools/upload` | Multipart ZIP; `X-CSRF` required, omit JSON content type | `bundles.upload` |
| `POST /api/bundle-tools/upload/exists` | `{name}` | `bundles.upload` |
| `POST /api/bundle-tools/upload/install` | Inspected upload/install document | `bundles.upload` |
| `/api/bundle-tools/tools` | POST `install`, `remove`; GET `latest` | `bundles.tools` |
| `GET /api/bundle-tools/projects` | Source projects | `bundles.build` |
| `POST /api/bundle-tools/projects/{action}` | `create`, `import`, `pull`, `checkout`, `check`, `refs`, `build`, `rollback`, `remove` | `bundles.build`; removal also `bundles.sources.delete`; remote credentials need account permission |
| `POST /api/bundle-tools/accounts/{action}` | `save` settings/token; `delete` or `test` with `{name}` | `bundles.accounts.manage` |
| `POST /api/bundle-tools/remote/{action}` | `owners`, `repositories` | `bundles.accounts.use`, rate limited |
| `POST /api/bundle-tools/projects/workflow` | Review/direct workflow configuration | `bundles.settings` |
| `POST /api/bundle-tools/projects/compare` | Repository comparison document | `bundles.build`, `bundles.accounts.use` |
| `POST /api/bundle-tools/projects/{merge,review}` | Review/merge document | Build, git-write, account-use and matching merge/review permission |
| `POST /api/bundle-tools/packages/info` | Package metadata query | `bundles.build` |
| `POST /api/bundle-tools/packages/review` | Package-change review document | Build, git-write, accounts, packages, review |
| `GET /api/bundle-tools/jobs/{id}` | Job and outcome | Permission for that job's kind |
| `GET /api/bundles/metadata` | Tags and autostart metadata | `bundles.read` |
| `POST /api/bundles/{tags,autostart}` | Metadata change document | `bundles.read` plus matching permission |
| `POST /api/bundles/delete-info` | `{name}` deletion preview | `bundles.read`, `bundles.delete` |
| `POST /api/bundles/delete` | Confirmed deletion document | Read/delete/stop plus permissions for selected data/source flags |

`projects/delivery` and `packages/set` currently return `409 bundleTools.workflow`; use the configured review workflow.
The detailed JSON payloads are defined by the supervisor's BundleTools handlers and the panel UI at the recorded source
commit. Account tokens are encrypted on the supervisor and never returned to the browser.

## Setup routes

First-time setup uses the local setup key and is rate limited. POST routes:
`/api/setup/validate`, `/install`, `/finish`, `/pick`, `/pick-status`, `/job`, `/cancel`.
The setup document contains `{key,dashboardName,username,password,confirmation,locale,serverRoot,backend}`;
job/pick-status/cancel use `{key}`. The directory picker is available only for a direct loopback request.
`GET /api/setup/console` reports setup-console availability; it does not replace the key requirement.
Follow the setup UI and [installation guide](docs/windows.md) for supported ordering and validation.
