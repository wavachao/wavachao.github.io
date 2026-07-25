#!/usr/bin/env python3
"""Extract the generated Hexo archive into data files used by the new Jekyll UI."""

from __future__ import annotations

import html
import re
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ARCHIVES = ROOT / "archives"
OUTPUT = ROOT / "_data" / "legacy_posts.yml"
TOPICS_OUTPUT = ROOT / "_data" / "legacy_topics.yml"

ARTICLE_PATTERN = re.compile(
    r'<a href="([^"]+)">\s*<div class="card-image">.*?'
    r'<span class="card-title">(.*?)</span>',
    re.DOTALL,
)
DATE_PATTERN = re.compile(r'class="publish-date">.*?(\d{4}-\d{2}-\d{2})', re.DOTALL)
CATEGORY_PATTERN = re.compile(
    r'<a href="/categories/[^"]+/" class="post-category">\s*(.*?)\s*</a>',
    re.DOTALL,
)
TAG_PATTERN = re.compile(r'<span class="chip bg-color">(.*?)</span>', re.DOTALL)
SUMMARY_PATTERN = re.compile(
    r'<div class="summary block-with-text">\s*(.*?)\s*</div>',
    re.DOTALL,
)
TAG_STRIPPER = re.compile(r"<[^>]+>")
WHITESPACE = re.compile(r"\s+")


def clean(value: str) -> str:
    value = TAG_STRIPPER.sub(" ", value)
    return WHITESPACE.sub(" ", html.unescape(value)).strip()


def archive_pages() -> list[Path]:
    pages = [ARCHIVES / "index.html"]
    numbered = sorted(
        (ARCHIVES / "page").glob("*/index.html"),
        key=lambda path: int(path.parent.name),
    )
    return pages + numbered


def extract() -> list[dict[str, object]]:
    posts: list[dict[str, object]] = []
    seen: set[str] = set()

    for page in archive_pages():
        source = page.read_text(encoding="utf-8")
        for block in source.split('<div class="cd-timeline-block">')[1:]:
            article = ARTICLE_PATTERN.search(block)
            date = DATE_PATTERN.search(block)
            if not article or not date:
                continue

            path, title = article.groups()
            if path in seen:
                continue
            seen.add(path)

            category = CATEGORY_PATTERN.search(block)
            summary = SUMMARY_PATTERN.search(block)
            tags = [clean(tag) for tag in TAG_PATTERN.findall(block)]
            published = date.group(1)

            posts.append(
                {
                    "title": clean(title),
                    "path": path,
                    "date": published,
                    "year": published[:4],
                    "category": clean(category.group(1)) if category else "Notes",
                    "tags": tags,
                    "summary": clean(summary.group(1)) if summary else "",
                }
            )

    posts.sort(key=lambda post: str(post["date"]), reverse=True)
    return posts


def write_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )


def main() -> None:
    posts = extract()
    seen = {str(post["path"]) for post in posts}

    # The first generated Hexo archive page is now the new Jekyll archive UI.
    # Keep its previously extracted entries when refreshing the remaining
    # paginated legacy archive files.
    if OUTPUT.exists():
        previous = yaml.safe_load(OUTPUT.read_text(encoding="utf-8")) or []
        posts.extend(post for post in previous if str(post["path"]) not in seen)
        posts.sort(key=lambda post: str(post["date"]), reverse=True)

    categories = Counter(str(post["category"]) for post in posts)
    tags = Counter(tag for post in posts for tag in post["tags"])

    write_yaml(OUTPUT, posts)
    write_yaml(
        TOPICS_OUTPUT,
        {
            "categories": [
                {"name": name, "count": count}
                for name, count in categories.most_common()
            ],
            "tags": [
                {"name": name, "count": count}
                for name, count in tags.most_common()
            ],
        },
    )
    print(f"Extracted {len(posts)} posts into {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
