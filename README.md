# wavachao.github.io

Personal homepage and technical blog powered by GitHub Pages and Jekyll.

## Edit the homepage

Most homepage copy, profile details, links, and project cards live in:

```text
_data/profile.yml
```

Edit that file instead of changing the page layout. The homepage template is
`index.html`, and the shared visual system lives in `assets/css/site.css`.

## Publish a blog post

1. Copy `content/POST_TEMPLATE.md`.
2. Rename it to `_posts/YYYY-MM-DD-short-title.md`.
3. Update the front matter at the top.
4. Write the article in Markdown.
5. Commit and push to the Pages branch.

The new article automatically appears on `/blog/` and `/archives/`.

## Add blog images

Upload images to `wavachao/blog-img`, then use the GitHub Raw URL in Markdown:

```markdown
![Description](https://raw.githubusercontent.com/wavachao/blog-img/main/filename.png)
```

## Preview locally

With Ruby and Bundler installed:

```bash
bundle install
bundle exec jekyll serve
```

Then open `http://127.0.0.1:4000`.

## Page responsibilities

- `/` — professional profile and selected work
- `/blog/` — curated blog homepage and recent writing
- `/archives/` — full chronological timeline and search
- `/categories/` and `/tags/` — subject indexes
- `_posts/` — new Markdown articles
- existing dated folders — preserved legacy articles and URLs

## Legacy content

The 132 existing Hexo articles keep their original URLs, but their bodies now
use the shared Jekyll article layout. Their archive metadata is stored in
`_data/legacy_posts.yml`.

Legacy article images are self-hosted in `wavachao/blog-img`. The original
external URL mapping is preserved in that repository at
`legacy/sources.json`, including the two architecture diagrams recreated after
their imgkr originals became unavailable.

The migration utilities are:

```bash
python3 scripts/extract_legacy_posts.py
python3 scripts/migrate_legacy_articles.py
python3 scripts/migrate_image_urls.py
```

The extractor refreshes the preserved generated archive pages and keeps metadata
already extracted from the original first archive page.
