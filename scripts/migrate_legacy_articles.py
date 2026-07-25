#!/usr/bin/env python3
"""Move generated Hexo article bodies into the shared Jekyll post layout."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
POSTS_DATA = ROOT / "_data" / "legacy_posts.yml"


class ArticleContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.active = False
        self.finished = False
        self.depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if not self.active and tag == "div" and attributes.get("id") == "articleContent":
            self.active = True
            self.depth = 1
            return

        if self.active:
            if tag == "div":
                self.depth += 1
            self.parts.append(self.get_starttag_text())

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.active:
            self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag: str) -> None:
        if not self.active:
            return
        if tag == "div":
            self.depth -= 1
            if self.depth == 0:
                self.active = False
                self.finished = True
                return
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self.active:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self.active:
            self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self.active:
            self.parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        if self.active:
            self.parts.append(f"<!--{data}-->")


def article_body(source: str) -> str:
    parser = ArticleContentParser()
    parser.feed(source)
    if not parser.finished:
        raise ValueError("articleContent container was not found or was not balanced")
    return "".join(parser.parts).strip()


def front_matter(post: dict[str, object]) -> str:
    summary = str(post.get("summary") or "")
    metadata = {
        "layout": "post",
        "title": str(post["title"]),
        "date": f"{post['date']} 00:00:00 +0800",
        "categories": [str(post.get("category") or "Notes")],
        "tags": list(post.get("tags") or []),
        "description": summary[:180],
        "permalink": str(post["path"]),
        "legacy": True,
    }
    return yaml.safe_dump(
        metadata,
        allow_unicode=True,
        sort_keys=False,
        width=110,
    )


def main() -> None:
    posts = yaml.safe_load(POSTS_DATA.read_text(encoding="utf-8"))
    migrated = 0
    skipped = 0

    for post in posts:
        article = ROOT / str(post["path"]).lstrip("/") / "index.html"
        source = article.read_text(encoding="utf-8")

        if source.startswith("---\n") and "\nlegacy: true\n" in source:
            skipped += 1
            continue

        body = article_body(source)
        output = (
            "---\n"
            f"{front_matter(post)}"
            "---\n"
            "{% raw %}\n"
            '<div class="legacy-article-content cjk-supported">\n'
            f"{body}\n"
            "</div>\n"
            "{% endraw %}\n"
        )
        article.write_text(output, encoding="utf-8")
        migrated += 1

    print(f"Migrated {migrated} legacy articles; skipped {skipped} already migrated files")


if __name__ == "__main__":
    main()
