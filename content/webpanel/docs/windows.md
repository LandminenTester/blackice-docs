# Windows setup

Windows 10 1809+ x86-64 with ConPTY. BlackICE requires a roughly 2013+ x86-64 CPU, 512 MB RAM minimum for the server alone (2 GB+ recommended), and several GB disk space.

1. Extract the release outside the BlackICE server directory.
2. Open `Start.exe`. The control terminal stays open.
3. Open `http://127.0.0.1:20772`. Read the setup key from `.local/supervisor.log`.
4. Enter dashboard name, username and matching passwords (at least 8 characters).
5. The server folder `server` inside the panel folder is created automatically; use "Change folder" to pick another one with the system folder dialog. An existing server needs `REServer.exe` and `cfg/server.cfg`; format and write access are checked.
6. For installation, select an empty directory. The official ZIP is staged, extracted with path checks and validated. Cancel and retry are available; existing files are preserved.
7. Finish and sign in. The server starts automatically by default; change this under Settings.

Both processes run as the same account. Start protects `.local` for that user and SYSTEM. Never publish private state. While setup is incomplete, a Supervisor restart generates a new setup key.

`scripts/stop-web.ps1` stops only the Webhost. `scripts/control.ps1 -Action status|start|stop|restart|shutdown` controls the Supervisor. Stop the game before shutting down the Supervisor. For autostart use Task Scheduler under the same account, running Start.exe at sign-in.

Windows native address flags can fail before Winsock initialization. Set `sv_bindaddr "127.0.0.1:20770"` and `sv_voip_addr "127.0.0.1:20771"` in `cfg/server.cfg` instead.

## Direct terminal lifecycle

Start opens the control terminal and, for a managed native game, a separate server terminal. Q or Ctrl+C in Start stops the complete stack. Closing its X delegates graceful shutdown to an independent worker; inspect .local/controller-stop.log if it fails. Closing the server terminal or entering exit stops only the game. Settings → Start server with the panel controls auto-start. K explicitly keeps services running when leaving control; W stops only Webhost according to its configured shutdown mode. For unattended use, use service/background operation rather than an interactive Start window.

[Build guide / Build-Anleitung](building.md)
