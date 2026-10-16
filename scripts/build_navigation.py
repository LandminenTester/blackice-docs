"""Generate GitBook and MkDocs navigation from one shared manifest."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
navigation = json.loads((root / "navigation.json").read_text(encoding="utf-8"))
resources = json.loads((root / "resources.json").read_text(encoding="utf-8"))
for resource in resources:
    for field in ("path", "guide", "reference"):
        if not (root / "content" / resource[field]).is_file():
            raise SystemExit(f"Resource target missing: {resource[field]}")
summary = ["# Summary", ""]
nav = []
for group, pages in navigation.items():
    summary += [f"## {group}", ""]
    nav.append({group: [{label: path} for label, path in pages.items()]})
    for label, path in pages.items():
        if not (root / "content" / path).is_file():
            raise SystemExit(f"Navigation target missing: {path}")
        summary.append(f"* [{label}]({path})")
    summary.append("")
(root / "content/SUMMARY.md").write_text("\n".join(summary), encoding="utf-8")
de_labels = json.loads((root / "locales/nav.de.json").read_text(encoding="utf-8"))
de_summary = ["# Inhalt", ""]
for group, pages in navigation.items():
    de_summary += ["## " + de_labels.get(group, group), ""]
    de_summary += [f"* [{de_labels.get(label,label)}]({Path(path).with_name(Path(path).stem+'.de.md').as_posix()})" for label,path in pages.items()]
    de_summary.append("")
(root / "content/SUMMARY.de.md").write_text("\n".join(de_summary), encoding="utf-8")
config = {
    "site_name": "LandminenTester Docs",
    "site_description": "Documentation for LandminenTester bundles, tools and resources for BlackICE servers.",
    "site_url": "https://blackice.landminentester.de/",
    "repo_url": "https://github.com/LandminenTester/blackice-docs",
    "docs_dir": "content", "site_dir": "site",
    "edit_uri": "edit/main/content/",
    "theme": {"name": "mkdocs", "custom_dir": "theme", "highlightjs": False},
    "markdown_extensions": ["tables", "fenced_code", "attr_list", {"toc": {"permalink": "#"}}, {"codehilite": {"guess_lang": False}}],
    "extra": {"resources": resources},
    "hooks": ["hooks/localization.py"],
    "plugins": ["search", {"i18n": {
        "docs_structure": "suffix", "reconfigure_material": False,
        "languages": [
            {"locale": "en", "default": True, "name": "English", "build": True},
            {"locale": "de", "name": "Deutsch", "build": True,
             "nav_translations": json.loads((root / "locales/nav.de.json").read_text(encoding="utf-8"))}
        ]
    }}],
    "nav": nav,
    "exclude_docs": "SUMMARY.md\nSUMMARY.de.md\n",
    "validation": {"links": {"not_found": "warn", "unrecognized_links": "warn", "anchors": "warn"}},
}
(root / "mkdocs.yml").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
print(f"Generated navigation for {sum(map(len, navigation.values()))} pages")
