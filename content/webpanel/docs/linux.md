# Native Linux setup

Reference: Debian 13 (trixie), x86-64. Other glibc distributions require a library check; musl/Alpine and ARM are not supported by these packages.

`sudo apt install ca-certificates libicu76 libssl3t64 libstdc++6 zlib1g`

Extract the Linux package, then run `./Start`. .NET and the PTY helper are included. Read `.local/supervisor.log` for the setup key and open localhost:20772. Choose Linux and an existing installation or empty target directory.

The OCI installer accesses the official registry directly, selects linux/amd64, verifies layer SHA-256 digests and extracts only `/opt/replay/seed`. A Docker daemon is not required. Existing installations need executable `REServer`, `cfg/server.cfg` and write access. Run `LD_LIBRARY_PATH=/srv/replay ldd /srv/replay/REServer`; no library may be missing. The official bundled libstdc++ is used through the backend's library path.

For systemd create user `replay-panel` and private directories `/var/lib/replay-panel` and `/srv/replay` owned by that account (0700). Extract the package under `/opt/replay-panel`. Install `deploy/replay-panel-*.service` into `/etc/systemd/system`, then run:

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now replay-panel-supervisor replay-panel-web
sudo journalctl -u replay-panel-supervisor -n 30
```

Both services use the same UID and runtime path. Socket/config mode is 0600 and the runtime directory is 0700. Stopping only the web service exercises the chosen shutdown mode. Stopping the Supervisor stops its game server.

## Interactive terminals

Use a writable release directory. Install tmux for SSH, and xterm for desktop terminal windows. Start is a self-contained executable. On a desktop it can open a control terminal; the managed server gets another terminal via x-terminal-emulator. In SSH, control stays in the current terminal and the server has its own tmux session. C attaches it; Ctrl+B then D detaches back to control without stopping the game. Closing a server terminal/session sends a graceful stop. Closing Start, Ctrl+C or Q stops the whole stack. Docker opens no server window.

[Build guide / Build-Anleitung](building.md) · [tmux reference](https://github.com/tmux/tmux/wiki/Getting-Started)
