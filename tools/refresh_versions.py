#!/usr/bin/env python3
"""Refresh podman/private/known_versions.bzl from the Podman GitHub releases.

Resolves a Podman release (default: the latest stable) and reads the
sha256 of each per-platform asset across both upstreams —
`mgoltzsche/podman-static` (the daemonless Linux engine bundle) and
`containers/podman` (the macOS/Windows client) — then rewrites the
`KNOWN_VERSIONS` map + `DEFAULT_VERSION` in place. Prefers the GitHub
API's per-asset `digest` field (no download); falls back to streaming +
hashing the asset when a digest is absent.

Only `KNOWN_VERSIONS` and `DEFAULT_VERSION` are rewritten; the docstring,
`GITHUB_DOWNLOAD`, and `PLATFORMS` table are preserved verbatim (asset
names / layout change rarely and live under review).

Zero non-stdlib deps — runs on any CPython 3.8+ without `pip install`.

Usage:

    tools/refresh_versions.py                 # pin the latest stable release
    tools/refresh_versions.py --version 5.8.2 # pin a specific version
    tools/refresh_versions.py --replace       # drop prior pins, write only the new one

Set GITHUB_TOKEN (or GH_TOKEN) to raise the API rate limit. Invoke from
the repo root.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWN_VERSIONS_BZL = REPO_ROOT / "podman" / "private" / "known_versions.bzl"

API_LATEST = "https://api.github.com/repos/{repo}/releases/latest"
API_BY_TAG = "https://api.github.com/repos/{repo}/releases/tags/v{version}"

# The repo whose latest stable tag defines "latest" when --version is
# omitted. mgoltzsche/podman-static tracks upstream podman versions and
# is the daemonless engine source, so anchor on it.
ANCHOR_REPO = "mgoltzsche/podman-static"

# Platform key order preserved in the generated dict for stable diffs.
PLATFORM_ORDER = (
    "linux_amd64",
    "linux_arm64",
    "darwin_amd64",
    "darwin_arm64",
    "windows_amd64",
    "windows_arm64",
)


def _request(url: str) -> urllib.request.Request:
    headers = {
        "User-Agent": "rules_podman-refresher",
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def _http_json(url: str) -> dict:
    with urllib.request.urlopen(_request(url)) as resp:
        return json.loads(resp.read())


def _read_literals() -> dict:
    """Parse KNOWN_VERSIONS + PLATFORMS literals out of known_versions.bzl."""
    src = KNOWN_VERSIONS_BZL.read_text()
    tree = ast.parse(src)
    out: Dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], "id", None)
            if name in ("KNOWN_VERSIONS", "PLATFORMS"):
                out[name] = ast.literal_eval(node.value)
    return out


def _download_and_hash(url: str) -> str:
    print(f"   ... hashing {url}", file=sys.stderr)
    h = hashlib.sha256()
    with urllib.request.urlopen(_request(url)) as resp:
        while True:
            chunk = resp.read(1 << 20)  # 1 MiB
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _asset_sha256(asset: dict) -> str:
    digest: Optional[str] = asset.get("digest")
    if digest and digest.startswith("sha256:"):
        return digest[len("sha256:"):]
    return _download_and_hash(asset["browser_download_url"])


def _collect(version: str, platforms: dict) -> Dict[str, str]:
    """Return {platform_key: sha256_hex} for the given version, across repos."""
    releases: Dict[str, dict] = {}  # repo -> {asset_name: asset}
    out: Dict[str, str] = {}
    for key in PLATFORM_ORDER:
        spec = platforms.get(key)
        if not spec:
            continue
        repo = spec["repo"]
        if repo not in releases:
            try:
                rel = _http_json(API_BY_TAG.format(repo=repo, version=version))
                releases[repo] = {a["name"]: a for a in rel.get("assets", [])}
            except Exception as exc:  # noqa: BLE001 — surface + skip the repo
                print(f"   ! {repo} has no v{version} release ({exc}); skipping its platforms", file=sys.stderr)
                releases[repo] = {}
        asset_name = spec["asset"].format(version=version)
        asset = releases[repo].get(asset_name)
        if asset is None:
            print(f"   ! {repo} v{version} has no asset {asset_name!r} ({key}); skipping", file=sys.stderr)
            continue
        out[key] = _asset_sha256(asset)
    return out


def _version_tuple(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (0,)


def _render_known_versions(merged: Dict[str, Dict[str, str]]) -> str:
    lines = ["KNOWN_VERSIONS = {"]
    for version in sorted(merged, key=_version_tuple, reverse=True):
        lines.append(f'    "{version}": {{')
        for key in PLATFORM_ORDER:
            sha = merged[version].get(key)
            if sha:
                lines.append(f'        "{key}": "{sha}",')
        lines.append("    },")
    lines.append("}")
    return "\n".join(lines)


def _splice(src: str, merged: Dict[str, Dict[str, str]], default_version: str) -> str:
    """Replace only the KNOWN_VERSIONS block and DEFAULT_VERSION line."""
    new_block = _render_known_versions(merged)
    # The dict is generated with a closing `}` at column 0.
    src, n = re.subn(
        r"^KNOWN_VERSIONS = \{.*?^\}",
        lambda _m: new_block,
        src,
        count=1,
        flags=re.DOTALL | re.MULTILINE,
    )
    if n != 1:
        raise SystemExit("could not locate the KNOWN_VERSIONS block to replace")
    src, n = re.subn(
        r'^DEFAULT_VERSION = ".*?"',
        f'DEFAULT_VERSION = "{default_version}"',
        src,
        count=1,
        flags=re.MULTILINE,
    )
    if n != 1:
        raise SystemExit("could not locate the DEFAULT_VERSION line to replace")
    return src


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--version", default=None, help="Pin a specific Podman version (e.g. 5.8.2). Default: latest stable.")
    parser.add_argument("--replace", action="store_true", help="Replace the existing KNOWN_VERSIONS map instead of merging.")
    args = parser.parse_args(argv)

    lits = _read_literals()
    platforms = lits["PLATFORMS"]

    version = args.version
    if not version:
        latest = _http_json(API_LATEST.format(repo=ANCHOR_REPO))
        version = latest["tag_name"].lstrip("v")
        print(f"-> latest stable {ANCHOR_REPO} release is v{version}", file=sys.stderr)

    print(f"-> resolving Podman {version}", file=sys.stderr)
    new_pins = _collect(version, platforms)
    if not new_pins:
        raise SystemExit(f"no assets resolved for {version}; nothing written")

    merged: Dict[str, Dict[str, str]] = {} if args.replace else dict(lits["KNOWN_VERSIONS"])
    merged[version] = new_pins

    src = KNOWN_VERSIONS_BZL.read_text()
    KNOWN_VERSIONS_BZL.write_text(_splice(src, merged, version))
    print(f"-> wrote {KNOWN_VERSIONS_BZL.relative_to(REPO_ROOT)}; default is now {version}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
