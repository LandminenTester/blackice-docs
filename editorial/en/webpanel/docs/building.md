# Build the panel from source

Use a terminal you keep open, such as VS Code's terminal, PowerShell or your Linux shell. Work in the repository folder containing `global.json`, `src` and `ui`, not in the game server directory. Run each command separately and fix the first error before continuing.

## Install the build tools

Git, .NET SDK **10.0.401**, Node **24.19.0** and npm are the versions documented by this source revision. `global.json` selects the SDK and `ui/package-lock.json` locks frontend dependencies. A downloaded panel release includes .NET and does not need development tools.

Before replacing active files, press `Q` in this panel's Start terminal. Stop Vite separately with Ctrl+C if it is running. Keep private `.local` files and game data. To build while an existing release runs, publish into a separate staging directory.

## Windows

Run in the panel repository:

```powershell
npm --prefix ui ci
npm --prefix ui run check
npm --prefix ui run build

dotnet build src/Supervisor -c Release
dotnet build src/Web -c Release

dotnet publish src/Supervisor -c Release -r win-x64 --self-contained true -o artifacts/supervisor
dotnet publish src/Web -c Release -r win-x64 --self-contained true -o artifacts/web

dotnet publish src/Supervisor -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o .local/launcher
Copy-Item .local/launcher/Supervisor.exe Start.exe -Force
 # Keep the repository VERSION file beside Start.exe; match Directory.Build.props when changing the version.
Copy-Item licenses artifacts/web/wwwroot/licenses -Recurse -Force
.\Start.exe
```

`npm ci` restores exact packages, `check` validates Svelte/TypeScript and `build` writes `src/Web/wwwroot`. `dotnet build` compiles C#; `publish` creates the runtime packages. Keep `Start.exe` beside `artifacts`, and keep the repository's `VERSION` file beside the launcher. Do not package stale UI output after a failed build.

## Linux

These commands use Debian 13 x86-64. Install Git, the specified .NET SDK and Node first; then run:

```sh
sudo apt install build-essential ca-certificates libicu76 libssl3t64 libstdc++6 zlib1g tmux
# Only for a graphical desktop:
sudo apt install xterm
cd /path/to/blackice-server-panel

npm --prefix ui ci
npm --prefix ui run check
npm --prefix ui run build
dotnet build src/Supervisor -c Release
dotnet build src/Web -c Release

dotnet publish src/Supervisor -c Release -r linux-x64 --self-contained true -o artifacts/supervisor
dotnet publish src/Web -c Release -r linux-x64 --self-contained true -o artifacts/web
cc -O2 -Wall -Wextra native/terminal.c -lutil -o artifacts/supervisor/replay-terminal

dotnet publish src/Supervisor -c Release -r linux-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o .local/launcher
cp .local/launcher/Supervisor Start
chmod +x Start
cp -R licenses artifacts/web/wwwroot/
./Start
```

The C helper provides BlackICE's pseudoterminal (PTY); it requires `cc` and `libutil` when building and is included in releases. A desktop opens a server terminal. SSH uses tmux: `C` attaches, Ctrl+B then D detaches, `exit` stops the game, and `Q` in the controller stops the stack.

## Docker

```sh
docker version
docker build -t replay-panel:local .
```

Docker builds the frontend, C# applications and PTY helper in the image. Host Node and SDK installations are not required for that build. Follow [Docker setup](docker.md) for the separate services and persistent volumes.

## Test the build

```powershell
dotnet run --project tests/Core.Tests
dotnet publish tests/ConsoleFixture -c Release -o .local/fixture
dotnet run --project tests/Backend.Tests -- .local/fixture
node scripts/test-panel.mjs
node scripts/test-setup.mjs
```

Fixture tests use disposable directories and ports; never point them at a production configuration. Linux backend tests also need the PTY helper next to the test program. See [development](development.md) for further platform and installation tests.

## Common errors

| Error | Next step |
| --- | --- |
| `MSB1003` | Work from the repository and specify `src/Web` or `src/Supervisor`. |
| `NETSDK1045` | Install the SDK in `global.json`, not only a runtime. |
| Missing `vite` / `svelte-check` | Run `npm --prefix ui ci`. |
| `EPERM` on Rolldown | Stop this project's development/language-server process holding the native module. |
| `MSB3027` | Stop this panel before replacing loaded files, or publish elsewhere. |
| `NU1301` / network error | Check proxy, certificates and connectivity; do not disable TLS checks. |
| Missing `cc` / `libutil` | Install `build-essential` and compile the helper. |
| Linux permission denied | Check executable permissions and service-account access. |
| Port already used | Use or gracefully stop the existing panel. |
| Missing release files | Keep the launcher beside both artifact directories. |

Keep full build logs with `Tee-Object` in PowerShell or `tee` in Linux. See [operations](operations.md) before deployment.
