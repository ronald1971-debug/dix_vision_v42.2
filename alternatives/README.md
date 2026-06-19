# Alternatives Directory - Alternative Implementations

## ⚠️ IMPORTANT WARNING

**The intelligence engine plugin alternatives in this directory are LEGACY NON-COMPLIANT VERSIONS.**

These files do **NOT** inherit from `MicrostructurePlugin` and are **NOT contract-compliant**. They should **NOT** be used in production or copied to the main system.

## Purpose

This directory contains alternative implementations of various system components. These include:

1. **Legacy implementations** that were replaced with contract-compliant versions
2. **Alternative approaches** to specific problems
3. **Different deployment configurations** for various cloud platforms
4. **Experimental implementations** for research and testing
5. **Backup implementations** for fallback scenarios

## Directory Structure

### `intelligence_engine/plugins/` ⚠️ CRITICAL WARNING
**STATUS: LEGACY NON-COMPLIANT - DO NOT USE**

These are the **original plugin implementations** that were replaced with contract-compliant versions in the main system. They do **NOT** inherit from `MicrostructurePlugin` and will **FAIL** contract compliance checks.

**Files that MUST NOT be used:**
- `microstructure/microstructure_v1.py` - Legacy version
- `orderflow_imbalance/v1.py` - Legacy version  
- `order_book_pressure/v1.py` - Legacy version
- `vpin_imbalance/v1.py` - Legacy version
- `regime_classifier/v1.py` - Legacy version
- `footprint_delta/v1.py` - Legacy version
- `liquidity_physics/v1.py` - Legacy version
- `on_chain_pulse/v1.py` - Legacy version
- `news_reaction/v1.py` - Legacy version
- `sentiment_aggregator/v1.py` - Legacy version
- `trader_imitation/v1.py` - Legacy version
- `microstructure_advanced.py` - Legacy version

**Current Status:** The main system (`intelligence_engine/plugins/`) contains the **contract-compliant versions** of these plugins.

### `alt_data_engine/`
**STATUS: Alternative data processing implementations**

Contains alternative implementations for data processing:
- `macro_feed.py` - Alternative macro economic data feed
- `news_parser.py` - Alternative news parsing engine  
- `orchestrator.py` - Alternative data orchestration
- `sentiment.py` - Alternative sentiment analysis

### `apps/`
**STATUS: Alternative frontend applications**

Contains alternative frontend implementations:
- `agent-runtime/` - Alternative agent runtime application
- `dashboard/` - Alternative dashboard implementation
- `desktop/` - Alternative desktop application

### `cloud/`
**STATUS: Alternative deployment configurations**

Contains deployment configurations for various platforms:
- `Caddyfile` - Caddy web server configuration
- `fly.toml` - Fly.io deployment configuration
- `k8s/deployment.yaml` - Kubernetes deployment
- `railway.json` - Railway deployment configuration
- `render.yaml` - Render deployment configuration
- `systemd/dix-vision.service` - Systemd service configuration

### `cognitive_control_center/`
**STATUS: Alternative cognitive control implementation**

Contains alternative implementations for cognitive control:
- Agent operations center
- Core lifecycle management
- Shared services (auth, chat, LLM, pairing, QR)
- Shared tools and domain-specific implementations
- Test files

### `cognitive_engine/`
**STATUS: Alternative cognitive engine implementations**

Contains alternative implementations for cognitive components:
- `attention_engine/` - Alternative attention management
- `cognitive_economy/` - Alternative resource optimization
- `cognitive_health/` - Alternative health monitoring
- `cognitive_simulator/` - Alternative simulation engine
- `collective_intelligence/` - Alternative multi-agent coordination
- `concept_formation/` - Alternative concept learning
- `constitution_v2/` - Alternative constitution implementation
- `contradiction_engine/` - Alternative contradiction resolution
- `curiosity_engine/` - Alternative curiosity-driven learning
- `digital_twin/` - Alternative digital twin modeling
- `discovery_engine/` - Alternative pattern discovery
- `epistemology_engine/` - Alternative knowledge management
- `failing_engine/` - Alternative failure handling
- `failure_engine/` - Alternative failure detection
- `hypothesis_engine/` - Alternative hypothesis management
- `identity_layer/` - Alternative agent identity
- `institutional_memory/` - Alternative long-term memory
- `knowledge_graph/` - Alternative knowledge representation
- `knowledge_preservation/` - Alternative knowledge archiving

## Usage Guidelines

### DO NOT USE (Production)
- `intelligence_engine/plugins/` - Legacy non-compliant plugin implementations
- Any implementation marked as "legacy" or "non-compliant"

### USE WITH CAUTION (Development/Testing)
- `alt_data_engine/` - Alternative data processing implementations
- `apps/` - Alternative frontend applications (testing only)
- `cognitive_control_center/` - Alternative cognitive control (research)
- `cognitive_engine/` - Alternative cognitive implementations (research)

### SAFE TO USE (Deployment Options)
- `cloud/` - Alternative deployment configurations (choose appropriate platform)

## Migration Status

### Migrated to Main System ✅
- All 11 intelligence engine plugins now have contract-compliant versions in `intelligence_engine/plugins/`
- Plugin system infrastructure implemented with contract compliance
- System integration complete and tested

### Not Migrated ⏳
- `microstructure_advanced` - Registry entry exists but no compliant implementation
- Alternative cognitive engine implementations
- Alternative data processing implementations
- Alternative frontend applications

## Contract Compliance

### Contract-Compliant Components ✅
- **Main System:** All 11 plugins in `intelligence_engine/plugins/`
- **Plugin Registry:** `registry/plugins.yaml`
- **Plugin Loader:** `plugin_system/plugin_loader.py`
- **System Integration:** `system_integration.py`

### Non-Compliant Components ⚠️
- **Alternatives:** All 12 plugin files in `alternatives/intelligence_engine/plugins/`
- **Reason:** These are legacy versions that don't inherit from `MicrostructurePlugin`

## Recommendation

For production use, **always use the main system components** in:
- `intelligence_engine/plugins/` (contract-compliant versions)
- `registry/plugins.yaml` (current registry)
- `plugin_system/` (new plugin infrastructure)

The alternatives directory should only be used for:
- Reference and comparison
- Research and development
- Testing new approaches
- Deployment configuration options
- Emergency fallback scenarios

## Status

- **Main System:** ✅ Production Ready - Contract Compliant
- **Plugin Registry:** ✅ All plugins enabled and active  
- **Alternatives:** ⚠️ Documentation needed - Legacy non-compliant versions present
- **Overall:** ✅ Healthy - Main system fully operational

Last Updated: 2026-06-18