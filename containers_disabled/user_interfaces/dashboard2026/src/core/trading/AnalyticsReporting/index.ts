/**
 * Performance Analytics and Reporting - Phase 14 Index
 * DIX VISION v42.2 - Phase 14: Performance Analytics and Reporting (Weeks 45-48)
 */

export { performanceAnalyticsEngine } from '../PerformanceAnalytics';
export type {
  PerformanceAnalytics,
  TimePeriod,
  PerformanceMetrics,
  ReturnMetrics,
  RollingReturns,
  BenchmarkComparison,
  RiskMetrics,
  EfficiencyMetrics,
  ConsistencyMetrics,
  TradeMetrics,
  PerformanceAttribution,
  FactorAttribution,
  SectorAttribution,
  SectorPerformance,
  TimingAttribution,
  SelectionAttribution,
  PerformanceRiskAnalysis,
  ConcentrationRisk,
  TopPosition,
  LiquidityRisk,
  LeverageRisk,
  CorrelationRisk,
  TailRisk,
  ExtremeLoss,
  PerformanceComparison,
  PeerComparison,
  PeriodComparison,
  PerformanceInsight
} from '../PerformanceAnalytics';

export { reportSystem } from '../ReportSystem';
export type {
  ReportSystem,
  Report,
  ReportType,
  ReportContent,
  ReportSection,
  Subsection,
  Chart,
  ChartData,
  Dataset,
  ChartConfig,
  Annotation,
  Table,
  TableColumn,
  TableRow,
  ReportSummary,
  Appendix,
  ReportMetadata,
  ReportTemplate,
  TemplateSection,
  ReportConfig,
  TableConfig,
  ReportSchedule,
  ReportScheduleItem,
  DeliveryMethod,
  DeliveryConfig,
  AuthConfig
} from '../ReportSystem';

export { realTimePerformanceDashboard } from '../RealTimeDashboard';
export type {
  PerformanceDashboard,
  DashboardLayout,
  Widget,
  WidgetType,
  WidgetPosition,
  WidgetSize,
  WidgetConfig,
  Threshold,
  DashboardFilters,
  TimeRange,
  RealTimeMetrics,
  DashboardAlert
} from '../RealTimeDashboard';

export { automatedReportGenerator } from '../AutomatedReportGenerator';
export type {
  AutomatedReportGenerator,
  GeneratorConfig,
  ReportJob,
  ReportJobType,
  JobStatus,
  ReportJobConfig,
  DataSource,
  ScheduleConfig,
  ReportOutput,
  OutputMetadata,
  GeneratorStatus,
  GeneratorStats
} from '../AutomatedReportGenerator';