/**
 * Plugin Rating and Review System
 * DIX VISION v42.2 - Phase 5: Plugin Marketplace & Ecosystem (Weeks 13-14)
 * 
 * Production-grade rating and review system with comprehensive rating metrics,
 * review validation, reputation tracking, and quality assurance for plugins.
 */

export interface PluginRating {
  pluginId: string;
  averageRating: number;
  totalReviews: number;
  ratingDistribution: {
    oneStar: number;
    twoStars: number;
    threeStars: number;
    fourStars: number;
    fiveStars: number;
  };
  categoryRatings: Map<string, number>;
  recentRatings: number[];
  lastUpdated: number;
}

export interface DetailedReview {
  id: string;
  pluginId: string;
  userId: string;
  username: string;
  rating: number; // 1-5
  title: string;
  content: string;
  pros: string[];
  cons: string[];
  category: string;
  version: string;
  createdAt: number;
  updatedAt: number;
  verified: boolean; // Verified purchase/install
  helpful: number;
  notHelpful: number;
  helpfulUsers: string[]; // Track users who marked as helpful
  response?: {
    authorId: string;
    authorName: string;
    content: string;
    createdAt: number;
  };
  status: 'published' | 'pending' | 'rejected' | 'flagged';
  flaggedReason?: string;
}

export interface RatingMetrics {
  totalRatedPlugins: number;
  totalReviews: number;
  averageRating: number;
  topRatedPlugins: string[];
  mostReviewedPlugins: string[];
  recentReviewActivity: number;
  reviewQualityScore: number;
  lastCalculated: number;
}

export interface ReviewValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

class PluginRatingSystem {
  private ratings: Map<string, PluginRating> = new Map();
  private reviews: Map<string, DetailedReview[]> = new Map();
  private userRatings: Map<string, Map<string, number>> = new Map(); // userId -> pluginId -> rating
  private metrics: RatingMetrics = {
    totalRatedPlugins: 0,
    totalReviews: 0,
    averageRating: 0,
    topRatedPlugins: [],
    mostReviewedPlugins: [],
    recentReviewActivity: 0,
    reviewQualityScore: 0,
    lastCalculated: Date.now()
  };
  private isInitialized: boolean = false;
  private metricsUpdateInterval?: number;

  /**
   * Initialize the rating system
   */
  initialize(): void {
    if (this.isInitialized) {
      console.warn('Plugin Rating System already initialized');
      return;
    }

    console.log('Initializing Plugin Rating System...');
    
    // Load sample ratings
    this.loadSampleData();
    
    // Start metrics update cycle
    this.startMetricsUpdate();
    
    this.isInitialized = true;
    console.log('Plugin Rating System initialized successfully');
  }

  /**
   * Load sample data
   */
  private loadSampleData(): void {
    const samplePlugins = ['ml-indicators-pro', 'sentiment-analyzer', 'advanced-charting', 'portfolio-optimizer', 'community-chat'];
    
    samplePlugins.forEach(pluginId => {
      const rating: PluginRating = {
        pluginId,
        averageRating: 3.5 + Math.random() * 1.5, // 3.5-5.0
        totalReviews: 50 + Math.floor(Math.random() * 500),
        ratingDistribution: {
          oneStar: Math.floor(Math.random() * 10),
          twoStars: Math.floor(Math.random() * 20),
          threeStars: Math.floor(Math.random() * 50),
          fourStars: Math.floor(Math.random() * 100),
          fiveStars: Math.floor(Math.random() * 200)
        },
        categoryRatings: new Map(),
        recentRatings: Array.from({ length: 10 }, () => 3 + Math.random() * 2),
        lastUpdated: Date.now()
      };

      // Normalize distribution to match total
      const total = Object.values(rating.ratingDistribution).reduce((sum, count) => sum + count, 0);
      if (total > 0) {
        Object.keys(rating.ratingDistribution).forEach(key => {
          rating.ratingDistribution[key as keyof typeof rating.ratingDistribution] = 
            Math.round((rating.ratingDistribution[key as keyof typeof rating.ratingDistribution] / total) * rating.totalReviews);
        });
      }

      // Calculate average from distribution
      rating.averageRating = (
        rating.ratingDistribution.oneStar * 1 +
        rating.ratingDistribution.twoStars * 2 +
        rating.ratingDistribution.threeStars * 3 +
        rating.ratingDistribution.fourStars * 4 +
        rating.ratingDistribution.fiveStars * 5
      ) / rating.totalReviews;

      this.ratings.set(pluginId, rating);
      
      // Generate sample reviews
      this.reviews.set(pluginId, this.generateSampleReviews(pluginId, rating.totalReviews));
    });

    this.updateMetrics();
  }

  /**
   * Generate sample reviews
   */
  private generateSampleReviews(pluginId: string, count: number): DetailedReview[] {
    const reviews: DetailedReview[] = [];
    const sampleTitles = [
      'Excellent plugin, highly recommended',
      'Good but needs some improvements',
      'Perfect for my use case',
      'Had some issues but support was great',
      'Best plugin I\'ve used',
      'Works as expected',
      'Could use better documentation'
    ];
    
    const samplePros = [
      'Easy to install and configure',
      'Great performance',
      'Excellent documentation',
      'Responsive support',
      'Regular updates',
      'Feature-rich'
    ];
    
    const sampleCons = [
      'Could use better UI',
      'Some features are confusing',
      'Performance could be improved',
      'Limited customization options',
      'Needs more tutorials'
    ];

    for (let i = 0; i < count; i++) {
      const rating = Math.floor(3 + Math.random() * 3); // 3-5 stars
      reviews.push({
        id: `review_${pluginId}_${i}`,
        pluginId,
        userId: `user_${i}`,
        username: `user${i}`,
        rating,
        title: sampleTitles[i % sampleTitles.length],
        content: 'Detailed review content...',
        pros: samplePros.slice(0, 1 + Math.floor(Math.random() * 3)),
        cons: rating < 5 ? sampleCons.slice(0, Math.floor(Math.random() * 2)) : [],
        category: 'general',
        version: '1.0.0',
        createdAt: Date.now() - 86400000 * i,
        updatedAt: Date.now() - 86400000 * i,
        verified: Math.random() > 0.3,
        helpful: Math.floor(Math.random() * 50),
        notHelpful: Math.floor(Math.random() * 10),
        helpfulUsers: [],
        status: 'published'
      });
    }
    
    return reviews;
  }

  /**
   * Add a review for a plugin
   */
  addReview(review: Omit<DetailedReview, 'id' | 'createdAt' | 'updatedAt' | 'helpful' | 'notHelpful'>): { success: boolean; review?: DetailedReview; error?: string } {
    // Validate review
    const validation = this.validateReview(review);
    if (!validation.isValid) {
      return { success: false, error: validation.errors.join(', ') };
    }

    const newReview: DetailedReview = {
      ...review,
      id: `review_${Date.now()}`,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      helpful: 0,
      notHelpful: 0
    };

    // Check if user already rated this plugin
    const userRatings = this.userRatings.get(review.userId) || new Map();
    if (userRatings.has(review.pluginId)) {
      return { success: false, error: 'User has already rated this plugin' };
    }

    // Store review
    const pluginReviews = this.reviews.get(review.pluginId) || [];
    pluginReviews.push(newReview);
    this.reviews.set(review.pluginId, pluginReviews);

    // Update user ratings
    userRatings.set(review.pluginId, review.rating);
    this.userRatings.set(review.userId, userRatings);

    // Update plugin rating
    this.updatePluginRating(review.pluginId, review.rating);
    
    console.log(`Review added: ${newReview.id} for ${review.pluginId}`);
    
    return { success: true, review: newReview };
  }

  /**
   * Validate a review
   */
  validateReview(review: Omit<DetailedReview, 'id' | 'createdAt' | 'updatedAt' | 'helpful' | 'notHelpful'>): ReviewValidation {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Required fields
    if (!review.pluginId) errors.push('Plugin ID is required');
    if (!review.userId) errors.push('User ID is required');
    if (!review.username) errors.push('Username is required');
    if (!review.title) errors.push('Title is required');
    if (!review.content) errors.push('Content is required');

    // Rating validation
    if (review.rating !== undefined) {
      if (!Number.isInteger(review.rating) || review.rating < 1 || review.rating > 5) {
        errors.push('Rating must be an integer between 1 and 5');
      }
    }

    // Content length validation
    if (review.content && review.content.length < 50) {
      warnings.push('Review content is too short, consider adding more detail');
    }
    if (review.content && review.content.length > 5000) {
      errors.push('Review content is too long (max 5000 characters)');
    }

    // Title validation
    if (review.title && review.title.length > 200) {
      errors.push('Title is too long (max 200 characters)');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Update plugin rating
   */
  private updatePluginRating(pluginId: string, newRating: number): void {
    const existingRating = this.ratings.get(pluginId);
    if (!existingRating) {
      // Create new rating entry
      const newRatingEntry: PluginRating = {
        pluginId,
        averageRating: newRating,
        totalReviews: 1,
        ratingDistribution: {
          oneStar: 0,
          twoStars: 0,
          threeStars: 0,
          fourStars: 0,
          fiveStars: 0
        },
        categoryRatings: new Map(),
        recentRatings: [newRating],
        lastUpdated: Date.now()
      };
      
      // Add to distribution
      const distKey = this.getRatingKey(newRating);
      newRatingEntry.ratingDistribution[distKey] = 1;
      
      this.ratings.set(pluginId, newRatingEntry);
      return;
    }

    // Update distribution
    const distKey = this.getRatingKey(newRating);
    existingRating.ratingDistribution[distKey]++;
    existingRating.totalReviews++;

    // Add to recent ratings
    existingRating.recentRatings.push(newRating);
    if (existingRating.recentRatings.length > 20) {
      existingRating.recentRatings.shift();
    }

    // Recalculate average
    existingRating.averageRating = this.calculateAverageRating(existingRating.ratingDistribution);
    existingRating.lastUpdated = Date.now();
  }

  /**
   * Get rating key from numeric rating
   */
  private getRatingKey(rating: number): keyof PluginRating['ratingDistribution'] {
    const keys: (keyof PluginRating['ratingDistribution'])[] = ['oneStar', 'twoStars', 'threeStars', 'fourStars', 'fiveStars'];
    return keys[rating - 1];
  }

  /**
   * Calculate average rating from distribution
   */
  private calculateAverageRating(distribution: PluginRating['ratingDistribution']): number {
    const total = Object.values(distribution).reduce((sum, count) => sum + count, 0);
    if (total === 0) return 0;

    const sum = (
      distribution.oneStar * 1 +
      distribution.twoStars * 2 +
      distribution.threeStars * 3 +
      distribution.fourStars * 4 +
      distribution.fiveStars * 5
    );

    return Math.round((sum / total) * 10) / 10;
  }

  /**
   * Get rating for a plugin
   */
  getPluginRating(pluginId: string): PluginRating | undefined {
    return this.ratings.get(pluginId);
  }

  /**
   * Get reviews for a plugin
   */
  getReviews(pluginId: string, options?: {
    limit?: number;
    sortBy?: 'recent' | 'helpful' | 'rating';
    minRating?: number;
  }): DetailedReview[] {
    let reviews = this.reviews.get(pluginId) || [];

    // Filter by minimum rating
    if (options && options.minRating !== undefined && options.minRating !== null) {
      reviews = reviews.filter(r => r.rating >= options.minRating!);
    }

    // Sort reviews
    switch (options?.sortBy) {
      case 'recent':
        reviews.sort((a, b) => b.createdAt - a.createdAt);
        break;
      case 'helpful':
        reviews.sort((a, b) => b.helpful - a.helpful);
        break;
      case 'rating':
        reviews.sort((a, b) => b.rating - a.rating);
        break;
      default:
        reviews.sort((a, b) => b.createdAt - a.createdAt);
    }

    // Limit results
    if (options?.limit) {
      reviews = reviews.slice(0, options.limit);
    }

    return reviews;
  }

  /**
   * Get user's rating for a plugin
   */
  getUserRating(userId: string, pluginId: string): number | undefined {
    const userRatings = this.userRatings.get(userId);
    return userRatings?.get(pluginId);
  }

  /**
   * Get all plugins rated by a user
   */
  getUserRatedPlugins(userId: string): string[] {
    const userRatings = this.userRatings.get(userId);
    return userRatings ? Array.from(userRatings.keys()) : [];
  }

  /**
   * Mark review as helpful
   */
  markReviewHelpful(reviewId: string, pluginId: string, userId: string): void {
    const reviews = this.reviews.get(pluginId);
    if (!reviews) return;

    const review = reviews.find(r => r.id === reviewId);
    if (review) {
      if (!review.helpfulUsers) {
        review.helpfulUsers = [];
      }
      if (!review.helpfulUsers.includes(userId)) {
        review.helpful++;
        review.helpfulUsers.push(userId);
      }
    }
  }

  /**
   * Mark review as not helpful
   */
  markReviewNotHelpful(reviewId: string, pluginId: string, _userId: string): void {
    const reviews = this.reviews.get(pluginId);
    if (!reviews) return;

    const review = reviews.find(r => r.id === reviewId);
    if (review) {
      review.notHelpful++;
    }
  }

  /**
   * Add response to review
   */
  addReviewResponse(pluginId: string, reviewId: string, responseData: { authorId: string; authorName: string; content: string }): void {
    const reviews = this.reviews.get(pluginId);
    if (!reviews) return;

    const review = reviews.find(r => r.id === reviewId);
    if (review) {
      review.response = {
        authorId: responseData.authorId,
        authorName: responseData.authorName,
        content: responseData.content,
        createdAt: Date.now()
      };
      review.updatedAt = Date.now();
    }
  }

  /**
   * Update review
   */
  updateReview(pluginId: string, reviewId: string, updates: Partial<DetailedReview>): { success: boolean; error?: string } {
    const reviews = this.reviews.get(pluginId);
    if (!reviews) {
      return { success: false, error: 'Plugin reviews not found' };
    }

    const review = reviews.find(r => r.id === reviewId);
    if (!review) {
      return { success: false, error: 'Review not found' };
    }

    // Prevent changing rating after submission
    if (updates.rating && updates.rating !== review.rating) {
      return { success: false, error: 'Cannot change rating after submission' };
    }

    Object.assign(review, updates);
    review.updatedAt = Date.now();

    return { success: true };
  }

  /**
   * Flag review for review
   */
  flagReview(pluginId: string, reviewId: string, reason: string): void {
    const reviews = this.reviews.get(pluginId);
    if (!reviews) return;

    const review = reviews.find(r => r.id === reviewId);
    if (review) {
      review.status = 'flagged';
      review.flaggedReason = reason;
    }
  }

  /**
   * Get top rated plugins
   */
  getTopRatedPlugins(limit: number = 10): Array<{ pluginId: string; rating: number }> {
    return Array.from(this.ratings.values())
      .sort((a, b) => b.averageRating - a.averageRating)
      .slice(0, limit)
      .map(r => ({ pluginId: r.pluginId, rating: r.averageRating }));
  }

  /**
   * Get most reviewed plugins
   */
  getMostReviewedPlugins(limit: number = 10): Array<{ pluginId: string; reviews: number }> {
    return Array.from(this.ratings.values())
      .sort((a, b) => b.totalReviews - a.totalReviews)
      .slice(0, limit)
      .map(r => ({ pluginId: r.pluginId, reviews: r.totalReviews }));
  }

  /**
   * Update system metrics
   */
  private updateMetrics(): void {
    this.metrics.totalRatedPlugins = this.ratings.size;
    this.metrics.totalReviews = Array.from(this.ratings.values())
      .reduce((sum, r) => sum + r.totalReviews, 0);
    
    this.metrics.averageRating = this.metrics.totalReviews > 0 
      ? Array.from(this.ratings.values())
          .reduce((sum, r) => sum + r.averageRating * r.totalReviews, 0) / this.metrics.totalReviews
      : 0;

    this.metrics.topRatedPlugins = Array.from(this.ratings.values())
      .sort((a, b) => b.averageRating - a.averageRating)
      .slice(0, 10)
      .map(r => r.pluginId);

    this.metrics.mostReviewedPlugins = Array.from(this.ratings.values())
      .sort((a, b) => b.totalReviews - a.totalReviews)
      .slice(0, 10)
      .map(r => r.pluginId);

    // Calculate review quality score (based on review length and detail)
    let totalLength = 0;
    let totalProCons = 0;
    let totalReviewsCount = 0;

    this.reviews.forEach(reviews => {
      reviews.forEach(review => {
        totalLength += review.content.length;
        totalProCons += review.pros.length + review.cons.length;
        totalReviewsCount++;
      });
    });

    this.metrics.reviewQualityScore = totalReviewsCount > 0
      ? ((totalLength / 100) + totalProCons) / totalReviewsCount
      : 0;

    // Recent activity (reviews in last 7 days)
    const sevenDaysAgo = Date.now() - 86400000 * 7;
    this.metrics.recentReviewActivity = Array.from(this.reviews.values())
      .reduce((sum, reviews) => sum + reviews.filter(r => r.createdAt > sevenDaysAgo).length, 0);

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
   * Get system metrics
   */
  getMetrics(): RatingMetrics {
    return { ...this.metrics };
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
   * Reset the rating system
   */
  reset(): void {
    this.ratings.clear();
    this.reviews.clear();
    this.userRatings.clear();
    
    this.metrics = {
      totalRatedPlugins: 0,
      totalReviews: 0,
      averageRating: 0,
      topRatedPlugins: [],
      mostReviewedPlugins: [],
      recentReviewActivity: 0,
      reviewQualityScore: 0,
      lastCalculated: Date.now()
    };
    
    console.log('Plugin Rating System reset');
  }
}

// Singleton instance
export const pluginRatingSystem = new PluginRatingSystem();

export default PluginRatingSystem;