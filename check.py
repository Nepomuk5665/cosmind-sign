#!/usr/bin/env python3
"""Checks that every override still applies cleanly to the DocuSeal image it is built on.

An override replaces one of DocuSeal's files as a whole, so it is only right while DocuSeal's own
file is the one it was made from. ``upstream.json`` records, for the pinned version and digest, the
SHA-256 of every DocuSeal file an override replaces and of DocuSeal's licence files. This script
reads DocuSeal's files out of the base image (``docker create`` and ``docker cp``, nothing runs) or
from a directory holding them, and fails on:

- a replaced file that DocuSeal changed or removed (port DocuSeal's change into the override, then
  record; the hint names the files to diff between the two versions);
- a file we add that DocuSeal now ships itself, or a string our locale file sets that DocuSeal's
  English strings no longer have;
- DocuSeal's LICENSE or LICENSE_ADDITIONAL_TERMS changed (read them again before recording);
- a page that no longer renders DocuSeal's attribution, an attribution partial that no longer
  renders the "Powered by" partial our Source link and the once-per-page rule live in, or a layout
  that no longer renders the head tags our stylesheet and titles come through;
- a partial an override renders that exists neither in DocuSeal nor among the overrides;
- an image whose version (``/app/.version``) is not the recorded one, or a Dockerfile whose base
  digest is not the recorded one (nor, in our deployment repository, the pin in images.json).

    python3 check.py                       # DocuSeal's image named in the Dockerfile (needs docker)
    python3 check.py --image <reference>   # another reference to the same image, e.g. a mirror
    python3 check.py --tree <directory>    # DocuSeal's /app, already extracted
    python3 check.py --record [...]        # after porting: write the hashes of this version

Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OVERRIDES = HERE / "overrides"
UPSTREAM_JSON = HERE / "upstream.json"
DOCKERFILE = HERE / "Dockerfile"
# In our deployment repository the pin lives two levels up; the public mirror has no such file.
IMAGES_JSON = HERE.parent / "images.json"

# Files we add, never DocuSeal's: everything under our own folder of /packs, and our locale file
# (named to load after DocuSeal's i18n.yml, so its keys win).
ADDED = ("public/packs/cosmind/", "config/locales/zz_cosmind.yml")
LOCALE_FILE = "config/locales/zz_cosmind.yml"
UPSTREAM_LOCALE = "config/locales/i18n.yml"
LICENCE_FILES = ("LICENSE", "LICENSE_ADDITIONAL_TERMS")
# DocuSeal's pages that must keep rendering its attribution (and with it our Source link): the
# signing form, its completed and other end pages, and the pages after sending a copy.
ATTRIBUTION_PAGES = (
    "app/views/submit_form/show.html.erb",
    "app/views/submit_form/completed.html.erb",
    "app/views/submit_form/success.html.erb",
    "app/views/submit_form/declined.html.erb",
    "app/views/submit_form/expired.html.erb",
    "app/views/submit_form/archived.html.erb",
    "app/views/submit_form/awaiting.html.erb",
    "app/views/submit_form/delegated.html.erb",
    "app/views/send_submission_email/success.html.erb",
)
ATTRIBUTION_RENDER = "render 'shared/attribution'"
# DocuSeal's attribution partial renders "Powered by" through this one, which we replace.
ATTRIBUTION_PARTIAL = "app/views/shared/_attribution.html.erb"
POWERED_BY_RENDER = "render 'shared/powered_by'"
# The layouts the signing form, its end pages and the drawing page on a phone use; each must render
# the head tags, which carry our title, icons and stylesheet.
HEAD_TAGS_LAYOUTS = (
    "app/views/layouts/form.html.erb",
    "app/views/layouts/plain.html.erb",
    "app/views/submit_form_draw_signature/show.html.erb",
)
HEAD_TAGS_RENDER = "render 'layouts/head_tags'"
DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}")
RENDER_RE = re.compile(r"render(?:\(|\s+)(?:partial:\s*)?'([a-z_]+/[a-z_]+)'")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_added(name: str) -> bool:
    return name.startswith(ADDED)


def locale_keys(text: str, locale: str = "en") -> set[str]:
    """The keys of one locale's top level, read line by line (stdlib has no YAML parser): the lines
    indented by two spaces between `<locale>:` and the next top-level line."""
    keys, inside = set(), False
    for line in text.splitlines():
        if line and not line.startswith((" ", "#")):
            inside = line.split(":")[0] == locale
            continue
        match = re.match(r"^  ([a-z0-9_]+):", line)
        if inside and match:
            keys.add(match.group(1))
    return keys


def override_files() -> list[str]:
    """Every override, as its path under /app."""
    return sorted(p.relative_to(OVERRIDES).as_posix() for p in OVERRIDES.rglob("*") if p.is_file())


def dockerfile_digest() -> str:
    match = re.search(r"^ARG DOCUSEAL_IMAGE=\S+@(sha256:[0-9a-f]{64})$", DOCKERFILE.read_text(), re.M)
    if not match:
        raise SystemExit("Dockerfile: no `ARG DOCUSEAL_IMAGE=<image>@sha256:<64 hex>` line")
    return match.group(1)


def dockerfile_image() -> str:
    return re.search(r"^ARG DOCUSEAL_IMAGE=(\S+)$", DOCKERFILE.read_text(), re.M).group(1)


def static_problems(recorded: dict) -> list[str]:
    """What can be checked without DocuSeal's files: the pins agree, every override is accounted for."""
    problems = []
    digest = dockerfile_digest()
    if recorded.get("digest") != digest:
        problems.append(f"upstream.json records {recorded.get('digest')}, the Dockerfile builds on {digest}")
    if IMAGES_JSON.is_file():
        pinned = json.loads(IMAGES_JSON.read_text())["docuseal"]
        if (pinned["digest"], pinned["version"]) != (digest, recorded.get("version")):
            problems.append(
                f"images.json pins {pinned['version']} {pinned['digest']}, "
                f"the Dockerfile and upstream.json say {recorded.get('version')} {digest}"
            )
    replaced = set(recorded.get("replaced", {}))
    for name in override_files():
        if name not in replaced and not is_added(name):
            problems.append(
                f"overrides/{name}: neither a recorded replacement nor one of our files ({', '.join(ADDED)})"
            )
    for name in sorted(replaced - set(override_files())):
        problems.append(f"upstream.json records {name}, but no override replaces it")
    return problems


def upstream_problems(recorded: dict, tree: Path) -> list[str]:
    problems = []
    version_file = tree / ".version"
    if version_file.is_file() and version_file.read_text().strip() != recorded.get("version"):
        problems.append(
            f"the image is DocuSeal {version_file.read_text().strip()}, upstream.json records {recorded.get('version')}"
        )
    changed = []
    for name, digest in sorted(recorded.get("replaced", {}).items()):
        path = tree / name
        if not path.is_file():
            problems.append(f"{name}: DocuSeal no longer has it; the override would add a file nothing uses")
        elif sha256(path) != digest:
            changed.append(name)
            problems.append(f"{name}: DocuSeal changed it; port the change into overrides/{name}")
    for name in override_files():
        if is_added(name) and (tree / name).exists():
            problems.append(f"{name}: DocuSeal ships this file now; ours would replace it")
    for name in LICENCE_FILES:
        path = tree / name
        if not path.is_file() or sha256(path) != recorded.get("licence", {}).get(name):
            problems.append(f"{name}: DocuSeal changed its licence file; read it again before recording")
    for name in ATTRIBUTION_PAGES:
        path = tree / name
        if not path.is_file() or ATTRIBUTION_RENDER not in path.read_text():
            problems.append(f"{name}: no longer renders the attribution ({ATTRIBUTION_RENDER})")
    path = tree / ATTRIBUTION_PARTIAL
    if not path.is_file() or POWERED_BY_RENDER not in path.read_text():
        problems.append(f"{ATTRIBUTION_PARTIAL}: no longer renders {POWERED_BY_RENDER}")
    ours = OVERRIDES / LOCALE_FILE
    upstream_locale = tree / UPSTREAM_LOCALE
    if ours.is_file():
        theirs = locale_keys(upstream_locale.read_text()) if upstream_locale.is_file() else set()
        for key in sorted(locale_keys(ours.read_text()) - theirs):
            problems.append(f"{LOCALE_FILE}: DocuSeal's English strings no longer have {key}")
    for name in HEAD_TAGS_LAYOUTS:
        path = tree / name
        if not path.is_file() or HEAD_TAGS_RENDER not in path.read_text():
            problems.append(f"{name}: no longer renders the head tags ({HEAD_TAGS_RENDER})")
    for name in override_files():
        if not name.endswith(".erb"):
            continue
        for partial in RENDER_RE.findall((OVERRIDES / name).read_text()):
            folder, base = partial.split("/")
            candidates = [f"app/views/{folder}/_{base}.html.erb", f"app/views/{folder}/_{base}.json.erb"]
            if not any((tree / c).is_file() or (OVERRIDES / c).is_file() for c in candidates):
                problems.append(f"overrides/{name}: renders '{partial}', which exists nowhere")
    if changed:
        problems.append(
            "to see what DocuSeal changed: git diff <recorded version>..<new version> -- "
            + " ".join(changed)
            + " (in github.com/docusealco/docuseal)"
        )
    return problems


def extract(image: str, into: Path) -> Path:
    """DocuSeal's /app files this check reads, copied out of ``image`` without running it."""
    container = subprocess.run(
        ["docker", "create", "--platform", "linux/arm64", image], check=True, capture_output=True, text=True
    ).stdout.strip()
    try:
        (into / "app").mkdir(parents=True)
        (into / "config").mkdir(parents=True)
        for source, target in (
            ("/app/app/views", into / "app" / "views"),
            ("/app/public", into / "public"),
            ("/app/config/locales", into / "config" / "locales"),
            ("/app/.version", into / ".version"),
            ("/app/LICENSE", into / "LICENSE"),
            ("/app/LICENSE_ADDITIONAL_TERMS", into / "LICENSE_ADDITIONAL_TERMS"),
        ):
            subprocess.run(["docker", "cp", f"{container}:{source}", str(target)], check=True, capture_output=True)
    finally:
        subprocess.run(["docker", "rm", container], check=False, capture_output=True)
    return into


def record(tree: Path) -> dict:
    version = (tree / ".version").read_text().strip() if (tree / ".version").is_file() else None
    if not version:
        raise SystemExit("the tree has no .version, so the version cannot be recorded")
    replaced = {}
    for name in override_files():
        if is_added(name):
            continue
        if not (tree / name).is_file():
            raise SystemExit(f"{name}: DocuSeal has no such file; remove the override")
        replaced[name] = sha256(tree / name)
    return {
        "version": version,
        "digest": dockerfile_digest(),
        "replaced": replaced,
        "licence": {name: sha256(tree / name) for name in LICENCE_FILES},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--image", help="the base image to read DocuSeal's files from (default: the Dockerfile's)")
    source.add_argument("--tree", type=Path, help="a directory holding DocuSeal's /app files")
    parser.add_argument("--record", action="store_true", help="write upstream.json from DocuSeal's files")
    args = parser.parse_args(argv)

    recorded = json.loads(UPSTREAM_JSON.read_text()) if UPSTREAM_JSON.is_file() else {}
    with tempfile.TemporaryDirectory() as work:
        if args.tree:
            tree = args.tree
        else:
            if shutil.which("docker") is None:
                raise SystemExit("needs docker, or --tree with DocuSeal's /app files")
            tree = extract(args.image or dockerfile_image(), Path(work) / "upstream")
        if args.record:
            recorded = record(tree)
            UPSTREAM_JSON.write_text(json.dumps(recorded, indent=2, sort_keys=True) + "\n")
            print(f"recorded DocuSeal {recorded['version']} ({recorded['digest']}) in {UPSTREAM_JSON.name}")
        problems = static_problems(recorded) + upstream_problems(recorded, tree)

    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        return 1
    print(
        f"OK: {len(override_files())} overrides apply cleanly to DocuSeal {recorded['version']} ({recorded['digest']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
