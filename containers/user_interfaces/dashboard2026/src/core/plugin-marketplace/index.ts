/**
 * Plugin Marketplace & Ecosystem - Core Index
 * DIX VISION v42.2 - Phase 5: Plugin Marketplace & Ecosystem (Weeks 13-14)
 * 
 * Production-grade plugin marketplace system with community support,
 * development framework, rating system, and comprehensive developer tools.
 */

// Plugin Marketplace
export { pluginMarketplace } from './PluginMarketplace';
export type {
  PluginPackage,
  PluginReview,
  PluginInstallation,
  MarketplaceMetrics
} from './PluginMarketplace';

// Plugin SDK
export { pluginSDK } from './PluginSDK';
export type {
  PluginManifest,
  PluginConfigurationSchema,
  ConfigProperty,
  PluginAPI,
  Indicator,
  IndicatorParameter,
  PluginTestSuite,
  PluginTestCase,
  DevelopmentMetrics
} from './PluginSDK';

// Community Support
export { communityPluginSupport } from './CommunityPluginSupport';
export type {
  PluginDeveloper,
  PluginRepository,
  GitCommit,
  PluginIssue,
  PullRequest,
  PRReview,
  Comment,
  Reaction,
  CommunityMetrics
} from './CommunityPluginSupport';

// Rating System
export { pluginRatingSystem } from './PluginRatingSystem';
export type {
  PluginRating,
  DetailedReview,
  RatingMetrics,
  ReviewValidation
} from './PluginRatingSystem';