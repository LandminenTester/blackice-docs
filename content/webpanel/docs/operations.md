# Operations

Private configuration: `.local/panel.json`, or the service's configured state path. `REPLAY_PANEL_CONFIG` chooses the file. `REPLAY_PANEL_RUNTIME` chooses Linux IPC storage. Passwords use PBKDF2-SHA256, 210000 iterations, 16-byte random salts. Data-protection keys preserve sessions across Webhost restarts. Protect and back up config and keys together.

**Backup:** gracefully stop the game; copy server `cfg`, `data/ugc` (including bundle VFS), `settings` and any other server-specific persistent data, plus panel state. Store backups privately because registration keys and password hashes are included. **Restore:** stop both panel processes, restore to writable directories, preserve the instance/container identity for Docker, then start Supervisor and Webhost. Test restored data before reopening public game ports.

**Manual updates:** back up first, stop game and panel processes, extract a new panel release outside live files, replace binaries/UI/scripts/docs, keep private state. Update BlackICE separately, preserving cfg, bundles/VFS, logs and settings. Fresh installations disable auto-update. Do not overwrite data with a clean server ZIP. On Docker update the pinned official image separately and recreate only the owned server container while preserving storage and updating the configured full container ID/ownership label. REServer runtime updates are available under Settings → REServer updates (server-updates.md); native panel updates use Settings → Panel updates.

**HTTPS:** run the panel on localhost behind a proxy. Keep the game/voice ports separate. Set explicit `allowedHosts` (including external port if nonstandard), `trustedProxies` (actual proxy IP), and `publicUrl` to the HTTPS URL. Secure cookies are then required. Do not trust arbitrary forwarding headers or expose HTTP directly.

Example private configuration additions:
```json
{"allowedHosts":["panel.example.org"],"trustedProxies":["127.0.0.1"],"publicUrl":"https://panel.example.org"}
```

Example nginx location (within a TLS-enabled virtual host):
```nginx
location / {
 proxy_pass http://127.0.0.1:20772;
 proxy_set_header Host $host;
 proxy_set_header X-Forwarded-Proto https;
 proxy_set_header X-Forwarded-For $remote_addr;
 proxy_buffering off;
 proxy_read_timeout 1h;
}
```

Diagnostics:
- Supervisor unavailable: check same user, matching pipe/socket and config, directory permissions, Supervisor log/service.
- External server: stop it in the original console before starting through the panel.
- Unknown bundle state: refresh and inspect native logs; a timed-out action is not automatically retried.
- Installation error: inspect Supervisor error log. Check network/registry, empty target, available disk and Linux dependencies.
- Graceful stop timed out: inspect game state before explicitly forcing it.
- Docker unavailable: check socket group, daemon health and owned container ID/label.
- Wrong login after migration: use `admin` with the existing password.
- Lost password: stop both processes, privately back up state and replace passwordSalt/passwordHash using the same documented PBKDF2 parameters with a fresh salt. Never set a plaintext password or publish credentials.
