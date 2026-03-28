from __future__ import annotations


def build_tgram_url(bot_token: str, chat_id: str) -> str:
    bt = bot_token.strip()
    cid = str(chat_id).strip()
    return f"tgram://{bt}/{cid}"


def parse_tgram_url(url: str) -> tuple[str, str] | None:
    u = url.strip()
    if not u.startswith("tgram://"):
        return None
    rest = u[8:]
    if "/" not in rest:
        return None
    token, chat = rest.split("/", 1)
    if not token or not chat:
        return None
    return token, chat


def split_apprise_urls(urls: list[str]) -> tuple[tuple[str, str] | None, list[str]]:
    tgram: tuple[str, str] | None = None
    other: list[str] = []
    for u in urls:
        parsed = parse_tgram_url(u)
        if parsed:
            if tgram is None:
                tgram = parsed
            else:
                other.append(u)
        else:
            other.append(u)
    return tgram, other


def merge_apprise_urls(
    telegram: tuple[str, str] | None,
    other: list[str],
) -> list[str]:
    out: list[str] = []
    if telegram and telegram[0] and telegram[1]:
        out.append(build_tgram_url(telegram[0], telegram[1]))
    out.extend(other)
    return out
