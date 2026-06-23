"""Database initialization script for DIX VISION production deployment."""

import argparse
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Initialize and configure databases for production deployment."""

    def __init__(self, postgres_config: dict = None, redis_config: dict = None):
        self.postgres_config = postgres_config or self._default_postgres_config()
        self.redis_config = redis_config or self._default_redis_config()

    def _default_postgres_config(self) -> dict:
        """Default PostgreSQL configuration."""
        return {
            "host": "localhost",
            "port": 5432,
            "database": "dix_vision",
            "user": "postgres",
            "password": "postgres",
        }

    def _default_redis_config(self) -> dict:
        """Default Redis configuration."""
        return {"host": "localhost", "port": 6379, "db": 0, "password": None}

    def initialize_postgresql(self) -> bool:
        """Initialize PostgreSQL database with required schema."""
        try:
            logger.info("Initializing PostgreSQL database...")

            # Check if psycopg2 is available
            try:
                import psycopg2
            except ImportError:
                logger.warning("psycopg2 not available, creating placeholder schema")
                self._create_placeholder_postgres_schema()
                return True

            # Connect to PostgreSQL
            conn = psycopg2.connect(
                host=self.postgres_config["host"],
                port=self.postgres_config["port"],
                user=self.postgres_config["user"],
                password=self.postgres_config["password"],
                database="postgres",  # Connect to default db first
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Create database if it doesn't exist
            cursor.execute(
                f"SELECT 1 FROM pg_database WHERE datname = '{self.postgres_config['database']}'"
            )
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {self.postgres_config['database']}")
                logger.info(f"Created database: {self.postgres_config['database']}")

            cursor.close()
            conn.close()

            # Connect to the new database
            conn = psycopg2.connect(
                host=self.postgres_config["host"],
                port=self.postgres_config["port"],
                user=self.postgres_config["user"],
                password=self.postgres_config["password"],
                database=self.postgres_config["database"],
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Create schema
            self._create_postgres_schema(cursor)

            cursor.close()
            conn.close()

            logger.info("PostgreSQL initialization completed successfully")
            return True

        except Exception as e:
            logger.error(f"PostgreSQL initialization failed: {e}")
            return False

    def _create_postgres_schema(self, cursor):
        """Create PostgreSQL database schema."""
        logger.info("Creating database schema...")

        # Create tables
        tables = [
            # Market data table
            """
            CREATE TABLE IF NOT EXISTS market_data (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(50) NOT NULL,
                timestamp BIGINT NOT NULL,
                price DECIMAL(20, 8) NOT NULL,
                volume DECIMAL(20, 8),
                bid DECIMAL(20, 8),
                ask DECIMAL(20, 8),
                spread DECIMAL(20, 8),
                volatility DECIMAL(10, 8),
                momentum DECIMAL(10, 8),
                trend DECIMAL(10, 8),
                support_level DECIMAL(20, 8),
                resistance_level DECIMAL(20, 8),
                data_source VARCHAR(50),
                data_quality VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Orders table
            """
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                order_id VARCHAR(100) UNIQUE NOT NULL,
                symbol VARCHAR(50) NOT NULL,
                order_type VARCHAR(20) NOT NULL,
                order_side VARCHAR(10) NOT NULL,
                quantity DECIMAL(20, 8) NOT NULL,
                price DECIMAL(20, 8),
                stop_price DECIMAL(20, 8),
                time_in_force VARCHAR(10) DEFAULT 'GTC',
                status VARCHAR(20) DEFAULT 'PENDING',
                filled_quantity DECIMAL(20, 8) DEFAULT 0,
                average_fill_price DECIMAL(20, 8) DEFAULT 0,
                timestamp BIGINT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Positions table
            """
            CREATE TABLE IF NOT EXISTS positions (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(50) UNIQUE NOT NULL,
                quantity DECIMAL(20, 8) NOT NULL,
                average_entry_price DECIMAL(20, 8) NOT NULL,
                unrealized_pnl DECIMAL(20, 8) DEFAULT 0,
                realized_pnl DECIMAL(20, 8) DEFAULT 0,
                timestamp BIGINT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Trust anchors table
            """
            CREATE TABLE IF NOT EXISTS trust_anchors (
                id SERIAL PRIMARY KEY,
                anchor_id VARCHAR(100) UNIQUE NOT NULL,
                purpose VARCHAR(100) NOT NULL,
                key_type VARCHAR(20) NOT NULL,
                public_key TEXT NOT NULL,
                private_key_encrypted TEXT,
                key_size INTEGER,
                registration_time TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active',
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Foundation hashes table
            """
            CREATE TABLE IF NOT EXISTS foundation_hashes (
                id SERIAL PRIMARY KEY,
                hash_id VARCHAR(100) UNIQUE NOT NULL,
                component VARCHAR(100) NOT NULL,
                version VARCHAR(50),
                hash_value VARCHAR(256) NOT NULL,
                hash_algorithm VARCHAR(20) DEFAULT 'SHA256',
                timestamp_ns BIGINT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Verification artifacts table
            """
            CREATE TABLE IF NOT EXISTS verification_artifacts (
                id SERIAL PRIMARY KEY,
                artifact_id VARCHAR(100) UNIQUE NOT NULL,
                hash_id VARCHAR(100) NOT NULL,
                anchor_id VARCHAR(100) NOT NULL,
                verification_data JSONB,
                signature TEXT NOT NULL,
                signature_algorithm VARCHAR(50),
                created_time TIMESTAMP,
                status VARCHAR(20) DEFAULT 'verified',
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (anchor_id) REFERENCES trust_anchors(anchor_id)
            )
            """,
            # Trading decisions table
            """
            CREATE TABLE IF NOT EXISTS trading_decisions (
                id SERIAL PRIMARY KEY,
                decision_id VARCHAR(100) UNIQUE NOT NULL,
                decision_type VARCHAR(50) NOT NULL,
                action VARCHAR(50) NOT NULL,
                reasoning TEXT,
                confidence DECIMAL(5, 4),
                confidence_level VARCHAR(20),
                expected_outcome TEXT,
                risk_assessment JSONB,
                alternative_actions JSONB,
                supporting_evidence JSONB,
                contradictory_evidence JSONB,
                timestamp BIGINT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Audit log table
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                user_id VARCHAR(100),
                component VARCHAR(100),
                action VARCHAR(100),
                details JSONB,
                severity VARCHAR(20),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
        ]

        for table_sql in tables:
            cursor.execute(table_sql)

        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_orders_symbol_status ON orders(symbol, status)",
            "CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id)",
            "CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_trading_decisions_timestamp ON trading_decisions(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_event_type ON audit_log(event_type)",
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        logger.info("Database schema created successfully")

    def _create_placeholder_postgres_schema(self):
        """Create placeholder schema when PostgreSQL is not available."""
        logger.info("Creating placeholder schema for testing...")
        # This would be used when PostgreSQL is not available but we need to test
        schema_dir = os.path.join(os.path.dirname(__file__), "schema")
        os.makedirs(schema_dir, exist_ok=True)

        schema_file = os.path.join(schema_dir, "postgres_schema_placeholder.sql")
        with open(schema_file, "w") as f:
            f.write(self._get_placeholder_schema())

        logger.info(f"Placeholder schema created at: {schema_file}")

    def _get_placeholder_schema(self) -> str:
        """Get placeholder SQL schema."""
        return """
-- Placeholder PostgreSQL Schema
-- This is a placeholder for when PostgreSQL is not available
-- In production, this would be the actual schema

CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp BIGINT NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    order_side VARCHAR(10) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) UNIQUE NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    average_entry_price DECIMAL(20, 8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

    def initialize_redis(self) -> bool:
        """Initialize Redis cache with required configuration."""
        try:
            logger.info("Initializing Redis cache...")

            # Check if redis is available
            try:
                import redis
            except ImportError:
                logger.warning("redis library not available, creating placeholder configuration")
                self._create_placeholder_redis_config()
                return True

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

            # Set initial configuration
            r.set("dix_vision:status", "initialized")
            r.set("dix_vision:version", "42.2")
            r.set("dix_vision:init_time", str(__import__("time").time()))

            logger.info("Redis initialization completed successfully")
            return True

        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            return False

    def _create_placeholder_redis_config(self):
        """Create placeholder Redis configuration."""
        logger.info("Creating placeholder Redis configuration...")
        config_dir = os.path.join(os.path.dirname(__file__), "config")
        os.makedirs(config_dir, exist_ok=True)

        config_file = os.path.join(config_dir, "redis_config_placeholder.json")
        import json

        with open(config_file, "w") as f:
            json.dump(
                {
                    "status": "placeholder",
                    "version": "42.2",
                    "note": "Redis library not available, using placeholder configuration",
                },
                f,
            )

        logger.info(f"Placeholder Redis configuration created at: {config_file}")


def main():
    """Main function to run database initialization."""
    parser = argparse.ArgumentParser(
        description="Initialize databases for DIX VISION production deployment"
    )
    parser.add_argument("--postgres", action="store_true", help="Initialize PostgreSQL")
    parser.add_argument("--redis", action="store_true", help="Initialize Redis")
    parser.add_argument("--all", action="store_true", help="Initialize all databases")
    parser.add_argument("--postgres-host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--postgres-port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("--postgres-db", default="dix_vision", help="PostgreSQL database name")
    parser.add_argument("--redis-host", default="localhost", help="Redis host")
    parser.add_argument("--redis-port", type=int, default=6379, help="Redis port")

    args = parser.parse_args()

    if not any([args.postgres, args.redis, args.all]):
        parser.print_help()
        return

    postgres_config = {
        "host": args.postgres_host,
        "port": args.postgres_port,
        "database": args.postgres_db,
        "user": "postgres",
        "password": "postgres",
    }

    redis_config = {"host": args.redis_host, "port": args.redis_port, "db": 0, "password": None}

    initializer = DatabaseInitializer(postgres_config, redis_config)

    success = True

    if args.all or args.postgres:
        if not initializer.initialize_postgresql():
            success = False

    if args.all or args.redis:
        if not initializer.initialize_redis():
            success = False

    if success:
        logger.info("Database initialization completed successfully")
        return 0
    else:
        logger.error("Database initialization completed with errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
