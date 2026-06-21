"""
DIXVISION Production Configuration
Comprehensive production environment configuration for deployment

Production-ready configuration including:
- Environment settings and variables
- Component deployment parameters
- Security configurations
- Monitoring and alerting settings
- Resource allocation and scaling
- Backup and disaster recovery
- Performance tuning parameters
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from pathlib import Path


class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "dixvision"
    username: str = "dixvision_user"
    password: str = ""  # Load from environment in production
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    def __post_init__(self):
        """Load password from environment if not set"""
        if not self.password:
            self.password = os.getenv("DB_PASSWORD", "")


@dataclass
class CacheConfig:
    """Cache configuration (Redis)"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""  # Load from environment
    max_connections: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    
    def __post_init__(self):
        """Load password from environment if not set"""
        if not self.password:
            self.password = os.getenv("CACHE_PASSWORD", "")


@dataclass
class MessageQueueConfig:
    """Message queue configuration (RabbitMQ)"""
    host: str = "localhost"
    port: int = 5672
    username: str = "dixvision"
    password: str = ""  # Load from environment
    virtual_host: str = "/dixvision"
    heartbeat: int = 60
    blocked_connection_timeout: int = 300
    
    def __post_init__(self):
        """Load password from environment if not set"""
        if not self.password:
            self.password = os.getenv("MQ_PASSWORD", "")


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_encryption: bool = True
    encryption_key: str = ""  # Load from environment
    enable_authentication: bool = True
    session_timeout: int = 3600
    max_login_attempts: int = 5
    password_policy_min_length: int = 12
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 100
    enable_audit_logging: bool = True
    enable_cors: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    
    def __post_init__(self):
        """Load encryption key from environment if not set"""
        if not self.encryption_key:
            self.encryption_key = os.getenv("ENCRYPTION_KEY", "")


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enable_metrics: bool = True
    metrics_port: int = 9090
    enable_tracing: bool = True
    tracing_endpoint: str = "http://localhost:4318"
    enable_logging: bool = True
    log_level: LogLevel = LogLevel.INFO
    log_file_path: str = "/var/log/dixvision"
    log_retention_days: int = 30
    enable_health_checks: bool = True
    health_check_interval: int = 30
    enable_alerting: bool = True
    alert_webhook_url: str = ""
    alert_email_recipients: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Load sensitive data from environment"""
        if not self.alert_webhook_url:
            self.alert_webhook_url = os.getenv("ALERT_WEBHOOK_URL", "")


@dataclass
class ResourceConfig:
    """Resource allocation configuration"""
    max_workers: int = 8
    max_memory_mb: int = 4096
    max_cpu_percent: float = 80.0
    connection_pool_size: int = 100
    thread_pool_size: int = 50
    async_workers: int = 4
    enable_resource_monitoring: bool = True
    resource_check_interval: int = 60


@dataclass
class BackupConfig:
    """Backup and recovery configuration"""
    enable_backups: bool = True
    backup_interval_hours: int = 6
    backup_retention_days: int = 30
    backup_location: str = "/backups/dixvision"
    enable_encrypted_backups: bool = True
    enable_compression: bool = True
    backup_bucket: str = ""  # For cloud backups
    disaster_recovery_site: str = ""
    
    def __post_init__(self):
        """Load backup configuration from environment"""
        if not self.backup_bucket:
            self.backup_bucket = os.getenv("BACKUP_BUCKET", "")
        if not self.disaster_recovery_site:
            self.disaster_recovery_site = os.getenv("DR_SITE", "")


@dataclass
class PerformanceConfig:
    """Performance tuning configuration"""
    enable_query_caching: bool = True
    query_cache_ttl: int = 300
    enable_connection_pooling: bool = True
    enable_async_operations: bool = True
    batch_size: int = 100
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_backoff_ms: int = 100
    enable_compression: bool = True
    compression_level: int = 6


@dataclass
class ComponentConfig:
    """Individual component configuration"""
    indira_enabled: bool = True
    dyon_enabled: bool = True
    dashboard2026_enabled: bool = True
    execution_enabled: bool = True
    multi_domain_enabled: bool = True
    dashmeme_enabled: bool = True
    monitoring_enabled: bool = True
    
    # Component-specific settings
    indira_max_signals_per_second: int = 100
    dyon_max_analysis_threads: int = 4
    dashboard_max_concurrent_users: int = 50
    execution_max_orders_per_second: int = 1000
    multi_domain_max_concurrent_orders: int = 100
    dashmeme_max_tokens_tracked: int = 1000


@dataclass
class NetworkConfig:
    """Network configuration"""
    bind_host: str = "0.0.0.0"
    bind_port: int = 8000
    enable_ssl: bool = True
    ssl_cert_path: str = ""
    ssl_key_path: str = ""
    enable_http2: bool = True
    max_request_size_mb: int = 100
    request_timeout: int = 30
    keepalive_timeout: int = 5
    
    def __post_init__(self):
        """Load SSL paths from environment"""
        if not self.ssl_cert_path:
            self.ssl_cert_path = os.getenv("SSL_CERT_PATH", "")
        if not self.ssl_key_path:
            self.ssl_key_path = os.getenv("SSL_KEY_PATH", "")


@dataclass
class ProductionConfig:
    """Complete production configuration"""
    environment: Environment = Environment.PRODUCTION
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    message_queue: MessageQueueConfig = field(default_factory=MessageQueueConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    resources: ResourceConfig = field(default_factory=ResourceConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    components: ComponentConfig = field(default_factory=ComponentConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    
    # Environment-specific overrides
    debug_mode: bool = False
    maintenance_mode: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "environment": self.environment.value,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "username": self.database.username,
                "pool_size": self.database.pool_size
            },
            "cache": {
                "host": self.cache.host,
                "port": self.cache.port,
                "max_connections": self.cache.max_connections
            },
            "monitoring": {
                "enable_metrics": self.monitoring.enable_metrics,
                "enable_tracing": self.monitoring.enable_tracing,
                "log_level": self.monitoring.log_level.value
            },
            "security": {
                "enable_encryption": self.security.enable_encryption,
                "enable_authentication": self.security.enable_authentication,
                "enable_rate_limiting": self.security.enable_rate_limiting
            },
            "components": {
                "indira_enabled": self.components.indira_enabled,
                "dyon_enabled": self.components.dyon_enabled,
                "execution_enabled": self.components.execution_enabled
            },
            "network": {
                "bind_host": self.network.bind_host,
                "bind_port": self.network.bind_port,
                "enable_ssl": self.network.enable_ssl
            },
            "debug_mode": self.debug_mode,
            "maintenance_mode": self.maintenance_mode
        }
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate environment-specific requirements
        if self.environment == Environment.PRODUCTION:
            if not self.security.encryption_key:
                issues.append("Encryption key must be set in production")
            if not self.security.enable_authentication:
                issues.append("Authentication must be enabled in production")
            if not self.backup.enable_backups:
                issues.append("Backups must be enabled in production")
            if not self.monitoring.enable_alerting:
                issues.append("Alerting must be enabled in production")
        
        # Validate resource limits
        if self.resources.max_workers < 1:
            issues.append("Max workers must be at least 1")
        if self.resources.max_memory_mb < 512:
            issues.append("Max memory must be at least 512MB")
        
        # Validate network configuration
        if self.network.bind_port < 1 or self.network.bind_port > 65535:
            issues.append("Invalid port number")
        
        return issues
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ProductionConfig':
        """Load configuration from file"""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Convert nested dicts to config objects
        database_config = DatabaseConfig(**config_data.get('database', {}))
        cache_config = CacheConfig(**config_data.get('cache', {}))
        message_queue_config = MessageQueueConfig(**config_data.get('message_queue', {}))
        security_config = SecurityConfig(**config_data.get('security', {}))
        monitoring_config = MonitoringConfig(**config_data.get('monitoring', {}))
        resource_config = ResourceConfig(**config_data.get('resources', {}))
        backup_config = BackupConfig(**config_data.get('backup', {}))
        performance_config = PerformanceConfig(**config_data.get('performance', {}))
        component_config = ComponentConfig(**config_data.get('components', {}))
        network_config = NetworkConfig(**config_data.get('network', {}))
        
        return cls(
            environment=Environment(config_data.get('environment', 'production')),
            database=database_config,
            cache=cache_config,
            message_queue=message_queue_config,
            security=security_config,
            monitoring=monitoring_config,
            resources=resource_config,
            backup=backup_config,
            performance=performance_config,
            components=component_config,
            network=network_config,
            debug_mode=config_data.get('debug_mode', False),
            maintenance_mode=config_data.get('maintenance_mode', False)
        )
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to file"""
        config_dict = {
            'environment': self.environment.value,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database,
                'username': self.database.username,
                'password': self.database.password,
                'pool_size': self.database.pool_size,
                'max_overflow': self.database.max_overflow
            },
            'cache': {
                'host': self.cache.host,
                'port': self.cache.port,
                'db': self.cache.db,
                'password': self.cache.password,
                'max_connections': self.cache.max_connections
            },
            'message_queue': {
                'host': self.message_queue.host,
                'port': self.message_queue.port,
                'username': self.message_queue.username,
                'password': self.message_queue.password,
                'virtual_host': self.message_queue.virtual_host
            },
            'security': {
                'enable_encryption': self.security.enable_encryption,
                'encryption_key': self.security.encryption_key,
                'enable_authentication': self.security.enable_authentication,
                'session_timeout': self.security.session_timeout,
                'enable_rate_limiting': self.security.enable_rate_limiting,
                'enable_audit_logging': self.security.enable_audit_logging
            },
            'monitoring': {
                'enable_metrics': self.monitoring.enable_metrics,
                'metrics_port': self.monitoring.metrics_port,
                'enable_tracing': self.monitoring.enable_tracing,
                'tracing_endpoint': self.monitoring.tracing_endpoint,
                'enable_logging': self.monitoring.enable_logging,
                'log_level': self.monitoring.log_level.value,
                'log_file_path': self.monitoring.log_file_path,
                'enable_health_checks': self.monitoring.enable_health_checks,
                'enable_alerting': self.monitoring.enable_alerting
            },
            'resources': {
                'max_workers': self.resources.max_workers,
                'max_memory_mb': self.resources.max_memory_mb,
                'max_cpu_percent': self.resources.max_cpu_percent,
                'connection_pool_size': self.resources.connection_pool_size,
                'enable_resource_monitoring': self.resources.enable_resource_monitoring
            },
            'backup': {
                'enable_backups': self.backup.enable_backups,
                'backup_interval_hours': self.backup.backup_interval_hours,
                'backup_retention_days': self.backup.backup_retention_days,
                'backup_location': self.backup.backup_location,
                'enable_encrypted_backups': self.backup.enable_encrypted_backups
            },
            'performance': {
                'enable_query_caching': self.performance.enable_query_caching,
                'query_cache_ttl': self.performance.query_cache_ttl,
                'enable_connection_pooling': self.performance.enable_connection_pooling,
                'batch_size': self.performance.batch_size,
                'timeout_seconds': self.performance.timeout_seconds
            },
            'components': {
                'indira_enabled': self.components.indira_enabled,
                'dyon_enabled': self.components.dyon_enabled,
                'dashboard2026_enabled': self.components.dashboard2026_enabled,
                'execution_enabled': self.components.execution_enabled,
                'multi_domain_enabled': self.components.multi_domain_enabled,
                'dashmeme_enabled': self.components.dashmeme_enabled
            },
            'network': {
                'bind_host': self.network.bind_host,
                'bind_port': self.network.bind_port,
                'enable_ssl': self.network.enable_ssl,
                'ssl_cert_path': self.network.ssl_cert_path,
                'ssl_key_path': self.network.ssl_key_path,
                'enable_http2': self.network.enable_http2
            },
            'debug_mode': self.debug_mode,
            'maintenance_mode': self.maintenance_mode
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)


class ConfigManager:
    """Configuration management for production deployment"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "production_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> ProductionConfig:
        """Load configuration from file or create default"""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            return ProductionConfig.from_file(str(config_file))
        else:
            # Create default configuration
            config = ProductionConfig()
            config.to_file(self.config_path)
            logging.info(f"Created default configuration at {self.config_path}")
            return config
    
    def reload_config(self) -> ProductionConfig:
        """Reload configuration from file"""
        self.config = ProductionConfig.from_file(self.config_path)
        return self.config
    
    def update_config(self, updates: Dict[str, Any]) -> ProductionConfig:
        """Update configuration with partial updates"""
        # Convert updates to appropriate config objects
        if 'database' in updates:
            updates['database'] = DatabaseConfig(**updates['database'])
        if 'cache' in updates:
            updates['cache'] = CacheConfig(**updates['cache'])
        if 'security' in updates:
            updates['security'] = SecurityConfig(**updates['security'])
        
        # Update config attributes
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Save updated config
        self.config.to_file(self.config_path)
        return self.config
    
    def validate_current_config(self) -> List[str]:
        """Validate current configuration"""
        return self.config.validate()
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        return self.config.to_dict()


# Default configuration manager instance
config_manager = ConfigManager()


def get_production_config() -> ProductionConfig:
    """Get the current production configuration"""
    return config_manager.config


def reload_production_config() -> ProductionConfig:
    """Reload production configuration"""
    return config_manager.reload_config()


if __name__ == '__main__':
    # Example usage
    config = get_production_config()
    print("Current configuration:")
    print(json.dumps(config.to_dict(), indent=2))
    
    # Validate configuration
    issues = config.validate()
    if issues:
        print("\nConfiguration issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nConfiguration is valid")
