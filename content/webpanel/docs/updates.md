# Dashboard updates

In **Settings → Panel updates**, the panel checks the latest stable public release from LandminenTester/blackice-server-panel. It displays installed/latest versions and release notes. Checks are cached for one minute; no GitHub token is required. Drafts and prereleases are excluded.

Choose **Download and verify**. The supervisor downloads the exact Windows x64 ZIP or Linux x64 tar.gz, verifies length and GitHub's SHA-256 asset digest, rejects unsafe paths/links and checks platform files and VERSION. It stages everything without touching the running installation. Progress and cancellation are available.

Once ready, choose **Install and restart** and confirm the interruption. A copy of the currently running updater operates outside the installation being replaced. It stops the managed server, Webhost, Supervisor and control terminal, saves the existing artifacts/Start/configuration, swaps the staged artifacts and Start, then opens a new control terminal. Server startup follows the auto-start setting. Configuration, data-protection keys, users, downloaded game files and bundles are retained. No unattended update is installed.

Settings-write permission is required to view/check updates. Download/install additionally requires user-management permission. In-place installation is enabled only for a native package with an open Start control terminal. Docker and systemd deployments expose the version check, but are upgraded through Compose/systemd deployment tools; the dashboard does not replace an immutable container or gain host service-manager access.

On an SSH host the new control terminal is a tmux session; use `tmux list-sessions` and attach to `replay-panel-<instance-prefix>`.

The new panel must answer the version and web readiness probes. Failed startup restores the old package automatically. Browser disconnection is expected during installation; the page reconnects and reads the persisted result. If it cannot reconnect, open Start and inspect:

- `.local/panel-update.json`: last job/result.
- `.local/updates/<job>/apply.log`: installation/recovery log.
- `.local/updates/<job>/backup`: previous artifacts, Start, VERSION and configuration.

Keep backups until the new version works. For manual recovery, stop all remaining panel processes using the direct stop command, move the failed artifacts/Start aside, restore the backup artifacts/Start and, only if configuration migration failed, restore panel.json. Keep the keys directory. Start again. If the stop command fails, inspect process identity before touching active binaries. Never replace the game-server directory with a panel package.

When building a release, VERSION must match the assemblies' Directory.Build.props version. The CI packages this file and verifies replacement plus startup-failure rollback on Windows and Linux. Version 0.5.1 uses the former repository URL and cannot verify renamed release assets. Install 1.0.0 manually once, retaining .local; subsequent native releases can be installed in the dashboard.

### Update channels

**Settings → Updates → Update channel** selects the release stream. **Stable** (default) only offers normal releases. **Experimental** additionally offers pre-releases tagged `vX.Y.Z-experimental.N`, which carry new, unfinished features and can be unstable; a stable release that supersedes a pre-release is offered as well. Switching back to Stable never downgrades; it only stops offering pre-releases. Pre-releases are marked with an **Experimental** tag in the panel and on GitHub (they are never marked "Latest"), use the same SHA-256 verification and automatic rollback, and Docker users must pin the exact image version themselves.
