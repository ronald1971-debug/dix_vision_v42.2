/**
 * Risk & Compliance Module Index
 * Central exports for risk management, compliance, and governance systems.
 */

// Advanced Risk Management
export {
  AdvancedRiskManagementSystem,
  type RiskMetric,
  type VaRResult,
  type VaRComponent,
  type PortfolioRiskProfile,
  type GreeksExposure,
  type CorrelationMatrix,
  type LiquidityRisk,
  type AssetLiquidity,
  type LiquidityGap,
  type MarketDepth,
  type ConcentrationRisk,
  type SectorConcentration,
  type AssetConcentration,
  type GeographicConcentration,
  type CurrencyConcentration,
  type StressTestScenario,
  type StressTestParameters,
  type StressTestImpact,
  type RealTimeRiskMonitor,
  type RiskAlert,
  type RiskLimit
} from './management/AdvancedRiskManagement';

// Compliance Management
export {
  ComplianceManagementSystem,
  type ComplianceRule,
  type ComplianceViolation,
  type TradeSurveillanceResult,
  type SurveillanceCheck,
  type Anomaly,
  type MarketAbuseDetection,
  type Evidence,
  type PositionLimit,
  type PositionLimitBreach,
  type BestExecutionAnalysis,
  type ExecutionQuality,
  type PriceImprovement,
  type TimingAnalysis,
  type VenueAnalysis,
  type VenueAlternative,
  type RegulatoryReport,
  type ReportData,
  type TradeReport,
  type PositionReport,
  type AccountReport,
  type ReportMetric,
  type AuditTrail,
  type ComplianceConfiguration,
  type ReportingSchedule,
  type ReportSchedule,
  type AlertConfiguration,
  type EscalationRule
} from './compliance/ComplianceManagement';

// Portfolio Governance
export {
  PortfolioGovernanceSystem,
  type GovernancePolicy,
  type PolicyCondition,
  type PolicyAction,
  type PreTradeRiskControl,
  type TradeProposal,
  type RiskAssessment,
  type RiskFactor,
  type PortfolioImpact,
  type PolicyCheckResult,
  type PostTradeAnalytics,
  type ExecutionAnalysis,
  type PerformanceAnalysis,
  type PerformanceAttribution,
  type ComplianceAnalysis,
  type RiskImpactAnalysis,
  type GovernanceAnalysis,
  type AuthorizationWorkflow,
  type WorkflowTrigger,
  type ApprovalLevel,
  type ApprovalRequest,
  type PositionLimitEnforcement,
  type LimitEnforcement,
  type BlockedAction,
  type LimitWarning,
  type MultiLevelApprovalSystem,
  type ApprovalSystemConfiguration,
  type ApprovalMatrix,
  type ApprovalCriteria,
  type TimeoutSettings,
  type NotificationSettings,
  type EscalationSettings,
  type ApprovalHistory,
  type PolicyEnforcement,
  type EnforcementResult,
  type EnforcedAction,
  type GovernanceAudit,
  type AuditScope,
  type AuditFinding
} from './governance/PortfolioGovernance';

// Module Instances
export const advancedRiskManagement = new AdvancedRiskManagementSystem();
export const complianceManagement = new ComplianceManagementSystem();
export const portfolioGovernance = new PortfolioGovernanceSystem();

// Initialize all systems
export function initializeRiskCompliance(): void {
  advancedRiskManagement.initialize();
  complianceManagement.initialize();
  portfolioGovernance.initialize();
}

// Module Information
export const RiskComplianceModuleInfo = {
  name: 'Risk & Compliance Module',
  version: '1.0.0',
  description: 'Comprehensive risk management, compliance, and governance systems for institutional trading',
  components: [
    'Advanced Risk Management',
    'Compliance Management',
    'Portfolio Governance'
  ],
  features: [
    'Multi-asset risk analytics',
    'Real-time risk monitoring',
    'VaR and CVaR calculations',
    'Stress testing',
    'Trade surveillance',
    'Market abuse detection',
    'Position limit monitoring',
    'Best execution analysis',
    'Regulatory reporting',
    'Pre-trade controls',
    'Post-trade analytics',
    'Authorization workflows',
    'Policy enforcement'
  ],
  integrationPoints: [
    'Portfolio Management',
    'Trading Execution',
    'Order Management',
    'Risk Monitoring',
    'Compliance Reporting'
  ]
};