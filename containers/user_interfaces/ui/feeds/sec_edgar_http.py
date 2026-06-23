"""SEC EDGAR HTTP adapter for regulatory filings (SRC-REG-SEC-EDGAR-001).

Fetches SEC filings from EDGAR full-text search and converts them into
canonical regulatory filing data.

Layered split:

* :func:`search_edgar_filings` — HTTP fetcher for SEC filings.
* :func:`parse_edgar_filing` — pure filing → ``Filing`` projection.
* :class::`SECEDGARHTTPPoller` — periodic poller with error handling.
* :class:`FeedStatus` — frozen telemetry snapshot.

INV-15: the parser is pure (caller-supplied ``ts_ns``); the poller
uses HTTP but every event it emits is funneled into the harness.

SEC EDGAR API reference:
https://www.sec.gov/edgar/sec-api-documentation
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import httpx

LOG = logging.getLogger(__name__)

#: SEC EDGAR API endpoint.
SEC_EDGAR_URL = "https://efts.sec.gov/LATEST/search-index"

#: Default poll interval (seconds).
DEFAULT_POLL_INTERVAL_S = 300.0  # 5 minutes

#: Default search terms for relevant filings.
DEFAULT_SEARCH_TERMS: tuple[str, ...] = (
    "cryptocurrency",
    "bitcoin",
    "ethereum",
    "digital assets",
    "blockchain",
)

#: Venue tag stamped onto every emitted filing.
VENUE_TAG = "SEC"


def parse_edgar_filing(
    filing_data: Mapping[str, Any],
    *,
    ts_ns: int,
    venue: str = VENUE_TAG,
) -> dict[str, Any] | None:
    """Project SEC filing data into a regulatory filing structure.

    Returns ``None`` (never raises) if ``filing_data`` is malformed.
    """
    try:
        # SEC EDGAR search-index format
        # Each filing typically contains fields like: ticker, cik, form, date, etc.
        cik = str(filing_data.get("cik", ""))
        ticker = str(filing_data.get("ticker", ""))
        form_type = str(filing_data.get("form", ""))
        file_date = str(filing_data.get("file_date", ""))

        # Extract filing description if available
        description = str(filing_data.get("description", f"{form_type} filing"))

        # Extract document link if available
        filing_url = str(filing_data.get("filing_url", ""))

    except (KeyError, ValueError, TypeError):
        return None

    if not cik:
        return None
    if not form_type:
        return None

    return {
        "ts_ns": ts_ns,
        "source": venue,
        "cik": cik,
        "ticker": ticker,
        "form_type": form_type,
        "description": description,
        "file_date": file_date,
        "filing_url": filing_url,
    }


async def search_edgar_filings(
    search_term: str,
    client: httpx.AsyncClient,
    limit: int = 25,
) -> list[dict[str, Any]] | None:
    """Search SEC EDGAR for filings matching search term."""

    headers = {
        "User-Agent": "DixVision/1.0 (Market Intelligence System)",
        "Accept": "application/json",
    }

    try:
        # Build search parameters
        params = {
            "q": search_term,
            "page": 1,
            "size": limit,
        }

        response = await client.get(SEC_EDGAR_URL, headers=headers, params=params, timeout=15.0)
        response.raise_for_status()
        data = response.json()

        # Parse search results
        filings = data.get("filings", [])
        return filings
    except Exception as e:
        LOG.warning(f"Failed to search SEC EDGAR for '{search_term}': {e}")
        return None


@dataclass(frozen=True, slots=True)
class FeedStatus:
    """Snapshot of poller health — exposed by ``GET /api/feeds/sec/status``."""

    running: bool
    search_terms: tuple[str, ...]
    last_tick_ts_ns: int | None
    filings_received: int
    errors: int


class SECEDGARHTTPPoller:
    """HTTP poller streaming SEC regulatory filings into a sink.

    The sink callable runs synchronously; for cross-thread state
    mutation use :class:`ui.feeds.runner.FeedRunner` which wraps
    the poller and bridges to the FastAPI sync world.
    """

    def __init__(
        self,
        search_terms: Sequence[str],
        sink: Callable[[dict[str, Any]], None],
        *,
        clock_ns: Callable[[], int],
        poll_interval_s: float = DEFAULT_POLL_INTERVAL_S,
        venue: str = VENUE_TAG,
    ) -> None:
        if not search_terms:
            raise ValueError("SECEDGARHTTPPoller: at least one search term required")
        if poll_interval_s <= 0:
            raise ValueError("SECEDGARHTTPPoller: poll_interval_s must be positive")

        self._search_terms: tuple[str, ...] = tuple(search_terms)
        self._sink = sink
        self._clock_ns = clock_ns
        self._poll_interval_s = poll_interval_s
        self._venue = venue
        self._stop_event = asyncio.Event()
        self._filings_received = 0
        self._errors = 0
        self._last_tick_ts_ns: int | None = None
        self._running = False

    @property
    def search_terms(self) -> tuple[str, ...]:
        return self._search_terms

    def status(self) -> FeedStatus:
        return FeedStatus(
            running=self._running,
            search_terms=self._search_terms,
            last_tick_ts_ns=self._last_tick_ts_ns,
            filings_received=self._filings_received,
            errors=self._errors,
        )

    def stop(self) -> None:
        """Signal the run loop to exit on its next iteration."""
        self._stop_event.set()

    async def run(self) -> None:
        """Search SEC EDGAR periodically until ``stop()``."""
        self._running = True
        try:
            async with httpx.AsyncClient() as client:
                while not self._stop_event.is_set():
                    await self._search_filings(client)

                    try:
                        await asyncio.wait_for(
                            self._stop_event.wait(),
                            timeout=self._poll_interval_s,
                        )
                    except TimeoutError:
                        pass
        finally:
            self._running = False

    async def _search_filings(self, client: httpx.AsyncClient) -> None:
        """Search for filings matching all search terms and emit data."""
        for search_term in self._search_terms:
            if self._stop_event.is_set():
                break

            filings = await search_edgar_filings(search_term, client=client)
            if filings is None:
                self._errors += 1
                continue

            for filing in filings:
                if self._stop_event.is_set():
                    break

                filing_data = parse_edgar_filing(filing, ts_ns=self._clock_ns(), venue=self._venue)
                if filing_data is None:
                    self._errors += 1
                    continue

                self._filings_received += 1
                self._last_tick_ts_ns = filing_data["ts_ns"]
                try:
                    self._sink(filing_data)
                except Exception:  # noqa: BLE001
                    self._errors += 1
                    LOG.exception("sec_edgar_http: sink failed")


__all__ = [
    "SEC_EDGAR_URL",
    "DEFAULT_POLL_INTERVAL_S",
    "DEFAULT_SEARCH_TERMS",
    "VENUE_TAG",
    "parse_edgar_filing",
    "search_edgar_filings",
    "FeedStatus",
    "SECEDGARHTTPPoller",
]
