"""Redis initialization script for DIX VISION production deployment."""

import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedisInitializer:
    """Initialize and configure Redis for production deployment."""

    def __init__(self, redis_config: dict = None):
        self.redis_config = redis_config or self._default_redis_config()

    def _default_redis_config(self) -> dict:
        """Default Redis configuration."""
        return {"host": "localhost", "port": 6379, "db": 0, "password": None}

    def initialize_redis(self) -> bool:
        """Initialize Redis with production configuration."""
        try:
            logger.info("Initializing Redis for production...")

            # Check if redis is available
            try:
                import redis
            except ImportError:
                logger.warning("redis library not available")
                logger.info("Install redis library: pip install redis>=5.0.0")
                return False

            # Connect to Redis
            r = redis.Redis(
                host=self.redis_config["host"],
                port=self.redis_config["port"],
                db=self.redis_config["db"],
                password=self.redis_config.get("password"),
                decode_responses=True,
            )

            # Test connection
            r.ping()
            logger.info("Successfully connected to Redis")

            # Set system configuration
            self._set_system_config(r)

            # Set cache configurations
            self._set_cache_config(r)

            # Set monitoring keys
            self._set_monitoring_keys(r)

            logger.info("Redis initialization completed successfully")
            return True

        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            return False

    def _set_system_config(self, r):
        """Set system configuration in Redis."""
        import time

        logger.info("Setting system configuration...")

        config = {
            "dix_vision:status": "initialized",
            "dix_vision:version": "42.2",
            "dix_vision:init_time": str(time.time()),
            "dix_vision:environment": "production",
            "dix_vision:deployment": "production",
        }

        for key, value in config.items():
            r.set(key, value)

        logger.info("System configuration set")

    def _set_cache_config(self, r):
        """Set cache configuration."""
        logger.info("Setting cache configuration...")

        cache_config = {
            "cache:market_data:ttl": "60",  # 1 minute
            "cache:decisions:ttl": "300",  # 5 minutes
            "cache:risk_metrics:ttl": "600",  # 10 minutes
            "cache:patterns:ttl": "1800",  # 30 minutes
            "cache:enabled": "true",
        }

        for key, value in cache_config.items():
            r.set(key, value)

        logger.info("Cache configuration set")

    def _set_monitoring_keys(self, r):
        """Set monitoring and health check keys."""
        logger.info("Setting monitoring keys...")

        # Health check
        r.set("health:status", "ok")
        r.set("health:last_check", str(__import__("time").time()))

        # Performance metrics
        r.set("metrics:total_requests", "0")
        r.set("metrics:errors", "0")
        r.set("metrics:latency_avg", "0")

        logger.info("Monitoring keys set")

    def test_redis_connection(self) -> bool:
        """Test Redis connection and basic operations."""
        try:
            import redis

            r = redis.Redis(
                host=self.redis_config["host"],
                port=self.redis_config["port"],
                db=self.redis_config["db"],
                password=self.redis_config.get("password"),
                decode_responses=True,
            )

            # Test ping
            r.ping()

            # Test set/get
            r.set("test:connection", "ok")
            result = r.get("test:connection")
            r.delete("test:connection")

            return result == "ok"

        except Exception as e:
            logger.error(f"Redis connection test failed: {e}")
            return False


def main():
    """Main function to run Redis initialization."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize Redis for DIX VISION production deployment"
    )
    parser.add_argument("--host", default="localhost", help="Redis host")
    parser.add_argument("--port", type=int, default=6379, help="Redis port")
    parser.add_argument("--test", action="store_true", help="Test Redis connection only")

    args = parser.parse_args()

    redis_config = {"host": args.host, "port": args.port, "db": 0, "password": None}

    initializer = RedisInitializer(redis_config)

    if args.test:
        if initializer.test_redis_connection():
            logger.info("Redis connection test passed")
            return 0
        else:
            logger.error("Redis connection test failed")
            return 1
    else:
        if initializer.initialize_redis():
            logger.info("Redis initialization completed successfully")
            return 0
        else:
            logger.error("Redis initialization failed")
            return 1


if __name__ == "__main__":
    sys.exit(main())
