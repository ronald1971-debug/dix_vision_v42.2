"""Reddit HTTP adapter for social sentiment (SRC-SOCIAL-REDDIT-001).

Fetches Reddit posts/comments from public subreddits and converts them into
canonical social sentiment data.

Layered split:

* :func:`fetch_reddit_posts` — HTTP fetcher for Reddit data.
* :func:`parse_reddit_post` — pure post → ``SocialPost`` projection.
* :class:`RedditHTTPPoller` — periodic poller with error handling.
* :class:`FeedStatus` — frozen telemetry snapshot.

INV-15: the parser is pure (caller-supplied ``ts_ns``); the poller
uses HTTP but every event it emits is funneled into the harness.

Reddit API reference:
https://www.reddit.com/dev/api/
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import httpx

LOG = logging.getLogger(__name__)

#: Reddit public API endpoint.
REDDIT_API_URL = "https://www.reddit.com"

#: Default poll interval (seconds).
DEFAULT_POLL_INTERVAL_S = 60.0

#: Default subreddits to monitor.
DEFAULT_SUBREDDITS: tuple[str, ...] = (
    "cryptocurrency",
    "bitcoin",
    "ethereum",
    "defi",
    "wallstreetbets",
)

#: Venue tag stamped onto every emitted social post.
VENUE_TAG = "REDDIT"


def parse_reddit_post(
    post_data: Mapping[str, Any],
    *,
    ts_ns: int,
    venue: str = VENUE_TAG,
) -> dict[str, Any] | None:
    """Project Reddit post data into a social sentiment structure.

    Returns ``None`` (never raises) if ``post_data`` is malformed.
    """
    try:
        # Reddit API format: {"data": {"title": "...", "selftext": "...", "author": "...", ...}}
        data = post_data.get("data", {})
        
        title = str(data.get("title", ""))
        author = str(data.get("author", "[deleted]"))
        subreddit = str(data.get("subreddit", ""))
        ups = int(data.get("ups", 0))
        num_comments = int(data.get("num_comments", 0))
        
        # Combine title and selftext for content analysis
        content = title
        selftext = data.get("selftext", "")
        if selftext:
            content += "\n\n" + str(selftext)
        
        # Create timestamp from Reddit's created_utc
        created_utc = data.get("created_utc")
        if created_utc:
            post_timestamp = int(created_utc)
        else:
            post_timestamp = ts_ns // 1_000_000_000
        
    except (KeyError, ValueError, TypeError):
        return None

    if not title:
        return None
    if ups < 0:  # Filter out heavily downvoted content
        return None

    return {
        "ts_ns": ts_ns,
        "source": venue,
        "author": author,
        "subreddit": subreddit,
        "content": content,
        "upvotes": ups,
        "comments": num_comments,
        "post_timestamp": post_timestamp,
    }


async def fetch_reddit_posts(
    subreddit: str,
    client: httpx.AsyncClient,
    limit: int = 25,
) -> list[dict[str, Any]] | None:
    """Fetch posts from a subreddit."""
    url = f"{REDDIT_API_URL}/r/{subreddit}/new.json?limit={limit}"
    
    headers = {
        "User-Agent": "DixVision/1.0 (Market Intelligence System)",
    }

    try:
        response = await client.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        posts = data.get("data", {}).get("children", [])
        return posts
    except Exception as e:
        LOG.warning(f"Failed to fetch Reddit posts from r/{subreddit}: {e}")
        return None


@dataclass(frozen=True, slots=True)
class FeedStatus:
    """Snapshot of poller health — exposed by ``GET /api/feeds/reddit/status``."""

    running: bool
    subreddits: tuple[str, ...]
    last_tick_ts_ns: int | None
    posts_received: int
    errors: int


class RedditHTTPPoller:
    """HTTP poller streaming Reddit social sentiment into a sink.

    The sink callable runs synchronously; for cross-thread state
    mutation use :class:`ui.feeds.runner.FeedRunner` which wraps
    the poller and bridges to the FastAPI sync world.
    """

    def __init__(
        self,
        subreddits: Sequence[str],
        sink: Callable[[dict[str, Any]], None],
        *,
        clock_ns: Callable[[], int],
        poll_interval_s: float = DEFAULT_POLL_INTERVAL_S,
        venue: str = VENUE_TAG,
    ) -> None:
        if not subreddits:
            raise ValueError("RedditHTTPPoller: at least one subreddit required")
        if poll_interval_s <= 0:
            raise ValueError("RedditHTTPPoller: poll_interval_s must be positive")

        self._subreddits: tuple[str, ...] = tuple(subreddits)
        self._sink = sink
        self._clock_ns = clock_ns
        self._poll_interval_s = poll_interval_s
        self._venue = venue
        self._stop_event = asyncio.Event()
        self._posts_received = 0
        self._errors = 0
        self._last_tick_ts_ns: int | None = None
        self._running = False

    @property
    def subreddits(self) -> tuple[str, ...]:
        return self._subreddits

    def status(self) -> FeedStatus:
        return FeedStatus(
            running=self._running,
            subreddits=self._subreddits,
            last_tick_ts_ns=self._last_tick_ts_ns,
            posts_received=self._posts_received,
            errors=self._errors,
        )

    def stop(self) -> None:
        """Signal the run loop to exit on its next iteration."""
        self._stop_event.set()

    async def run(self) -> None:
        """Poll subreddits periodically until ``stop()``."""
        self._running = True
        try:
            async with httpx.AsyncClient() as client:
                while not self._stop_event.is_set():
                    await self._poll_subreddits(client)

                    try:
                        await asyncio.wait_for(
                            self._stop_event.wait(),
                            timeout=self._poll_interval_s,
                        )
                    except TimeoutError:
                        pass
        finally:
            self._running = False

    async def _poll_subreddits(self, client: httpx.AsyncClient) -> None:
        """Fetch posts from all subreddits and emit social data."""
        for subreddit in self._subreddits:
            if self._stop_event.is_set():
                break

            posts = await fetch_reddit_posts(subreddit, client=client)
            if posts is None:
                self._errors += 1
                continue

            for post in posts:
                if self._stop_event.is_set():
                    break

                social_data = parse_reddit_post(post, ts_ns=self._clock_ns(), venue=self._venue)
                if social_data is None:
                    self._errors += 1
                    continue

                self._posts_received += 1
                self._last_tick_ts_ns = social_data["ts_ns"]
                try:
                    self._sink(social_data)
                except Exception:  # noqa: BLE001
                    self._errors += 1
                    LOG.exception("reddit_http: sink failed")


__all__ = [
    "REDDIT_API_URL",
    "DEFAULT_POLL_INTERVAL_S",
    "DEFAULT_SUBREDDITS",
    "VENUE_TAG",
    "parse_reddit_post",
    "fetch_reddit_posts",
    "FeedStatus",
    "RedditHTTPPoller",
]