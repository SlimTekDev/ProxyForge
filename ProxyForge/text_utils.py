"""Display helpers for ProxyForge. Fix common DB/encoding mojibake for UI."""
import re


def fix_apostrophe_mojibake(s: str) -> str:
    """Replace UTF-8-mojibake apostrophe (ΓÇÖ), en-dash (ΓÇô), and similar with correct characters.
    Use when displaying text from DB that may have been stored or transmitted with wrong encoding.
    """
    if not s or not isinstance(s, str):
        return s
    s = (
        s.replace("\u2019", "'")  # Unicode right single quote
        .replace("\u2018", "'")   # Unicode left single quote
        .replace("ΓÇÖ", "'")     # UTF-8 U+2019 misinterpreted as Latin-1
        .replace("â€™", "'")     # common Windows mojibake for '
        .replace("Ã¢â‚¬â„¢", "'")
    )
    # En-dash mojibake: UTF-8 bytes E2 80 93 (U+2013) misinterpreted as Latin-1 or CP1252 (use escapes only to avoid syntax errors)
    s = s.replace("\u00e2\u0080\u0093", "\u2013")   # Latin-1: â + \x80 + \x93
    s = s.replace("\u0393\u00c7\u00f4", "\u2013")   # "ΓÇô" visual (Gamma, C-cedilla, o-circumflex)
    s = s.replace("\u00e2\u20ac\u201c", "\u2013")   # Windows: â + euro + curly quote
    return s


def clean_html_and_mojibake(text, preserve_newlines=True):
    """Strip HTML tags and fix mojibake in text from 40K/Wahapedia DB columns.
    Use for one-off DB cleaning or before display.
    - Removes all HTML tags (div, span, img, table, etc.).
    - Converts <br> to newline before stripping so structure is preserved.
    - Decodes common HTML entities (&nbsp;, &amp;, &quot;, &#39;, etc.).
    - Fixes apostrophe/quote mojibake (ΓÇÖ -> ', etc.).
    - Normalizes whitespace (collapse spaces, trim). If preserve_newlines=True, keeps \\n.
    """
    if text is None:
        return None
    s = str(text).strip()
    if not s:
        return s
    # Convert line breaks to newline before stripping tags
    for br in ("<br>", "<br/>", "<br />", "</br>"):
        s = s.replace(br, "\n")
    # Remove all HTML tags
    s = re.sub(r"<[^>]+>", "", s)
    # Decode common entities
    s = (
        s.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&apos;", "'")
    )
    try:
        import html
        s = html.unescape(s)
    except Exception:
        pass
    s = fix_apostrophe_mojibake(s)
    # Normalize whitespace: collapse runs of space, trim each line and overall
    if preserve_newlines:
        lines = [" ".join(ln.split()) for ln in s.split("\n")]
        s = "\n".join(ln for ln in lines if ln is not None)
    else:
        s = " ".join(s.split())
    return s.strip() if s else s
