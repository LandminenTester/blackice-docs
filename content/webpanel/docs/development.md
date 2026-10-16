# Development

Prerequisites: Git, .NET SDK 10.0.401 (global.json), Node 24.19.0 and npm. Linux also needs cc, libc headers and libutil. Editor suggestions: VS Code with C# and Svelte support.

Follow the individual Windows/Linux commands in [Building](building.md) from an already open terminal. The build scripts are optional conveniences. Restore exact npm versions with `npm --prefix ui ci`; .NET lockfiles are committed. Run `npm --prefix ui run check` before building.

Backend contract: `IServerBackend` exposes status, start, stop/force, command, console and logs. Platform integrations live in Supervisor; Web never accesses game files or Docker Engine. BundleManager serializes console queries and actions, delimits responses using echo markers, and waits for exact native lifecycle events. Loaded bundles can be stopped: never infer running state from the loaded list alone.

Private IPC uses JSON-line request/reply, current-user pipes on Windows and 0600 Unix sockets on Linux. Setup routes forward opaque payloads to Supervisor, which owns the setup key, password hashes, filesystem checks and installation jobs.

Typed `ui/src/locales.ts` defines English keys and requires a complete German catalog. Every user-facing error uses a stable code. Add a code to both catalogs when expanding the backend. BlackICE logs, usernames and bundle names remain original. UI controls live under `ui/src/components`; preserve keyboard, focus and reduced-motion behavior.

Tests:
- `dotnet publish tests/ConsoleFixture -c Release -o .local/fixture`
- `dotnet run --project tests/Backend.Tests -- .local/fixture` (on Linux place replay-terminal beside the test executable).
- `node scripts/test-panel.mjs`: disposable console fixture only, port 20774.
- `node scripts/test-setup.mjs`: protected wizard and concurrency, port 20775.
- `node scripts/test-install.mjs`: actual Windows download, isolated server ports 30770/30771.
- `docker build -f tests/Linux.Dockerfile -t replay-panel-linux-tests .`; `docker run --rm replay-panel-linux-tests`.
- `docker build -t replay-panel:next .`; `node scripts/test-install.mjs --linux` / `--docker`: Debian 13 and Engine integration, disposable volumes and HTTP port 20776.

Never point fixture tests at a production directory. Runtime downloads are vendor artifacts and subject to upstream availability. Release builds package Windows/Linux self-contained runtimes, Linux terminal helper, docs and scripts; Docker uses separate services and a versioned image.
