/**
 * Community Plugin Support System
 * DIX VISION v42.2 - Phase 5: Plugin Marketplace & Ecosystem (Weeks 13-14)
 * 
 * Production-grade community plugin support system with developer collaboration,
 * version control, issue tracking, pull requests, and community governance.
 */

export interface PluginDeveloper {
  id: string;
  username: string;
  email: string;
  organization?: string;
  bio: string;
  plugins: string[];
  reputation: number;
  contributions: number;
  joinedAt: number;
  verified: boolean;
  avatar?: string;
}

export interface PluginRepository {
  pluginId: string;
  repositoryUrl: string;
  branch: string;
  commits: GitCommit[];
  issues: PluginIssue[];
  pullRequests: PullRequest[];
  contributors: PluginDeveloper[];
  lastUpdated: number;
}

export interface GitCommit {
  id: string;
  message: string;
  author: string;
  timestamp: number;
  changes: {
    files: number;
    additions: number;
    deletions: number;
  };
}

export interface PluginIssue {
  id: string;
  title: string;
  description: string;
  author: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  labels: string[];
  createdAt: number;
  updatedAt: number;
  comments: Comment[];
  assignee?: string;
}

export interface PullRequest {
  id: string;
  title: string;
  description: string;
  author: string;
  status: 'open' | 'merged' | 'closed' | 'rejected';
  baseBranch: string;
  headBranch: string;
  additions: number;
  deletions: number;
  files: number;
  createdAt: number;
  updatedAt: number;
  reviews: PRReview[];
  mergeCommit?: string;
}

export interface PRReview {
  reviewer: string;
  status: 'approved' | 'changes_requested' | 'commented' | 'pending';
  comments: string[];
  timestamp: number;
}

export interface Comment {
  author: string;
  content: string;
  timestamp: number;
  reactions: Reaction[];
}

export interface Reaction {
  emoji: string;
  count: number;
  users: string[];
}

export interface CommunityMetrics {
  totalDevelopers: number;
  totalRepositories: number;
  totalCommits: number;
  totalIssues: number;
  totalPullRequests: number;
  activeContributors: number;
  openIssues: number;
  mergedPRs: number;
  lastCalculated: number;
}

class CommunityPluginSupport {
  private developers: Map<string, PluginDeveloper> = new Map();
  private repositories: Map<string, PluginRepository> = new Map();
  private issues: Map<string, PluginIssue[]> = new Map();
  private pullRequests: Map<string, PullRequest[]> = new Map();
  private metrics: CommunityMetrics = {
    totalDevelopers: 0,
    totalRepositories: 0,
    totalCommits: 0,
    totalIssues: 0,
    totalPullRequests: 0,
    activeContributors: 0,
    openIssues: 0,
    mergedPRs: 0,
    lastCalculated: Date.now()
  };
  private isInitialized: boolean = false;
  private metricsUpdateInterval?: number;

  /**
   * Initialize community plugin support
   */
  initialize(): void {
    if (this.isInitialized) {
      console.warn('Community Plugin Support already initialized');
      return;
    }

    console.log('Initializing Community Plugin Support...');
    
    // Load sample developers and repositories
    this.loadSampleData();
    
    // Start metrics update cycle
    this.startMetricsUpdate();
    
    this.isInitialized = true;
    console.log('Community Plugin Support initialized successfully');
  }

  /**
   * Load sample data
   */
  private loadSampleData(): void {
    // Sample developers
    const sampleDevelopers: PluginDeveloper[] = [
      {
        id: 'dev1',
        username: 'quantdev',
        email: 'quantdev@example.com',
        organization: 'QuantLabs',
        bio: 'Machine learning engineer specializing in trading algorithms',
        plugins: ['ml-indicators-pro', 'portfolio-optimizer'],
        reputation: 850,
        contributions: 42,
        joinedAt: Date.now() - 86400000 * 365,
        verified: true
      },
      {
        id: 'dev2',
        username: 'chartmaster',
        email: 'chartmaster@example.com',
        organization: 'ChartMasters',
        bio: 'Frontend developer focused on data visualization',
        plugins: ['advanced-charting'],
        reputation: 720,
        contributions: 28,
        joinedAt: Date.now() - 86400000 * 180,
        verified: true
      },
      {
        id: 'dev3',
        username: 'socialtrader',
        email: 'social@example.com',
        bio: 'Community builder and social features developer',
        plugins: ['community-chat', 'sentiment-analyzer'],
        reputation: 650,
        contributions: 35,
        joinedAt: Date.now() - 86400000 * 120,
        verified: false
      }
    ];

    sampleDevelopers.forEach(dev => {
      this.developers.set(dev.id, dev);
    });

    // Sample repositories
    const sampleRepos: PluginRepository[] = [
      {
        pluginId: 'ml-indicators-pro',
        repositoryUrl: 'https://github.com/quantdev/ml-indicators-pro',
        branch: 'main',
        commits: this.generateSampleCommits(15),
        issues: this.generateSampleIssues(8),
        pullRequests: this.generateSamplePRs(5),
        contributors: [sampleDevelopers[0], sampleDevelopers[2]],
        lastUpdated: Date.now() - 86400000 * 7
      },
      {
        pluginId: 'advanced-charting',
        repositoryUrl: 'https://github.com/chartmaster/advanced-charting',
        branch: 'main',
        commits: this.generateSampleCommits(23),
        issues: this.generateSampleIssues(12),
        pullRequests: this.generateSamplePRs(8),
        contributors: [sampleDevelopers[1]],
        lastUpdated: Date.now() - 86400000 * 14
      },
      {
        pluginId: 'community-chat',
        repositoryUrl: 'https://github.com/socialtrader/community-chat',
        branch: 'develop',
        commits: this.generateSampleCommits(18),
        issues: this.generateSampleIssues(6),
        pullRequests: this.generateSamplePRs(4),
        contributors: [sampleDevelopers[2], sampleDevelopers[0]],
        lastUpdated: Date.now() - 86400000 * 5
      }
    ];

    sampleRepos.forEach(repo => {
      this.repositories.set(repo.pluginId, repo);
      this.issues.set(repo.pluginId, repo.issues);
      this.pullRequests.set(repo.pluginId, repo.pullRequests);
    });

    this.updateMetrics();
  }

  /**
   * Generate sample commits
   */
  private generateSampleCommits(count: number): GitCommit[] {
    const commits: GitCommit[] = [];
    for (let i = 0; i < count; i++) {
      commits.push({
        id: `commit_${i}`,
        message: [
          'Add new feature',
          'Fix bug in calculation',
          'Update documentation',
          'Refactor code structure',
          'Improve performance'
        ][i % 5],
        author: ['quantdev', 'chartmaster', 'socialtrader'][i % 3],
        timestamp: Date.now() - 86400000 * i,
        changes: {
          files: 1 + Math.floor(Math.random() * 5),
          additions: 10 + Math.floor(Math.random() * 100),
          deletions: Math.floor(Math.random() * 20)
        }
      });
    }
    return commits;
  }

  /**
   * Generate sample issues
   */
  private generateSampleIssues(count: number): PluginIssue[] {
    const issues: PluginIssue[] = [];
    const statuses: PluginIssue['status'][] = ['open', 'in_progress', 'resolved', 'closed'];
    const priorities: PluginIssue['priority'][] = ['low', 'medium', 'high', 'critical'];
    
    for (let i = 0; i < count; i++) {
      issues.push({
        id: `issue_${i}`,
        title: [
          'Memory leak in indicator calculation',
          'Chart rendering performance issue',
          'API rate limiting problem',
          'UI component not responsive',
          'Data update delay',
          'Plugin configuration bug'
        ][i % 6],
        description: 'Detailed description of the issue...',
        author: ['quantdev', 'chartmaster', 'socialtrader'][i % 3],
        status: statuses[i % statuses.length],
        priority: priorities[i % priorities.length],
        labels: ['bug', 'enhancement', 'performance', 'ui'].slice(0, 1 + Math.floor(Math.random() * 3)),
        createdAt: Date.now() - 86400000 * (i * 2),
        updatedAt: Date.now() - 86400000 * i,
        comments: [],
        assignee: ['quantdev', 'chartmaster', 'socialtrader'][i % 3]
      });
    }
    return issues;
  }

  /**
   * Generate sample pull requests
   */
  private generateSamplePRs(count: number): PullRequest[] {
    const prs: PullRequest[] = [];
    const statuses: PullRequest['status'][] = ['open', 'merged', 'closed'];
    
    for (let i = 0; i < count; i++) {
      prs.push({
        id: `pr_${i}`,
        title: [
          'Add new indicator type',
          'Improve chart performance',
          'Update API integration',
          'Fix configuration bug',
          'Add new data source support'
        ][i % 5],
        description: 'Description of changes...',
        author: ['quantdev', 'chartmaster', 'socialtrader'][i % 3],
        status: statuses[i % statuses.length],
        baseBranch: 'main',
        headBranch: `feature/branch-${i}`,
        additions: 50 + Math.floor(Math.random() * 200),
        deletions: 10 + Math.floor(Math.random() * 50),
        files: 2 + Math.floor(Math.random() * 8),
        createdAt: Date.now() - 86400000 * (i * 3),
        updatedAt: Date.now() - 86400000 * i,
        reviews: this.generateSampleReviews(1 + Math.floor(Math.random() * 3)),
        mergeCommit: statuses[i % statuses.length] === 'merged' ? `commit_${i}` : undefined
      });
    }
    return prs;
  }

  /**
   * Generate sample reviews
   */
  private generateSampleReviews(count: number): PRReview[] {
    const reviews: PRReview[] = [];
    const statuses: PRReview['status'][] = ['approved', 'changes_requested', 'commented', 'pending'];
    
    for (let i = 0; i < count; i++) {
      reviews.push({
        reviewer: ['quantdev', 'chartmaster', 'socialtrader'][i % 3],
        status: statuses[i % statuses.length],
        comments: i === 0 ? ['Looks good to me'] : ['Please address the comments'],
        timestamp: Date.now() - 86400000 * i
      });
    }
    return reviews;
  }

  /**
   * Register a developer
   */
  registerDeveloper(developer: PluginDeveloper): void {
    this.developers.set(developer.id, developer);
    console.log(`Developer registered: ${developer.username}`);
  }

  /**
   * Get developer by ID
   */
  getDeveloper(developerId: string): PluginDeveloper | undefined {
    return this.developers.get(developerId);
  }

  /**
   * Get developer by username
   */
  getDeveloperByUsername(username: string): PluginDeveloper | undefined {
    return Array.from(this.developers.values()).find(d => d.username === username);
  }

  /**
   * Get all developers
   */
  getAllDevelopers(): PluginDeveloper[] {
    return Array.from(this.developers.values());
  }

  /**
   * Get top developers by reputation
   */
  getTopDevelopers(limit: number = 10): PluginDeveloper[] {
    return Array.from(this.developers.values())
      .sort((a, b) => b.reputation - a.reputation)
      .slice(0, limit);
  }

  /**
   * Get repository for a plugin
   */
  getRepository(pluginId: string): PluginRepository | undefined {
    return this.repositories.get(pluginId);
  }

  /**
   * Get all repositories
   */
  getAllRepositories(): PluginRepository[] {
    return Array.from(this.repositories.values());
  }

  /**
   * Get issues for a plugin
   */
  getIssues(pluginId: string): PluginIssue[] {
    return this.issues.get(pluginId) || [];
  }

  /**
   * Create an issue
   */
  createIssue(pluginId: string, issue: Omit<PluginIssue, 'id' | 'createdAt' | 'updatedAt' | 'comments'>): PluginIssue {
    const newIssue: PluginIssue = {
      ...issue,
      id: `issue_${Date.now()}`,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      comments: []
    };

    const pluginIssues = this.issues.get(pluginId) || [];
    pluginIssues.push(newIssue);
    this.issues.set(pluginId, pluginIssues);

    console.log(`Issue created: ${newIssue.id} for ${pluginId}`);
    return newIssue;
  }

  /**
   * Update an issue
   */
  updateIssue(pluginId: string, issueId: string, updates: Partial<PluginIssue>): void {
    const pluginIssues = this.issues.get(pluginId);
    if (!pluginIssues) return;

    const issue = pluginIssues.find(i => i.id === issueId);
    if (issue) {
      Object.assign(issue, updates);
      issue.updatedAt = Date.now();
    }
  }

  /**
   * Add comment to issue
   */
  addCommentToIssue(pluginId: string, issueId: string, comment: Omit<Comment, 'reactions' | 'timestamp'>): void {
    const pluginIssues = this.issues.get(pluginId);
    if (!pluginIssues) return;

    const issue = pluginIssues.find(i => i.id === issueId);
    if (issue) {
      const newComment: Comment = {
        ...comment,
        timestamp: Date.now(),
        reactions: []
      };
      issue.comments.push(newComment);
    }
  }

  /**
   * Get pull requests for a plugin
   */
  getPullRequests(pluginId: string): PullRequest[] {
    return this.pullRequests.get(pluginId) || [];
  }

  /**
   * Create a pull request
   */
  createPullRequest(pluginId: string, pr: Omit<PullRequest, 'id' | 'createdAt' | 'updatedAt' | 'reviews'>): PullRequest {
    const newPR: PullRequest = {
      ...pr,
      id: `pr_${Date.now()}`,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      reviews: []
    };

    const pluginPRs = this.pullRequests.get(pluginId) || [];
    pluginPRs.push(newPR);
    this.pullRequests.set(pluginId, pluginPRs);

    console.log(`Pull request created: ${newPR.id} for ${pluginId}`);
    return newPR;
  }

  /**
   * Review a pull request
   */
  reviewPullRequest(pluginId: string, prId: string, review: Omit<PRReview, 'timestamp'>): void {
    const pluginPRs = this.pullRequests.get(pluginId);
    if (!pluginPRs) return;

    const pr = pluginPRs.find(p => p.id === prId);
    if (pr) {
      const newReview: PRReview = {
        ...review,
        timestamp: Date.now()
      };
      pr.reviews.push(newReview);
      pr.updatedAt = Date.now();
    }
  }

  /**
   * Merge a pull request
   */
  mergePullRequest(pluginId: string, prId: string): void {
    const pluginPRs = this.pullRequests.get(pluginId);
    if (!pluginPRs) return;

    const pr = pluginPRs.find(p => p.id === prId);
    if (pr) {
      pr.status = 'merged';
      pr.mergeCommit = `merge_${Date.now()}`;
      pr.updatedAt = Date.now();
    }
  }

  /**
   * Update community metrics
   */
  private updateMetrics(): void {
    this.metrics.totalDevelopers = this.developers.size;
    this.metrics.totalRepositories = this.repositories.size;
    
    let totalCommits = 0;
    let totalIssues = 0;
    let totalPRs = 0;
    let openIssues = 0;
    let mergedPRs = 0;

    this.repositories.forEach(repo => {
      totalCommits += repo.commits.length;
      totalIssues += repo.issues.length;
      totalPRs += repo.pullRequests.length;
      openIssues += repo.issues.filter(i => i.status === 'open').length;
      mergedPRs += repo.pullRequests.filter(pr => pr.status === 'merged').length;
    });

    this.metrics.totalCommits = totalCommits;
    this.metrics.totalIssues = totalIssues;
    this.metrics.totalPullRequests = totalPRs;
    this.metrics.openIssues = openIssues;
    this.metrics.mergedPRs = mergedPRs;
    
    // Calculate active contributors (developers with activity in last 30 days)
    const thirtyDaysAgo = Date.now() - 86400000 * 30;
    this.metrics.activeContributors = Array.from(this.developers.values()).filter(dev => {
      const lastActivity = Array.from(this.repositories.values()).find((repo: PluginRepository) =>
        repo.contributors.some((c: PluginDeveloper) => c.id === dev.id)
      )?.lastUpdated || 0;
      return lastActivity > thirtyDaysAgo;
    }).length;

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
   * Get community metrics
   */
  getMetrics(): CommunityMetrics {
    return { ...this.metrics };
  }

  /**
   * Get developer contributions
   */
  getDeveloperContributions(developerId: string): {
    repositories: string[];
    commits: number;
    issues: number;
    pullRequests: number;
  } {
    const repositories: string[] = [];
    let commits = 0;
    let issues = 0;
    let pullRequests = 0;

    this.repositories.forEach((repo, pluginId) => {
      const isContributor = repo.contributors.some(c => c.id === developerId);
      if (isContributor) {
        repositories.push(pluginId);
        commits += repo.commits.filter(c => c.author === this.developers.get(developerId)?.username).length;
        issues += repo.issues.filter(i => i.author === this.developers.get(developerId)?.username).length;
        pullRequests += repo.pullRequests.filter(pr => pr.author === this.developers.get(developerId)?.username).length;
      }
    });

    return { repositories, commits, issues, pullRequests };
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
   * Reset the system
   */
  reset(): void {
    this.developers.clear();
    this.repositories.clear();
    this.issues.clear();
    this.pullRequests.clear();
    
    this.metrics = {
      totalDevelopers: 0,
      totalRepositories: 0,
      totalCommits: 0,
      totalIssues: 0,
      totalPullRequests: 0,
      activeContributors: 0,
      openIssues: 0,
      mergedPRs: 0,
      lastCalculated: Date.now()
    };
    
    console.log('Community Plugin Support reset');
  }
}

// Singleton instance
export const communityPluginSupport = new CommunityPluginSupport();

export default CommunityPluginSupport;