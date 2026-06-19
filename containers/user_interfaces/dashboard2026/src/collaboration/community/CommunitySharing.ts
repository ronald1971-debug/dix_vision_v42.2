/**
 * Community & Sharing Features - Phase 16
 * DIX VISION v42.2 - Phase 16: Collaboration & Social Features (Weeks 51-54)
 * 
 * This module implements community and sharing features including:
 * - Strategy sharing and publishing
 * - Performance leaderboards
 * - Community discussion forums
 * - Strategy following and copying
 * - Collaborative research environments
 * - Knowledge base and wiki
 * - Asset class-specific communities
 */

export interface StrategyPublication {
  strategyId: string;
  authorId: string;
  authorName: string;
  authorAvatar?: string;
  title: string;
  description: string;
  strategyCode: string;
  assetClasses: string[];
  tags: string[];
  publishDate: number;
  lastModified: number;
  version: number;
  status: 'draft' | 'published' | 'archived' | 'deleted';
  visibility: 'public' | 'private' | 'restricted';
  permissions: string[];
  metrics: StrategyMetrics;
  reviews: StrategyReview[];
  followers: number;
  isVerified: boolean;
}

export interface StrategyMetrics {
  totalViews: number;
  uniqueViews: number;
  totalDownloads: number;
  totalCopies: number;
  averageRating: number;
  ratingCount: number;
  sharpeRatio: number;
  maxDrawdown: number;
  annualReturn: number;
  volatility: number;
  winRate: number;
  profitFactor: number;
  lastUpdated: number;
}

export interface StrategyReview {
  reviewId: string;
  strategyId: string;
  reviewerId: string;
  reviewerName: string;
  rating: number;
  title: string;
  content: string;
  helpfulVotes: number;
  createdAt: number;
  lastModified: number;
}

export interface CommunityLeaderboard {
  leaderboardId: string;
  name: string;
  description: string;
  assetClass: string;
  period: 'daily' | 'weekly' | 'monthly' | 'yearly' | 'all-time';
  metrics: LeaderboardMetrics;
  entries: LeaderboardEntry[];
  lastUpdated: number;
  isActive: boolean;
}

export interface LeaderboardMetrics {
  sortBy: 'return' | 'sharpe' | 'winrate' | 'profit' | 'consistency';
  minValue?: number;
  maxValue?: number;
  excludeStrategy?: string[];
  assetClassFilter?: string[];
}

export interface LeaderboardEntry {
  entryId: string;
  userId: string;
  username: string;
  avatar?: string;
  rank: number;
  value: number;
  change: number;
  strategyId?: string;
  strategyName?: string;
  badge?: string;
  streak?: number;
}

export interface CommunityForum {
  forumId: string;
  name: string;
  description: string;
  category: string;
  assetClass?: string;
  moderators: string[];
  memberCount: number;
  threadCount: number;
  postCount: number;
  rules: ForumRule[];
  createdAt: number;
  lastActivity: number;
}

export interface ForumRule {
  ruleId: string;
  title: string;
  description: string;
  enforce: boolean;
  penalty?: string;
}

export interface ForumThread {
  threadId: string;
  forumId: string;
  authorId: string;
  authorName: string;
  authorAvatar?: string;
  title: string;
  content: string;
  tags: string[];
  category: string;
  isPinned: boolean;
  isLocked: boolean;
  isAnswered: boolean;
  viewCount: number;
  replyCount: number;
  voteCount: number;
  createdAt: number;
  lastModified: number;
  lastActivity: number;
  answers: ForumReply[];
}

export interface ForumReply {
  replyId: string;
  threadId: string;
  authorId: string;
  authorName: string;
  authorAvatar?: string;
  content: string;
  voteCount: number;
  isAccepted: boolean;
  createdAt: number;
  lastModified: number;
}

export interface StrategyFollowing {
  followingId: string;
  userId: string;
  strategyId: string;
  strategyName: string;
  authorId: string;
  authorName: string;
  followDate: number;
  autoCopyEnabled: boolean;
  copySettings: CopySettings;
  notifications: boolean;
  performance: FollowingPerformance;
}

export interface CopySettings {
  positionSizeType: 'fixed' | 'percentage' | 'risk-parity';
  positionSize: number;
  maxPositionSize?: number;
  stopLossPercentage?: number;
  takeProfitPercentage?: number;
  maxDailyTrades?: number;
  assetClassFilter?: string[];
  reverseSignals?: boolean;
  timeFilter?: TimeFilter;
}

export interface TimeFilter {
  enabled: boolean;
  tradingHours: TradingHours[];
  timezone: string;
}

export interface TradingHours {
  day: number; // 0-6 (Sunday-Saturday)
  startHour: number;
  endHour: number;
}

export interface FollowingPerformance {
  totalCopied: number;
  successfulCopies: number;
  totalProfit: number;
  totalLoss: number;
  winRate: number;
  averageReturn: number;
  lastUpdated: number;
}

export interface CollaborativeResearch {
  researchId: string;
  title: string;
  description: string;
  ownerId: string;
  ownerName: string;
  collaborators: Collaborator[];
  researchType: 'backtest' | 'analysis' | 'optimization' | 'paper';
  assetClasses: string[];
  status: 'draft' | 'in-progress' | 'completed' | 'published';
  createdAt: number;
  lastModified: number;
  data: ResearchData;
  conclusions: ResearchConclusion[];
  publications: ResearchPublication[];
}

export interface Collaborator {
  userId: string;
  username: string;
  role: 'owner' | 'editor' | 'viewer' | 'commenter';
  permissions: string[];
  joinedAt: number;
  lastActivity: number;
}

export interface ResearchData {
  dataSources: string[];
  parameters: Record<string, any>;
  results: Record<string, any>;
  charts: ChartData[];
  notes: string[];
}

export interface ChartData {
  chartId: string;
  title: string;
  type: string;
  data: any[];
  settings: Record<string, any>;
}

export interface ResearchConclusion {
  conclusionId: string;
  authorId: string;
  authorName: string;
  title: string;
  content: string;
  confidence: number;
  supportingData: string[];
  createdAt: number;
}

export interface ResearchPublication {
  publicationId: string;
  title: string;
  venue: string;
  url: string;
  publishDate: number;
  doi?: string;
}

export interface KnowledgeBase {
  knowledgeBaseId: string;
  name: string;
  description: string;
  category: string;
  articles: KnowledgeArticle[];
  categories: KnowledgeCategory[];
  contributors: string[];
  viewCount: number;
  searchCount: number;
  lastUpdated: number;
}

export interface KnowledgeArticle {
  articleId: string;
  title: string;
  slug: string;
  content: string;
  authorId: string;
  authorName: string;
  category: string;
  tags: string[];
  status: 'draft' | 'published' | 'archived';
  viewCount: number;
  helpfulVotes: number;
  relatedArticles: string[];
  createdAt: number;
  lastModified: number;
  lastReviewed: number;
}

export interface KnowledgeCategory {
  categoryId: string;
  name: string;
  slug: string;
  description: string;
  parentId?: string;
  order: number;
  articleCount: number;
}

export interface AssetClassCommunity {
  communityId: string;
  assetClass: string;
  name: string;
  description: string;
  icon: string;
  bannerImage?: string;
  memberCount: number;
  onlineCount: number;
  activeCount: number;
  moderators: string[];
  features: CommunityFeature[];
  resources: CommunityResource[];
  topContributors: Contributor[];
  discussions: string[];
  createdAt: number;
  lastActivity: number;
}

export interface CommunityFeature {
  featureId: string;
  name: string;
  description: string;
  enabled: boolean;
}

export interface CommunityResource {
  resourceId: string;
  title: string;
  description: string;
  type: 'guide' | 'tutorial' | 'tool' | 'indicator' | 'strategy';
  url: string;
  authorId: string;
  authorName: string;
  rating: number;
  downloads: number;
  createdAt: number;
}

export interface Contributor {
  userId: string;
  username: string;
  avatar?: string;
  contributionScore: number;
  strategies: number;
  posts: number;
  helpfulVotes: number;
  badge?: string;
}

export interface CommunitySharingSystem {
  strategies: Map<string, StrategyPublication>;
  leaderboards: Map<string, CommunityLeaderboard>;
  forums: Map<string, CommunityForum>;
  threads: Map<string, ForumThread>;
  followings: Map<string, StrategyFollowing>;
  research: Map<string, CollaborativeResearch>;
  knowledgeBases: Map<string, KnowledgeBase>;
  assetCommunities: Map<string, AssetClassCommunity>;
  config: CommunityConfig;
  lastUpdated: number;
}

export interface CommunityConfig {
  enableStrategySharing: boolean;
  enableLeaderboards: boolean;
  enableForums: boolean;
  enableFollowing: boolean;
  enableResearch: boolean;
  enableKnowledgeBase: boolean;
  enableAssetCommunities: boolean;
  moderationEnabled: boolean;
  autoModerationRules: string[];
  contentFiltering: boolean;
  reputationSystem: boolean;
  maxStrategiesPerUser: number;
  maxForumPosts: number;
  maxFollowers: number;
}

export class CommunitySharingSystemImplementation {
  private system: CommunitySharingSystem;

  constructor() {
    this.system = {
      strategies: new Map(),
      leaderboards: new Map(),
      forums: new Map(),
      threads: new Map(),
      followings: new Map(),
      research: new Map(),
      knowledgeBases: new Map(),
      assetCommunities: new Map(),
      config: {
        enableStrategySharing: true,
        enableLeaderboards: true,
        enableForums: true,
        enableFollowing: true,
        enableResearch: true,
        enableKnowledgeBase: true,
        enableAssetCommunities: true,
        moderationEnabled: true,
        autoModerationRules: [],
        contentFiltering: true,
        reputationSystem: true,
        maxStrategiesPerUser: 50,
        maxForumPosts: 1000,
        maxFollowers: 500
      },
      lastUpdated: Date.now()
    };
  }

  initialize(): void {
    this.loadDefaultCommunities();
    this.loadDefaultForums();
    this.loadDefaultLeaderboards();
  }

  getConfig(): CommunityConfig {
    return this.system.config;
  }

  updateConfig(config: Partial<CommunityConfig>): void {
    this.system.config = { ...this.system.config, ...config };
    this.system.lastUpdated = Date.now();
  }

  // Strategy Sharing Methods
  async publishStrategy(userId: string, strategy: Omit<StrategyPublication, 'strategyId' | 'authorId' | 'publishDate' | 'lastModified' | 'metrics' | 'reviews' | 'followers' | 'isVerified'>): Promise<StrategyPublication> {
    const publication: StrategyPublication = {
      ...strategy,
      strategyId: `strategy_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      authorId: userId,
      publishDate: Date.now(),
      lastModified: Date.now(),
      metrics: {
        totalViews: 0,
        uniqueViews: 0,
        totalDownloads: 0,
        totalCopies: 0,
        averageRating: 0,
        ratingCount: 0,
        sharpeRatio: 0,
        maxDrawdown: 0,
        annualReturn: 0,
        volatility: 0,
        winRate: 0,
        profitFactor: 0,
        lastUpdated: Date.now()
      },
      reviews: [],
      followers: 0,
      isVerified: false
    };
    
    this.system.strategies.set(publication.strategyId, publication);
    this.system.lastUpdated = Date.now();
    return publication;
  }

  getStrategy(strategyId: string): StrategyPublication | undefined {
    return this.system.strategies.get(strategyId);
  }

  getStrategiesByAuthor(authorId: string): StrategyPublication[] {
    return Array.from(this.system.strategies.values()).filter(s => s.authorId === authorId);
  }

  searchStrategies(query: string, filters?: { assetClass?: string; tags?: string[]; status?: string }): StrategyPublication[] {
    let results = Array.from(this.system.strategies.values());
    
    if (query) {
      const lowerQuery = query.toLowerCase();
      results = results.filter(s => 
        s.title.toLowerCase().includes(lowerQuery) ||
        s.description.toLowerCase().includes(lowerQuery) ||
        s.tags.some(t => t.toLowerCase().includes(lowerQuery))
      );
    }
    
    if (filters?.assetClass) {
      results = results.filter(s => s.assetClasses.includes(filters.assetClass!));
    }
    
    if (filters?.tags?.length) {
      results = results.filter(s => filters.tags!.some(t => s.tags.includes(t)));
    }
    
    if (filters?.status) {
      results = results.filter(s => s.status === filters.status);
    }
    
    return results.sort((a, b) => b.publishDate - a.publishDate);
  }

  async updateStrategyMetrics(strategyId: string, metrics: Partial<StrategyMetrics>): Promise<void> {
    const strategy = this.system.strategies.get(strategyId);
    if (strategy) {
      strategy.metrics = { ...strategy.metrics, ...metrics, lastUpdated: Date.now() };
      this.system.lastUpdated = Date.now();
    }
  }

  async addStrategyReview(review: Omit<StrategyReview, 'reviewId' | 'createdAt' | 'lastModified'>): Promise<StrategyReview> {
    const newReview: StrategyReview = {
      ...review,
      reviewId: `review_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: Date.now(),
      lastModified: Date.now()
    };
    
    const strategy = this.system.strategies.get(review.strategyId);
    if (strategy) {
      strategy.reviews.push(newReview);
      this.updateStrategyRating(review.strategyId);
      this.system.lastUpdated = Date.now();
    }
    
    return newReview;
  }

  private updateStrategyRating(strategyId: string): void {
    const strategy = this.system.strategies.get(strategyId);
    if (strategy && strategy.reviews.length > 0) {
      const totalRating = strategy.reviews.reduce((sum, r) => sum + r.rating, 0);
      strategy.metrics.averageRating = totalRating / strategy.reviews.length;
      strategy.metrics.ratingCount = strategy.reviews.length;
    }
  }

  // Leaderboard Methods
  async createLeaderboard(leaderboard: Omit<CommunityLeaderboard, 'leaderboardId' | 'entries' | 'lastUpdated' | 'isActive'>): Promise<CommunityLeaderboard> {
    const newLeaderboard: CommunityLeaderboard = {
      ...leaderboard,
      leaderboardId: `leaderboard_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      entries: [],
      lastUpdated: Date.now(),
      isActive: true
    };
    
    this.system.leaderboards.set(newLeaderboard.leaderboardId, newLeaderboard);
    this.system.lastUpdated = Date.now();
    return newLeaderboard;
  }

  getLeaderboard(leaderboardId: string): CommunityLeaderboard | undefined {
    return this.system.leaderboards.get(leaderboardId);
  }

  getLeaderboardsByAssetClass(assetClass: string): CommunityLeaderboard[] {
    return Array.from(this.system.leaderboards.values()).filter(l => l.assetClass === assetClass);
  }

  async updateLeaderboardEntries(leaderboardId: string, entries: LeaderboardEntry[]): Promise<void> {
    const leaderboard = this.system.leaderboards.get(leaderboardId);
    if (leaderboard) {
      leaderboard.entries = entries;
      leaderboard.lastUpdated = Date.now();
      this.system.lastUpdated = Date.now();
    }
  }

  // Forum Methods
  async createForum(forum: Omit<CommunityForum, 'forumId' | 'memberCount' | 'threadCount' | 'postCount' | 'createdAt' | 'lastActivity'>): Promise<CommunityForum> {
    const newForum: CommunityForum = {
      ...forum,
      forumId: `forum_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      memberCount: 0,
      threadCount: 0,
      postCount: 0,
      createdAt: Date.now(),
      lastActivity: Date.now()
    };
    
    this.system.forums.set(newForum.forumId, newForum);
    this.system.lastUpdated = Date.now();
    return newForum;
  }

  getForum(forumId: string): CommunityForum | undefined {
    return this.system.forums.get(forumId);
  }

  getForumsByCategory(category: string): CommunityForum[] {
    return Array.from(this.system.forums.values()).filter(f => f.category === category);
  }

  async createThread(thread: Omit<ForumThread, 'threadId' | 'viewCount' | 'replyCount' | 'voteCount' | 'createdAt' | 'lastModified' | 'lastActivity' | 'answers'>): Promise<ForumThread> {
    const newThread: ForumThread = {
      ...thread,
      threadId: `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      viewCount: 0,
      replyCount: 0,
      voteCount: 0,
      createdAt: Date.now(),
      lastModified: Date.now(),
      lastActivity: Date.now(),
      answers: []
    };
    
    this.system.threads.set(newThread.threadId, newThread);
    
    const forum = this.system.forums.get(thread.forumId);
    if (forum) {
      forum.threadCount++;
      forum.lastActivity = Date.now();
    }
    
    this.system.lastUpdated = Date.now();
    return newThread;
  }

  getThread(threadId: string): ForumThread | undefined {
    return this.system.threads.get(threadId);
  }

  getThreadsByForum(forumId: string): ForumThread[] {
    return Array.from(this.system.threads.values()).filter(t => t.forumId === forumId);
  }

  async addReply(reply: Omit<ForumReply, 'replyId' | 'createdAt' | 'lastModified'>): Promise<ForumReply> {
    const newReply: ForumReply = {
      ...reply,
      replyId: `reply_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: Date.now(),
      lastModified: Date.now()
    };
    
    const thread = this.system.threads.get(reply.threadId);
    if (thread) {
      thread.answers.push(newReply);
      thread.replyCount++;
      thread.lastModified = Date.now();
      thread.lastActivity = Date.now();
      
      const forum = this.system.forums.get(thread.forumId);
      if (forum) {
        forum.postCount++;
        forum.lastActivity = Date.now();
      }
      
      this.system.lastUpdated = Date.now();
    }
    
    return newReply;
  }

  // Strategy Following Methods
  async followStrategy(userId: string, strategyId: string, copySettings?: Partial<CopySettings>): Promise<StrategyFollowing> {
    const strategy = this.system.strategies.get(strategyId);
    if (!strategy) {
      throw new Error('Strategy not found');
    }

    const followingId = `following_${userId}_${strategyId}`;
    const following: StrategyFollowing = {
      followingId,
      userId,
      strategyId,
      strategyName: strategy.title,
      authorId: strategy.authorId,
      authorName: strategy.authorName,
      followDate: Date.now(),
      autoCopyEnabled: !!copySettings,
      copySettings: copySettings ? { ...this.getDefaultCopySettings(), ...copySettings } : this.getDefaultCopySettings(),
      notifications: true,
      performance: {
        totalCopied: 0,
        successfulCopies: 0,
        totalProfit: 0,
        totalLoss: 0,
        winRate: 0,
        averageReturn: 0,
        lastUpdated: Date.now()
      }
    };
    
    this.system.followings.set(followingId, following);
    
    strategy.followers++;
    this.system.lastUpdated = Date.now();
    
    return following;
  }

  unfollowStrategy(userId: string, strategyId: string): void {
    const followingId = `following_${userId}_${strategyId}`;
    this.system.followings.delete(followingId);
    
    const strategy = this.system.strategies.get(strategyId);
    if (strategy && strategy.followers > 0) {
      strategy.followers--;
    }
    
    this.system.lastUpdated = Date.now();
  }

  getUserFollowings(userId: string): StrategyFollowing[] {
    return Array.from(this.system.followings.values()).filter(f => f.userId === userId);
  }

  getStrategyFollowers(strategyId: string): StrategyFollowing[] {
    return Array.from(this.system.followings.values()).filter(f => f.strategyId === strategyId);
  }

  private getDefaultCopySettings(): CopySettings {
    return {
      positionSizeType: 'percentage',
      positionSize: 10,
      stopLossPercentage: 5,
      takeProfitPercentage: 10,
      timeFilter: {
        enabled: false,
        tradingHours: [],
        timezone: 'UTC'
      }
    };
  }

  // Collaborative Research Methods
  async createResearch(research: Omit<CollaborativeResearch, 'researchId' | 'createdAt' | 'lastModified' | 'data' | 'conclusions' | 'publications'>): Promise<CollaborativeResearch> {
    const newResearch: CollaborativeResearch = {
      ...research,
      researchId: `research_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: Date.now(),
      lastModified: Date.now(),
      data: {
        dataSources: [],
        parameters: {},
        results: {},
        charts: [],
        notes: []
      },
      conclusions: [],
      publications: []
    };
    
    this.system.research.set(newResearch.researchId, newResearch);
    this.system.lastUpdated = Date.now();
    return newResearch;
  }

  getResearch(researchId: string): CollaborativeResearch | undefined {
    return this.system.research.get(researchId);
  }

  getUserResearch(userId: string): CollaborativeResearch[] {
    return Array.from(this.system.research.values()).filter(r => 
      r.ownerId === userId || r.collaborators.some(c => c.userId === userId)
    );
  }

  async addCollaborator(researchId: string, userId: string, role: Collaborator['role']): Promise<void> {
    const research = this.system.research.get(researchId);
    if (research) {
      research.collaborators.push({
        userId,
        username: '', // Will be filled in from user system
        role,
        permissions: this.getPermissionsByRole(role),
        joinedAt: Date.now(),
        lastActivity: Date.now()
      });
      research.lastModified = Date.now();
      this.system.lastUpdated = Date.now();
    }
  }

  private getPermissionsByRole(role: Collaborator['role']): string[] {
    switch (role) {
      case 'owner':
        return ['read', 'write', 'delete', 'manage', 'publish'];
      case 'editor':
        return ['read', 'write', 'publish'];
      case 'viewer':
        return ['read'];
      case 'commenter':
        return ['read', 'comment'];
      default:
        return [];
    }
  }

  // Knowledge Base Methods
  async createKnowledgeBase(kb: Omit<KnowledgeBase, 'knowledgeBaseId' | 'articles' | 'categories' | 'contributors' | 'viewCount' | 'searchCount' | 'lastUpdated'>): Promise<KnowledgeBase> {
    const newKB: KnowledgeBase = {
      ...kb,
      knowledgeBaseId: `kb_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      articles: [],
      categories: [],
      contributors: [],
      viewCount: 0,
      searchCount: 0,
      lastUpdated: Date.now()
    };
    
    this.system.knowledgeBases.set(newKB.knowledgeBaseId, newKB);
    this.system.lastUpdated = Date.now();
    return newKB;
  }

  getKnowledgeBase(kbId: string): KnowledgeBase | undefined {
    return this.system.knowledgeBases.get(kbId);
  }

  async createArticle(article: Omit<KnowledgeArticle, 'articleId' | 'viewCount' | 'helpfulVotes' | 'createdAt' | 'lastModified' | 'lastReviewed'>): Promise<KnowledgeArticle> {
    const newArticle: KnowledgeArticle = {
      ...article,
      articleId: `article_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      viewCount: 0,
      helpfulVotes: 0,
      createdAt: Date.now(),
      lastModified: Date.now(),
      lastReviewed: Date.now()
    };
    
    const kb = this.system.knowledgeBases.get(article.category); // Assuming category maps to KB
    if (kb) {
      kb.articles.push(newArticle);
      kb.lastUpdated = Date.now();
    }
    
    this.system.lastUpdated = Date.now();
    return newArticle;
  }

  searchArticles(query: string, category?: string): KnowledgeArticle[] {
    let results: KnowledgeArticle[] = [];
    
    this.system.knowledgeBases.forEach(kb => {
      if (!category || kb.category === category) {
        results = results.concat(kb.articles);
      }
    });
    
    if (query) {
      const lowerQuery = query.toLowerCase();
      results = results.filter(a => 
        a.title.toLowerCase().includes(lowerQuery) ||
        a.content.toLowerCase().includes(lowerQuery) ||
        a.tags.some(t => t.toLowerCase().includes(lowerQuery))
      );
    }
    
    return results.sort((a, b) => b.viewCount - a.viewCount);
  }

  // Asset Class Community Methods
  async createAssetClassCommunity(community: Omit<AssetClassCommunity, 'communityId' | 'memberCount' | 'onlineCount' | 'activeCount' | 'features' | 'resources' | 'topContributors' | 'discussions' | 'createdAt' | 'lastActivity'>): Promise<AssetClassCommunity> {
    const newCommunity: AssetClassCommunity = {
      ...community,
      communityId: `community_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      memberCount: 0,
      onlineCount: 0,
      activeCount: 0,
      features: [],
      resources: [],
      topContributors: [],
      discussions: [],
      createdAt: Date.now(),
      lastActivity: Date.now()
    };
    
    this.system.assetCommunities.set(newCommunity.communityId, newCommunity);
    this.system.lastUpdated = Date.now();
    return newCommunity;
  }

  getAssetClassCommunity(communityId: string): AssetClassCommunity | undefined {
    return this.system.assetCommunities.get(communityId);
  }

  getCommunityByAssetClass(assetClass: string): AssetClassCommunity | undefined {
    return Array.from(this.system.assetCommunities.values()).find(c => c.assetClass === assetClass);
  }

  private loadDefaultCommunities(): void {
    const defaultCommunities = [
      {
        assetClass: 'stocks',
        name: 'Stock Trading Community',
        description: 'Everything about stock trading strategies, analysis, and discussion',
        icon: '📈',
        moderators: ['admin']
      },
      {
        assetClass: 'forex',
        name: 'Forex Trading Community',
        description: 'Currency trading discussions and strategies',
        icon: '💱',
        moderators: ['admin']
      },
      {
        assetClass: 'crypto',
        name: 'Crypto Trading Community',
        description: 'Cryptocurrency trading and blockchain analysis',
        icon: '₿',
        moderators: ['admin']
      },
      {
        assetClass: 'futures',
        name: 'Futures Trading Community',
        description: 'Commodities and futures trading strategies',
        icon: '📊',
        moderators: ['admin']
      },
      {
        assetClass: 'options',
        name: 'Options Trading Community',
        description: 'Options strategies and Greeks analysis',
        icon: '🎯',
        moderators: ['admin']
      }
    ];

    defaultCommunities.forEach(c => this.createAssetClassCommunity(c));
  }

  private loadDefaultForums(): void {
    const defaultForums = [
      {
        name: 'Strategy Discussion',
        description: 'Share and discuss trading strategies',
        category: 'strategies',
        moderators: ['admin'],
        rules: []
      },
      {
        name: 'Technical Analysis',
        description: 'Technical analysis techniques and indicators',
        category: 'technical',
        moderators: ['admin'],
        rules: []
      },
      {
        name: 'Fundamental Analysis',
        description: 'Fundamental analysis and market research',
        category: 'fundamental',
        moderators: ['admin'],
        rules: []
      },
      {
        name: 'Trading Psychology',
        description: 'Trading psychology and risk management',
        category: 'psychology',
        moderators: ['admin'],
        rules: []
      },
      {
        name: 'Help & Support',
        description: 'Get help with trading and platform issues',
        category: 'support',
        moderators: ['admin'],
        rules: []
      }
    ];

    defaultForums.forEach(f => this.createForum(f));
  }

  private loadDefaultLeaderboards(): void {
    const assetClasses = ['stocks', 'forex', 'crypto', 'futures', 'options'];
    const periods: CommunityLeaderboard['period'][] = ['weekly', 'monthly', 'yearly', 'all-time'];

    assetClasses.forEach(assetClass => {
      periods.forEach(period => {
        this.createLeaderboard({
          name: `${assetClass.charAt(0).toUpperCase() + assetClass.slice(1)} ${period.charAt(0).toUpperCase() + period.slice(1)} Leaderboard`,
          description: `Top performers in ${assetClass} trading (${period})`,
          assetClass,
          period,
          metrics: {
            sortBy: 'return',
            assetClassFilter: [assetClass]
          }
        });
      });
    });
  }
}

export const communitySharingSystem = new CommunitySharingSystemImplementation();
export default CommunitySharingSystemImplementation;