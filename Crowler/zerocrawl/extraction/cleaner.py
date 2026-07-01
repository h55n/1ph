"""
ZeroCrawl — HTML → Markdown Cleaner
Runs both markdownify and html2text, picks the better output.
"""
from __future__ import annotations

import re


def _score_markdown(md: str) -> float:
    """
    Score a markdown string for quality.
    Higher = better.
    """
    if not md:
        return 0.0

    words = len(md.split())
    headings = len(re.findall(r'^#{1,6}\s', md, re.MULTILINE))
    noise_chars = len(re.findall(r'[\\|<>\[\]{}]', md))
    blank_lines = len(re.findall(r'\n{3,}', md))

    score = words * 1.0
    score += headings * 5.0
    score -= noise_chars * 0.5
    score -= blank_lines * 0.3
    return score


def _clean_markdown(md: str) -> str:
    """Clean common markdown artifacts."""
    if not md:
        return ""

    # Collapse 3+ newlines to 2
    md = re.sub(r'\n{3,}', '\n\n', md)
    # Remove trailing whitespace on lines
    md = re.sub(r'[ \t]+\n', '\n', md)
    # Remove leading/trailing whitespace
    md = md.strip()
    return md


def html_to_markdown(html: str, prefer: str = "auto") -> str:
    """
    Convert HTML to Markdown.
    Runs both markdownify and html2text, picks higher-scoring output.
    prefer: 'auto' | 'markdownify' | 'html2text'
    """
    if not html:
        return ""

    md_markdownify = ""
    md_html2text = ""

    # Try markdownify
    if prefer in ("auto", "markdownify"):
        try:
            import markdownify
            md_markdownify = markdownify.markdownify(
                html,
                heading_style="ATX",
                bullets="-",
                strip=["script", "style"],
            )
            md_markdownify = _clean_markdown(md_markdownify)
        except Exception:
            pass

    # Try html2text
    if prefer in ("auto", "html2text"):
        try:
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0       # No line wrapping
            h.unicode_snob = True
            h.protect_links = True
            md_html2text = _clean_markdown(h.handle(html))
        except Exception:
            pass

    if prefer == "markdownify":
        return md_markdownify or md_html2text
    if prefer == "html2text":
        return md_html2text or md_markdownify

    # Auto: pick the better one
    score_mk = _score_markdown(md_markdownify)
    score_h2t = _score_markdown(md_html2text)

    if score_mk >= score_h2t:
        return md_markdownify or md_html2text
    return md_html2text or md_markdownify


def extract_plain_text(html: str) -> str:
    """Extract plain text from HTML, no markdown formatting."""
    try:
        from selectolax.parser import HTMLParser
        tree = HTMLParser(html)
        return tree.text(separator="\n", strip=True)
    except Exception:
        pass
    try:
        import re
        return re.sub(r'<[^>]+>', ' ', html).strip()
    except Exception:
        return ""
