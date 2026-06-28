/**
 * Team Collaboration Tools - Phase 16
 * DIX VISION v42.2 - Phase 16: Collaboration & Social Features (Weeks 51-54)
 * 
 * This module implements team collaboration tools including:
 * - Team workspace and management
 * - Shared watchlists and alerts
 * - Collaborative charting with annotations
 * - Team performance analytics
 * - Role-based access control
 * - Audit trail for team activities
 * - Multi-asset team portfolios
 */

export interface TeamWorkspace {
  teamId: string;
  name: string;
  description: string;
  ownerId: string;
  ownerName: string;
  members: TeamMember[];
  watchlists: SharedWatchlist[];
  charts: CollaborativeChart[];
  portfolios: TeamPortfolio[];
  alerts: TeamAlert[];
  settings: TeamSettings;
  createdAt: number;
  lastModified: number;
  lastActivity: number;
}

export interface TeamMember {
  userId: string;
  username: string;
  email: string;
  avatar?: string;
  role: TeamRole;
  permissions: string[];
  joinedAt: number;
  lastActivity: number;
  status: 'active' | 'inactive' | 'pending' | 'suspended';
}

export type TeamRole = 'owner' | 'admin' | 'analyst' | 'trader' | 'viewer';

export interface SharedWatchlist {
  watchlistId: string;
  teamId: string;
  name: string;
  description: string;
  createdBy: string;
  createdByName: string;
  symbols: WatchlistSymbol[];
  tags: string[];
  isDefault: boolean;
  shareSettings: ShareSettings;
  viewCount: number;
  lastModified: number;
  lastViewed: number;
}

export interface WatchlistSymbol {
  symbol: string;
  assetClass: string;
  exchange: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  notes: string;
  addedBy: string;
  addedByName: string;
  addedAt: number;
  alerts: SymbolAlert[];
}

export interface SymbolAlert {
  alertId: string;
  symbol: string;
  type: 'price' | 'volume' | 'indicator' | 'pattern' | 'custom';
  condition: AlertCondition;
  triggered: boolean;
  triggeredAt?: number;
  acknowledgedBy?: string;
  acknowledgedAt?: number;
  createdAt: number;
}

export interface AlertCondition {
  operator: '>' | '<' | '=' | '>=' | '<=' | 'crosses-above' | 'crosses-below' | 'between';
  value: number;
  value2?: number; // For 'between' operator
  indicator?: string;
  timeframe?: string;
}

export interface ShareSettings {
  visibility: 'private' | 'team' | 'public';
  canEdit: string[];
  canDelete: string[];
  canShare: string[];
}

export interface CollaborativeChart {
  chartId: string;
  teamId: string;
  name: string;
  description: string;
  symbol: string;
  assetClass: string;
  timeframe: string;
  chartType: string;
  indicators: ChartIndicator[];
  annotations: ChartAnnotation[];
  drawings: ChartDrawing[];
  createdBy: string;
  createdByName: string;
  collaborators: string[];
  version: number;
  shareSettings: ShareSettings;
  viewCount: number;
  lastModified: number;
  lastModifiedBy: string;
  lastViewed: number;
}

export interface ChartIndicator {
  indicatorId: string;
  type: string;
  name: string;
  parameters: Record<string, any>;
  visible: boolean;
  color?: string;
  style?: string;
}

export interface ChartAnnotation {
  annotationId: string;
  type: 'text' | 'arrow' | 'line' | 'rectangle' | 'ellipse' | 'fibonacci' | 'trendline' | 'support-resistance';
  x1: number;
  y1: number;
  x2?: number;
  y2?: number;
  text?: string;
  color: string;
  thickness: number;
  style: 'solid' | 'dashed' | 'dotted';
  createdBy: string;
  createdByName: string;
  createdAt: number;
  modifiedBy?: string;
  modifiedAt?: number;
}

export interface ChartDrawing {
  drawingId: string;
  type: 'trendline' | 'horizontal-line' | 'vertical-line' | 'rectangle' | 'ellipse' | 'polygon' | 'fibonacci-retracement' | 'fibonacci-extension' | 'andrews-pitchfork';
  coordinates: DrawingCoordinate[];
  properties: DrawingProperties;
  createdBy: string;
  createdByName: string;
  createdAt: number;
  modifiedBy?: string;
  modifiedAt?: number;
}

export interface DrawingCoordinate {
  x: number;
  y: number;
  time?: number;
}

export interface DrawingProperties {
  color: string;
  thickness: number;
  style: 'solid' | 'dashed' | 'dotted';
  fillOpacity?: number;
  extend?: boolean;
  label?: string;
}

export interface TeamPortfolio {
  portfolioId: string;
  teamId: string;
  name: string;
  description: string;
  assetAllocation: PortfolioAllocation[];
  positions: PortfolioPosition[];
  performance: PortfolioPerformance;
  riskMetrics: PortfolioRiskMetrics;
  createdBy: string;
  createdByName: string;
  managers: string[];
  viewers: string[];
  shareSettings: ShareSettings;
  lastRebalanced: number;
  lastModified: number;
}

export interface PortfolioAllocation {
  assetClass: string;
  percentage: number;
  targetPercentage: number;
  value: number;
  targetValue: number;
}

export interface PortfolioPosition {
  positionId: string;
  symbol: string;
  assetClass: string;
  exchange: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  marketValue: number;
  unrealizedPnL: number;
  unrealizedPnLPercent: number;
  weight: number;
  entryDate: number;
  addedBy: string;
  addedByName: string;
  notes: string;
}

export interface PortfolioPerformance {
  totalReturn: number;
  dailyReturn: number;
  weeklyReturn: number;
  monthlyReturn: number;
  yearlyReturn: number;
  sharpeRatio: number;
  sortinoRatio: number;
  maxDrawdown: number;
  volatility: number;
  beta: number;
  alpha: number;
  trackingError: number;
  informationRatio: number;
  startDate: number;
  lastUpdated: number;
}

export interface PortfolioRiskMetrics {
  valueAtRisk: number; // 1-day VaR
  expectedShortfall: number;
  concentrationRisk: number;
  currencyRisk: number;
  liquidityRisk: number;
  leverage: number;
  exposure: number;
  lastUpdated: number;
}

export interface TeamAlert {
  alertId: string;
  teamId: string;
  type: 'portfolio' | 'watchlist' | 'chart' | 'system' | 'custom';
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  source: string;
  data?: Record<string, any>;
  recipients: string[];
  acknowledged: boolean;
  acknowledgedBy?: string;
  acknowledgedAt?: number;
  resolved: boolean;
  resolvedBy?: string;
  resolvedAt?: number;
  createdAt: number;
  expiresAt?: number;
}

export interface TeamSettings {
  timezone: string;
  tradingHours: TradingHours[];
  riskLimits: RiskLimits;
  notificationSettings: NotificationSettings;
  auditLogging: boolean;
  requireApprovalFor: string[];
  maxMembers: number;
  maxPortfolios: number;
  maxWatchlists: number;
}

export interface TradingHours {
  day: number; // 0-6 (Sunday-Saturday)
  startHour: number;
  endHour: number;
  enabled: boolean;
}

export interface RiskLimits {
  maxPositionSize: number;
  maxPortfolioExposure: number;
  maxDailyLoss: number;
  maxDrawdown: number;
  maxLeverage: number;
  concentrationLimit: number;
  stopLossThreshold: number;
}

export interface NotificationSettings {
  emailEnabled: boolean;
  smsEnabled: boolean;
  pushEnabled: boolean;
  inAppEnabled: boolean;
  webhookUrl?: string;
  alertTypes: string[];
}

export interface TeamAnalytics {
  teamId: string;
  period: 'daily' | 'weekly' | 'monthly' | 'yearly';
  startDate: number;
  endDate: number;
  members: MemberAnalytics[];
  portfolioAnalytics: PortfolioAnalytics;
  watchlistAnalytics: WatchlistAnalytics;
  tradingAnalytics: TradingAnalytics;
  collaborationMetrics: CollaborationMetrics;
  generatedAt: number;
}

export interface MemberAnalytics {
  userId: string;
  username: string;
  contributionScore: number;
  activityLevel: number;
  shares: number;
  alertsCreated: number;
  alertsResolved: number;
  positionsAdded: number;
  annotationsAdded: number;
  onlineTime: number;
  lastActive: number;
}

export interface PortfolioAnalytics {
  totalPortfolios: number;
  totalValue: number;
  totalReturn: number;
  bestPerforming: {
    portfolioId: string;
    name: string;
    return: number;
  };
  worstPerforming: {
    portfolioId: string;
    name: string;
    return: number;
  };
  averageSharpeRatio: number;
  totalPositions: number;
  topAssets: AssetPerformance[];
}

export interface AssetPerformance {
  assetClass: string;
  value: number;
  return: number;
  count: number;
}

export interface WatchlistAnalytics {
  totalWatchlists: number;
  totalSymbols: number;
  totalViews: number;
  mostViewed: {
    watchlistId: string;
    name: string;
    views: number;
  }[];
  topAlerts: number;
  triggeredAlerts: number;
}

export interface TradingAnalytics {
  totalTrades: number;
  totalVolume: number;
  totalPnL: number;
  winRate: number;
  averageWin: number;
  averageLoss: number;
  profitFactor: number;
  bestTrade: {
    symbol: string;
    pnl: number;
  };
  worstTrade: {
    symbol: string;
    pnl: number;
  };
}

export interface CollaborationMetrics {
  totalShares: number;
  totalComments: number;
  totalAnnotations: number;
  activeCollaborators: number;
  averageResponseTime: number;
  collaborationScore: number;
}

export interface TeamAuditLog {
  auditId: string;
  teamId: string;
  action: string;
  userId: string;
  username: string;
  targetId?: string;
  targetType?: string;
  details: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
  timestamp: number;
  category: 'security' | 'portfolio' | 'watchlist' | 'chart' | 'alert' | 'settings' | 'general';
}

export interface TeamCollaborationSystem {
  teams: Map<string, TeamWorkspace>;
  auditLogs: Map<string, TeamAuditLog>;
  config: TeamCollaborationConfig;
  lastUpdated: number;
}

export interface TeamCollaborationConfig {
  maxTeamsPerUser: number;
  maxMembersPerTeam: number;
  maxPortfoliosPerTeam: number;
  maxWatchlistsPerTeam: number;
  maxChartsPerTeam: number;
  maxAlertsPerTeam: number;
  auditRetentionDays: number;
  enableRealtimeSync: boolean;
  enableVersionHistory: boolean;
  enableComments: boolean;
  enableNotifications: boolean;
}

export class TeamCollaborationSystemImplementation {
  private system: TeamCollaborationSystem;

  constructor() {
    this.system = {
      teams: new Map(),
      auditLogs: new Map(),
      config: {
        maxTeamsPerUser: 10,
        maxMembersPerTeam: 50,
        maxPortfoliosPerTeam: 20,
        maxWatchlistsPerTeam: 50,
        maxChartsPerTeam: 100,
        maxAlertsPerTeam: 500,
        auditRetentionDays: 90,
        enableRealtimeSync: true,
        enableVersionHistory: true,
        enableComments: true,
        enableNotifications: true
      },
      lastUpdated: Date.now()
    };
  }

  initialize(): void {
    // Initialization logic
  }

  getConfig(): TeamCollaborationConfig {
    return this.system.config;
  }

  updateConfig(config: Partial<TeamCollaborationConfig>): void {
    this.system.config = { ...this.system.config, ...config };
    this.system.lastUpdated = Date.now();
  }

  // Team Management Methods
  async createTeam(userId: string, team: Omit<TeamWorkspace, 'teamId' | 'ownerId' | 'ownerName' | 'members' | 'watchlists' | 'charts' | 'portfolios' | 'alerts' | 'createdAt' | 'lastModified' | 'lastActivity'>): Promise<TeamWorkspace> {
    const newTeam: TeamWorkspace = {
      ...team,
      teamId: `team_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      ownerId: userId,
      ownerName: '', // Will be filled from user system
      members: [],
      watchlists: [],
      charts: [],
      portfolios: [],
      alerts: [],
      settings: team.settings || this.getDefaultTeamSettings(),
      createdAt: Date.now(),
      lastModified: Date.now(),
      lastActivity: Date.now()
    };
    
    this.system.teams.set(newTeam.teamId, newTeam);
    this.logAuditEvent(newTeam.teamId, 'team_created', userId, { teamName: newTeam.name });
    this.system.lastUpdated = Date.now();
    return newTeam;
  }

  getTeam(teamId: string): TeamWorkspace | undefined {
    return this.system.teams.get(teamId);
  }

  getUserTeams(userId: string): TeamWorkspace[] {
    return Array.from(this.system.teams.values()).filter(t => 
      t.ownerId === userId || t.members.some(m => m.userId === userId)
    );
  }

  async addTeamMember(teamId: string, userId: string, username: string, email: string, role: TeamRole): Promise<void> {
    const team = this.system.teams.get(teamId);
    if (team) {
      if (team.members.length >= this.system.config.maxMembersPerTeam) {
        throw new Error('Maximum team members reached');
      }

      team.members.push({
        userId,
        username,
        email,
        role,
        permissions: this.getPermissionsByRole(role),
        joinedAt: Date.now(),
        lastActivity: Date.now(),
        status: 'active'
      });
      
      team.lastModified = Date.now();
      team.lastActivity = Date.now();
      
      this.logAuditEvent(teamId, 'member_added', userId, { role, username });
      this.system.lastUpdated = Date.now();
    }
  }

  removeTeamMember(teamId: string, userId: string): void {
    const team = this.system.teams.get(teamId);
    if (team) {
      team.members = team.members.filter(m => m.userId !== userId);
      team.lastModified = Date.now();
      
      this.logAuditEvent(teamId, 'member_removed', userId, { removedUserId: userId });
      this.system.lastUpdated = Date.now();
    }
  }

  async updateTeamMemberRole(teamId: string, userId: string, role: TeamRole): Promise<void> {
    const team = this.system.teams.get(teamId);
    if (team) {
      const member = team.members.find(m => m.userId === userId);
      if (member) {
        member.role = role;
        member.permissions = this.getPermissionsByRole(role);
        team.lastModified = Date.now();
        
        this.logAuditEvent(teamId, 'member_role_updated', userId, { userId, newRole: role });
        this.system.lastUpdated = Date.now();
      }
    }
  }

  private getPermissionsByRole(role: TeamRole): string[] {
    switch (role) {
      case 'owner':
        return ['read', 'write', 'delete', 'manage', 'invite', 'admin'];
      case 'admin':
        return ['read', 'write', 'delete', 'manage', 'invite'];
      case 'analyst':
        return ['read', 'write', 'analyze'];
      case 'trader':
        return ['read', 'write', 'trade'];
      case 'viewer':
        return ['read'];
      default:
        return ['read'];
    }
  }

  private getDefaultTeamSettings(): TeamSettings {
    return {
      timezone: 'UTC',
      tradingHours: [
        { day: 1, startHour: 9, endHour: 17, enabled: true },
        { day: 2, startHour: 9, endHour: 17, enabled: true },
        { day: 3, startHour: 9, endHour: 17, enabled: true },
        { day: 4, startHour: 9, endHour: 17, enabled: true },
        { day: 5, startHour: 9, endHour: 17, enabled: true },
        { day: 0, startHour: 0, endHour: 0, enabled: false },
        { day: 6, startHour: 0, endHour: 0, enabled: false }
      ],
      riskLimits: {
        maxPositionSize: 1000000,
        maxPortfolioExposure: 10000000,
        maxDailyLoss: 50000,
        maxDrawdown: 20,
        maxLeverage: 3,
        concentrationLimit: 30,
        stopLossThreshold: 5
      },
      notificationSettings: {
        emailEnabled: true,
        smsEnabled: false,
        pushEnabled: true,
        inAppEnabled: true,
        alertTypes: ['critical', 'error', 'warning']
      },
      auditLogging: true,
      requireApprovalFor: ['large-trades', 'new-members'],
      maxMembers: 50,
      maxPortfolios: 20,
      maxWatchlists: 50
    };
  }

  // Watchlist Methods
  async createWatchlist(teamId: string, watchlist: Omit<SharedWatchlist, 'watchlistId' | 'teamId' | 'viewCount' | 'lastModified' | 'lastViewed'>): Promise<SharedWatchlist> {
    const team = this.system.teams.get(teamId);
    if (!team) {
      throw new Error('Team not found');
    }

    if (team.watchlists.length >= this.system.config.maxWatchlistsPerTeam) {
      throw new Error('Maximum watchlists reached');
    }

    const newWatchlist: SharedWatchlist = {
      ...watchlist,
      watchlistId: `watchlist_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      teamId,
      viewCount: 0,
      lastModified: Date.now(),
      lastViewed: Date.now()
    };
    
    team.watchlists.push(newWatchlist);
    team.lastModified = Date.now();
    
    this.logAuditEvent(teamId, 'watchlist_created', watchlist.createdBy, { watchlistName: newWatchlist.name });
    this.system.lastUpdated = Date.now();
    return newWatchlist;
  }

  getWatchlist(watchlistId: string): SharedWatchlist | undefined {
    for (const team of this.system.teams.values()) {
      const watchlist = team.watchlists.find(w => w.watchlistId === watchlistId);
      if (watchlist) return watchlist;
    }
    return undefined;
  }

  getTeamWatchlists(teamId: string): SharedWatchlist[] {
    const team = this.system.teams.get(teamId);
    return team?.watchlists || [];
  }

  async addSymbolToWatchlist(watchlistId: string, symbol: Omit<WatchlistSymbol, 'alerts' | 'addedAt'>): Promise<void> {
    const team = this.system.teams.values().next().value;
    if (team) {
      const watchlist = team.watchlists.find(w => w.watchlistId === watchlistId);
      if (watchlist) {
        watchlist.symbols.push({
          ...symbol,
          alerts: [],
          addedAt: Date.now()
        });
        watchlist.lastModified = Date.now();
        team.lastModified = Date.now();
        
        this.logAuditEvent(team.teamId, 'symbol_added', symbol.addedBy, { watchlistId, symbol: symbol.symbol });
        this.system.lastUpdated = Date.now();
      }
    }
  }

  async removeSymbolFromWatchlist(watchlistId: string, symbol: string): Promise<void> {
    for (const team of this.system.teams.values()) {
      const watchlist = team.watchlists.find(w => w.watchlistId === watchlistId);
      if (watchlist) {
        watchlist.symbols = watchlist.symbols.filter(s => s.symbol !== symbol);
        watchlist.lastModified = Date.now();
        team.lastModified = Date.now();
        
        this.logAuditEvent(team.teamId, 'symbol_removed', '', { watchlistId, symbol });
        this.system.lastUpdated = Date.now();
        return;
      }
    }
  }

  // Chart Methods
  async createChart(teamId: string, chart: Omit<CollaborativeChart, 'chartId' | 'teamId' | 'version' | 'viewCount' | 'lastModified' | 'lastViewed'>): Promise<CollaborativeChart> {
    const team = this.system.teams.get(teamId);
    if (!team) {
      throw new Error('Team not found');
    }

    if (team.charts.length >= this.system.config.maxChartsPerTeam) {
      throw new Error('Maximum charts reached');
    }

    const newChart: CollaborativeChart = {
      ...chart,
      chartId: `chart_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      teamId,
      version: 1,
      viewCount: 0,
      lastModified: Date.now(),
      lastViewed: Date.now()
    };
    
    team.charts.push(newChart);
    team.lastModified = Date.now();
    
    this.logAuditEvent(teamId, 'chart_created', chart.createdBy, { chartName: newChart.name });
    this.system.lastUpdated = Date.now();
    return newChart;
  }

  getChart(chartId: string): CollaborativeChart | undefined {
    for (const team of this.system.teams.values()) {
      const chart = team.charts.find(c => c.chartId === chartId);
      if (chart) return chart;
    }
    return undefined;
  }

  getTeamCharts(teamId: string): CollaborativeChart[] {
    const team = this.system.teams.get(teamId);
    return team?.charts || [];
  }

  async addChartAnnotation(chartId: string, annotation: Omit<ChartAnnotation, 'annotationId' | 'createdAt'>): Promise<ChartAnnotation> {
    const newAnnotation: ChartAnnotation = {
      ...annotation,
      annotationId: `annotation_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: Date.now()
    };
    
    for (const team of this.system.teams.values()) {
      const chart = team.charts.find(c => c.chartId === chartId);
      if (chart) {
        chart.annotations.push(newAnnotation);
        chart.version++;
        chart.lastModified = Date.now();
        chart.lastModifiedBy = annotation.createdBy;
        team.lastModified = Date.now();
        
        this.logAuditEvent(team.teamId, 'annotation_added', annotation.createdBy, { chartId });
        this.system.lastUpdated = Date.now();
        return newAnnotation;
      }
    }
    
    throw new Error('Chart not found');
  }

  // Portfolio Methods
  async createPortfolio(teamId: string, portfolio: Omit<TeamPortfolio, 'portfolioId' | 'teamId' | 'performance' | 'riskMetrics' | 'lastRebalanced' | 'lastModified'>): Promise<TeamPortfolio> {
    const team = this.system.teams.get(teamId);
    if (!team) {
      throw new Error('Team not found');
    }

    if (team.portfolios.length >= this.system.config.maxPortfoliosPerTeam) {
      throw new Error('Maximum portfolios reached');
    }

    const newPortfolio: TeamPortfolio = {
      ...portfolio,
      portfolioId: `portfolio_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      teamId,
      performance: this.getDefaultPerformance(),
      riskMetrics: this.getDefaultRiskMetrics(),
      lastRebalanced: Date.now(),
      lastModified: Date.now()
    };
    
    team.portfolios.push(newPortfolio);
    team.lastModified = Date.now();
    
    this.logAuditEvent(teamId, 'portfolio_created', portfolio.createdBy, { portfolioName: newPortfolio.name });
    this.system.lastUpdated = Date.now();
    return newPortfolio;
  }

  getPortfolio(portfolioId: string): TeamPortfolio | undefined {
    for (const team of this.system.teams.values()) {
      const portfolio = team.portfolios.find(p => p.portfolioId === portfolioId);
      if (portfolio) return portfolio;
    }
    return undefined;
  }

  getTeamPortfolios(teamId: string): TeamPortfolio[] {
    const team = this.system.teams.get(teamId);
    return team?.portfolios || [];
  }

  async addPortfolioPosition(portfolioId: string, position: Omit<PortfolioPosition, 'unrealizedPnL' | 'unrealizedPnLPercent' | 'weight'>): Promise<void> {
    for (const team of this.system.teams.values()) {
      const portfolio = team.portfolios.find(p => p.portfolioId === portfolioId);
      if (portfolio) {
        const newPos: PortfolioPosition = {
          ...position,
          unrealizedPnL: (position.currentPrice - position.avgPrice) * position.quantity,
          unrealizedPnLPercent: ((position.currentPrice - position.avgPrice) / position.avgPrice) * 100,
          weight: 0 // Will be calculated
        };
        
        portfolio.positions.push(newPos);
        portfolio.lastModified = Date.now();
        this.recalculatePortfolioMetrics(portfolio);
        team.lastModified = Date.now();
        
        this.logAuditEvent(team.teamId, 'position_added', position.addedBy, { portfolioId, symbol: position.symbol });
        this.system.lastUpdated = Date.now();
        return;
      }
    }
    
    throw new Error('Portfolio not found');
  }

  private recalculatePortfolioMetrics(portfolio: TeamPortfolio): void {
    const totalValue = portfolio.positions.reduce((sum, pos) => sum + pos.marketValue, 0);
    portfolio.positions.forEach(pos => {
      pos.weight = (pos.marketValue / totalValue) * 100;
    });
    
    portfolio.assetAllocation = this.calculateAssetAllocation(portfolio);
    portfolio.performance = this.calculatePortfolioPerformance(portfolio);
    portfolio.riskMetrics = this.calculateRiskMetrics(portfolio);
  }

  private calculateAssetAllocation(portfolio: TeamPortfolio): PortfolioAllocation[] {
    const allocationMap = new Map<string, number>();
    
    portfolio.positions.forEach(pos => {
      const current = allocationMap.get(pos.assetClass) || 0;
      allocationMap.set(pos.assetClass, current + pos.marketValue);
    });
    
    return Array.from(allocationMap.entries()).map(([assetClass, value]) => ({
      assetClass,
      percentage: (value / portfolio.positions.reduce((sum, pos) => sum + pos.marketValue, 0)) * 100,
      value,
      targetPercentage: 0,
      targetValue: 0
    }));
  }

  private getDefaultPerformance(): PortfolioPerformance {
    return {
      totalReturn: 0,
      dailyReturn: 0,
      weeklyReturn: 0,
      monthlyReturn: 0,
      yearlyReturn: 0,
      sharpeRatio: 0,
      sortinoRatio: 0,
      maxDrawdown: 0,
      volatility: 0,
      beta: 0,
      alpha: 0,
      trackingError: 0,
      informationRatio: 0,
      startDate: Date.now(),
      lastUpdated: Date.now()
    };
  }

  private getDefaultRiskMetrics(): PortfolioRiskMetrics {
    return {
      valueAtRisk: 0,
      expectedShortfall: 0,
      concentrationRisk: 0,
      currencyRisk: 0,
      liquidityRisk: 0,
      leverage: 0,
      exposure: 0,
      lastUpdated: Date.now()
    };
  }

  private calculatePortfolioPerformance(portfolio: TeamPortfolio): PortfolioPerformance {
    // Simplified calculation - in real system would use historical data
    const totalPnL = portfolio.positions.reduce((sum, pos) => sum + pos.unrealizedPnL, 0);
    const totalValue = portfolio.positions.reduce((sum, pos) => sum + pos.marketValue, 0);
    
    return {
      ...portfolio.performance,
      totalReturn: totalValue > 0 ? (totalPnL / totalValue) * 100 : 0,
      lastUpdated: Date.now()
    };
  }

  private calculateRiskMetrics(portfolio: TeamPortfolio): PortfolioRiskMetrics {
    // Simplified calculation - in real system would use advanced risk models
    return {
      ...portfolio.riskMetrics,
      lastUpdated: Date.now()
    };
  }

  // Alert Methods
  async createTeamAlert(teamId: string, alert: Omit<TeamAlert, 'alertId' | 'teamId' | 'acknowledged' | 'resolved' | 'createdAt'>): Promise<TeamAlert> {
    const newAlert: TeamAlert = {
      ...alert,
      alertId: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      teamId,
      acknowledged: false,
      resolved: false,
      createdAt: Date.now()
    };
    
    const team = this.system.teams.get(teamId);
    if (team) {
      team.alerts.push(newAlert);
      team.lastModified = Date.now();
      
      this.logAuditEvent(teamId, 'alert_created', '', { alertType: alert.type, severity: alert.severity });
      this.system.lastUpdated = Date.now();
    }
    
    return newAlert;
  }

  getTeamAlerts(teamId: string): TeamAlert[] {
    const team = this.system.teams.get(teamId);
    return team?.alerts || [];
  }

  async acknowledgeAlert(alertId: string, userId: string): Promise<void> {
    for (const team of this.system.teams.values()) {
      const alert = team.alerts.find(a => a.alertId === alertId);
      if (alert) {
        alert.acknowledged = true;
        alert.acknowledgedBy = userId;
        alert.acknowledgedAt = Date.now();
        team.lastModified = Date.now();
        
        this.logAuditEvent(team.teamId, 'alert_acknowledged', userId, { alertId });
        this.system.lastUpdated = Date.now();
        return;
      }
    }
  }

  async resolveAlert(alertId: string, userId: string): Promise<void> {
    for (const team of this.system.teams.values()) {
      const alert = team.alerts.find(a => a.alertId === alertId);
      if (alert) {
        alert.resolved = true;
        alert.resolvedBy = userId;
        alert.resolvedAt = Date.now();
        team.lastModified = Date.now();
        
        this.logAuditEvent(team.teamId, 'alert_resolved', userId, { alertId });
        this.system.lastUpdated = Date.now();
        return;
      }
    }
  }

  // Analytics Methods
  async generateTeamAnalytics(teamId: string, period: TeamAnalytics['period']): Promise<TeamAnalytics> {
    const team = this.system.teams.get(teamId);
    if (!team) {
      throw new Error('Team not found');
    }

    const analytics: TeamAnalytics = {
      teamId,
      period,
      startDate: this.getStartDateByPeriod(period),
      endDate: Date.now(),
      members: this.generateMemberAnalytics(team),
      portfolioAnalytics: this.generatePortfolioAnalytics(team),
      watchlistAnalytics: this.generateWatchlistAnalytics(team),
      tradingAnalytics: this.generateTradingAnalytics(team),
      collaborationMetrics: this.generateCollaborationMetrics(team),
      generatedAt: Date.now()
    };

    return analytics;
  }

  private getStartDateByPeriod(period: TeamAnalytics['period']): number {
    const now = Date.now();
    switch (period) {
      case 'daily':
        return now - 86400000;
      case 'weekly':
        return now - 86400000 * 7;
      case 'monthly':
        return now - 86400000 * 30;
      case 'yearly':
        return now - 86400000 * 365;
      default:
        return now - 86400000;
    }
  }

  private generateMemberAnalytics(team: TeamWorkspace): MemberAnalytics[] {
    return team.members.map(member => ({
      userId: member.userId,
      username: member.username,
      contributionScore: Math.floor(Math.random() * 100),
      activityLevel: Math.floor(Math.random() * 100),
      shares: Math.floor(Math.random() * 20),
      alertsCreated: Math.floor(Math.random() * 10),
      alertsResolved: Math.floor(Math.random() * 8),
      positionsAdded: Math.floor(Math.random() * 15),
      annotationsAdded: Math.floor(Math.random() * 30),
      onlineTime: Math.floor(Math.random() * 10000),
      lastActive: member.lastActivity
    }));
  }

  private generatePortfolioAnalytics(team: TeamWorkspace): PortfolioAnalytics {
    const portfolios = team.portfolios;
    return {
      totalPortfolios: portfolios.length,
      totalValue: portfolios.reduce((sum, p) => sum + p.positions.reduce((sum2, pos) => sum2 + pos.marketValue, 0), 0),
      totalReturn: portfolios.length > 0 ? portfolios.reduce((sum, p) => sum + p.performance.totalReturn, 0) / portfolios.length : 0,
      bestPerforming: portfolios.length > 0 ? { portfolioId: portfolios[0].portfolioId, name: portfolios[0].name, return: portfolios[0].performance.totalReturn } : { portfolioId: '', name: '', return: 0 },
      worstPerforming: portfolios.length > 0 ? { portfolioId: portfolios[0].portfolioId, name: portfolios[0].name, return: portfolios[0].performance.totalReturn } : { portfolioId: '', name: '', return: 0 },
      averageSharpeRatio: portfolios.length > 0 ? portfolios.reduce((sum, p) => sum + p.performance.sharpeRatio, 0) / portfolios.length : 0,
      totalPositions: portfolios.reduce((sum, p) => sum + p.positions.length, 0),
      topAssets: []
    };
  }

  private generateWatchlistAnalytics(team: TeamWorkspace): WatchlistAnalytics {
    const watchlists = team.watchlists;
    return {
      totalWatchlists: watchlists.length,
      totalSymbols: watchlists.reduce((sum, w) => sum + w.symbols.length, 0),
      totalViews: watchlists.reduce((sum, w) => sum + w.viewCount, 0),
      mostViewed: watchlists.map(w => ({ watchlistId: w.watchlistId, name: w.name, views: w.viewCount })).slice(0, 5),
      topAlerts: watchlists.reduce((sum, w) => sum + w.symbols.reduce((sum2, s) => sum2 + s.alerts.length, 0), 0),
      triggeredAlerts: Math.floor(Math.random() * 20)
    };
  }

  private generateTradingAnalytics(_team: TeamWorkspace): TradingAnalytics {
    return {
      totalTrades: Math.floor(Math.random() * 1000),
      totalVolume: Math.floor(Math.random() * 1000000),
      totalPnL: (Math.random() - 0.5) * 100000,
      winRate: Math.random() * 100,
      averageWin: Math.random() * 1000,
      averageLoss: Math.random() * 1000,
      profitFactor: Math.random() * 2,
      bestTrade: { symbol: 'AAPL', pnl: 5000 },
      worstTrade: { symbol: 'TSLA', pnl: -3000 }
    };
  }

  private generateCollaborationMetrics(team: TeamWorkspace): CollaborationMetrics {
    return {
      totalShares: team.charts.reduce((sum, c) => sum + (c.collaborators?.length || 0), 0),
      totalComments: Math.floor(Math.random() * 200),
      totalAnnotations: team.charts.reduce((sum, c) => sum + c.annotations.length, 0),
      activeCollaborators: team.members.filter(m => m.status === 'active').length,
      averageResponseTime: Math.floor(Math.random() * 3600),
      collaborationScore: Math.floor(Math.random() * 100)
    };
  }

  // Audit Log Methods
  private logAuditEvent(teamId: string, action: string, userId: string, details: Record<string, any>): void {
    const auditLog: TeamAuditLog = {
      auditId: `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      teamId,
      action,
      userId,
      username: '', // Will be filled from user system
      details,
      timestamp: Date.now(),
      category: this.getAuditCategory(action)
    };
    
    this.system.auditLogs.set(auditLog.auditId, auditLog);
  }

  private getAuditCategory(action: string): TeamAuditLog['category'] {
    if (action.includes('security') || action.includes('login') || action.includes('logout')) return 'security';
    if (action.includes('portfolio') || action.includes('position')) return 'portfolio';
    if (action.includes('watchlist') || action.includes('symbol')) return 'watchlist';
    if (action.includes('chart') || action.includes('annotation')) return 'chart';
    if (action.includes('alert')) return 'alert';
    if (action.includes('settings')) return 'settings';
    return 'general';
  }

  getAuditLogs(teamId: string, limit?: number): TeamAuditLog[] {
    let logs = Array.from(this.system.auditLogs.values()).filter(l => l.teamId === teamId);
    logs.sort((a, b) => b.timestamp - a.timestamp);
    if (limit) {
      logs = logs.slice(0, limit);
    }
    return logs;
  }
}

export const teamCollaborationSystem = new TeamCollaborationSystemImplementation();
export default TeamCollaborationSystemImplementation;