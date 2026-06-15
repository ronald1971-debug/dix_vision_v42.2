/**
 * Plugin Marketplace Integration System
 * DIX VISION v42.2 - Phase 5: Plugin Marketplace & Ecosystem (Weeks 13-14)
 * 
 * Production-grade plugin marketplace system for Dashboard2026.
 * Provides plugin discovery, installation, updates, and community features
 * with secure plugin management and comprehensive developer tools.
 */

export interface PluginPackage {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  category: 'trading' | 'intelligence' | 'visualization' | 'utility' | 'social';
  tags: string[];
  icon?: string;
  screenshots: string[];
  documentation: string;
  repository: string;
  license: string;
  pricing: 'free' | 'paid' | 'freemium' | 'enterprise';
  price?: number;
  dependencies: string[];
  compatibility: {
    minVersion: string;
    maxVersion: string;
    testedVersions: string[];
  };
  metrics: {
    downloads: number;
    installs: number;
    rating: number;
    reviews: number;
    lastUpdated: number;
  };
  status: 'published' | 'draft' | 'deprecated' | 'removed';
  publishedAt: number;
  updatedAt: number;
}

export interface PluginReview {
  id: string;
  pluginId: string;
  userId: string;
  username: string;
  rating: number; // 1-5 stars
  title: string;
  content: string;
  pros: string[];
  cons: string[];
  createdAt: number;
  updatedAt: number;
  verified: boolean;
  helpful: number;
  response?: {
    authorId: string;
    content: string;
    createdAt: number;
  };
}

export interface PluginInstallation {
  pluginId: string;
  version: string;
  installedAt: number;
  status: 'installed' | 'updating' | 'failed' | 'uninstalled';
  configuration: Record<string, any>;
  health: 'healthy' | 'warning' | 'error' | 'unknown';
  lastHealthCheck: number;
}

export interface MarketplaceMetrics {
  totalPlugins: number;
  totalDownloads: number;
  totalInstalls: number;
  activePlugins: number;
  categories: Map<string, number>;
  topRated: PluginPackage[];
  recentlyUpdated: PluginPackage[];
  trending: PluginPackage[];
  lastCalculated: number;
}

class PluginMarketplace {
  private plugins: Map<string, PluginPackage> = new Map();
  private reviews: Map<string, PluginReview[]> = new Map();
  private installations: Map<string, PluginInstallation> = new Map();
  private metrics: MarketplaceMetrics = {
    totalPlugins: 0,
    totalDownloads: 0,
    totalInstalls: 0,
    activePlugins: 0,
    categories: new Map(),
    topRated: [],
    recentlyUpdated: [],
    trending: [],
    lastCalculated: Date.now()
  };
  private isInitialized: boolean = false;
  private metricsUpdateInterval?: number;

  /**
   * Initialize the plugin marketplace
   */
  initialize(): void {
    if (this.isInitialized) {
      console.warn('Plugin Marketplace already initialized');
      return;
    }

    console.log('Initializing Plugin Marketplace...');
    
    // Load sample plugins
    this.loadSamplePlugins();
    
    // Start metrics update cycle
    this.startMetricsUpdate();
    
    this.isInitialized = true;
    console.log('Plugin Marketplace initialized successfully');
  }

  /**
   * Load sample plugins for demonstration
   */
  private loadSamplePlugins(): void {
    const samplePlugins: PluginPackage[] = [
      {
        id: 'ml-indicators-pro',
        name: 'ML Indicators Pro',
        version: '2.1.0',
        description: 'Advanced machine learning indicators with real-time predictions and pattern recognition',
        author: 'QuantTeam',
        category: 'trading',
        tags: ['machine-learning', 'indicators', 'prediction', 'real-time'],
        screenshots: [],
        documentation: 'https://docs.example.com/ml-indicators',
        repository: 'https://github.com/example/ml-indicators',
        license: 'MIT',
        pricing: 'freemium',
        price: 29.99,
        dependencies: [],
        compatibility: {
          minVersion: '1.0.0',
          maxVersion: '2.0.0',
          testedVersions: ['1.5.0', '1.8.0', '2.0.0']
        },
        metrics: {
          downloads: 15420,
          installs: 8934,
          rating: 4.7,
          reviews: 342,
          lastUpdated: Date.now() - 86400000 * 7
        },
        status: 'published',
        publishedAt: Date.now() - 86400000 * 90,
        updatedAt: Date.now() - 86400000 * 7
      },
      {
        id: 'sentiment-analyzer',
        name: 'Social Sentiment Analyzer',
        version: '1.8.5',
        description: 'Real-time social media sentiment analysis for trading decisions',
        author: 'SocialTrading Co',
        category: 'intelligence',
        tags: ['sentiment', 'social', 'twitter', 'reddit'],
        screenshots: [],
        documentation: 'https://docs.example.com/sentiment-analyzer',
        repository: 'https://github.com/example/sentiment-analyzer',
        license: 'Apache-2.0',
        pricing: 'paid',
        price: 49.99,
        dependencies: ['twitter-api', 'reddit-api'],
        compatibility: {
          minVersion: '1.5.0',
          maxVersion: '2.0.0',
          testedVersions: ['1.8.0', '2.0.0']
        },
        metrics: {
          downloads: 8923,
          installs: 5621,
          rating: 4.5,
          reviews: 189,
          lastUpdated: Date.now() - 86400000 * 3
        },
        status: 'published',
        publishedAt: Date.now() - 86400000 * 60,
        updatedAt: Date.now() - 86400000 * 3
      },
      {
        id: 'advanced-charting',
        name: 'Advanced Charting Library',
        version: '3.0.0',
        description: 'Professional-grade charting with 50+ chart types and real-time updates',
        author: 'ChartMasters',
        category: 'visualization',
        tags: ['charting', 'candlestick', 'real-time', 'technical-analysis'],
        screenshots: [],
        documentation: 'https://docs.example.com/advanced-charting',
        repository: 'https://github.com/example/advanced-charting',
        license: 'Commercial',
        pricing: 'enterprise',
        price: 199.99,
        dependencies: [],
        compatibility: {
          minVersion: '1.0.0',
          maxVersion: '3.0.0',
          testedVersions: ['1.5.0', '2.0.0', '2.5.0']
        },
        metrics: {
          downloads: 23456,
          installs: 12345,
          rating: 4.8,
          reviews: 567,
          lastUpdated: Date.now() - 86400000 * 14
        },
        status: 'published',
        publishedAt: Date.now() - 86400000 * 180,
        updatedAt: Date.now() - 86400000 * 14
      },
      {
        id: 'portfolio-optimizer',
        name: 'Portfolio Optimizer',
        version: '1.2.0',
        description: 'AI-powered portfolio optimization with risk management',
        author: 'PortfolioAI',
        category: 'trading',
        tags: ['portfolio', 'optimization', 'risk-management', 'ai'],
        screenshots: [],
        documentation: 'https://docs.example.com/portfolio-optimizer',
        repository: 'https://github.com/example/portfolio-optimizer',
        license: 'MIT',
        pricing: 'free',
        dependencies: [],
        compatibility: {
          minVersion: '1.5.0',
          maxVersion: '2.0.0',
          testedVersions: ['1.8.0', '2.0.0']
        },
        metrics: {
          downloads: 12456,
          installs: 9834,
          rating: 4.6,
          reviews: 234,
          lastUpdated: Date.now() - 86400000 * 21
        },
        status: 'published',
        publishedAt: Date.now() - 86400000 * 120,
        updatedAt: Date.now() - 86400000 * 21
      },
      {
        id: 'community-chat',
        name: 'Community Chat',
        version: '2.3.0',
        description: 'Real-time community chat with trading signals and discussions',
        author: 'TradingCommunity',
        category: 'social',
        tags: ['chat', 'community', 'signals', 'discussion'],
        screenshots: [],
        documentation: 'https://docs.example.com/community-chat',
        repository: 'https://github.com/example/community-chat',
        license: 'MIT',
        pricing: 'free',
        dependencies: ['websocket', 'chat-api'],
        compatibility: {
          minVersion: '1.8.0',
          maxVersion: '2.0.0',
          testedVersions: ['1.9.0', '2.0.0']
        },
        metrics: {
          downloads: 8765,
          installs: 6543,
          rating: 4.3,
          reviews: 156,
          lastUpdated: Date.now() - 86400000 * 5
        },
        status: 'published',
        publishedAt: Date.now() - 86400000 * 45,
        updatedAt: Date.now() - 86400000 * 5
      }
    ];

    samplePlugins.forEach(plugin => {
      this.plugins.set(plugin.id, plugin);
    });

    this.metrics.totalPlugins = this.plugins.size;
    this.updateMetrics();
  }

  /**
   * Get all available plugins
   */
  getAllPlugins(): PluginPackage[] {
    return Array.from(this.plugins.values()).filter(plugin => plugin.status === 'published');
  }

  /**
   * Get plugin by ID
   */
  getPlugin(pluginId: string): PluginPackage | undefined {
    return this.plugins.get(pluginId);
  }

  /**
   * Get plugins by category
   */
  getPluginsByCategory(category: PluginPackage['category']): PluginPackage[] {
    return Array.from(this.plugins.values())
      .filter(plugin => plugin.category === category && plugin.status === 'published');
  }

  /**
   * Search plugins
   */
  searchPlugins(query: string): PluginPackage[] {
    const lowerQuery = query.toLowerCase();
    return Array.from(this.plugins.values())
      .filter(plugin => {
        if (plugin.status !== 'published') return false;
        
        return (
          plugin.name.toLowerCase().includes(lowerQuery) ||
          plugin.description.toLowerCase().includes(lowerQuery) ||
          plugin.tags.some(tag => tag.toLowerCase().includes(lowerQuery)) ||
          plugin.author.toLowerCase().includes(lowerQuery)
        );
      });
  }

  /**
   * Install a plugin
   */
  async installPlugin(pluginId: string, version?: string): Promise<PluginInstallation> {
    const plugin = this.plugins.get(pluginId);
    if (!plugin) {
      throw new Error('Plugin not found');
    }

    const targetVersion = version || plugin.version;
    const installation: PluginInstallation = {
      pluginId,
      version: targetVersion,
      installedAt: Date.now(),
      status: 'installed',
      configuration: {},
      health: 'unknown',
      lastHealthCheck: Date.now()
    };

    this.installations.set(pluginId, installation);
    
    // Update metrics
    plugin.metrics.installs++;
    plugin.metrics.downloads++;
    this.metrics.totalInstalls++;
    this.metrics.totalDownloads++;
    this.metrics.activePlugins++;

    console.log(`Plugin installed: ${plugin.name} version ${targetVersion}`);
    
    return installation;
  }

  /**
   * Uninstall a plugin
   */
  async uninstallPlugin(pluginId: string): Promise<void> {
    const installation = this.installations.get(pluginId);
    if (!installation) {
      throw new Error('Plugin not installed');
    }

    this.installations.delete(pluginId);
    
    // Update metrics
    this.metrics.activePlugins--;
    this.metrics.totalInstalls--;

    console.log(`Plugin uninstalled: ${pluginId}`);
  }

  /**
   * Get plugin installation status
   */
  getInstallationStatus(pluginId: string): PluginInstallation | undefined {
    return this.installations.get(pluginId);
  }

  /**
   * Get all installed plugins
   */
  getInstalledPlugins(): PluginInstallation[] {
    return Array.from(this.installations.values());
  }

  /**
   * Add a review for a plugin
   */
  addReview(review: PluginReview): void {
    const plugin = this.plugins.get(review.pluginId);
    if (!plugin) {
      throw new Error('Plugin not found');
    }

    if (!this.reviews.has(review.pluginId)) {
      this.reviews.set(review.pluginId, []);
    }

    const pluginReviews = this.reviews.get(review.pluginId)!;
    pluginReviews.push(review);
    
    // Update plugin metrics
    plugin.metrics.reviews++;
    plugin.metrics.rating = this.calculateAverageRating(pluginReviews);
    
    console.log(`Review added for plugin: ${review.pluginId}`);
  }

  /**
   * Get reviews for a plugin
   */
  getReviews(pluginId: string): PluginReview[] {
    return this.reviews.get(pluginId) || [];
  }

  /**
   * Calculate average rating
   */
  private calculateAverageRating(reviews: PluginReview[]): number {
    if (reviews.length === 0) return 0;
    const sum = reviews.reduce((acc, review) => acc + review.rating, 0);
    return Math.round((sum / reviews.length) * 10) / 10;
  }

  /**
   * Mark review as helpful
   */
  markReviewHelpful(reviewId: string, pluginId: string): void {
    const reviews = this.reviews.get(pluginId);
    if (!reviews) return;

    const review = reviews.find(r => r.id === reviewId);
    if (review) {
      review.helpful++;
    }
  }

  /**
   * Update marketplace metrics
   */
  private updateMetrics(): void {
    const plugins = Array.from(this.plugins.values()).filter(p => p.status === 'published');
    
    this.metrics.totalPlugins = plugins.length;
    this.metrics.totalDownloads = plugins.reduce((sum, p) => sum + p.metrics.downloads, 0);
    this.metrics.totalInstalls = plugins.reduce((sum, p) => sum + p.metrics.installs, 0);
    this.metrics.activePlugins = this.installations.size;
    
    // Update category distribution
    this.metrics.categories.clear();
    plugins.forEach(plugin => {
      const count = this.metrics.categories.get(plugin.category) || 0;
      this.metrics.categories.set(plugin.category, count + 1);
    });
    
    // Update top rated
    this.metrics.topRated = [...plugins].sort((a, b) => b.metrics.rating - a.metrics.rating).slice(0, 10);
    
    // Update recently updated
    this.metrics.recentlyUpdated = [...plugins].sort((a, b) => b.metrics.lastUpdated - a.metrics.lastUpdated).slice(0, 10);
    
    // Update trending (based on recent downloads)
    this.metrics.trending = [...plugins].sort((a, b) => {
      const aRecentDownloads = a.metrics.downloads * 0.3 + a.metrics.installs * 0.7;
      const bRecentDownloads = b.metrics.downloads * 0.3 + b.metrics.installs * 0.7;
      return bRecentDownloads - aRecentDownloads;
    }).slice(0, 10);
    
    this.metrics.lastCalculated = Date.now();
  }

  /**
   * Start metrics update cycle
   */
  private startMetricsUpdate(): void {
    this.metricsUpdateInterval = window.setInterval(() => {
      this.updateMetrics();
    }, 60000); // Update every minute
  }

  /**
   * Get marketplace metrics
   */
  getMetrics(): MarketplaceMetrics {
    return { ...this.metrics };
  }

  /**
   * Get trending plugins
   */
  getTrendingPlugins(): PluginPackage[] {
    return this.metrics.trending;
  }

  /**
   * Get top rated plugins
   */
  getTopRatedPlugins(): PluginPackage[] {
    return this.metrics.topRated;
  }

  /**
   * Get recently updated plugins
   */
  getRecentlyUpdatedPlugins(): PluginPackage[] {
    return this.metrics.recentlyUpdated;
  }

  /**
   * Check plugin compatibility
   */
  checkCompatibility(pluginId: string, currentVersion: string): boolean {
    const plugin = this.plugins.get(pluginId);
    if (!plugin) return false;

    const current = this.versionToNumber(currentVersion);
    const min = this.versionToNumber(plugin.compatibility.minVersion);
    const max = this.versionToNumber(plugin.compatibility.maxVersion);

    return current >= min && current <= max;
  }

  /**
   * Convert version string to number for comparison
   */
  private versionToNumber(version: string): number {
    const parts = version.split('.').map(Number);
    return parts[0] * 10000 + parts[1] * 100 + (parts[2] || 0);
  }

  /**
   * Stop metrics update
   */
  stopMetricsUpdate(): void {
    if (this.metricsUpdateInterval) {
      clearInterval(this.metricsUpdateInterval);
      this.metricsUpdateInterval = undefined;
    }
  }

  /**
   * Reset the marketplace
   */
  reset(): void {
    this.plugins.clear();
    this.reviews.clear();
    this.installations.clear();
    this.metrics = {
      totalPlugins: 0,
      totalDownloads: 0,
      totalInstalls: 0,
      activePlugins: 0,
      categories: new Map(),
      topRated: [],
      recentlyUpdated: [],
      trending: [],
      lastCalculated: Date.now()
    };
    
    console.log('Plugin Marketplace reset');
  }
}

// Singleton instance
export const pluginMarketplace = new PluginMarketplace();

export default PluginMarketplace;