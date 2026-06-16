/**
 * Asset Class-Specific Enhancements - Phase 17 Index
 * DIX VISION v42.2 - Phase 17: Asset Class-Specific Enhancements (Weeks 55-62)
 */

export { stockTradingEnhancements } from './stocks/StockTradingEnhancements';
export type {
  EarningsEvent,
  EarningsCalendar,
  InstitutionalOwnership,
  Institution,
  SectorOwnership,
  InsiderTradingAlert,
  InsiderProfile,
  InsiderPerformance,
  TradingPattern,
  SectorAnalysis,
  SectorPerformance,
  SectorComposition,
  SectorCompany,
  MarketCapRange,
  StyleDistribution,
  GeographyDistribution,
  SectorTrend,
  SectorCatalyst,
  SectorValuation,
  OptionsFlow as StockOptionsFlow,
  UnusualActivity,
  LargeOptionTrade,
  ETFTracking,
  CreationRedemptionActivity,
  ETFHolding,
  ETFPerformance,
  ArbitrageOpportunity,
  ExtendedHours,
  ExtendedHoursSession,
  VolumeProfile,
  VolumeLevel,
  PriceMovement,
  CircuitBreaker,
  CircuitBreakerInfo
} from './stocks/StockTradingEnhancements';

export { forexTradingEnhancements } from './forex/ForexTradingEnhancements';
export type {
  CentralBankPolicy,
  CurrencyImpact,
  EconomicEvent,
  HistoricalEventData,
  CurrencyCorrelationMatrix,
  CorrelationData,
  CorrelationPair,
  HeatMapData,
  HeatMapCell,
  CurrencyCluster,
  InterestRateDifferential,
  CarryTradeOpportunity,
  SwapPoints,
  ForwardRate,
  YieldCurveDifferential,
  GeopoliticalEvent,
  MarketImpact,
  CarryTradeScanner,
  CarryTradeFilter,
  MultiTimeframeCorrelation,
  TimeframeCorrelation,
  TimeframeDivergence,
  TrendAnalysis,
  KeyLevel,
  SessionOverlap,
  SessionOverlapDetail,
  LiquidityProfile,
  VolatilityProfile,
  TradingOpportunity
} from './forex/ForexTradingEnhancements';

export { futuresTradingEnhancements } from './futures/FuturesTradingEnhancements';
export type {
  COTReport,
  PositionData,
  PositionChanges,
  ConcentrationData,
  COTExtremes,
  ExtremeLevel,
  HistoricalExtremes,
  COTSentiment,
  MarketDepth,
  DepthLevel,
  RollYieldAnalysis as RollYield,
  RollStrategy,
  SeasonalPattern,
  SeasonalDataPoint,
  SeasonalForecast,
  WeatherEvent,
  PriceImpact,
  SimilarEvent,
  MicroContract,
  ContractSpecifications,
  TradingHours as FuturesTradingHours,
  SettlementType,
  DeliverySpecification,
  PositionLimits,
  TradingSchedule,
  MarginOptimization,
  MarginRecommendation,
  StressTest,
  DeliveryCalendar,
  DeliveryContract,
  DeliverySchedule,
  DeliveryNotification
} from './futures/FuturesTradingEnhancements';

export { optionsTradingEnhancements } from './options/OptionsTradingEnhancements';
export type {
  VolatilitySurface,
  VolatilityPoint,
  SurfaceQuality,
  VolatilityAnomaly,
  GreeksAnalysis,
  PortfolioPosition,
  Greeks,
  OptionsRiskMetrics,
  ScenarioAnalysis,
  HedgeRecommendation,
  OptionsFlow as OptionsOptionsFlow,
  UnusualActivity as OptionsUnusualActivity,
  InstitutionalFlow,
  RetailFlow,
  OptionsSentiment,
  FlowMomentum,
  IVRankPercentile,
  HistoricalIVPoint,
  IVPrediction,
  StrategyBuilder,
  OptionStrategyType,
  StrategyLeg,
  StrategyParameters,
  PayoffProfile,
  PayoffPoint,
  RiskRewardProfile,
  StrategyProbability,
  MarketCondition,
  EventDrivenStrategy,
  ExpectedMove,
  EventStrategy,
  HistoricalEventPerformance,
  EventRiskAssessment,
  MultiLegExecution,
  ExecutionOrder,
  ExecutionTiming,
  LegExecutionStatus,
  ExpirationCalendar,
  Expiration,
  NotableDate,
  VolumeProfile as OptionsVolumeProfile,
  VolumeByStrike,
  NotificationSchedule,
  ExpirationNotification
} from './options/OptionsTradingEnhancements';

// Module Instances
export const stockTradingSystem = stockTradingEnhancements;
export const forexTradingSystem = forexTradingEnhancements;
export const futuresTradingSystem = futuresTradingEnhancements;
export const optionsTradingSystem = optionsTradingEnhancements;

// Initialize all asset class systems
export function initializeAssetClassIndex(): void {
  // Asset class systems are initialized via their individual initialize methods
  // which are called when the systems are first instantiated
  console.log('📈 Asset Class Trading Systems Ready');
}

// Module Information
export const AssetClassModuleInfo = {
  name: 'Asset Class-Specific Enhancements',
  version: '1.0.0',
  description: 'Comprehensive enhancements for stocks, forex, futures, and options trading',
  components: [
    'Stock Trading Enhancements',
    'Forex Trading Enhancements',
    'Futures Trading Enhancements',
    'Options Trading Enhancements'
  ],
  features: [
    'Earnings tracking and analysis',
    'Institutional ownership tracking',
    'Insider trading alerts',
    'Sector analysis and trends',
    'Options flow analysis',
    'Extended hours trading',
    'Volume profile analysis',
    'COT report analysis',
    'Roll yield analysis',
    'Seasonal pattern analysis',
    'Volatility surface construction',
    'Greeks analysis',
    'Options flow analysis',
    'Strategy building tools',
    'Multi-leg execution'
  ],
  assetClasses: [
    'Stocks',
    'Forex',
    'Futures',
    'Options'
  ],
  integrationPoints: [
    'Portfolio Management',
    'Trading Execution',
    'Risk Management',
    'Market Data',
    'Order Management'
  ]
};