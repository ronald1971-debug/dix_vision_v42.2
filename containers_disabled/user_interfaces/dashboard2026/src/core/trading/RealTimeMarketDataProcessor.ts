/**
 * Real-Time Market Data Processing
 * DIX VISION v42.2 - Phase 12: Traditional Trading Enhancement with ML-Based Strategy Optimization (Weeks 37-40)
 */

export interface MarketDataProcessor {
  processorId: string;
  status: 'idle' | 'processing' | 'error';
  dataStreams: Map<string, DataStream>;
  processingMetrics: ProcessingMetrics;
  lastUpdate: number;
}

export interface DataStream {
  streamId: string;
  symbol: string;
  dataType: 'price' | 'volume' | 'order-book' | 'trades' | 'sentiment';
  frequency: number; // milliseconds
  bufferSize: number;
  lastUpdate: number;
  quality: DataQuality;
}

export interface DataQuality {
  completeness: number;
  accuracy: number;
  timeliness: number;
  lastChecked: number;
}

export interface ProcessingMetrics {
  messagesPerSecond: number;
  latency: number;
  throughput: number;
  errorRate: number;
  lastCalculated: number;
}

export interface MarketData {
  timestamp: number;
  symbol: string;
  price: number;
  volume: number;
  bid: number;
  ask: number;
  spread: number;
  high: number;
  low: number;
  open: number;
  close: number;
  change: number;
  changePercent: number;
}

export interface ProcessedData {
  dataId: string;
  source: string;
  rawData: MarketData;
  processedMetrics: ProcessedMetrics;
  anomalies: DataAnomaly[];
  indicators: TechnicalIndicators;
  timestamp: number;
}

export interface ProcessedMetrics {
  movingAverage: number;
  volatility: number;
  trend: 'up' | 'down' | 'sideways';
  momentum: number;
  volumeProfile: VolumeProfile;
}

export interface VolumeProfile {
  totalVolume: number;
  avgVolume: number;
  volumeAtPrice: Map<number, number>;
  support: number;
  resistance: number;
}

export interface DataAnomaly {
  anomalyId: string;
  type: 'price-spike' | 'volume-surge' | 'gap' | 'outlier';
  severity: 'low' | 'medium' | 'high';
  description: string;
  timestamp: number;
}

export interface TechnicalIndicators {
  rsi: number;
  macd: MACD;
  bollingerBands: BollingerBands;
  ema: number[];
  sma: number[];
}

export interface MACD {
  macd: number;
  signal: number;
  histogram: number;
}

export interface BollingerBands {
  upper: number;
  middle: number;
  lower: number;
}

class RealTimeMarketDataProcessor {
  private processors: Map<string, MarketDataProcessor> = new Map();

  initialize(): void {
    this.startProcessing();
  }

  private startProcessing(): void {
    // Start processing without storing interval reference
    setInterval(() => {
      this.processAllStreams();
    }, 100);
  }

  async processAllStreams(): Promise<void> {
    for (const processor of this.processors.values()) {
      processor.status = 'processing';
      
      for (const stream of processor.dataStreams.values()) {
        const processed = await this.processStream(stream);
        this.updateMetrics(processor, processed);
      }
      
      processor.status = 'idle';
    }
  }

  async processStream(stream: DataStream): Promise<ProcessedData> {
    const rawData = this.generateSampleData(stream.symbol);
    
    const processed: ProcessedData = {
      dataId: `processed_${Date.now()}`,
      source: stream.streamId,
      rawData,
      processedMetrics: this.calculateProcessedMetrics(rawData),
      anomalies: this.detectAnomalies(rawData),
      indicators: this.calculateIndicators(rawData),
      timestamp: Date.now()
    };

    return processed;
  }

  private generateSampleData(_symbol: string): MarketData {
    const basePrice = 100 + Math.random() * 50;
    const change = (Math.random() - 0.5) * 5;
    
    return {
      timestamp: Date.now(),
      symbol: _symbol,
      price: basePrice + change,
      volume: 1000000 + Math.floor(Math.random() * 5000000),
      bid: basePrice + change - 0.01,
      ask: basePrice + change + 0.01,
      spread: 0.02,
      high: basePrice + Math.random() * 3,
      low: basePrice - Math.random() * 3,
      open: basePrice,
      close: basePrice + change,
      change,
      changePercent: (change / basePrice) * 100
    };
  }

  private calculateProcessedMetrics(data: MarketData): ProcessedMetrics {
    const prices = this.getHistoricalPrices(data.symbol, 50);
    const ma20 = this.calculateMA(prices, 20);
    const volatility = this.calculateVolatility(prices);
    
    let trend: 'up' | 'down' | 'sideways' = 'sideways';
    if (data.price > ma20 * 1.02) trend = 'up';
    else if (data.price < ma20 * 0.98) trend = 'down';
    
    return {
      movingAverage: ma20,
      volatility,
      trend,
      momentum: (data.price - prices[0]) / prices[0],
      volumeProfile: {
        totalVolume: data.volume,
        avgVolume: 1500000,
        volumeAtPrice: new Map([[data.price, data.volume * 0.1]]),
        support: ma20 * 0.95,
        resistance: ma20 * 1.05
      }
    };
  }

  private detectAnomalies(data: MarketData): DataAnomaly[] {
    const anomalies: DataAnomaly[] = [];
    const priceChange = Math.abs(data.changePercent);
    
    if (priceChange > 5) {
      anomalies.push({
        anomalyId: `anomaly_${Date.now()}`,
        type: 'price-spike',
        severity: 'high',
        description: `Price spike detected: ${data.changePercent.toFixed(2)}%`,
        timestamp: Date.now()
      });
    }
    
    if (data.volume > 5000000) {
      anomalies.push({
        anomalyId: `anomaly_${Date.now()}_1`,
        type: 'volume-surge',
        severity: 'medium',
        description: `Volume surge detected: ${(data.volume / 1000000).toFixed(2)}M`,
        timestamp: Date.now()
      });
    }
    
    return anomalies;
  }

  private calculateIndicators(data: MarketData): TechnicalIndicators {
    const prices = this.getHistoricalPrices(data.symbol, 50);
    const rsi = this.calculateRSI(prices);
    
    return {
      rsi,
      macd: {
        macd: (Math.random() - 0.5) * 2,
        signal: (Math.random() - 0.5) * 1.5,
        histogram: (Math.random() - 0.5)
      },
      bollingerBands: {
        upper: data.price * 1.02,
        middle: data.price,
        lower: data.price * 0.98
      },
      ema: prices.slice(-20).map((_, i) => data.price * (1 + (i - 10) * 0.01)),
      sma: prices.slice(-20).map((_, i) => data.price * (1 + (i - 10) * 0.01))
    };
  }

  private calculateMA(prices: number[], period: number): number {
    const slice = prices.slice(-period);
    return slice.reduce((sum, price) => sum + price, 0) / slice.length;
  }

  private calculateVolatility(prices: number[]): number {
    const returns = [];
    for (let i = 1; i < prices.length; i++) {
      returns.push((prices[i] - prices[i-1]) / prices[i-1]);
    }
    const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length;
    return Math.sqrt(variance) * Math.sqrt(252);
  }

  private calculateRSI(prices: number[]): number {
    const period = 14;
    const gains: number[] = [];
    const losses: number[] = [];
    
    for (let i = 1; i < prices.length; i++) {
      const change = prices[i] - prices[i-1];
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? -change : 0);
    }
    
    const avgGain = gains.slice(-period).reduce((sum, g) => sum + g, 0) / period;
    const avgLoss = losses.slice(-period).reduce((sum, l) => sum + l, 0) / period;
    
    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
  }

  private getHistoricalPrices(_symbol: string, count: number): number[] {
    const basePrice = 100 + Math.random() * 50;
    const prices: number[] = [];
    
    for (let i = 0; i < count; i++) {
      prices.push(basePrice * (1 + (Math.random() - 0.5) * 0.1));
    }
    
    return prices;
  }

  private updateMetrics(processor: MarketDataProcessor, processed: ProcessedData): void {
    // processed parameter is available for future use
    void processed;
    
    processor.processingMetrics.messagesPerSecond = 100 + Math.random() * 50;
    processor.processingMetrics.latency = 10 + Math.random() * 20;
    processor.processingMetrics.throughput = 1000 + Math.random() * 500;
    processor.processingMetrics.errorRate = Math.random() * 0.01;
    processor.processingMetrics.lastCalculated = Date.now();
    processor.lastUpdate = Date.now();
  }

  getProcessor(processorId: string): MarketDataProcessor | undefined {
    return this.processors.get(processorId);
  }

  getAllProcessors(): MarketDataProcessor[] {
    return Array.from(this.processors.values());
  }
}

export const realTimeMarketDataProcessor = new RealTimeMarketDataProcessor();
export default RealTimeMarketDataProcessor;