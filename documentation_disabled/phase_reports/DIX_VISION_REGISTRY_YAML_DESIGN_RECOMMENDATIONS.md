# DIX VISION Registry YAML Files - Design Recommendations

**Date:** June 21, 2026
**System:** DIX VISION v42.2
**Purpose:** Registry YAML file structure recommendations
**Architecture:** Signal-First (85/15), Zero-Loss Unification, Tier-0 Contract Compliance

---

## 🎯 EXECUTIVE SUMMARY

Based on the current DIX VISION system architecture with signal-first architecture, multi-domain trading, INDIRA 30X cognitive enhancement, and comprehensive enhancement systems, here are recommendations for registry YAML file structure and content.

**Key Principle:** Registry files should store **configuration, metadata, and relationships** while **implementation logic** remains in Python code. Registry files enable operator control without code changes, supporting the dashboard control system and trading form optimization from Phase 1.

---

## 🎯 RECOMMENDED REGISTRY STRUCTURE

### **Primary Registry Directory:**
```
containers/trading/registry/
├── signal_first_registry.yaml           # Signal-First Architecture Configuration
├── trading_form_registry.yaml          # Trading Form Optimization Ratios
├── strategy_registry.yaml              # Trading Strategy Metadata
├── trader_archetypes.yaml             # Trader Behavioral Profiles
├── domain_registry.yaml                # Multi-Domain Configurations
├── enhancement_system_registry.yaml     # Enhancement System Configurations
├── cognitive_system_registry.yaml      # Cognitive System Configurations
└── risk_management_registry.yaml       # Risk Parameters and Limits
```

---

## 🎯 REGISTRY FILE 1: signal_first_registry.yaml

**Purpose:** Signal-first architecture configuration (85/15 baseline)

**Content:**
```yaml
signal_first_config:
  baseline_ratio:
    signal: 0.85  # 85% signal processing
    world: 0.15    # 15% world context
  
  dashboard_control:
    enabled: true
    slider_range:
      min: 0.50
      max: 0.95
      default: 0.85
    allow_manual_override: true
  
  auto_adjustment:
    enabled: true
    by_regime: true
    by_trading_form: true
  
  governance:
    require_approval: true
    audit_trail: true
```

**Rationale:** Central signal-first configuration for the entire system, enabling dashboard control from Phase 1.

---

## 🎯 REGISTRY FILE 2: trading_form_registry.yaml

**Purpose:** Trading form optimization ratios and configurations

**Content:**
```yaml
trading_forms:
  discretionary_hybrid:
    category: discretionary_hybrid
    domain: crypto
    timeframe: swing
    execution_mode: semi_auto
    optimal_ratio:
      signal: 0.85
      world: 0.15
    allowed_range:
      signal: [0.70, 0.95]
      world: [0.05, 0.30]
  
  liquidity_focused:
    category: liquidity_focused
    domain: crypto
    timeframe: intraday
    execution_mode: auto
    optimal_ratio:
      signal: 0.80
      world: 0.20
    allowed_range:
      signal: [0.65, 0.90]
      world: [0.10, 0.35]
  
  # ... additional trading forms
```

**Rationale:** Enables Phase 1 trading form optimization with form-specific optimal ratios.

---

## 🎯 REGISTRY FILE 3: strategy_registry.yaml

**Purpose:** Trading strategy metadata and configurations

**Content:**
```yaml
strategies:
  discretionary_hybrid:
    name: Discretionary Hybrid
    category: discretionary_hybrid
    domain: crypto
    timeframe: swing
    execution_mode: semi_auto
    performance:
      win_rate: 0.65
      sharpe_ratio: 1.8
      max_drawdown: 0.15
    operational_requirements:
      latency_ms: 100
      data_sources: [orderbook, trades, social]
    signal_first_compatibility: true
    optimal_signal_ratio: 0.85
  
  liquidity_focused:
    name: Liquidity Focused
    category: liquidity_focused
    domain: crypto
    timeframe: intraday
    execution_mode: auto
    performance:
      win_rate: 0.70
      sharpe_ratio: 2.1
      max_drawdown: 0.12
    operational_requirements:
      latency_ms: 50
      data_sources: [orderbook, trades]
    signal_first_compatibility: true
    optimal_signal_ratio: 0.80
  
  # ... additional strategies
```

**Rationale:** Strategy metadata for dashboard selection and trading form optimization.

---

## 🎯 REGISTRY FILE 4: trader_archetypes.yaml

**Purpose:** Trader behavioral profiles and preferences

**Content:**
```yaml
trader_archetypes:
  scalper:
    name: Scalper
    category: volatility_options
    domain: crypto
    timeframe: scalping
    execution_mode: auto
    risk_profile: aggressive
    signal_first_preference: 0.90  # High signal, low world
    max_positions: 10
    position_duration_minutes: [1, 60]
    preferred_strategies: [scalping_momentum, volatility_exploitation]
  
  swing_trader:
    name: Swing Trader
    category: trend_momentum
    domain: crypto
    timeframe: swing
    execution_mode: semi_auto
    risk_profile: moderate
    signal_first_preference: 0.85  # Standard baseline
    max_positions: 5
    position_duration_days: [1, 7]
    preferred_strategies: [trend_following, mean_reversion]
  
  # ... additional archetypes
```

**Rationale:** Trader behavioral profiles for strategy selection and signal-first preference customization.

---

## 🎯 REGISTRY FILE 5: domain_registry.yaml

**Purpose:** Multi-domain trading configurations

**Content:**
```yaml
domains:
  crypto:
    name: Cryptocurrency
    enabled: true
    exchanges: [binance, coinbase, kraken]
    assets: [BTC, ETH, SOL, ADA]
    base_currency: USD
    fee_rate: 0.001
    latency_requirements_ms: 50
    signal_first_compatibility: true
    domain_specific_ratios:
      signal: 0.85
      world: 0.15
  
  forex:
    name: Foreign Exchange
    enabled: true
    exchanges: [oanda, ig]
    assets: [EURUSD, GBPUSD, USDJPY]
    base_currency: USD
    fee_rate: 0.0002
    latency_requirements_ms: 20
    signal_first_compatibility: true
    domain_specific_ratios:
      signal: 0.80
      world: 0.20
  
  stocks:
    name: Stocks
    enabled: false  # Can be enabled later
    exchanges: [ibkr, alpaca]
    assets: [AAPL, GOOGL, MSFT]
    base_currency: USD
    fee_rate: 0.0005
    latency_requirements_ms: 100
    signal_first_compatibility: true
    domain_specific_ratios:
      signal: 0.75
      world: 0.25
  
  # ... additional domains
```

**Rationale:** Multi-domain support from existing trading/multi_domain/ with signal-first compatibility.

---

## 🎯 REGISTRY FILE 6: enhancement_system_registry.yaml

**Purpose:** Enhancement system configurations (10/10 trading enhancement)

**Content:**
```yaml
enhancement_systems:
  ai_meta_controllers:
    name: AI Meta Controllers
    enabled: true
    controller_types: [risk_meta, regime_meta, resource_meta]
    signal_first_integration: true
    world_context_integration: true
  
  regime_classification:
    name: Regime Classification
    enabled: true
    regime_types: [trending, ranging, volatile, quiet]
    signal_first_integration: true
    world_context_integration: true
  
  crisis_trading:
    name: Crisis Trading
    enabled: true
    crisis_types: [flash_crash, liquidity_crisis, extreme_volatility]
    signal_first_integration: true
    auto_ratio_adjustment: true
  
  # ... additional enhancement systems
```

**Rationale:** Enhancement system configurations from advanced_trading_enhancement_system.yaml with signal-first integration.

---

## 🎯 REGISTRY FILE 7: cognitive_system_registry.yaml

**Purpose:** Cognitive system configurations (INDIRA 30X + enhancements)

**Content:**
```yaml
cognitive_systems:
  indira_cognitive:
    name: INDIRA Cognitive
    domain: MARKET_DOMAIN
    enhancement_level: 30X
    brain_subsystems: 17
    signal_first_integration: true
    dashboard_control_enabled: true
    trading_form_optimization_enabled: true
  
  dyon_cognitive:
    name: DYON Cognitive
    domain: SYSTEM_DOMAIN
    enhancement_level: Phase1
    signal_first_integration: true
    dashboard_control_enabled: true
    trading_form_optimization_enabled: false  # System-level configuration
  
  intelligence_engine_cognitive:
    name: Intelligence Engine Cognitive
    domain: RUNTIME_COGNITIVE_DOMAIN
    signal_first_integration: true
    dashboard_control_enabled: true
    trading_form_optimization_enabled: true
  
  # ... additional cognitive systems
```

**Rationale:** Cognitive system configurations with signal-first integration status.

---

## 🎯 REGISTRY FILE 8: risk_management_registry.yaml

**Purpose:** Risk parameters and limits

**Content:**
```yaml
risk_management:
  position_limits:
    max_total_exposure: 0.10  # 10% of portfolio
    max_single_position: 0.02  # 2% per position
    max_positions: 10
  
  stop_loss:
    enabled: true
    default_percentage: 0.02  # 2%
    max_percentage: 0.05  # 5%
  
  leverage:
    enabled: true
    max_leverage: 3.0
    default_leverage: 1.0
  
  drawdown_limits:
    daily_max: 0.03  # 3%
    weekly_max: 0.05  # 5%
    monthly_max: 0.10  # 10%
  
  signal_first_risk_adjustment:
    enabled: true
    high_signal_ratio_risk_reduction: true  # Reduce risk when signal ratio is high
```

**Rationale:** Risk management parameters with signal-first risk adjustment integration.

---

## 🎯 ADDITIONAL OPTIONAL REGISTRY FILES

### **9. data_source_registry.yaml**
- Data source configurations (exchanges, APIs, data providers)
- Data quality requirements
- Update frequencies

### **10. execution_registry.yaml**
- Execution parameters
- Order routing configurations
- Slippage tolerance

### **11. learning_system_registry.yaml**
- Learning system configurations
- Model hyperparameters
- Training schedules

### **12. governance_registry.yaml**
- Governance configurations
- Approval workflows
- Audit trail settings

---

## 🎯 REGISTRY FILE PRINCIPLES

### **1. Configuration vs Implementation**
- ✅ Store configurations in YAML
- ❌ Store implementation logic in Python
- ✅ YAML enables operator control without code changes

### **2. Signal-First Integration**
- ✅ Include signal-first compatibility flags
- ✅ Include optimal signal ratios
- ✅ Include dashboard control settings
- ✅ Enable trading form optimization

### **3. Zero-Loss Guarantee**
- ✅ Backward compatibility with existing configurations
- ✅ Migration scripts with validation
- ✅ Backup before any changes
- ✅ Rollback capability

### **4. Domain Separation**
- ✅ Separate registry files per domain
- ✅ Clear domain boundaries
- ✅ No cross-domain dependencies in single files

### **5. Operator Sovereignty**
- ✅ All configurations operator-controllable
- ✅ Dashboard control integration
- ✅ Manual override capability
- ✅ Audit trail for all changes

---

## 🎯 MIGRATION STRATEGY

### **Current Registry Files:**
- ✅ `strategy_registry.yaml` (44,174 bytes) - Keep, enhance with signal-first
- ✅ `advanced_trading_enhancement_system.yaml` (25,645 bytes) - Keep, integrate with enhancement_system_registry.yaml

### **Missing Registry Files to Create:**
- `signal_first_registry.yaml` - NEW (Phase 1 integration)
- `trading_form_registry.yaml` - NEW (Phase 1 integration)
- `trader_archetypes.yaml` - NEW (if not already created)
- `domain_registry.yaml` - NEW (from existing multi_domain/)
- `cognitive_system_registry.yaml` - NEW (from cognitive enhancement)
- `risk_management_registry.yaml` - NEW

### **Migration Steps:**
1. Analyze existing YAML files
2. Create unified schema preserving all data
3. Add signal-first integration fields
4. Add dashboard control fields
5. Validate data integrity
6. Create backup before merge
7. Migrate with validation scripts
8. Test with TradingSystemEnhancer

---

## 🎯 VALIDATION REQUIREMENTS

### **Registry Validation:**
- ✅ YAML syntax validation
- ✅ Schema validation (type checking)
- ✅ Signal-first ratio validation (must be 0.5-0.95)
- ✅ Domain separation validation
- ✅ Backward compatibility validation
- ✅ Cross-reference validation (strategies → forms → domains)

### **Integration Validation:**
- ✅ TradingSystemEnhancer can read registry
- ✅ Dashboard control can update registry
- ✅ Signal-first engine can use registry ratios
- ✅ Zero-loss guarantee verified

---

## 🎯 SUMMARY

**Recommended Registry Structure:** 8 primary registry files + 4 optional files
**Key Features:** Signal-first integration, dashboard control, trading form optimization
**Zero-Loss Guarantee:** Migration with validation, backup, and rollback
**Operator Sovereignty:** All configurations operator-controllable via dashboard
**Contract Compliance:** Tier-0 production implementation

**Next Steps:**
1. Create signal_first_registry.yaml (NEW)
2. Create trading_form_registry.yaml (NEW)
3. Enhance existing strategy_registry.yaml with signal-first fields
4. Create domain_registry.yaml from existing multi_domain/ code
5. Create cognitive_system_registry.yaml from cognitive enhancement
6. Implement migration and validation scripts
7. Test with TradingSystemEnhancer integration

---

**Recommendation Status:** ✅ Ready for implementation with Phase 1 signal-first architecture integration