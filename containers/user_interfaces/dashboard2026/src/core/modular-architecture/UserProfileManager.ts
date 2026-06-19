/**
 * User Profile Manager
 * DIX VISION v42.2 - Phase 1: Architecture Optimization
 * 
 * User profile-based module loading system that allows customization
 * of active features based on user needs and preferences.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { moduleRegistry } from './ModuleRegistry';
import { UserProfile } from './ModuleTypes';

interface UserProfileConfig {
  profile: UserProfile;
  maxMemoryMB: number;
  maxModules: number;
  preloadRoutes: string[];
  disabledCategories: ('trading' | 'intelligence' | 'operations')[];
}

interface UserProfileContextType {
  currentProfile: UserProfile;
  setProfile: (profile: UserProfile) => void;
  profileConfig: UserProfileConfig;
  updateProfileConfig: (config: Partial<UserProfileConfig>) => void;
  isProfileValid: boolean;
  profileRecommendations: string[];
}

const DEFAULT_PROFILES: Record<UserProfile, UserProfileConfig> = {
  minimal: {
    profile: 'minimal',
    maxMemoryMB: 128,
    maxModules: 5,
    preloadRoutes: ['mission-control', 'operator'],
    disabledCategories: ['intelligence']
  },
  standard: {
    profile: 'standard',
    maxMemoryMB: 256,
    maxModules: 10,
    preloadRoutes: ['mission-control', 'markets', 'portfolio', 'operator'],
    disabledCategories: []
  },
  professional: {
    profile: 'professional',
    maxMemoryMB: 512,
    maxModules: 20,
    preloadRoutes: [
      'mission-control',
      'markets',
      'portfolio',
      'execution',
      'indira-cognitive-center',
      'dyon-workspace',
      'operator'
    ],
    disabledCategories: []
  }
};

const UserProfileContext = createContext<UserProfileContextType | undefined>(undefined);

export function UserProfileProvider({ children }: { children: ReactNode }) {
  const [currentProfile, setCurrentProfile] = useState<UserProfile>('standard');
  const [profileConfig, setProfileConfig] = useState<UserProfileConfig>(DEFAULT_PROFILES.standard);

  // Load profile from localStorage on mount
  useEffect(() => {
    const savedProfile = localStorage.getItem('dix UserProfile') as UserProfile;
    if (savedProfile && ['minimal', 'standard', 'professional'].includes(savedProfile)) {
      setCurrentProfile(savedProfile);
      setProfileConfig(DEFAULT_PROFILES[savedProfile]);
    }
  }, []);

  // Update module registry when profile changes
  useEffect(() => {
    moduleRegistry.setUserProfile(currentProfile);
    console.log(`User profile changed to: ${currentProfile}`);
    
    // Save to localStorage
    localStorage.setItem('dix UserProfile', currentProfile);
  }, [currentProfile]);

  const setProfile = (profile: UserProfile) => {
    setCurrentProfile(profile);
    setProfileConfig(DEFAULT_PROFILES[profile]);
  };

  const updateProfileConfig = (config: Partial<UserProfileConfig>) => {
    setProfileConfig(prev => ({ ...prev, ...config }));
  };

  // Check if current profile is within limits
  const isProfileValid = React.useMemo(() => {
    const metrics = moduleRegistry.getSystemMetrics();
    const currentMemory = metrics.loadedMemoryEstimate;
    const currentModules = metrics.loadedModules;

    return currentMemory <= profileConfig.maxMemoryMB && 
           currentModules <= profileConfig.maxModules;
  }, [profileConfig, moduleRegistry]);

  // Generate recommendations based on current usage
  const profileRecommendations = React.useMemo(() => {
    const metrics = moduleRegistry.getSystemMetrics();
    const recommendations: string[] = [];

    const currentMemory = metrics.loadedMemoryEstimate;
    const currentModules = metrics.loadedModules;
    const memoryUtilization = (currentMemory / profileConfig.maxMemoryMB) * 100;
    const moduleUtilization = (currentModules / profileConfig.maxModules) * 100;

    if (memoryUtilization > 80) {
      recommendations.push(`Memory usage at ${memoryUtilization.toFixed(0)}%. Consider upgrading to professional profile or unloading unused modules.`);
    } else if (memoryUtilization < 30 && currentProfile === 'professional') {
      recommendations.push('Memory usage low. Consider downgrading to standard profile for better performance.');
    }

    if (moduleUtilization > 80) {
      recommendations.push(`Module count at ${moduleUtilization.toFixed(0)}%. Consider upgrading to professional profile or consolidating modules.`);
    }

    if (currentProfile === 'minimal' && profileConfig.disabledCategories.length === 0) {
      recommendations.push('Minimal profile has disabled categories. Enable trading or intelligence features for full functionality.');
    }

    if (recommendations.length === 0) {
      recommendations.push('Current profile configuration is optimal for your usage patterns.');
    }

    return recommendations;
  }, [currentProfile, profileConfig, moduleRegistry]);

  const value: UserProfileContextType = {
    currentProfile,
    setProfile,
    profileConfig,
    updateProfileConfig,
    isProfileValid,
    profileRecommendations
  };

  return (
    <UserProfileContext.Provider value={value}>
      {children}
    </UserProfileContext.Provider>
  );
}

export function useUserProfile(): UserProfileContextType {
  const context = useContext(UserProfileContext);
  if (context === undefined) {
    throw new Error('useUserProfile must be used within a UserProfileProvider');
  }
  return context;
}

/**
 * Profile comparison utility
 */
export function compareProfiles(profile1: UserProfile, profile2: UserProfile): {
  memoryDifference: number;
  moduleDifference: number;
  featureDifference: string[];
} {
  const config1 = DEFAULT_PROFILES[profile1];
  const config2 = DEFAULT_PROFILES[profile2];

  const memoryDifference = config2.maxMemoryMB - config1.maxMemoryMB;
  const moduleDifference = config2.maxModules - config1.maxModules;

  // Determine feature differences
  const features1 = new Set([
    ...config1.preloadRoutes,
    ...config1.disabledCategories.map(cat => `no-${cat}`)
  ]);
  const features2 = new Set([
    ...config2.preloadRoutes,
    ...config2.disabledCategories.map(cat => `no-${cat}`)
  ]);

  const featureDifference = Array.from(features2).filter(f => !features1.has(f));

  return {
    memoryDifference,
    moduleDifference,
    featureDifference
  };
}

/**
 * Get recommended profile based on usage patterns
 */
export function getRecommendedProfile(usageMetrics: {
  averageMemoryMB: number;
  averageActiveModules: number;
  usedIntelligenceFeatures: boolean;
  usedAdvancedTrading: boolean;
}): UserProfile {
  if (usageMetrics.usedIntelligenceFeatures && usageMetrics.usedAdvancedTrading) {
    return 'professional';
  }

  if (usageMetrics.averageMemoryMB > 200 || usageMetrics.averageActiveModules > 8) {
    return 'professional';
  }

  if (usageMetrics.usedIntelligenceFeatures || usageMetrics.usedAdvancedTrading) {
    return 'standard';
  }

  if (usageMetrics.averageMemoryMB > 100 || usageMetrics.averageActiveModules > 4) {
    return 'standard';
  }

  return 'minimal';
}