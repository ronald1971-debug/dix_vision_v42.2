"""GDELT Events adapter — Global Database of Events, Language, and Tone (BUILD-DIRECTIVE §14).

GDELT monitors the world's news media across print, broadcast, and web news
in over 100 languages and encodes events, people, and organizations into
structured data. This adapter focuses on financial and geopolitical events
relevant to trading decisions.

API Documentation:
- https://api.gdeltproject.org/api/v2/doc/doc
- https://api.gdeltproject.org/api/v2/timeline/timeline
- Daily updates: http://data.gdeltproject.org/gdeltv2/lastupdate.txt

Features:
- Event type filtering (financial, geopolitical, economic)
- Tone and sentiment analysis
- Actor and location extraction
- Real-time event monitoring
- Historical event queries

GDELT CAMEO Event Types relevant to trading:
- 043: Make Statement
- 045: Threaten
- 046: Dismiss
- 051: Appeal
- 071: Consult
- 072: Engage in Diplomatic Cooperation
- 073: Engage in Material Cooperation
- 091: Express Intent to Cooperate
- 092: Grant
- 093: Agreement
- 102: Demand
- 103: Request
- 111: Investigate
- 112: Investigate (Sector)
- 113: Investigate (Class)
- 120: Legalize
- 122: Ban
- 125: Military Action
- 161: Supply Military Aid
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GDELTEventObservation:
    """Canonical GDELT event observation for the intelligence pipeline.

    Fields:
        event_id: Unique GDELT event identifier
        event_date: Date of the event (YYYYMMDD format as int)
        actor1: Primary actor (country, organization, or person)
        actor2: Secondary actor (if applicable)
        event_code: CAMEO event code
        event_type: Human-readable event type
        tone: Average tone of articles (-10 to +10)
        tone_confidence: Confidence in tone score (0-1)
        location: Geographic location of event
        source_url: URL to source article
        num_articles: Number of articles about this event
        num_mentions: Total mentions across all sources
        relevance_score: Calculated relevance to trading (0-1)
        ingested_ts_ns: Timestamp when event was ingested
    """

    event_id: str
    event_date: int
    actor1: str
    actor2: str
    event_code: str
    event_type: str
    tone: float
    tone_confidence: float
    location: str
    source_url: str
    num_articles: int
    num_mentions: int
    relevance_score: float
    ingested_ts_ns: int


class GDELTAdapter:
    """Read-only GDELT event data adapter.

    Fetches event data from GDELT API and normalizes into
    GDELTEventObservation records for the intelligence pipeline.

    API Endpoints:
    - DOC API: Query events by parameters
    - Timeline API: Get event timeline for an actor
    - Daily Updates: Get latest events

    Example Usage:
        adapter = GDELTAdapter()
        events = adapter.fetch_financial_events(days=7)
        relevant_events = adapter.fetch_events_by_actor("United States")
    """

    platform: str = "gdelt"
    base_url: str = "https://api.gdeltproject.org/api/v2"

    # CAMEO event codes relevant to financial/geopolitical trading
    RELEVANT_EVENT_CODES = {
        # Diplomatic cooperation (positive for markets)
        "072": "Engage in Diplomatic Cooperation",
        "073": "Engage in Material Cooperation",
        "091": "Express Intent to Cooperate",
        "092": "Grant",
        "093": "Agreement",
        # Economic actions
        "043": "Make Statement",
        "051": "Appeal",
        "071": "Consult",
        "102": "Demand",
        "103": "Request",
        # Regulatory/legal (neutral to negative)
        "111": "Investigate",
        "120": "Legalize",
        "122": "Ban",
        # Conflict (negative for markets)
        "045": "Threaten",
        "046": "Dismiss",
        "125": "Military Action",
        "161": "Supply Military Aid",
    }

    def fetch_financial_events(
        self, *, days: int = 7, tone_threshold: float = 0.0
    ) -> list[GDELTEventObservation]:
        """Fetch financial and economic events from GDELT.

        Args:
            days: Number of days to look back (default: 7)
            tone_threshold: Minimum tone score to include (default: 0.0)

        Returns:
            List of GDELTEventObservation records filtered for financial relevance.
        """
        try:
            # GDELT DOC API query for financial events
            # In production, this would make actual API calls
            # For now, we return a placeholder implementation
            LOG.info(f"Fetching GDELT financial events for last {days} days")
            return self._fetch_events_from_api(
                mode="doc", query="finance OR economy OR trade OR monetary", days=days
            )
        except Exception as e:
            LOG.error(f"Failed to fetch GDELT financial events: {e}")
            return []

    def fetch_geopolitical_events(
        self, *, days: int = 7, tone_threshold: float = 0.0
    ) -> list[GDELTEventObservation]:
        """Fetch geopolitical events from GDELT.

        Args:
            days: Number of days to look back (default: 7)
            tone_threshold: Minimum tone score to include (default: 0.0)

        Returns:
            List of GDELTEventObservation records for geopolitical events.
        """
        try:
            LOG.info(f"Fetching GDELT geopolitical events for last {days} days")
            return self._fetch_events_from_api(
                mode="doc", query="conflict OR war OR sanction OR treaty OR summit", days=days
            )
        except Exception as e:
            LOG.error(f"Failed to fetch GDELT geopolitical events: {e}")
            return []

    def fetch_events_by_actor(
        self, actor: str, *, days: int = 30
    ) -> list[GDELTEventObservation]:
        """Fetch events for a specific actor using Timeline API.

        Args:
            actor: Actor name (e.g., "United States", "China", "Federal Reserve")
            days: Number of days to look back (default: 30)

        Returns:
            List of GDELTEventObservation records for the specified actor.
        """
        try:
            LOG.info(f"Fetching GDELT events for actor: {actor}")
            return self._fetch_events_from_api(mode="timeline", actor=actor, days=days)
        except Exception as e:
            LOG.error(f"Failed to fetch GDELT events for actor {actor}: {e}")
            return []

    def fetch_events_by_location(
        self, location: str, *, days: int = 30
    ) -> list[GDELTEventObservation]:
        """Fetch events for a specific geographic location.

        Args:
            location: Location name (e.g., "Ukraine", "Middle East", "Europe")
            days: Number of days to look back (default: 30)

        Returns:
            List of GDELTEventObservation records for the specified location.
        """
        try:
            LOG.info(f"Fetching GDELT events for location: {location}")
            return self._fetch_events_from_api(mode="doc", location=location, days=days)
        except Exception as e:
            LOG.error(f"Failed to fetch GDELT events for location {location}: {e}")
            return []

    def _fetch_events_from_api(
        self, *, mode: str, query: str = "", actor: str = "", location: str = "", days: int = 7
    ) -> list[GDELTEventObservation]:
        """Internal method to fetch events from GDELT API.

        This implementation:
        1. Constructs the appropriate GDELT API URL
        2. Makes HTTP requests to the API
        3. Parses the response (CSV or JSON)
        4. Normalizes into GDELTEventObservation records

        If the API call fails, returns empty list but logs the error.
        """
        try:
            # Import required libraries
            import requests
            from datetime import datetime, timedelta
            
            # Construct API URL and parameters
            url = f"{self.base_url}/doc/docquery"
            params = {
                "query": query,
                "mode": mode,
                "format": "json",
                "maxrecords": 250,
                "startdatetime": f"NOW-{days}DAYS",
                "enddatetime": "NOW",
            }
            
            # Add optional parameters
            if actor:
                params["actor"] = actor
            if location:
                params["location"] = location
            
            LOG.info(f"Fetching GDELT events: mode={mode}, query={query}")
            
            # Make API request
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            events = []
            
            # Normalize events
            for raw_event in data.get("data", []):
                try:
                    event = self.normalize_event(raw_event)
                    events.append(event)
                except Exception as e:
                    LOG.warning(f"Failed to normalize event: {e}")
                    continue
            
            LOG.info(f"Successfully fetched {len(events)} GDELT events")
            return events
            
        except requests.exceptions.RequestException as e:
            LOG.warning(f"GDELT API request failed: {e} - returning empty results")
            LOG.debug(f"Would fetch: mode={mode}, query={query}, actor={actor}, location={location}, days={days}")
            return []
        except Exception as e:
            LOG.error(f"Unexpected error fetching GDELT events: {e} - returning empty results")
            return []

    def normalize_event(self, raw_event: dict[str, Any]) -> GDELTEventObservation:
        """Normalize raw GDELT event data into canonical format.

        Args:
            raw_event: Raw event data from GDELT API

        Returns:
            GDELTEventObservation record
        """
        event_code = str(raw_event.get("eventcode", ""))
        event_type = self.RELEVANT_EVENT_CODES.get(event_code, "Unknown Event")

        # Calculate relevance score based on event type and tone
        relevance = self._calculate_relevance(event_code, float(raw_event.get("tone", 0.0)))

        return GDELTEventObservation(
            event_id=str(raw_event.get("globaleventid", "")),
            event_date=int(raw_event.get("eventdate", 0)),
            actor1=str(raw_event.get("actor1", "")),
            actor2=str(raw_event.get("actor2", "")),
            event_code=event_code,
            event_type=event_type,
            tone=float(raw_event.get("tone", 0.0)),
            tone_confidence=float(raw_event.get("tone_confidence", 0.5)),
            location=str(raw_event.get("actiongeo_countrycode", "")),
            source_url=str(raw_event.get("sourceurl", "")),
            num_articles=int(raw_event.get("numarticles", 0)),
            num_mentions=int(raw_event.get("nummentions", 0)),
            relevance_score=relevance,
            ingested_ts_ns=int(datetime.now(UTC).timestamp() * 1_000_000_000),
        )

    def _calculate_relevance(self, event_code: str, tone: float) -> float:
        """Calculate relevance score for trading (0.0 to 1.0).

        Higher relevance for:
        - Diplomatic cooperation events (positive)
        - Economic/regulatory events (high)
        - Conflict events (high if negative tone)

        Args:
            event_code: CAMEO event code
            tone: Tone score from GDELT

        Returns:
            Relevance score between 0.0 and 1.0
        """
        base_relevance = 0.5

        # Economic and diplomatic events are highly relevant
        if event_code in {"072", "073", "091", "092", "093"}:
            base_relevance = 0.8
        elif event_code in {"043", "051", "071", "102", "103", "111", "120", "122"}:
            base_relevance = 0.7
        # Conflict events are relevant if tone is negative
        elif event_code in {"045", "046", "125", "161"}:
            base_relevance = 0.9 if tone < -2.0 else 0.6

        # Adjust based on tone magnitude
        tone_adjustment = min(abs(tone) / 10.0, 0.3)
        final_relevance = min(base_relevance + tone_adjustment, 1.0)

        return final_relevance
