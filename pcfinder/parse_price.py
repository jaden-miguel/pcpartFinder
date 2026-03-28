from __future__ import annotations

import re


def parse_price_text(text: str) -> float | None:
    """
    Extract a single price from messy storefront text.
    Prefers the last plausible money token (often the sale price after strikethrough MSRP).
    """
    if not text:
        return None
    normalized = text.replace("\xa0", " ").strip()
    # Patterns: $1,234.56  |  1234,56 €  |  1234.56
    candidates: list[float] = []
    for m in re.finditer(
        r"""
        (?P<num>
            (?:\d{1,3}(?:[.,]\d{3})+|\d+)
            (?:[.,]\d{2})?
        )
        """,
        normalized,
        re.VERBOSE,
    ):
        raw = m.group("num")
        val = _money_string_to_float(raw)
        if val is not None and 0.01 <= val <= 500_000:
            candidates.append(val)
    if not candidates:
        return None
    return candidates[-1]


def _money_string_to_float(s: str) -> float | None:
    s = s.strip()
    if not s:
        return None
    last_sep = max(s.rfind(","), s.rfind("."))
    if last_sep == -1:
        try:
            return float(s)
        except ValueError:
            return None
    int_part = s[:last_sep].replace(",", "").replace(".", "")
    frac = s[last_sep + 1 :]
    if not int_part and not frac:
        return None
    try:
        whole = int(int_part) if int_part else 0
        frac_digits = "".join(c for c in frac if c.isdigit())[:2].ljust(2, "0")
        f = float(f"{whole}.{frac_digits}")
        return f
    except ValueError:
        return None
