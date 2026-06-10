/**
 * Development Configuration
 * 
 * Configuration flags for development and testing
 */

export const DEV_CONFIG = {
  // Enable mock WebSocket manager for testing without backend
  USE_MOCK_WEBSOCKET: true,
  
  // Mock data generation interval (milliseconds)
  MOCK_DATA_INTERVAL: 3000,
  
  // Enable detailed logging
  ENABLE_DEBUG_LOGGING: true,
  
  // Maximum activities to keep in memory (performance optimization)
  MAX_ACTIVITIES: 1000,
  
  // Maximum events to keep in memory
  MAX_EVENTS: 1000,
  
  // WebSocket reconnection delay (milliseconds)
  WEBSOCKET_RECONNECT_DELAY: 5000,
  
  // Maximum WebSocket reconnection attempts
  MAX_RECONNECT_ATTEMPTS: 10,
} as const;
