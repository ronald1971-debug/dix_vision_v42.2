/**
 * Stock Trading Enhancements - Phase 17
 * DIX VISION v42.2 - Phase 17: Asset Class-Specific Enhancements (Weeks 55-62)
 * 
 * This module implements stock-specific trading enhancements including:
 * - Earnings calendar and integration
 * - Institutional ownership tracking
 * - Insider trading alerts
 * - Sector and industry analysis
 * - Options flow tracking (unusual activity)
 * - ETF creation/redemption tracking
 * - Pre-market and after-hours analysis
 * - Circuit breaker monitoring
 */

export interface EarningsEvent {
  eventId: string;
  symbol: string;
  companyName: string;
  fiscalQuarter: string;
  reportDate: number;
  reportTime: 'pre-market' | 'after-market' | 'during-day';
  epsEstimate: number;
  epsActual: number;
  epsSurprise: number;
  epsSurprisePercent: number;
  revenueEstimate: number;
  revenueActual: number;
  revenueSurprise: number;
  revenueSurprisePercent: number;
  guidance?: string;
  callUrl?: string;
  transcriptUrl?: string;
  impact: 'positive' | 'negative' | 'neutral';
  priceReaction?: {
    preMarketChange: number;
    afterHoursChange: number;
    nextDayChange: number;
  };
  analystCount: number;
  createdAt: number;
}

export interface EarningsCalendar {
  calendarId: string;
  period: string;
  events: EarningsEvent[];
  lastUpdated: number;
}

export interface InstitutionalOwnership {
  ownershipId: string;
  symbol: string;
  companyName: string;
  totalSharesOutstanding: number;
  institutionalShares: number;
  institutionalOwnershipPercent: number;
  institutions: Institution[];
  changeFromPreviousQuarter: number;
  topHolders: Institution[];
  newPositions: Institution[];
  soldOutPositions: Institution[];
  sectorComparison: SectorOwnership;
  lastUpdated: number;
}

export interface Institution {
  institutionId: string;
  name: string;
  type: 'hedge-fund' | 'mutual-fund' | 'etf' | 'pension' | 'insurance' | 'bank' | 'other';
  shares: number;
  value: number;
  percentOfPortfolio: number;
  changeShares: number;
  changePercent: number;
  reportDate: number;
  filingType: '13F' | '13D' | '13G' | 'SC13G' | 'SC13D';
}

export interface SectorOwnership {
  sector: string;
  averageOwnershipPercent: number;
  currentOwnershipPercent: number;
  percentile: number;
}

export interface InsiderTradingAlert {
  alertId: string;
  insiderId: string;
  insiderName: string;
  insiderTitle: string;
  symbol: string;
  companyName: string;
  transactionType: 'buy' | 'sell' | 'option-exercise' | 'gift' | 'other';
  shares: number;
  price: number;
  value: number;
  totalSharesAfter: number;
  filingDate: number;
  isUnusual: boolean;
  unusualReason?: string;
  pattern?: 'cluster-buys' | 'cluster-sells' | 'timing-based' | 'regression';
  confidence: number;
  relatedAlerts: string[];
  createdAt: number;
}

export interface InsiderProfile {
  insiderId: string;
  name: string;
  title: string;
  symbol: string;
  companyName: string;
  transactions: InsiderTradingAlert[];
  performance: InsiderPerformance;
  patterns: TradingPattern[];
  lastUpdated: number;
}

export interface InsiderPerformance {
  totalTransactions: number;
  successfulSignals: number;
  averageReturn: number;
  winRate: number;
  signalAccuracy: number;
}

export interface TradingPattern {
  patternType: string;
  frequency: number;
  averageReturn: number;
  reliability: number;
}

export interface SectorAnalysis {
  sectorId: string;
  name: string;
  symbol: string;
  companies: string[];
  performance: SectorPerformance;
  composition: SectorComposition;
  trends: SectorTrend[];
  catalysts: SectorCatalyst[];
  riskFactors: string[];
  valuation: SectorValuation;
  lastUpdated: number;
}

export interface SectorPerformance {
  ytdReturn: number;
  monthlyReturn: number;
  weeklyReturn: number;
  dailyReturn: number;
  volatility: number;
  beta: number;
  correlationToMarket: number;
  relativeStrength: number;
}

export interface SectorComposition {
  topCompanies: SectorCompany[];
  marketCapDistribution: MarketCapRange[];
  styleDistribution: StyleDistribution;
  geography: GeographyDistribution;
}

export interface SectorCompany {
  symbol: string;
  name: string;
  weight: number;
  marketCap: number;
  performance: number;
}

export interface MarketCapRange {
  range: string;
  count: number;
  totalMarketCap: number;
  weight: number;
}

export interface StyleDistribution {
  growth: number;
  value: number;
  blend: number;
}

export interface GeographyDistribution {
  domestic: number;
  international: number;
}

export interface SectorTrend {
  trendId: string;
  name: string;
  direction: 'up' | 'down' | 'sideways';
  strength: number;
  duration: number;
  drivers: string[];
  timeframe: 'short-term' | 'medium-term' | 'long-term';
}

export interface SectorCatalyst {
  catalystId: string;
  name: string;
  type: 'regulatory' | 'economic' | 'technological' | 'market' | 'company-specific';
  impact: 'positive' | 'negative' | 'mixed';
  timing: string;
  probability: number;
  affectedCompanies: string[];
}

export interface SectorValuation {
  peRatio: number;
  pbRatio: number;
  psRatio: number;
  evEbitda: number;
  historicalPercentile: number;
  relativeValuation: string;
}

export interface OptionsFlow {
  flowId: string;
  symbol: string;
  date: number;
  putCallRatio: number;
  totalVolume: number;
  totalOpenInterest: number;
  unusualActivity: UnusualActivity[];
  impliedVolatility: number;
  ivRank: number;
  ivPercentile: number;
  maxPain: number;
  putCallSkew: number;
  largeTrades: LargeOptionTrade[];
  sentiment: 'bullish' | 'bearish' | 'neutral';
  createdAt: number;
}

export interface UnusualActivity {
  activityId: string;
  type: 'volume-spike' | 'oi-spike' | 'iv-spike' | 'price-movement';
  strike: number;
  expiry: number;
  optionType: 'call' | 'put';
  volume: number;
  avgVolume: number;
  openInterest: number;
  price: number;
  iv: number;
  ivChange: number;
  significance: number;
  explanation: string;
}

export interface LargeOptionTrade {
  tradeId: string;
  strike: number;
  expiry: number;
  optionType: 'call' | 'put';
  volume: number;
  price: number;
  totalValue: number;
  sweep: boolean;
  aggressive: boolean;
  timestamp: number;
}

export interface ETFTracking {
  etfId: string;
  symbol: string;
  name: string;
  underlying: string[];
  nav: number;
  premiumDiscount: number;
  creationRedemptionActivity: CreationRedemptionActivity;
  holdings: ETFHolding[];
  performance: ETFPerformance;
  arbitrageOpportunities: ArbitrageOpportunity[];
  lastUpdated: number;
}

export interface CreationRedemptionActivity {
  creations: number;
  redemptions: number;
  netFlow: number;
  feeRate: number;
  authorizedParticipants: string[];
  lastFeeCalculation: number;
}

export interface ETFHolding {
  symbol: string;
  name: string;
  shares: number;
  weight: number;
  value: number;
  sector: string;
}

export interface ETFPerformance {
  navReturn: number;
  priceReturn: number;
  trackingError: number;
  expenseRatio: number;
  yield: number;
}

export interface ArbitrageOpportunity {
  opportunityId: string;
  type: 'premium-discount' | 'creation-redemption' | 'in-kind';
  expectedReturn: number;
  risk: number;
  duration: number;
  createdAt: number;
}

export interface ExtendedHours {
  sessionId: string;
  symbol: string;
  date: number;
  preMarket: ExtendedHoursSession;
  afterMarket: ExtendedHoursSession;
  volumeProfile: VolumeProfile;
  priceMovement: PriceMovement;
  catalysts: string[];
  lastUpdated: number;
}

export interface ExtendedHoursSession {
  startTime: number;
  endTime: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  trades: number;
  avgTradeSize: number;
  volatility: number;
}

export interface VolumeProfile {
  priceLevels: VolumeLevel[];
  totalVolume: number;
  vwap: number;
}

export interface VolumeLevel {
  price: number;
  volume: number;
  percentage: number;
  time: number;
}

export interface PriceMovement {
  preMarketChange: number;
  preMarketPercent: number;
  afterMarketChange: number;
  afterMarketPercent: number;
  gap: number;
  gapPercent: number;
}

export interface CircuitBreaker {
  breakerId: string;
  symbol: string;
  level: 'level-1' | 'level-2' | 'level-3';
  triggeredAt: number;
  triggerPrice: number;
  referencePrice: number;
  pauseDuration: number;
  resumeTime: number;
  reason: string;
  marketCondition: 'limit-down' | 'limit-up' | 'wide-circuit' | 'liquidity-replenishment';
  impactedSecurities: string[];
  additionalInfo: CircuitBreakerInfo;
  createdAt: number;
}

export interface CircuitBreakerInfo {
  totalSharesTraded: number;
  totalVolume: number;
  affectedExchanges: string[];
  relatedSymbols: string[];
  historicalBreakers: CircuitBreaker[];
}

export class StockTradingEnhancementsSystem {
  private earningsCalendar: Map<string, EarningsCalendar>;
  private institutionalOwnership: Map<string, InstitutionalOwnership>;
  private insiderAlerts: Map<string, InsiderTradingAlert[]>;
  private insiderProfiles: Map<string, InsiderProfile>;
  private sectorAnalysis: Map<string, SectorAnalysis>;
  private optionsFlow: Map<string, OptionsFlow>;
  private etfTracking: Map<string, ETFTracking>;
  private extendedHours: Map<string, ExtendedHours>;
  private circuitBreakers: Map<string, CircuitBreaker>;
  private lastUpdated: number = Date.now();


  constructor() {
    this.earningsCalendar = new Map();
    this.institutionalOwnership = new Map();
    this.insiderAlerts = new Map();
    this.insiderProfiles = new Map();
    this.sectorAnalysis = new Map();
    this.optionsFlow = new Map();
    this.etfTracking = new Map();
    this.extendedHours = new Map();
    this.circuitBreakers = new Map();
    this.lastUpdated = Date.now();
  }

  initialize(): void {
    this.loadDefaultSectorAnalysis();
    this.loadDefaultETFs();
  }

  // Earnings Calendar Methods
  async createEarningsEvent(event: Omit<EarningsEvent, 'eventId' | 'createdAt'>): Promise<EarningsEvent> {
    const newEvent: EarningsEvent = {
      ...event,
      eventId: `earnings_${this.lastUpdated}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: this.lastUpdated
    };
    
    const periodKey = this.getEarningsPeriod(event.reportDate);
    let calendar = this.earningsCalendar.get(periodKey);
    if (!calendar) {
      calendar = {
        calendarId: `calendar_${periodKey}`,
        period: periodKey,
        events: [],
        lastUpdated: this.lastUpdated
      };
      this.earningsCalendar.set(periodKey, calendar);
    }
    
    calendar.events.push(newEvent);
    calendar.lastUpdated = this.lastUpdated;

    return newEvent;
  }

  getEarningsCalendar(period: string): EarningsCalendar | undefined {
    return this.earningsCalendar.get(period);
  }

  getEarningsEvents(symbol: string): EarningsEvent[] {
    const events: EarningsEvent[] = [];
    this.earningsCalendar.forEach(calendar => {
      events.push(...calendar.events.filter(e => e.symbol === symbol));
    });
    return events.sort((a, b) => a.reportDate - b.reportDate);
  }

  async updateEarningsImpact(eventId: string, impact: EarningsEvent['impact'], priceReaction?: EarningsEvent['priceReaction']): Promise<void> {
    this.earningsCalendar.forEach(calendar => {
      const event = calendar.events.find(e => e.eventId === eventId);
      if (event) {
        event.impact = impact;
        event.priceReaction = priceReaction;
        calendar.lastUpdated = this.lastUpdated;
    
      }
    });
  }

  private getEarningsPeriod(date: number): string {
    const d = new Date(date);
    return `${d.getFullYear()}-Q${Math.ceil((d.getMonth() + 1) / 3)}`;
  }

  // Institutional Ownership Methods
  async createInstitutionalOwnership(ownership: Omit<InstitutionalOwnership, 'ownershipId' | 'lastUpdated'>): Promise<InstitutionalOwnership> {
    const newOwnership: InstitutionalOwnership = {
      ...ownership,
      ownershipId: `ownership_${this.lastUpdated}_${Math.random().toString(36).substr(2, 9)}`,
      lastUpdated: this.lastUpdated
    };
    
    this.institutionalOwnership.set(newOwnership.symbol, newOwnership);

    return newOwnership;
  }

  getInstitutionalOwnership(symbol: string): InstitutionalOwnership | undefined {
    return this.institutionalOwnership.get(symbol);
  }

  async addInstitution(symbol: string, institution: Omit<Institution, 'institutionId'>): Promise<void> {
    const ownership = this.institutionalOwnership.get(symbol);
    if (ownership) {
      const newInstitution: Institution = {
        ...institution,
        institutionId: `inst_${this.lastUpdated}_${Math.random().toString(36).substr(2, 9)}`
      };
      ownership.institutions.push(newInstitution);
      ownership.institutionalShares += institution.shares;
      ownership.institutionalOwnershipPercent = (ownership.institutionalShares / ownership.totalSharesOutstanding) * 100;
      ownership.lastUpdated = this.lastUpdated;
  
    }
  }

  // Insider Trading Methods
  async createInsiderAlert(alert: Omit<InsiderTradingAlert, 'alertId' | 'createdAt'>): Promise<InsiderTradingAlert> {
    const newAlert: InsiderTradingAlert = {
      ...alert,
      alertId: `insider_${this.lastUpdated}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: this.lastUpdated
    };
    
    let alerts = this.insiderAlerts.get(alert.symbol);
    if (!alerts) {
      alerts = [];
      this.insiderAlerts.set(alert.symbol, alerts);
    }
    
    alerts.push(newAlert);
    
    // Update insider profile
    let profile = this.insiderProfiles.get(alert.insiderId);
    if (!profile) {
      profile = {
        insiderId: alert.insiderId,
        name: alert.insiderName,
        title: alert.insiderTitle,
        symbol: alert.symbol,
        companyName: alert.companyName,
        transactions: [],
        performance: {
          totalTransactions: 0,
          successfulSignals: 0,
          averageReturn: 0,
          winRate: 0,
          signalAccuracy: 0
        },
        patterns: [],
        lastUpdated: this.lastUpdated
      };
      this.insiderProfiles.set(alert.insiderId, profile);
    }
    
    profile.transactions.push(newAlert);
    profile.lastUpdated = this.lastUpdated;

    
    return newAlert;
  }

  getInsiderAlerts(symbol: string): InsiderTradingAlert[] {
    return this.insiderAlerts.get(symbol) || [];
  }

  getInsiderProfile(insiderId: string): InsiderProfile | undefined {
    return this.insiderProfiles.get(insiderId);
  }

  async detectUnusualInsiderActivity(symbol: string): Promise<InsiderTradingAlert[]> {
    const alerts = this.getInsiderAlerts(symbol);
    return alerts.filter(a => a.isUnusual);
  }

  // Sector Analysis Methods
  async createSectorAnalysis(analysis: Omit<SectorAnalysis, 'sectorId' | 'lastUpdated'>): Promise<SectorAnalysis> {
    const newAnalysis: SectorAnalysis = {
      ...analysis,
      sectorId: `sector_${this.lastUpdated}_${Math.random().toString(36).substr(2, 9)}`,
      lastUpdated: this.lastUpdated
    };
    
    this.sectorAnalysis.set(newAnalysis.symbol, newAnalysis);

    return newAnalysis;
  }

  getSectorAnalysis(symbol: string): SectorAnalysis | undefined {
    return this.sectorAnalysis.get(symbol);
  }

  async analyzeSectorTrends(sector: string): Promise<SectorTrend[]> {
    const trends: SectorTrend[] = [];
    this.sectorAnalysis.forEach(analysis => {
      if (analysis.name === sector) {
        trends.push(...analysis.trends);
      }
    });
    return trends;
  }

  // Options Flow Methods
  async createOptionsFlow(flow: Omit<OptionsFlow, 'flowId' | 'createdAt'>): Promise<OptionsFlow> {
    const newFlow: OptionsFlow = {
      ...flow,
      flowId: `flow_${this.lastUpdated}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: this.lastUpdated
    };
    
    this.optionsFlow.set(newFlow.symbol, newFlow);

    return newFlow;
  }

  getOptionsFlow(symbol: string): OptionsFlow | undefined {
    return this.optionsFlow.get(symbol);
  }

  async detectUnusualOptionsActivity(symbol: string): Promise<UnusualActivity[]> {
    const flow = this.optionsFlow.get(symbol);
    return flow?.unusualActivity.filter(a => a.significance > 70) || [];
  }

  // ETF Tracking Methods
  async createETFTracking(etf: Omit<ETFTracking, 'etfId' | 'lastUpdated'>): Promise<ETFTracking> {
    const newETF: ETFTracking = {
      ...etf,
      etfId: `etf_${this.lastUpdated}_${Math.random().toString(36).substr(2, 9)}`,
      lastUpdated: this.lastUpdated
    };
    
    this.etfTracking.set(newETF.symbol, newETF);

    return newETF;
  }

  getETFTracking(symbol: string): ETFTracking | undefined {
    return this.etfTracking.get(symbol);
  }

  async findArbitrageOpportunities(symbol: string): Promise<ArbitrageOpportunity[]> {
    const etf = this.etfTracking.get(symbol);
    return etf?.arbitrageOpportunities || [];
  }

  // Extended Hours Methods
  async createExtendedHours(session: Omit<ExtendedHours, 'sessionId' | 'lastUpdated'>): Promise<ExtendedHours> {
    const newSession: ExtendedHours = {
      ...session,
      sessionId: `session_${this.lastUpdated}_${Math.random().toString(36).substr(2, 9)}`,
      lastUpdated: this.lastUpdated
    };
    
    this.extendedHours.set(newSession.symbol, newSession);

    return newSession;
  }

  getExtendedHours(symbol: string): ExtendedHours | undefined {
    return this.extendedHours.get(symbol);
  }

  // Circuit Breaker Methods
  async createCircuitBreaker(breaker: Omit<CircuitBreaker, 'breakerId' | 'createdAt'>): Promise<CircuitBreaker> {
    const newBreaker: CircuitBreaker = {
      ...breaker,
      breakerId: `breaker_${this.lastUpdated}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: this.lastUpdated
    };
    
    this.circuitBreakers.set(newBreaker.symbol, newBreaker);

    return newBreaker;
  }

  getCircuitBreaker(symbol: string): CircuitBreaker | undefined {
    return this.circuitBreakers.get(symbol);
  }

  async getCircuitBreakerHistory(symbol: string): Promise<CircuitBreaker[]> {
    const breaker = this.circuitBreakers.get(symbol);
    return breaker?.additionalInfo.historicalBreakers || [];
  }

  private loadDefaultSectorAnalysis(): void {
    const defaultSectors = ['Technology', 'Healthcare', 'Financials', 'Energy', 'Consumer Discretionary'];
    defaultSectors.forEach(sector => {
      this.createSectorAnalysis({
        name: sector,
        symbol: sector.toLowerCase().replace(' ', '-'),
        companies: [],
        performance: {
          ytdReturn: 0,
          monthlyReturn: 0,
          weeklyReturn: 0,
          dailyReturn: 0,
          volatility: 0,
          beta: 1,
          correlationToMarket: 0.7,
          relativeStrength: 50
        },
        composition: {
          topCompanies: [],
          marketCapDistribution: [],
          styleDistribution: { growth: 50, value: 30, blend: 20 },
          geography: { domestic: 80, international: 20 }
        },
        trends: [],
        catalysts: [],
        riskFactors: [],
        valuation: {
          peRatio: 0,
          pbRatio: 0,
          psRatio: 0,
          evEbitda: 0,
          historicalPercentile: 50,
          relativeValuation: 'neutral'
        }
      });
    });
  }

  private loadDefaultETFs(): void {
    const defaultETFs = [
      {
        symbol: 'SPY',
        name: 'SPDR S&P 500 ETF Trust',
        underlying: ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA'],
        nav: 400,
        premiumDiscount: 0.05,
        creationRedemptionActivity: {
          creations: 0,
          redemptions: 0,
          netFlow: 0,
          feeRate: 0.09,
          authorizedParticipants: [],
          lastFeeCalculation: this.lastUpdated
        },
        holdings: [],
        performance: {
          navReturn: 0,
          priceReturn: 0,
          trackingError: 0.01,
          expenseRatio: 0.09,
          yield: 1.5
        },
        arbitrageOpportunities: []
      },
      {
        symbol: 'QQQ',
        name: 'Invesco QQQ Trust',
        underlying: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
        nav: 350,
        premiumDiscount: 0.02,
        creationRedemptionActivity: {
          creations: 0,
          redemptions: 0,
          netFlow: 0,
          feeRate: 0.20,
          authorizedParticipants: [],
          lastFeeCalculation: this.lastUpdated
        },
        holdings: [],
        performance: {
          navReturn: 0,
          priceReturn: 0,
          trackingError: 0.02,
          expenseRatio: 0.20,
          yield: 0.5
        },
        arbitrageOpportunities: []
      }
    ];

    defaultETFs.forEach(etf => this.createETFTracking(etf));
  }
}

export const stockTradingEnhancements = new StockTradingEnhancementsSystem();
export default StockTradingEnhancementsSystem;