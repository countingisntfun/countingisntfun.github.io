#!/usr/bin/env python3
import os
import re
from datetime import datetime
from pathlib import Path
import markdown

# Directories
CONTENT_DIR = Path("content")
BLOG_CONTENT_DIR = CONTENT_DIR / "blog"
NOTES_CONTENT_DIR = CONTENT_DIR / "notes"
BLOG_OUTPUT_DIR = Path("blog")
NOTES_OUTPUT_DIR = Path("notes")

def parse_frontmatter(content):
    """Extract frontmatter and content from markdown file."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content

    frontmatter_text = match.group(1)
    body = match.group(2)

    frontmatter = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body

def render_html_page(title, body_content):
    """Generate a complete HTML page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link rel="stylesheet" href="/css/style.css">
</head>
<body>
  <header>
    <h1>counting isn't fun</h1>
    <nav>
      <a href="/">home</a> ·
      <a href="/blog/">blog</a> ·
      <a href="/notes/">notes</a>
    </nav>
  </header>

  <main>
{body_content}
  </main>

  <footer>
    <small><a href="/blog/">← back to blog</a></small>
  </footer>
</body>
</html>
"""

def render_index_page(title, body_content):
    """Generate an index page (blog list or notes)."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link rel="stylesheet" href="/css/style.css">
</head>
<body>
  <header>
    <h1>counting isn't fun</h1>
    <nav>
      <a href="/">home</a> ·
      <a href="/blog/">blog</a> ·
      <a href="/notes/">notes</a>
    </nav>
  </header>

  <main>
{body_content}
  </main>

  <!-- <footer>
    <small>hello</small>
  </footer> -->
</body>
</html>
"""

def render_notes_page(title, body_content):
    """Generate the notes page with full-width cards."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link rel="stylesheet" href="/css/style.css">
</head>
<body>
  <header>
    <h1>counting isn't fun</h1>
    <nav>
      <a href="/">home</a> ·
      <a href="/blog/">blog</a> ·
      <a href="/notes/">notes</a>
    </nav>
  </header>

{body_content}

  <!-- <footer>
    <small>hello</small>
  </footer> -->
</body>
</html>
"""

def build_blog_posts():
    """Build individual blog post pages and collect metadata."""
    posts = []

    for md_file in BLOG_CONTENT_DIR.glob("*.md"):
        content = md_file.read_text()
        frontmatter, body = parse_frontmatter(content)

        # Convert markdown to HTML
        html_content = markdown.markdown(body)

        # Extract metadata
        title = frontmatter.get('title', md_file.stem)
        date = frontmatter.get('date', '')

        # Generate blog post HTML
        article_html = f"""    <article>
      <h2 class="post-title">{title}</h2>
      <p class="post-meta">
        <time datetime="{date}">{date}</time>
      </p>

{html_content}

    </article>"""

        # Write individual blog post
        output_filename = md_file.stem + ".html"
        output_path = BLOG_OUTPUT_DIR / output_filename
        output_path.write_text(render_html_page(title, article_html))

        # Store metadata for index
        posts.append({
            'title': title,
            'date': date,
            'filename': output_filename
        })

    return posts

def build_blog_index(posts):
    """Build the blog index page."""
    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)

    # Generate list items
    list_items = []
    for post in posts:
        list_items.append(
            f'      <li><a href="/blog/{post["filename"]}">{post["title"]}</a> – {post["date"]}</li>'
        )

    index_html = f"""    <ul reversed>
{chr(10).join(list_items)}
    </ul>"""

    output_path = BLOG_OUTPUT_DIR / "index.html"
    output_path.write_text(render_index_page("blog", index_html))

def build_notes():
    """Build the notes page with all notes embedded."""
    notes = []

    for md_file in NOTES_CONTENT_DIR.glob("*.md"):
        content = md_file.read_text()
        frontmatter, body = parse_frontmatter(content)

        # Convert markdown to HTML
        html_content = markdown.markdown(body)

        # Extract metadata
        date = frontmatter.get('date', '')

        notes.append({
            'date': date,
            'content': html_content
        })

    # Sort notes by date (newest first)
    notes.sort(key=lambda x: x['date'], reverse=True)

    # Generate note cards
    note_cards = []
    for note in notes:
        note_cards.append(f"""    <div class="note-card">
      <div class="note-date">
        <time datetime="{note['date']}">{note['date']}</time>
      </div>
      <div class="note-content">
{note['content']}
      </div>
    </div>""")

    notes_html = "\n\n".join(note_cards)

    output_path = NOTES_OUTPUT_DIR / "index.html"
    output_path.write_text(render_notes_page("notes", notes_html))

def main():
    """Main build function."""
    print("Building site...")

    # Build blog posts and index
    print("Building blog posts...")
    posts = build_blog_posts()
    print(f"  Generated {len(posts)} blog posts")

    print("Building blog index...")
    build_blog_index(posts)

    # Build notes page
    print("Building notes page...")
    build_notes()

    print("Build complete!")

if __name__ == "__main__":
    main()
