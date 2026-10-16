"""Import public documentation from explicit, clean source checkouts.

Usage: python scripts/sync_docs.py --panel PATH --bundle PATH --api PATH
No credentials, VFS files, build output or private environment settings are imported.
"""
import argparse
import json
from pathlib import Path
import posixpath
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def sync(source, section, repository):
    revision = git(source, "rev-parse", "HEAD")
    if git(source, "status", "--porcelain", "--untracked-files=normal"):
        raise SystemExit(f"Commit source changes before importing: {source}")
    tracked = set(git(source, "ls-files").splitlines())
    names = {p for p in tracked if p in {"README.md", "README.de.md", "SECURITY.md", "LICENSE", "NOTICE.md"}
             or (p.startswith("docs/") and Path(p).suffix.lower() in {".md", ".png", ".jpg", ".svg", ".yaml"})
             or p in {"examples/smoke/README.md", "examples/consumer/PlayerPreferences.cs", "tools/ldb_client.py"}}
    for name in sorted(names):
        dest = CONTENT / section / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if Path(name).suffix != ".md":
            dest.write_bytes((source / name).read_bytes())
            continue
        body = (source / name).read_text(encoding="utf-8-sig")

        def link(match):
            href = match[1]
            if href.startswith(("#", "http:", "https:", "mailto:")):
                return match[0]
            parsed = urlsplit(href)
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path)))
            if target in names:
                return match[0]
            if "releases" in parsed.path and target.startswith(".."):
                absolute = f"https://github.com/{repository}/releases"
            else:
                absolute = f"https://github.com/{repository}/blob/{revision}/{target.lstrip('/')}"
                if target in tracked or target.startswith(".."):
                    pass
                elif any(p.startswith(target.rstrip('/') + '/') for p in tracked):
                    absolute = f"https://github.com/{repository}/tree/{revision}/{target}"
            if parsed.fragment:
                absolute += "#" + parsed.fragment
            return "](" + absolute + ")"

        body = re.sub(r"\]\(([^\s)]+)\)", link, body)
        dest.write_text(body.rstrip() + "\n", encoding="utf-8")
    return {"repository": repository, "commit": revision, "files": sorted(names)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("panel", "bundle", "api"):
        parser.add_argument("--" + option, type=Path, required=True)
    args = parser.parse_args()
    sources = {}
    for path, section, repo in [
        (args.panel, "webpanel", "LandminenTester/blackice-server-panel"),
        (args.bundle, "lt-database", "LandminenTester/lt-database"),
        (args.api, "lt-database-api", "LandminenTester/lt-database-api"),
    ]:
        sources[section] = sync(path, section, repo)
    (CONTENT / "sources.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")
    from localize_imports import localize
    localize()
    print("Imported documentation from three pinned public source revisions.")


if __name__ == "__main__":
    main()
