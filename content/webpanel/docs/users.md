# Users and permissions

Permissions decide which panel actions an account can perform. Use individual accounts so you can change or revoke one person's access without sharing an administrator password. These are panel permissions; they do not restrict the operating-system account or someone using the native server console.

## Create an account

1. Sign in with an account that has **Manage users**.
2. Open **Users** and create a new account.
3. Choose a username of 3–32 letters, digits, dots, underscores or hyphens, starting with a letter or digit.
4. Set a password of 8–256 characters.
5. Select only the permissions that person needs, then save.

To change an existing account, edit its permissions or enabled state and save. Leave the password field empty to keep the old password. Deleting an account requires confirmation. At least one enabled account must retain **Manage users**.

## Administrator accounts

The original administrator retains all permissions. In the user editor, **Super admin** selects every permission and locks the individual switches. It grants full access; it is not a separate limited operator role.

Account changes revoke that account's existing sessions and open event streams. Older installations initialize the account list from the original salted password hash when first modified. After upgrading from older releases, sign in again. Password hashes are never returned to the browser. Back up the private configuration and encryption keys together.

## Core permissions

| Permission | What it allows |
| --- | --- |
| Server start / stop / restart / force-stop | Each server action separately |
| Console read / write | Read output / issue raw game-server commands |
| Logs read | Read and download server log files |
| Bundles read | List installed and loaded bundles |
| Bundles start / stop / restart | The corresponding action; also requires Bundles read |
| Settings write | Change startup, shutdown and general panel settings |
| Users manage | Create, edit, disable and delete accounts and grant permissions |

**Console write is broad access.** Raw BlackICE commands can change bundles and game state. A person who only needs to restart bundles should receive bundle permissions without Console write. Every signed-in account can view process status and choose its own interface language.

## Developer and bundle-tool permissions

The editor groups these under Server, Console/logs, Bundle operation, Projects/Git, Tools/accounts and Administration. Experimental bundle tools also require their feature switch to be enabled.

| Permission ID | What it allows |
| --- | --- |
| `bundles.upload` | Validate and install a compiled bundle ZIP |
| `bundles.build` | Manage source projects, run trusted builds and read source/build job logs |
| `bundles.settings` | Change feature/build preferences and per-project workflow overrides |
| `bundles.tools` | Check, install and remove panel-managed build tools |
| `bundles.accounts.manage` | Add, replace, test and remove shared provider credentials |
| `bundles.accounts.use` | Use shared credentials for an authorized repository operation |
| `bundles.git.write` | Create/push remote repositories and use offered write workflows |
| `bundles.review` | Create provider review requests |
| `bundles.merge` | Explicit direct remote merge |
| `bundles.packages` | Propose isolated package changes |
| `bundles.autostart` | Change managed startup entries |
| `bundles.tags` | Change server-wide categories |
| `bundles.delete` | Delete bundle runtime files and selected backups |
| `bundles.sources.delete` | Delete local source projects |
| `bundles.data.delete` | Delete verified exclusive local bundle data |

Remote creation and delivery require **build + account use + Git write** together. Remote Git actions additionally require the specific action's permission. Package proposals also require **packages + review**. Deletion requires read, delete and stop, plus source/data permissions if that scope was selected. Ordinary Git writers do not automatically receive merge or deletion rights.

## Shared credentials and trust

Git accounts belong to the server installation. Knowing an account label grants no access; account management and use are checked separately. Tokens are encrypted at rest and never returned by the API. Users manage can grant these powers, so that permission is itself trusted.

Build access executes project code as the panel's operating-system user. It is intended for trusted developers and is not a sandbox for untrusted repositories. See the [security boundary](../SECURITY.md#bundle-tools-experimental) before enabling it.
