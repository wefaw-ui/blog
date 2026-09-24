# Solivarii

A static blog. Posts are Markdown files in `content/`; `build.py` turns them into HTML.

## Setup

```sh
pip install -r requirements.txt
```

## Writing a post

```sh
python3 build.py new "My Post Title"   # creates content/my-post-title.md
```

Or create a file in `content/` by hand. The filename becomes the URL (`content/my-post.md` → `posts/my-post.html`). Every post starts with front matter:

```markdown
---
title: My Post Title
date: 2026-09-24
description: Optional one-line summary for search engines and link previews.
draft: true
---
Write in regular Markdown from here.
```

- `title` and `date` (YYYY-MM-DD) are required.
- `draft: true` keeps the post off the site. Remove it or set `false` to publish.
- Posts are listed newest first by `date`.

Supported Markdown: headings, **bold**, *italic*, links, images, lists, blockquotes, `inline code`, fenced code blocks, horizontal rules (`---`), tables, and footnotes (`[^1]`). Straight quotes and `--` become curly quotes and dashes automatically.

Images: put them in an `images/` folder and reference them as `![Alt text](../images/photo.jpg)`.

## Building

```sh
python3 build.py
```

This regenerates `index.html` and `posts/`. Upload the whole folder to any static host.

## Settings

At the top of `build.py`: `SITE_NAME`, `TAGLINE`, `X_URL`, `LISTMONK_URL`, `LISTMONK_LIST_UUID`.
