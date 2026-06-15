"""Scraper abstraction. YouTube oEmbed works with zero keys (great for the MVP slice).
Other platforms are stubbed behind the same interface; wire official APIs / a licensed
provider / Playwright fallback per the architecture notes."""
from __future__ import annotations

import re
from typing import Protocol

import httpx

PLATFORM_PATTERNS = {
    "youtube": re.compile(r"(youtube\.com|youtu\.be)", re.I),
    "tiktok": re.compile(r"tiktok\.com", re.I),
    "instagram": re.compile(r"instagram\.com", re.I),
    "linkedin": re.compile(r"linkedin\.com", re.I),
}


def detect_platform(url: str) -> str:
    for name, pat in PLATFORM_PATTERNS.items():
        if pat.search(url):
            return name
    return "unknown"


class FetchResult(dict):
    """Loose dict: embed_html, thumbnail_url, caption, media_type, external_id, metrics, posted_at."""


class ScraperProvider(Protocol):
    async def fetch(self, url: str) -> FetchResult: ...


class YouTubeScraper:
    async def fetch(self, url: str) -> FetchResult:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(
                "https://www.youtube.com/oembed",
                params={"url": url, "format": "json"},
            )
            r.raise_for_status()
            data = r.json()
        return FetchResult(
            embed_html=data.get("html"),
            thumbnail_url=data.get("thumbnail_url"),
            caption=data.get("title"),
            media_type="video",
            external_id=_yt_id(url),
            metrics={},  # populate via YouTube Data API v3 when YOUTUBE_API_KEY is set
            posted_at=None,
        )


class TikTokScraper:
    async def fetch(self, url: str) -> FetchResult:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get("https://www.tiktok.com/oembed", params={"url": url})
            r.raise_for_status()
            data = r.json()
        return FetchResult(
            embed_html=data.get("html"),
            thumbnail_url=data.get("thumbnail_url"),
            caption=data.get("title"),
            media_type="video",
            external_id=None,
            metrics={},
            posted_at=None,
        )


class UnsupportedScraper:
    def __init__(self, platform: str):
        self.platform = platform

    async def fetch(self, url: str) -> FetchResult:
        # Honest placeholder: Instagram/LinkedIn need app review / a data provider /
        # Playwright screenshot. Returns a preview-less record so the row still exists.
        return FetchResult(
            embed_html=None,
            thumbnail_url=None,
            caption=f"[{self.platform}] preview not available — wire a data provider",
            media_type="unknown",
            external_id=None,
            metrics={},
            posted_at=None,
        )


def get_scraper(platform: str) -> ScraperProvider:
    return {
        "youtube": YouTubeScraper,
        "tiktok": TikTokScraper,
    }.get(platform, lambda: UnsupportedScraper(platform))()


def _yt_id(url: str) -> str | None:
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", url)
    return m.group(1) if m else None
