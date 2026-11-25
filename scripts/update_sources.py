#!/usr/bin/env python3
"""Regenerate per-app AltStore source JSONs from upstream GitHub releases.

Each app gets its own source file (one JSON per app), in the same format as
INSAV's altsource.json / iPadn's altstore-source.json, so LiveContainer's
Sources tab can add each by URL and offer installs / updates.

Usage: python3 scripts/update_sources.py   (run from the repo root)

- Fetches each upstream repo's latest release (GitHub API; GITHUB_TOKEN is
used when present, otherwise unauthenticated).
- Downloads the .ipa asset and reads the REAL bundle ID / version / build /
minOS from its Info.plist. The tag alone is never trusted: AvPlay changed
its bundle ID from com.javdb.avplay to com.javdb.avplay2 in 2.2.2.
- Prepends a new version entry when (version, build) is new; keeps the
newest 5 versions. If the bundle ID changed, the app entry is updated and
the change is noted in the new version's description.
- The subtitle (source-level and app-level) is generated from the newest
version: "最近更新：YY/MM/DD，版本：VX.Y.Z". No purpose words: the
owner knows what each app is for.
- Writes <app>.json in the repo root. Safe to re-run: no change, no rewrite.
"""

import json
import os
import plistlib
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime

REPO = "thunderfireCN/livecontainer-sources"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"

APPS = [
    {
        "file": "airbeep.json",
        "upstream": "LinkPass888/AirBeep",
        "name": "AirBeep",
        "identifier": "com.linkpass888.airbeep.source",
        "developer": "LinkPass888",
        "category": "utilities",
        "tint": "#2563EB",
        "icon": "https://raw.githubusercontent.com/LinkPass888/AirBeep/main/Appicon.icon/Assets/call-recording-sound-icon-v5.png",
        "website": "https://github.com/LinkPass888/AirBeep",
        "description": (
            "本源由 Lyn 的公开仓库自动维护，"
            "安装包为作者发布的未签名 IPA。"
        ),
    },
    {
        "file": "avplay.json",
        "upstream": "anonymousjav/AvPlayRelease",
        "name": "AvPlay",
        "identifier": "com.javdb.avplay2.source",
        "developer": "anonymousjav",
        "category": "entertainment",
        "tint": "#111111",
        "icon": "https://raw.githubusercontent.com/anonymousjav/AvPlayRelease/main/resources/logo.png",
        "website": "https://github.com/anonymousjav/AvPlayRelease",
        "description": (
            "本源由 Lyn 的公开仓库自动维护，"
            "安装包为作者发布的 IPA。"
        ),
    },
    {
        "file": "cloudn.json",
        "upstream": "mengangs/Cloudn",
        "name": "Cloudn",
        "identifier": "com.mengangs.cloudn.source",
        "developer": "mengangs",
        "category": "utilities",
        "tint": "#EA580C",
        "icon": "https://raw.githubusercontent.com/mengangs/Cloudn/main/docs/assets/icon-light.png",
        "website": "https://github.com/mengangs/Cloudn",
        "description": (
            "本源由 Lyn 的公开仓库自动维护，"
            "安装包为作者发布的未签名 IPA。"
        ),
    },
    {
        "file": "hghubx.json",
        "upstream": "zxsos/HGhubX",
        "name": "HGhubX",
        "identifier": "com.hghubx.app.source",
        "developer": "zxsos",
        "category": "entertainment",
        "tint": "#0F3D4A",
        "icon": "https://raw.githubusercontent.com/zxsos/HGhubX/main/app-icon.png",
        "website": "https://github.com/zxsos/HGhubX",
        "description": (
            "Minireel/HGhub 的后续分支（原仓库已删库停更）。"
            "本源由 Lyn 的公开仓库自动维护，"
            "安装包为作者发布的未签名 IPA。"
            "注意：包名 com.hghubx.app 与旧版 HGhub 不同，装上是另一个 App，"
            "旧版的收藏与观看记录不会带过来。"
        ),
    },
    {
        # Upstream publishes iOS builds ONLY as prereleases, so
        # /releases/latest (which skips prereleases) 404s for this repo.
        # The list endpoint is used instead, picking the newest release
        # that carries a .ipa asset (Android releases only have .apk).
        # iOS tags carry a build suffix (v1.6b22), shown in the subtitle.
        "file": "iduanju.json",
        "upstream": "my-name-is-alan/iDuanJu",
        "prerelease": True,
        "version_template": "V{version}b{build}",
        "name": "i短剧",
        "identifier": "com.local.stv.source",
        "developer": "my-name-is-alan",
        "category": "entertainment",
        "tint": "#2563EB",
        "icon": "https://raw.githubusercontent.com/my-name-is-alan/iDuanJu/main/STV/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png",
        "website": "https://github.com/my-name-is-alan/iDuanJu",
        "description": (
            "App 本身不托管任何内容，"
            "数据由设备直接向各公开站点请求。本源由 Lyn 的公开仓库自动维护，"
            "安装包为作者发布的未签名 IPA。注意：上游只发预发布版，"
            "包名 com.local.STV，最低 iOS 18.0。"
        ),
    },
    {
        "file": "piliplus.json",
        "upstream": "bggRGjQaUbCoE/PiliPlus",
        "name": "PiliPlus",
        "identifier": "com.example.piliplus.source",
        "developer": "bggRGjQaUbCoE",
        "category": "entertainment",
        "tint": "#FB7299",
        "icon": "https://raw.githubusercontent.com/bggRGjQaUbCoE/PiliPlus/main/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png",
        "website": "https://github.com/bggRGjQaUbCoE/PiliPlus",
        "description": (
            "本源由 Lyn 的公开仓库自动维护，"
            "安装包为作者发布的未签名 IPA。"
            "注意：包名 com.example.piliplus，最低 iOS 15.0。"
        ),
    },
    {
        # iPadn ships two IPAs per release (standard + lite); the
        # standard build is used, the '-lite-' variant is skipped.
        "file": "ipadn.json",
        "upstream": "mengangs/ipadn",
        "asset_exclude_substr": "-lite-",
        "name": "iPadn",
        "identifier": "app.local.ipadn.source",
        "developer": "mengangs",
        "category": "utilities",
        "tint": "#000000",
        "icon": "https://raw.githubusercontent.com/mengangs/ipadn/main/docs/images/icon.png",
        "website": "https://github.com/mengangs/ipadn",
        "description": (
            "本源由 Lyn 的公开仓库自动维护，安装包为作者发布的未签名 IPA。"
            "注意：最低 iOS 16.0；请用小号 Apple ID 登录，不要用主号。"
        ),
    },
    {
        # Mirror of the upstream official source. Lyn chose the official
        # source on 2026-11-21; this mirror exists only so the subtitle
        # follows the house format (last update date + version).
        "file": "zhihu.json",
        "upstream": "huamurui/zhihu-minus-minus",
        "name": "知乎",
        "identifier": "com.huamurui.zhihuminusminus.source",
        "developer": "huamurui",
        "category": "social",
        "tint": "#0066FF",
        "icon": "https://raw.githubusercontent.com/huamurui/zhihu-minus-minus/main/src/assets/images/icon.png",
        "website": "https://github.com/huamurui/zhihu-minus-minus",
        "description": (
            "本源由 Lyn 的公开仓库自动维护，安装包为作者发布的未签名 IPA。"
            "注意：最低 iOS 16.4。"
        ),
    },
]

MAX_VERSIONS = 5
MAX_BODY_CHARS = 3000


def api_get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def read_ipa_info(ipa_path):
    with zipfile.ZipFile(ipa_path) as z:
        cands = [
            n for n in z.namelist()
            if n.startswith("Payload/") and n.count("/") == 2 and n.endswith(".app/Info.plist")
        ]
        if not cands:
            raise RuntimeError(f"no Info.plist in {ipa_path}")
        d = plistlib.loads(z.read(cands[0]))
    return {
        "bundle": d.get("CFBundleIdentifier"),
        "version": d.get("CFBundleShortVersionString"),
        "build": str(d.get("CFBundleVersion")),
        "min_os": d.get("MinimumOSVersion") or "15.0",
    }


def pick_ipa(app, assets):
    """First .ipa asset, skipping names containing asset_exclude_substr
    (e.g. iPadn ships a '-lite-' variant alongside the standard build).
    """
    cands = [a for a in assets if a["name"].lower().endswith(".ipa")]
    excl = app.get("asset_exclude_substr")
    if excl:
        cands = [a for a in cands if excl not in a["name"]]
    return cands[0] if cands else None


def fetch_release(app):
    """Return (release, ipa_asset) for an app.

    Normal repos use /releases/latest. Prerelease-only repos (iDuanJu)
    need the releases list, scanned newest-first for the first release
    carrying a .ipa asset.
    """
    if app.get("prerelease"):
        rels = api_get(f"https://api.github.com/repos/{app['upstream']}/releases?per_page=10")
        for rel in rels:
            asset = pick_ipa(app, rel.get("assets", []))
            if asset:
                return rel, asset
        return None, None
    rel = api_get(f"https://api.github.com/repos/{app['upstream']}/releases/latest")
    return rel, pick_ipa(app, rel.get("assets", []))


def display_version(app, entry):
    """Version string for the subtitle, e.g. 'V2.2.1'. Apps whose public
    version carries a build suffix (iDuanJu tags like v1.6b22) set
    version_template, e.g. 'V{version}b{build}' -> 'V1.6b22'.
    """
    tmpl = app.get("version_template", "V{version}")
    return tmpl.format(version=entry["version"],
                       build=entry.get("buildVersion", ""))


def make_subtitle(app, entry):
    """Subtitle from the newest version entry, e.g.
    '最近更新: 26/11/14，版本: V2.2.1'. Date is the version's release date.
    Colons are half-width ASCII, each followed by one half-width space;
    the comma stays full-width.
    """
    date_iso = entry.get("date")
    if date_iso:
        dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))
        return f"最近更新: {dt:%y/%m/%d}，版本: {display_version(app, entry)}"
    return f"版本: {display_version(app, entry)}"


def build_source(app, bundle, versions):
    subtitle = make_subtitle(app, versions[0]) if versions else ""
    return {
        "name": app["name"],
        "identifier": app["identifier"],
        "sourceURL": f"{RAW_BASE}/{app['file']}",
        "subtitle": subtitle,
        "description": app["description"],
        "iconURL": app["icon"],
        "website": app["website"],
        "tintColor": app["tint"],
        "featuredApps": [bundle],
        "apps": [
            {
                "name": app["name"],
                "bundleIdentifier": bundle,
                "developerName": app["developer"],
                "subtitle": subtitle,
                "localizedDescription": app["description"],
                "iconURL": app["icon"],
                "tintColor": app["tint"],
                "category": app["category"],
                "versions": versions,
                "appPermissions": {"entitlements": [], "privacy": {}},
            }
        ],
        "news": [],
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    changed = []
    succeeded = 0
    for app in APPS:
        try:
            rel, asset = fetch_release(app)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            # One dead upstream (e.g. repo blocked/removed) must not kill
            # the whole daily run; skip it and keep the others updating.
            print(f"[{app['name']}] upstream unreachable ({e}), skipped")
            continue
        if rel is None or asset is None:
            print(f"[{app['name']}] no .ipa release found, skipped")
            continue
        tag = (rel.get("tag_name") or "").strip()
        with tempfile.TemporaryDirectory() as td:
            ipa_path = os.path.join(td, asset["name"])
            try:
                urllib.request.urlretrieve(asset["browser_download_url"], ipa_path)
                info = read_ipa_info(ipa_path)
            except (urllib.error.HTTPError, urllib.error.URLError,
                    zipfile.BadZipFile, RuntimeError) as e:
                print(f"[{app['name']}] download/read failed ({e}), skipped")
                continue
            succeeded += 1
            if not info["bundle"] or not info["version"]:
                print(f"[{app['name']}] unreadable Info.plist, skipped")
                continue

            path = os.path.join(root, app["file"])
            existing = None
            if os.path.exists(path):
                with open(path, encoding="utf-8") as fh:
                    existing = json.load(fh)

            versions = []
            if existing:
                versions = existing.get("apps", [{}])[0].get("versions", [])
            is_new = not (versions and versions[0].get("version") == info["version"]
                          and str(versions[0].get("buildVersion")) == info["build"])
            if is_new:
                body = (rel.get("body") or "").strip()[:MAX_BODY_CHARS]
                old_bundle = None
                if existing:
                    old_bundle = existing.get("apps", [{}])[0].get("bundleIdentifier")
                note = ""
                if old_bundle and old_bundle != info["bundle"]:
                    note = (
                        f"⚠️ 注意：本版包名由 {old_bundle} 改为 {info['bundle']}，"
                        "与旧版不是同一个包名，装上会是另一个 App，数据不互通，"
                        "作者建议 iOS 用户先用云备份。\n\n"
                    )
                entry = {
                    "version": info["version"],
                    "buildVersion": info["build"],
                    "date": rel.get("published_at"),
                    "localizedDescription": (note + body) if body else note.rstrip("\n"),
                    "downloadURL": asset["browser_download_url"],
                    "size": asset["size"],
                    "minOSVersion": info["min_os"],
                }
                versions = [entry] + [v for v in versions
                                     if not (v.get("version") == info["version"]
                                             and str(v.get("buildVersion")) == info["build"])]
                versions = versions[:MAX_VERSIONS]

            source = build_source(app, info["bundle"], versions)
            if existing == source:
                print(f"[{app['name']}] already at {info['version']} ({info['build']})")
                continue
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(source, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            print(f"[{app['name']}] wrote {info['version']} ({info['build']}) "
                  f"bundle {info['bundle']} size {asset['size']}")
            changed.append(app["file"])
    print("changed:", changed if changed else "none")
    if succeeded == 0:
        print("ERROR: no app could be checked, all upstreams failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
