"""Internet access tool: search + optional fetch + cleaned page text."""

from __future__ import annotations

import asyncio
import re
from typing import Optional  # Only if you prefer Optional; see note below

import requests
from duckduckgo_search import DDGS

try:
    from bs4 import BeautifulSoup  # optional but recommended
except ImportError:  # pragma: no cover
    BeautifulSoup = None  # type: ignore

USER_AGENT = (
    "Mozilla/5.0 (compatible; MCP-Internet-Tool/1.0; +https://example.local)"
)
REQ_TIMEOUT = 10


def _clean_html(html: str, max_chars: int) -> str:
    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "lxml")
        txt = soup.get_text("\n", strip=True)
    else:
        txt = re.sub(r"<[^>]+>", " ", html)
    return " ".join(txt.split())[:max_chars]


async def _fetch_url(url: str, max_chars: int) -> str:
    loop = asyncio.get_running_loop()

    def _do_get() -> str:
        try:
            r = requests.get(
                url,
                timeout=REQ_TIMEOUT,
                headers={"User-Agent": USER_AGENT},
            )
            r.raise_for_status()
            return _clean_html(r.text, max_chars)
        except Exception as exc:  # pragma: no cover
            return f"[ERROR fetching {url}: {exc}]"

    return await loop.run_in_executor(None, _do_get)


async def internet_research(
    query: str,
    num_results: int = 3,
    max_chars: int = 4000,
    fetch: bool = True,
    safesearch: str = "moderate",
    timelimit: str | None = None,  # you can swap to Optional[str]
):
    """Search DuckDuckGo and optionally fetch pages; returns a JSON-safe dict."""
    results: list[dict] = []

    with DDGS() as ddgs:
        for hit in ddgs.text(
            query,
            safesearch=safesearch,
            timelimit=timelimit,
            max_results=num_results,
        ):
            results.append(
                {
                    "title": hit.get("title") or "",
                    "url": hit.get("href") or "",
                    "snippet": hit.get("body") or "",
                    "content": None,
                }
            )

    if not results or not fetch:
        return {"query": query, "results": results}

    tasks = [_fetch_url(item["url"], max_chars) for item in results if item["url"]]
    fetched = await asyncio.gather(*tasks, return_exceptions=True)

    i = 0
    for item in results:
        if not item["url"]:
            continue
        data = fetched[i]
        i += 1
        item["content"] = (
            f"[ERROR: {data}]" if isinstance(data, Exception) else data
        )

    return {"query": query, "results": results}


async def get_url(url: str, max_chars: int = 8000):
    """Fetch *url* and return plain text truncated to *max_chars* characters."""
    return await _fetch_url(url, max_chars)