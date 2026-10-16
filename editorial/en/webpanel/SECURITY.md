# Security policy

This project is developed primarily with AI assistance and reviewed/tested by its human maintainer. Automated checks and human review do not constitute an independent security audit. Operators are responsible for assessing their deployment.

Report vulnerabilities privately using [GitHub private vulnerability reporting](https://github.com/LandminenTester/blackice-server-panel/security/advisories/new). Include the panel/server version, platform, minimal reproduction, expected impact and sanitized evidence. Do not post credentials, tokens or exploitable details in public Issues. Ordinary bugs and improvement proposals belong in Issues.

The latest stable release is the supported version. Reports are handled by the maintainer without a guaranteed response time; coordinated fixes and independent reviews are welcome. The LAN bridge is an authenticated internal interface and must not be exposed publicly.

## Hardening notes

- **Setup key.** Until the first administrator exists, `/api/setup/*` is protected by a random 8-character key printed only to the Supervisor console and `.local/supervisor.log`. The browser terminal shows it **only when the panel is opened on the same computer** (loopback, no proxy headers, host `localhost`/`127.0.0.1`); remote visitors must read it from the console. Five wrong keys invalidate it and a new one is generated, and the setup endpoints are rate-limited. Complete the setup before exposing the port.
- **Docker socket.** Docker mode gives the **Supervisor** access to `/var/run/docker.sock`, which is root-equivalent on the host. The code only touches containers and networks it created itself (labelled with the instance id), but a compromised Supervisor could abuse the socket. Run the panel only on hosts you trust, never publish the Supervisor, and, if you want a stricter boundary, put a filtering proxy such as [`tecnativa/docker-socket-proxy`](https://github.com/Tecnativa/docker-socket-proxy) in front of the socket (allow only the container, network and image endpoints) or use rootless Docker/Podman. The panel itself has no built-in socket filter, because any component inside the Supervisor already holds the same access.
- **Server binary.** Validation on Linux runs `ldd` on the chosen `REServer` after checking that it is not group/world-writable. The panel executes that binary anyway when you start the server, so only point it at files you trust.
- **Updates.** Panel and server updates are verified against SHA-256 digests (integrity), not against a publisher signature. Release assets ship with `SHA256SUMS.txt` and a GitHub build provenance attestation; verify with `gh attestation verify <file> --repo LandminenTester/blackice-server-panel`. Automatic update checks (GitHub and artifacts.replay.re) can be switched off in **Settings → General**.
- **Console access.** Users with *Write console* can send arbitrary REServer commands. Grant it only to trusted operators.

## Bundle tools (experimental)

Bundle tools are off by default. **A build is code execution, not a sandbox.** MSBuild targets, analyzers and the chosen web build run with the panel OS user's rights; disabling npm install scripts does not make untrusted source safe. A malicious build can read files available to that OS user, including panel state or the credentials needed to decrypt stored tokens. Grant build access only to trusted developers, use narrowly scoped repository tokens and a low-privilege OS account, and separate development from a live-player server. Panel permissions do not isolate processes running under the same OS account.

Provider accounts belong to the **server installation**, not to the person who added them. Tokens are encrypted at rest, omitted from browser responses and redacted from job logs. Operators can replace a token, but there is no token-reveal/export action. Account management and account use are separately authorized; repository writes, build tools and bundle preferences also have their own permissions. A user-management administrator can grant these capabilities, so user management remains a trusted role. Back up the state directory and encryption keys together and protect both from unrelated OS users.

Managed outbound HTTP for setup, updates, package metadata and provider calls requires HTTPS and validates/pins DNS connections to public addresses. Provider authentication does not follow redirects. Git remote operations validate and pin public DNS addresses, disable proxies/redirects and keep TLS verification on. This intentionally excludes HTTP/private-network Git providers from dashboard workflows. These network guards do not constrain arbitrary code executed by a trusted build.

Nothing is pulled, built or updated automatically. Use private reports for suspected credential exposure and rotate affected provider tokens. See [Bundle Tools](docs/bundle-tools.md) and the [permission reference](docs/users.md).

## Remote merges and bundle lifecycle


Direct merge, review creation, package proposals, startup editing, categories and deletion have separate server-side capabilities. Operations do not retry remote writes after ambiguous failures. Runtime deletion preserves data by default; optional data deletion is restricted to the bundle's exclusive local non-linked VFS directory. Keep backups before irreversible actions. New APIs retain origin-bound credentials, outbound destination checks, CSRF protection and plain-text redacted logs.
