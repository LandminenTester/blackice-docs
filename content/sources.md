# Sources and maintenance

This repository documents independent BlackICE resources. [LandminenTester/blackice-docs](https://github.com/LandminenTester/blackice-docs) owns the site, theme, shared guides and translations. Brewery scripting documentation lives separately in [LandminenTester/docs](https://github.com/LandminenTester/docs).

## Where to edit

Product implementations and their English documentation are maintained in each product repository. The [source manifest](sources.json) records the exact imported commits. Commit source changes before running the importer. It refuses dirty source checkouts and imports only an explicit list of public files.

Shared pages such as this page and the quickstart are maintained here. Reviewed German translations live in `translations/de/`; the importer copies them to matching `content/*.de.md` files after splitting upstream bilingual panel guides. Code and configuration names stay unchanged so examples match the software.

## English and German

English is the default at `/`. German lives at `/de/`. The language switcher links to the equivalent page; it never redirects based on browser language. Search filters results to the selected language. The locale catalog translates navigation, controls, empty states and error messages.

Every navigated page has a German counterpart. If a future page lacks a translation, the site displays an explicit English-reference notice rather than pretending English content is German. Keep both versions current when changing instructions, and preserve explicit anchor IDs used by cross-links.

## Build, verify and publish

See the [repository README](https://github.com/LandminenTester/blackice-docs#build-and-preview) for local commands. GitHub Actions checks a strict MkDocs build, locale coverage, internal links and the compiled-example source match, then publishes `main` to GitHub Pages. The custom domain is `blackice.landminentester.de`.

The Markdown can also be exported as separate English/German GitBook spaces. GitBook imports content and navigation; the cyberpunk HTML/CSS theme is used by the public GitHub Pages site. GitBook's own hosting appearance and domain are configured in that service, not by this template.

Imported material retains its original licenses; product issues belong in the relevant source repository. Report sensitive security findings through that product's private reporting channel.
