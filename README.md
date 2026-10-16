# BlackICE documentation

Public guides: **[blackice.landminentester.de](https://blackice.landminentester.de/)**. English is the default; German is available at [/de/](https://blackice.landminentester.de/de/).

This repository contains the cyberpunk documentation library for independent LandminenTester BlackICE resources. The panel is standalone; only `lt_database` and `lt-database-api` form a required pair for bundle database access. Brewery scripting documentation remains separately maintained in [LandminenTester/docs](https://github.com/LandminenTester/docs).

## Build and preview

Requires Python 3.11 or later. Run from this repository:

```sh
python -m venv .venv
# Activate .venv using your shell's activation command.
python -m pip install -r requirements.txt
python scripts/build_navigation.py
python -m mkdocs build --strict
python scripts/check_docs.py
python -m mkdocs serve
```

Open the local URL printed by MkDocs. CI performs the same checks and publishes `main` through GitHub Pages. GitHub Pages settings select **GitHub Actions** and custom domain **blackice.landminentester.de**. Its DNS CNAME points to `landminentester.github.io`, without a repository path. HTTPS enforcement is enabled after GitHub provisions the certificate.

## Content and locales

| Location | Responsibility |
| --- | --- |
| `content/` | Public Markdown, shared guides and assets |
| `navigation.json` | Navigation source; generates MkDocs config and GitBook summaries |
| `resources.json` | Independent resources on the homepage |
| `translations/de/` | Reviewed German guides, copied to matching `*.de.md` during import |
| `editorial/en/` | Curated English panel guides replacing unclear upstream formatting |
| `locales/` | German navigation and UI catalogs; English strings are source keys |
| `hooks/localization.py` | Page-aware language links and translated UI |
| `theme/`, `content/assets/` | Cyberpunk layout, search, local fonts and logo |

`mkdocs-static-i18n` builds English at `/` and German at `/de/`. There is no browser-language redirect. Language links work without JavaScript and preserve the current document. Search filters the shared index to the selected locale. A future missing translation produces an explicit English-reference notice; CI requires a German counterpart for every navigation entry.

To add a page, write both language versions, add its navigation entry and translated label, regenerate navigation, build and run checks. Keep code/configuration identifiers unchanged. Preserve explicit anchors used by other pages. CI checks that the C# walkthrough in both languages matches the compiled consumer source.

## Sync product documentation

Commit product changes first; the importer refuses dirty sources:

```sh
python scripts/sync_docs.py --panel /path/to/blackice-server-panel --bundle /path/to/lt-database --api /path/to/lt-database-api
python scripts/build_navigation.py
python -m mkdocs build --strict
python scripts/check_docs.py
```

The importer records exact revisions in `content/sources.json`, imports allow-listed public files, separates upstream bilingual guides, then reapplies `editorial/en/` and `translations/de/`. Review both languages; a sync cannot automatically translate new upstream prose. Private settings, credentials, VFS data and build output are excluded. The manual **Sync product documentation** workflow opens a review PR if Actions is permitted to create pull requests.

## GitBook

The live cyberpunk site uses MkDocs on GitHub Pages. GitBook-hosted sites use GitBook's own theme settings. To prepare separate GitBook locales:

```sh
python scripts/export_gitbook.py
```

This creates ignored `.gitbook-export/en` and `.gitbook-export/de` trees with ordinary Markdown, assets, localized `SUMMARY.md` and `.gitbook.yaml`. Import each into its own GitBook space and configure English/German variants in your account. Root `.gitbook.yaml` remains an English Git Sync entry point. Connecting that account is separate from GitHub Pages.

## Logo downloads

The existing header mark was exported directly from its vector paths:

- [2056 × 2056 transparent PNG](content/assets/brand/lt-logo-2056-transparent.png)
- [2056 × 2056 graphite-background PNG](content/assets/brand/lt-logo-2056.png)
- [Scalable SVG](content/assets/brand/lt-logo.svg)

## Licenses

Imported content retains its upstream licenses and notices. Source revisions are recorded in `content/sources.json`. Fonts include OFL licenses. `DESIGN.md` records the visual system.
