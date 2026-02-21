"""Display helpers for ProxyForge. Fix common DB/encoding mojibake for UI."""


def fix_apostrophe_mojibake(s: str) -> str:
    """Replace UTF-8-mojibake apostrophe (ΓÇÖ) and similar with ASCII apostrophe.
    Use when displaying text from DB that may have been stored or transmitted with wrong encoding.
    """
    if not s or not isinstance(s, str):
        return s
    return (
        s.replace("\u2019", "'")  # Unicode right single quote
        .replace("\u2018", "'")   # Unicode left single quote
        .replace("ΓÇÖ", "'")     # UTF-8 U+2019 misinterpreted as Latin-1
        .replace("â€™", "'")     # common Windows mojibake for '
        .replace("Ã¢â‚¬â„¢", "'")
    )
