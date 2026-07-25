#!/usr/bin/env python3
"""Replace legacy image-bed URLs in migrated articles with GitHub raw URLs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
POSTS_DATA = ROOT / "_data" / "legacy_posts.yml"
RAW_BASE = "https://raw.githubusercontent.com/wavachao/blog-img/main/"
LEGACY_URL = re.compile(
    r"https?://(?:"
    r"incipe\.oss-cn-shenzhen\.aliyuncs\.com/"
    r"|gitee\.com/incipe-win/images/raw/(?:master|main)/"
    r")[^&\"'\s<>)]+"
)


def github_url(source_url: str) -> str:
    """Map a legacy root-level asset URL to its URL-encoded GitHub raw URL."""
    filename = unquote(Path(urlsplit(source_url).path).name)
    if not filename:
        raise ValueError(f"Unable to extract an asset filename from {source_url}")
    return f"{RAW_BASE}{quote(filename)}"


def article_paths() -> list[Path]:
    posts = yaml.safe_load(POSTS_DATA.read_text(encoding="utf-8"))
    return [ROOT / str(post["path"]).lstrip("/") / "index.html" for post in posts]


def content_paths() -> list[Path]:
    """Return articles plus legacy generated feeds that embed article bodies."""
    paths = article_paths()
    paths.extend(path for path in (ROOT / "atom.xml", ROOT / "search.xml") if path.is_file())
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--assets-dir",
        type=Path,
        help="Optional blog-img checkout used to verify every replacement target.",
    )
    args = parser.parse_args()

    assets_dir = args.assets_dir.resolve() if args.assets_dir else None
    changed_files = 0
    replacements = 0
    missing_assets: set[str] = set()

    for content_file in content_paths():
        source = content_file.read_text(encoding="utf-8")
        urls = LEGACY_URL.findall(source)

        if assets_dir:
            for url in urls:
                filename = unquote(Path(urlsplit(url).path).name)
                if not (assets_dir / filename).is_file():
                    missing_assets.add(filename)

        updated, count = LEGACY_URL.subn(lambda match: github_url(match.group()), source)
        if count:
            content_file.write_text(updated, encoding="utf-8")
            changed_files += 1
            replacements += count

    if missing_assets:
        names = ", ".join(sorted(missing_assets))
        raise SystemExit(f"Missing {len(missing_assets)} target assets: {names}")

    print(
        f"Replaced {replacements} legacy image URLs across "
        f"{changed_files} content files"
    )


if __name__ == "__main__":
    main()
