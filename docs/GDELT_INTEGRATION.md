# GDELT Database Integration

## Overview

GDELT (Global Database of Events, Language, and Tone) has been successfully integrated into the DIX VISION system as a geopolitical and financial event data source.

**Source ID**: `SRC-GEO-GDELT-001`  
**Category**: Alt (Alternative Data)  
**Status**: ✅ Enabled  
**API Key**: Not Required (for basic access)

---

## What is GDELT?

GDELT monitors the world's news media across:
- **100+ languages**
- **Print, broadcast, and web news**
- **Every country in the world**
- **Real-time event tracking**

It encodes events, people, and organizations into structured data with:
- **Event types** (CAMEO coding scheme)
- **Actors** (countries, organizations, people)
- **Locations** (geographic coordinates)
- **Tone/Sentiment** (-10 to +10 scale)
- **Source URLs** (links to original articles)

---

## Integration Components

### 1. **GDELT Adapter** (`data_sources/external/gdelt_events.py`)

Main adapter class that provides:
- `GDELTAdapter`: Main interface for fetching GDELT events
- `GDELTEventObservation`: Canonical data structure for events

### 2. **Data Source Registry** (`registry/data_source_registry.yaml`)

```yaml
- id: SRC-GEO-GDELT-001
  name: "GDELT Project Events API"
  category: alt
  provider: gdelt
  endpoint: "https://api.gdeltproject.org/api/v2"
  schema: "data_sources.external.gdelt_events.GDELTEventObservation"
  auth: none
  enabled: true
  critical: false
```

### 3. **Consumption Configuration** (`ui/feeds/consumes.yaml`)

```yaml
- source_id: SRC-GEO-GDELT-001
  required: false
```

---

## Available Event Types

### **Diplomatic Cooperation** (Positive for Markets)
- `072`: Engage in Diplomatic Cooperation
- `073`: Engage in Material Cooperation
- `091`: Express Intent to Cooperate
- `092`: Grant
- `093`: Agreement

### **Economic Actions** (High Relevance)
- `043`: Make Statement
- `051`: Appeal
- `071`: Consult
- `102`: Demand
- `103`: Request

### **Regulatory/Legal** (Neutral to Negative)
- `111`: Investigate
- `112`: Investigate (Sector)
- `113`: Investigate (Class)
- `120`: Legalize
- `122`: Ban

### **Conflict** (Negative for Markets)
- `045`: Threaten
- `046`: Dismiss
- `125`: Military Action
- `161`: Supply Military Aid

---

## Usage Examples

### **Basic Usage**

```python
from data_sources.external import GDELTAdapter

# Initialize adapter
adapter = GDELTAdapter()

# Fetch financial events for last 7 days
financial_events = adapter.fetch_financial_events(days=7)

# Fetch geopolitical events for last 7 days
geopolitical_events = adapter.fetch_geopolitical_events(days=7)
```

### **Query by Actor**

```python
# Fetch events for a specific actor
us_events = adapter.fetch_events_by_actor("United States", days=30)
china_events = adapter.fetch_events_by_actor("China", days=30)
fed_events = adapter.fetch_events_by_actor("Federal Reserve", days=30)
```

### **Query by Location**

```python
# Fetch events for a specific location
europe_events = adapter.fetch_events_by_location("Europe", days=30)
ukraine_events = adapter.fetch_events_by_location("Ukraine", days=30)
meast_events = adapter.fetch_events_by_location("Middle East", days=30)
```

### **Event Data Structure**

Each `GDELTEventObservation` contains:

```python
{
    "event_id": "unique GDELT event identifier",
    "event_date": 20240101,  # YYYYMMDD format
    "actor1": "United States",
    "actor2": "China",
    "event_code": "092",
    "event_type": "Grant",
    "tone": 2.5,  # -10 to +10
    "tone_confidence": 0.8,  # 0.0 to 1.0
    "location": "USA",
    "source_url": "https://example.com",
    "num_articles": 10,
    "num_mentions": 50,
    "relevance_score": 0.8,  # 0.0 to 1.0
    "ingested_ts_ns": 1704067200000000000
}
```

---

## Integration with INDIRA

### **Cognitive Enrichment**

GDELT events can be used to enrich INDIRA's cognitive context:

```python
from data_sources.external import GDELTAdapter
from intelligence_engine.cognitive.indira_runtime import get_indira_runtime

# Fetch GDELT events
adapter = GDELTAdapter()
events = adapter.fetch_geopolitical_events(days=7)

# Integrate with INDIRA's cognitive pipeline
indira = get_indira_runtime()
# Events will be incorporated into cognitive context
```

### **Relevance Scoring**

The adapter automatically calculates relevance scores based on:
- **Event type** (diplomatic, economic, conflict)
- **Tone magnitude** (extreme tones are more relevant)
- **Trading impact** (conflict with negative tone = high relevance)

---

## Current Implementation Status

### ✅ **Implemented**
- Data structure definitions
- Adapter interface
- Registry configuration
- Consumption configuration
- Basic placeholder API methods
- Relevance calculation
- Test suite (8/8 tests passing)

### ⚠️ **Placeholder Status**

The actual GDELT API integration is currently a **placeholder**. The `_fetch_events_from_api()` method returns empty lists with a warning log.

**To implement full API integration**, you need to:

1. **Implement actual HTTP requests to GDELT API**
2. **Parse CSV/JSON responses from GDELT**
3. **Handle rate limiting and pagination**
4. **Add error handling and retry logic**

### **GDELT API Endpoints**

- **DOC API**: `https://api.gdeltproject.org/api/v2/doc/doc`
- **Timeline API**: `https://api.gdeltproject.org/api/v2/timeline/timeline`
- **Daily Updates**: `http://data.gdeltproject.org/gdeltv2/lastupdate.txt`

---

## Testing

Run the integration test:

```bash
python tests/test_gdelt_integration.py
```

**Expected Output:**
```
============================================================
GDELT Integration Tests
============================================================

[OK] GDELT adapter instantiation successful
[OK] GDELTEventObservation structure correct
[OK] Relevant event codes defined correctly
[OK] All public fetch methods exist
[OK] Fetch methods return lists correctly
[OK] Relevance calculation works correctly
[OK] GDELT registry entry correct
[OK] GDELT consumption entry correct

============================================================
Test Results: 8 passed, 0 failed
============================================================

[SUCCESS] All tests passed! GDELT integration is ready.
```

---

## Next Steps for Full Implementation

### **1. Implement API Integration**

Edit `data_sources/external/gdelt_events.py`:

```python
def _fetch_events_from_api(self, *, mode, query, actor, location, days):
    import requests
    
    url = f"{self.base_url}/doc/docquery"
    params = {
        "query": query,
        "mode": mode,
        "format": "json",
        "maxrecords": 250,
        "startdatetime": f"NOW-{days}DAYS",
        "enddatetime": "NOW",
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Parse and normalize events
    return [self.normalize_event(event) for event in data]
```

### **2. Add Rate Limiting**

GDELT has rate limits. Implement proper rate limiting:

```python
import time
from datetime import timedelta

class GDELTAdapter:
    def __init__(self):
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
    
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
```

### **3. Add Error Handling**

```python
def fetch_financial_events(self, days=7):
    try:
        self._rate_limit()
        events = self._fetch_events_from_api(mode="doc", query="finance", days=days)
        return events
    except requests.RequestException as e:
        LOG.error(f"GDELT API request failed: {e}")
        return []
    except Exception as e:
        LOG.error(f"Unexpected error: {e}")
        return []
```

### **4. Add Caching**

Cache GDELT responses to reduce API calls:

```python
from functools import lru_cache
import hashlib

class GDELTAdapter:
    @lru_cache(maxsize=100)
    def _fetch_cached(self, cache_key):
        return self._fetch_events_from_api(...)
    
    def _make_cache_key(self, mode, query, actor, location, days):
        return hashlib.md5(f"{mode}{query}{actor}{location}{days}".encode()).hexdigest()
```

---

## Configuration Options

### **Enable/Disable GDELT**

Edit `registry/data_source_registry.yaml`:

```yaml
- id: SRC-GEO-GDELT-001
  enabled: true  # Change to false to disable
```

### **Adjust Relevance Threshold**

Modify the `_calculate_relevance()` method in `gdelt_events.py`:

```python
def _calculate_relevance(self, event_code, tone):
    # Adjust thresholds based on your needs
    base_relevance = 0.3  # Lower base threshold
    # ... rest of logic
```

---

## Benefits for Trading

### **Geopolitical Risk Assessment**
- Monitor conflicts, sanctions, and diplomatic events
- Early warning for market-impacting geopolitical developments
- Track actor relationships and tensions

### **Economic Intelligence**
- Central bank statements and policy changes
- Trade agreements and economic partnerships
- Regulatory actions and legal developments

### **Sentiment Analysis**
- Tone analysis across thousands of news sources
- Real-time sentiment shifts in global coverage
- Cross-lingual sentiment aggregation

### **Event Correlation**
- Correlate GDELT events with price movements
- Identify causal relationships between events and markets
- Build predictive models based on historical event data

---

## Resources

- **GDELT Project**: https://www.gdeltproject.org/
- **GDELT API Documentation**: https://api.gdeltproject.org/api/v2/doc/doc
- **GDELT Codebook**: https://www.gdeltproject.org/data/lookups/CSV-CAMEO.codebook.txt
- **GDELT Daily Updates**: http://data.gdeltproject.org/gdeltv2/lastupdate.txt

---

## Summary

✅ **GDELT has been successfully integrated** into DIX VISION with:
- Adapter interface following system patterns
- Registry and consumption configuration
- Test suite passing all checks
- Relevance scoring for trading relevance
- Support for multiple query types (financial, geopolitical, actor, location)

⚠️ **API integration is in placeholder status** - actual HTTP requests to GDELT need to be implemented for production use.

🎯 **Ready for:** Development, testing, and integration with INDIRA's cognitive pipeline once API calls are implemented.
