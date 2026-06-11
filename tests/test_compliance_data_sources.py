"""Compliance Integration Test for Data Sources

Tests the compliance system integration with:
- Source manager (compliance-aware source access)
- Cache layer (compliance-weighted TTL)
- Source priority adjustment based on compliance
"""

import unittest
from unittest.mock import Mock, patch
from system.source_manager import SourceManager
from system.cache_layer import DataCache, CachePolicy


class TestComplianceSourceManager(unittest.TestCase):
    """Test compliance integration with source manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.source_manager = SourceManager()
    
    def test_get_compliance_weight(self):
        """Test fetching compliance weight."""
        # Mock successful API response
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": 0.8}
            mock_get.return_value = mock_response
            
            weight = self.source_manager.get_compliance_weight()
            self.assertEqual(weight, 0.8)
    
    def test_get_compliance_weight_api_failure(self):
        """Test compliance weight fallback on API failure."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("API failure")
            
            weight = self.source_manager.get_compliance_weight()
            self.assertEqual(weight, 1.0)  # Fallback to 1.0
    
    def test_get_compliance_enabled_sources(self):
        """Test compliance-aware source filtering."""
        # Mock compliance weight
        with patch.object(self.source_manager, 'get_compliance_weight') as mock_weight:
            # Test with low compliance - should filter out premium sources
            mock_weight.return_value = 0.3
            
            indira_sources = self.source_manager.get_compliance_enabled_sources_for_agent("indira")
            
            # Bloomberg should be filtered out at 30% compliance
            self.assertNotIn("SRC-NEWS-BLOOMBERG-001", indira_sources)
            
            # Standard crypto sources should be available
            self.assertIn("SRC-CRYPTO-COINGECKO-001", indira_sources)
    
    def test_compliance_high_value_sources(self):
        """Test high-value source filtering."""
        with patch.object(self.source_manager, 'get_compliance_weight') as mock_weight:
            # Test with medium compliance - should allow high-value but not premium
            mock_weight.return_value = 0.6
            
            indira_sources = self.source_manager.get_compliance_enabled_sources_for_agent("indira")
            
            # TipRanks (high-value) should be available
            self.assertIn("SRC-EARNINGS-TIPRANKS-001", indira_sources)
            
            # Bloomberg (premium) should be filtered out
            self.assertNotIn("SRC-NEWS-BLOOMBERG-001", indira_sources)
    
    def test_compliance_premium_sources(self):
        """Test premium source filtering."""
        with patch.object(self.source_manager, 'get_compliance_weight') as mock_weight:
            # Test with high compliance - should allow all sources
            mock_weight.return_value = 0.9
            
            indira_sources = self.source_manager.get_compliance_enabled_sources_for_agent("indira")
            
            # All sources should be available
            self.assertIn("SRC-NEWS-BLOOMBERG-001", indira_sources)
            self.assertIn("SRC-EARNINGS-TIPRANKS-001", indira_sources)
            self.assertIn("SRC-CRYPTO-COINGECKO-001", indira_sources)
    
    def test_get_source_min_compliance(self):
        """Test minimum compliance level for sources."""
        # Premium sources
        self.assertGreaterEqual(
            self.source_manager._get_source_min_compliance("SRC-NEWS-BLOOMBERG-001"),
            0.7
        )
        
        # High-value sources
        self.assertGreaterEqual(
            self.source_manager._get_source_min_compliance("SRC-EARNINGS-TIPRANKS-001"),
            0.5
        )
        
        # Standard sources
        self.assertEqual(
            self.source_manager._get_source_min_compliance("SRC-CRYPTO-COINGECKO-001"),
            0.0
        )
    
    def test_compliance_weighted_priority(self):
        """Test priority adjustment based on compliance."""
        with patch.object(self.source_manager, 'get_compliance_weight') as mock_weight:
            # Test with low compliance - premium sources penalized
            mock_weight.return_value = 0.3
            
            bloomberg_priority = self.source_manager.get_compliance_weighted_priority(
                "SRC-NEWS-BLOOMBERG-001"
            )
            base_priority = self.source_manager._sources["SRC-NEWS-BLOOMBERG-001"].priority
            
            # Priority should be increased (penalized)
            self.assertGreater(bloomberg_priority, base_priority)
    
    def test_get_sources_sorted_by_priority(self):
        """Test source sorting by compliance-weighted priority."""
        with patch.object(self.source_manager, 'get_compliance_weight') as mock_weight:
            mock_weight.return_value = 0.8
            
            sorted_sources = self.source_manager.get_sources_sorted_by_priority("indira")
            
            # Should return a list
            self.assertIsInstance(sorted_sources, list)
            
            # Should contain some sources
            self.assertGreater(len(sorted_sources), 0)
    
    def test_get_compliance_summary(self):
        """Test compliance summary generation."""
        with patch.object(self.source_manager, 'get_compliance_weight') as mock_weight:
            mock_weight.return_value = 0.7
            
            summary = self.source_manager.get_compliance_summary("indira")
            
            # Should contain required fields
            self.assertIn("compliance_weight", summary)
            self.assertIn("compliance_tier", summary)
            self.assertIn("total_enabled_sources", summary)
            self.assertIn("compliance_filtered_sources", summary)
            
            # Compliance weight should match
            self.assertEqual(summary["compliance_weight"], 0.7)
            
            # Tier should be HIGH
            self.assertEqual(summary["compliance_tier"], "HIGH")


class TestComplianceCacheLayer(unittest.TestCase):
    """Test compliance integration with cache layer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = DataCache(max_size=100)
    
    def test_get_compliance_weighted_ttl(self):
        """Test TTL adjustment based on compliance."""
        with patch('requests.get') as mock_get:
            # High compliance - longer TTL
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": 0.9}
            mock_get.return_value = mock_response
            
            ttl = self.cache.get_compliance_weighted_ttl("coingecko", "crypto")
            base_ttl = CachePolicy.CRYPTO_PRICE_TTL
            
            # TTL should be increased
            self.assertGreater(ttl, base_ttl)
    
    def test_low_compliance_ttl(self):
        """Test TTL reduction at low compliance."""
        with patch('requests.get') as mock_get:
            # Low compliance - shorter TTL
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": 0.2}
            mock_get.return_value = mock_response
            
            ttl = self.cache.get_compliance_weighted_ttl("coingecko", "crypto")
            base_ttl = CachePolicy.CRYPTO_PRICE_TTL
            
            # TTL should be decreased
            self.assertLess(ttl, base_ttl)
    
    def test_get_base_ttl_for_category(self):
        """Test base TTL mapping for categories."""
        crypto_ttl = self.cache._get_base_ttl_for_category("crypto")
        self.assertEqual(crypto_ttl, CachePolicy.CRYPTO_PRICE_TTL)
        
        news_ttl = self.cache._get_base_ttl_for_category("news")
        self.assertEqual(news_ttl, CachePolicy.NEWS_TTL)
        
        default_ttl = self.cache._get_base_ttl_for_category("unknown")
        self.assertEqual(default_ttl, 60)  # Default
    
    def test_compliance_cache_summary(self):
        """Test cache summary with compliance context."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": 0.6}
            mock_get.return_value = mock_response
            
            summary = self.cache.get_compliance_cache_summary()
            
            # Should contain required fields
            self.assertIn("compliance_weight", summary)
            self.assertIn("compliance_tier", summary)
            self.assertIn("cache_size", summary)
            self.assertIn("hit_rate", summary)
            
            # Compliance weight should match
            self.assertEqual(summary["compliance_weight"], 0.6)


if __name__ == "__main__":
    unittest.main()