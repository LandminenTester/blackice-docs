# Server configuration

**Settings → Server config** edits the main keys of `cfg/server.cfg`: `sv_name`, `sv_desc`, `sv_region` (ISO 3166-1 alpha-3 country code, chosen from a list), `sv_dlc`, `sv_bindaddr`, `sv_endpoint` and `sv_lan`. Comments and all other lines stay unchanged and the original line endings are kept. The first save creates `cfg/server.cfg.panel.bak`. Changes apply after a server restart. Requires the `settings.write` permission. Names and descriptions must not contain quotes or backslashes.

## Additional keys and log archive

The editor also manages `sv_voip_addr`, `sv_privacy`, `sv_ugc_automatic_restarts` and, in `settings/server.settings.json`, `channel`, `auto_update` and `restart_after_update` (containers override these through the `CHANNEL`, `AUTO_UPDATE` and `RESTART_AFTER_UPDATE` environment variables). Region is a typable list of ISO 3166-1 alpha-3 codes. **Console → Log archive** lists the server's `logs/` files grouped by day and server start, shows a file and downloads all logs as one ZIP (permission `logs.read`).

## Bundle details, full start log and update checks

The bundle list shows `author`, `version` and `description` from the optional `[General]` table of each bundle's `config.toml`. **Console → Download full log (this start)** saves the complete server log file of the current (or last) server start; the log archive lists older starts. **Settings → General → Check for updates automatically** controls whether the panel contacts GitHub and artifacts.replay.re on its own; when off, checks happen only when you click a check button.
