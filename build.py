#!/usr/bin/env python3
"""Build Solivarii: turns content/*.md into static HTML.

    python3 build.py                 build the site
    python3 build.py new "Title"     start a new post in content/

Post format (content/<slug>.md): front matter, then Markdown.

    ---
    title: Post Title
    date: 2026-09-18
    description: Optional one-line summary.
    draft: true
    ---
    Regular Markdown here.
"""

import html
import re
import sys
from datetime import date
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("Missing dependency. Install it with: pip install -r requirements.txt")

# ---- Settings -------------------------------------------------------------
SITE_NAME = "Solivarii"
TAGLINE = "Essays on attention, craft, and the quiet work of making things."
X_URL = "https://x.com/solivarii"
LISTMONK_URL = "https://listmonk.example.com"  # your listmonk root URL
LISTMONK_LIST_UUID = "00000000-0000-0000-0000-000000000000"  # public list UUID
# ---------------------------------------------------------------------------

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
POSTS_OUT = ROOT / "posts"


MD_EXTENSIONS = ["extra", "smarty", "sane_lists"]
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def parse(path):
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        sys.exit(f"{path}: missing front matter (a --- block with title and date)")
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip().strip("\"'")
    for field in ("title", "date"):
        if not meta.get(field):
            sys.exit(f"{path}: front matter is missing '{field}'")
    try:
        post_date = date.fromisoformat(meta["date"])
    except ValueError:
        sys.exit(f"{path}: date '{meta['date']}' must be YYYY-MM-DD")
    return {
        "slug": path.stem,
        "title": meta["title"],
        "date": post_date,
        "description": meta.get("description") or TAGLINE,
        "draft": meta.get("draft", "").lower() in ("true", "yes"),
        "body": markdown.markdown(text[match.end():], extensions=MD_EXTENSIONS),
    }


def new_post(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    path = CONTENT / f"{slug}.md"
    if path.exists():
        sys.exit(f"{path} already exists")
    CONTENT.mkdir(exist_ok=True)
    path.write_text(f"---\ntitle: {title}\ndate: {date.today().isoformat()}\n"
                    f"description:\ndraft: true\n---\n\nStart writing here.\n",
                    encoding="utf-8")
    print(f"Created {path.relative_to(ROOT)} (draft: true — set to false to publish)")


def fmt_date(d):
    return d.strftime("%b %-d, %Y")


def page(title, content, base, description=TAGLINE):
    full_title = SITE_NAME if title == SITE_NAME else f"{title} — {SITE_NAME}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="#000000">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{base}style.css">
</head>
<body>
<div class="wrap">
<header class="site-header">
<a class="wordmark" href="{base}index.html">{SITE_NAME}</a>
<nav class="site-nav">
<a href="{X_URL}" rel="me noopener" target="_blank">X</a>
<a href="#newsletter">Newsletter</a>
</nav>
</header>
<main>
{content}
</main>
<footer class="site-footer">
<section class="newsletter" id="newsletter">
<h2>Newsletter</h2>
<p>New essays, sent occasionally. No noise.</p>
<form method="post" action="{LISTMONK_URL}/subscription/form">
<input type="hidden" name="nonce">
<input type="hidden" name="l" value="{LISTMONK_LIST_UUID}">
<label class="visually-hidden" for="email">Email address</label>
<input id="email" type="email" name="email" placeholder="you@example.com" required autocomplete="email">
<button type="submit">Subscribe</button>
</form>
</section>
<div class="colophon">
<span>&copy; {date.today().year} {SITE_NAME}</span>
<a href="{X_URL}" rel="me noopener" target="_blank">Follow on X</a>
</div>
</footer>
</div>
</body>
</html>
"""


def build():
    posts = sorted((p for p in map(parse, CONTENT.glob("*.md")) if not p["draft"]),
                   key=lambda p: p["date"], reverse=True)
    POSTS_OUT.mkdir(exist_ok=True)
    for old in POSTS_OUT.glob("*.html"):
        old.unlink()

    for post in posts:
        content = f"""<article class="post">
<p class="post-meta"><time datetime="{post['date'].isoformat()}">{fmt_date(post['date'])}</time></p>
<h1>{html.escape(post['title'])}</h1>
{post['body']}
</article>
<nav class="post-nav"><a href="../index.html">&larr; All essays</a></nav>"""
        (POSTS_OUT / f"{post['slug']}.html").write_text(
            page(post["title"], content, "../", post["description"]), encoding="utf-8")

    items = "\n".join(
        f'<li><a href="posts/{p["slug"]}.html"><span class="title">{html.escape(p["title"])}</span>'
        f'<time datetime="{p["date"].isoformat()}">{fmt_date(p["date"])}</time></a></li>'
        for p in posts)
    content = f"""<h1 class="intro">{SITE_NAME}. <span>{html.escape(TAGLINE)}</span></h1>
<ul class="post-list">
{items}
</ul>"""
    (ROOT / "index.html").write_text(page(SITE_NAME, content, ""), encoding="utf-8")
    print(f"Built {len(posts)} posts.")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "new":
        new_post(" ".join(sys.argv[2:]))
    elif len(sys.argv) == 1:
        build()
    else:
        sys.exit('Usage: python3 build.py  |  python3 build.py new "Post Title"')
