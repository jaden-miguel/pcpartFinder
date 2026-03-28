"""Fetch helpers when httpx hits 403 (TLS fingerprint): system curl + urllib."""

from __future__ import annotations

import asyncio
import os
import shutil
import urllib.error
import urllib.request

import httpx

__all__ = ["resilient_get_text", "resilient_get_bytes"]

_REFERER_REDDIT = "https://www.reddit.com/"
_REFERER_SLICK = "https://slickdeals.net/"


def _image_request_headers(url: str, user_agent: str) -> dict[str, str]:
    h: dict[str, str] = {
        "User-Agent": user_agent,
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    }
    lu = url.lower()
    if "redd.it" in lu or "redditmedia.com" in lu:
        h["Referer"] = _REFERER_REDDIT
    elif "slickdealscdn.com" in lu:
        h["Referer"] = _REFERER_SLICK
    return h


def _curl_executables() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for c in (
        shutil.which("curl"),
        "/usr/bin/curl",
        "/bin/curl",
        "/opt/homebrew/bin/curl",
        "/usr/local/bin/curl",
    ):
        if not c or c in seen:
            continue
        if os.path.isfile(c) and os.access(c, os.X_OK):
            seen.add(c)
            out.append(c)
    return out


async def _curl_once(
    curl_exe: str,
    url: str,
    *,
    accept: str,
    user_agent: str,
    timeout_sec: int,
) -> tuple[str | None, str | None]:
    try:
        proc = await asyncio.create_subprocess_exec(
            curl_exe,
            "-sL",
            "-f",
            "--max-time",
            str(timeout_sec),
            "-A",
            user_agent,
            "-H",
            f"Accept: {accept}",
            "-H",
            "Accept-Language: en-US,en;q=0.9",
            url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc.communicate()
    except FileNotFoundError:
        return None, f"{curl_exe} missing"
    if proc.returncode != 0:
        msg = err.decode().strip() or f"exit {proc.returncode}"
        return None, msg[:400]
    return out.decode("utf-8", errors="replace"), None


def _urllib_get_text_sync(
    url: str,
    *,
    accept: str,
    user_agent: str,
    timeout_sec: int,
) -> tuple[str | None, str | None]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": accept,
            "Accept-Language": "en-US,en;q=0.9",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            return resp.read().decode("utf-8", errors="replace"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code} {e.reason}"[:400]
    except Exception as e:
        return None, str(e)[:400]


async def resilient_get_text(
    url: str,
    *,
    accept: str,
    user_agent: str,
    timeout_sec: int = 25,
) -> tuple[str | None, str | None]:
    """
    Try each known curl binary, then urllib (stdlib). Returns (body, None) or (None, summary).
    """
    errs: list[str] = []
    for exe in _curl_executables():
        body, err = await _curl_once(
            exe, url, accept=accept, user_agent=user_agent, timeout_sec=timeout_sec
        )
        if body:
            return body, None
        if err:
            errs.append(err[:160])

    ubody, uerr = await asyncio.to_thread(
        _urllib_get_text_sync,
        url,
        accept=accept,
        user_agent=user_agent,
        timeout_sec=timeout_sec,
    )
    if ubody:
        return ubody, None
    if uerr:
        errs.append(uerr[:160])

    return None, " | ".join(errs) if errs else "no HTTP fallback available"


async def _curl_once_bytes(
    curl_exe: str,
    url: str,
    *,
    user_agent: str,
    timeout_sec: int,
    max_bytes: int,
) -> tuple[bytes | None, str | None]:
    hdrs = _image_request_headers(url, user_agent)
    args = [
        curl_exe,
        "-sL",
        "-f",
        "--max-time",
        str(timeout_sec),
        "-A",
        user_agent,
    ]
    for k, v in hdrs.items():
        if k == "User-Agent":
            continue
        args.extend(["-H", f"{k}: {v}"])
    args.append(url)
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc.communicate()
    except FileNotFoundError:
        return None, f"{curl_exe} missing"
    if proc.returncode != 0:
        msg = err.decode().strip() or f"exit {proc.returncode}"
        return None, msg[:400]
    if len(out) > max_bytes:
        return None, "response too large"
    return out, None


def _urllib_get_bytes_sync(
    url: str,
    *,
    user_agent: str,
    timeout_sec: int,
    max_bytes: int,
) -> tuple[bytes | None, str | None]:
    h = _image_request_headers(url, user_agent)
    req = urllib.request.Request(url, headers=h, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = resp.read(max_bytes + 1)
            if len(data) > max_bytes:
                return None, "response too large"
            return data, None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code} {e.reason}"[:400]
    except Exception as e:
        return None, str(e)[:400]


async def resilient_get_bytes(
    url: str,
    *,
    user_agent: str,
    timeout_sec: int = 25,
    max_bytes: int = 5 * 1024 * 1024,
) -> tuple[bytes | None, str | None]:
    """Binary GET for images: httpx, then curl, then urllib."""
    headers = _image_request_headers(url, user_agent)
    errs: list[str] = []
    try:
        async with httpx.AsyncClient(
            timeout=timeout_sec,
            follow_redirects=True,
            headers=headers,
        ) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.content
            if len(data) > max_bytes:
                return None, "response too large"
            return data, None
    except Exception as e:
        errs.append(str(e)[:200])

    for exe in _curl_executables():
        data, err = await _curl_once_bytes(
            exe, url, user_agent=user_agent, timeout_sec=timeout_sec, max_bytes=max_bytes
        )
        if data:
            return data, None
        if err:
            errs.append(err[:160])

    udata, uerr = await asyncio.to_thread(
        _urllib_get_bytes_sync,
        url,
        user_agent=user_agent,
        timeout_sec=timeout_sec,
        max_bytes=max_bytes,
    )
    if udata:
        return udata, None
    if uerr:
        errs.append(uerr[:160])

    return None, " | ".join(errs) if errs else "fetch failed"
