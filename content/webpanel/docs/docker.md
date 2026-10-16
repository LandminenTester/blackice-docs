# Docker setup

Linux x86-64, Docker Engine and Compose v2. Webhost and Supervisor are separate; only the Supervisor receives the Docker socket.

First download the versioned Docker archive from the public GitHub release and load it with `gzip -dc blackice-server-panel-docker.tar.gz | docker load`. This installs the exact image tag referenced by Compose without requiring a registry login.

1. Copy `deploy/compose.env.example` to private `.env`. Set absolute `PANEL_STATE`, `PANEL_RUNTIME` and `SERVER_PATH`. Set `DOCKER_GID` from `stat -c %g /var/run/docker.sock`.
2. Create these host directories, owned by UID/GID 10001 with mode 0700. The server directory must be empty for installation.
3. Run `docker compose --env-file .env -f deploy/compose.yaml up -d`.
4. Get the setup key using `docker compose --env-file .env -f deploy/compose.yaml logs supervisor` and open localhost:20772.
5. Select Docker, official download and the mounted `/server` directory.

The Supervisor pulls `ghcr.io/replayre/server`, creates an owned container with TTY/stdin, persistent storage, LAN configuration and disabled auto-updates. It verifies the full container ID and ownership label before control. `REPLAY_PANEL_HOST_SERVER` is the daemon-side bind path and must match your host directory. Game/voice use 20770/20771 TCP+UDP.

Build locally with `docker build -t replay-panel:local .` and replace both image fields in a private Compose copy. Use fixed release versions. The Docker socket gives the Supervisor powerful host access; keep it private and never mount it into Webhost. Both services use UID 10001; only the Supervisor additionally joins the socket group.

Stop only Webhost using `docker compose ... stop web` for keep-running behavior. A Supervisor stop also stops its game server. Back up host server files and private state.
