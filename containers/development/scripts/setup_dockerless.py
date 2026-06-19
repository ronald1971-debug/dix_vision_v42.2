"""Infrastructure setup without Docker - using SQLite and local caching.

This script sets up DIX VISION infrastructure using:
- SQLite database (no PostgreSQL required)
- Local Python caching (no Redis required)
- File-based storage for all data
"""

import sys
import os
import logging
import sqlite3
import json
import time
from typing import Dict, Any
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DockerlessInfrastructure:
    """Setup infrastructure without Docker dependencies."""

    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(self.base_path, "data", "dix_vision.db")
        self.cache_path = os.path.join(self.base_path, "data", "cache.json")

    def setup_sqlite_database(self) -> bool:
        """Setup SQLite database with production schema."""
        try:
            logger.info("Setting up SQLite database...")

            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            # Create connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create schema
            self._create_sqlite_schema(cursor)

            conn.commit()
            conn.close()

            logger.info(f"✅ SQLite database created: {self.db_path}")
            return True

        except Exception as e:
            logger.error(f"❌ SQLite database setup failed: {e}")
            return False

    def _create_sqlite_schema(self, cursor):
        """Create database schema in SQLite."""
        logger.info("Creating database schema...")

        # Create tables (SQLite-compatible schema)
        tables = [
            # Market data table
            """
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                price REAL NOT NULL,
                volume REAL,
                bid REAL,
                ask REAL,
                spread REAL,
                volatility REAL,
                momentum REAL,
                trend REAL,
                support_level REAL,
                resistance_level REAL,
                data_source TEXT,
                data_quality TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Orders table
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                order_type TEXT NOT NULL,
                order_side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL,
                stop_price REAL,
                time_in_force TEXT DEFAULT 'GTC',
                status TEXT DEFAULT 'PENDING',
                filled_quantity REAL DEFAULT 0,
                average_fill_price REAL DEFAULT 0,
                timestamp INTEGER,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Positions table
            """
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                quantity REAL NOT NULL,
                average_entry_price REAL NOT NULL,
                unrealized_pnl REAL DEFAULT 0,
                realized_pnl REAL DEFAULT 0,
                timestamp INTEGER,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Trust anchors table
            """
            CREATE TABLE IF NOT EXISTS trust_anchors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anchor_id TEXT UNIQUE NOT NULL,
                purpose TEXT NOT NULL,
                key_type TEXT NOT NULL,
                public_key TEXT NOT NULL,
                private_key_encrypted TEXT,
                key_size INTEGER,
                registration_time TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Foundation hashes table
            """
            CREATE TABLE IF NOT EXISTS foundation_hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash_id TEXT UNIQUE NOT NULL,
                component TEXT NOT NULL,
                version TEXT,
                hash_value TEXT NOT NULL,
                hash_algorithm TEXT DEFAULT 'SHA256',
                timestamp_ns INTEGER,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Verification artifacts table
            """
            CREATE TABLE IF NOT EXISTS verification_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artifact_id TEXT UNIQUE NOT NULL,
                hash_id TEXT NOT NULL,
                anchor_id TEXT NOT NULL,
                verification_data TEXT DEFAULT '{}',
                signature TEXT NOT NULL,
                signature_algorithm TEXT,
                created_time TIMESTAMP,
                status TEXT DEFAULT 'verified',
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (anchor_id) REFERENCES trust_anchors(anchor_id)
            )
            """,

            # Trading decisions table
            """
            CREATE TABLE IF NOT EXISTS trading_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id TEXT UNIQUE NOT NULL,
                decision_type TEXT NOT NULL,
                action TEXT NOT NULL,
                reasoning TEXT,
                confidence REAL,
                confidence_level TEXT,
                expected_outcome TEXT,
                risk_assessment TEXT DEFAULT '{}',
                alternative_actions TEXT DEFAULT '[]',
                supporting_evidence TEXT DEFAULT '[]',
                contradictory_evidence TEXT DEFAULT '[]',
                timestamp INTEGER,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,

            # Audit log table
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id TEXT,
                component TEXT,
                action TEXT,
                details TEXT DEFAULT '{}',
                severity TEXT DEFAULT 'INFO',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]

        for table_sql in tables:
            cursor.execute(table_sql)

        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_orders_symbol_status ON orders(symbol, status)",
            "CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id)",
            "CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_trading_decisions_timestamp ON trading_decisions(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)",
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        logger.info("✅ Database schema created")

    def setup_local_cache(self) -> bool:
        """Setup local file-based cache system."""
        try:
            logger.info("Setting up local cache...")

            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)

            # Initialize cache with default values
            cache_data = {
                "status": "initialized",
                "version": "42.2",
                "init_time": time.time(),
                "cache": {
                    "market_data": {},
                    "decisions": {},
                    "risk_metrics": {},
                    "patterns": {}
                },
                "config": {
                    "cache:market_data:ttl": "60",
                    "cache:decisions:ttl": "300",
                    "cache:risk_metrics:ttl": "600",
                    "cache:patterns:ttl": "1800",
                    "cache:enabled": "true"
                },
                "monitoring": {
                    "health:status": "ok",
                    "health:last_check": str(time.time()),
                    "metrics:total_requests": "0",
                    "metrics:errors": "0",
                    "metrics:latency_avg": "0"
                }
            }

            # Write cache file
            with open(self.cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)

            logger.info(f"✅ Local cache created: {self.cache_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Local cache setup failed: {e}")
            return False

    def create_dockerless_config(self) -> bool:
        """Create dockerless configuration file."""
        try:
            logger.info("Creating dockerless configuration...")

            config_path = os.path.join(self.base_path, ".env.dockerless")

            config_content = """
# DIX VISION Dockerless Configuration
# This configuration uses SQLite and local caching instead of Docker containers

# System Configuration
DIX_ENVIRONMENT=production
DIX_LOG_LEVEL=INFO
DIX_DEBUG=false
DIX_VERSION=42.2

# Database Configuration (SQLite)
DATABASE_TYPE=sqlite
SQLITE_PATH=data/dix_vision.db

# Cache Configuration (Local)
CACHE_TYPE=local
CACHE_PATH=data/cache.json

# Redis Configuration (Disabled)
REDIS_ENABLED=false

# PostgreSQL Configuration (Disabled)
POSTGRES_ENABLED=false

# InfluxDB Configuration (Disabled)
INFLUXDB_ENABLED=false

# Cryptographic Configuration
KEY_STORE_PATH=secure/keys
ENCRYPTION_KEY_PATH=secure/keys/master.key
SIGNATURE_ALGORITHM=RSA-PSS-4096
HASH_ALGORITHM=SHA3-256

# Trading Configuration
RISK_MAX_POSITION_SIZE=1000.0
RISK_MAX_PORTFOLIO_VALUE=1000000.0
RISK_MAX_DAILY_LOSS=0.02
RISK_MAX_DRAWDOWN=0.10
RISK_MAX_LEVERAGE=2.0

# Intelligence Engine Configuration
INTELLIGENCE_ENGINE_ENABLED=true
PATTERN_WINDOW_SIZE=500
DECISION_ENGINE_INTERVAL=0.5

# Monitoring Configuration
MONITORING_ENABLED=true
HEALTH_CHECK_ENABLED=true
PERFORMANCE_MONITORING_ENABLED=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_OUTPUT=stdout
LOG_FILE_PATH=logs/dix_vision.log
"""

            with open(config_path, 'w') as f:
                f.write(config_content)

            logger.info(f"✅ Dockerless configuration created: {config_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Dockerless configuration failed: {e}")
            return False

    def create_dockerless_adapters(self) -> bool:
        """Create adapter classes for dockerless operation."""
        try:
            logger.info("Creating dockerless adapters...")

            # Create adapters directory
            adapters_dir = os.path.join(self.base_path, "infrastructure", "adapters")
            os.makedirs(adapters_dir, exist_ok=True)

            # SQLite adapter
            sqlite_adapter = '''
"""SQLite adapter for dockerless database operations."""

import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SQLiteAdapter:
    """SQLite database adapter."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None

    def connect(self):
        """Establish database connection."""
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        return self

    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL query."""
        cursor = self._conn.cursor()
        cursor.execute(query, params)
        return cursor

    def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all results as dictionaries."""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one result as dictionary."""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def commit(self):
        """Commit transaction."""
        if self._conn:
            self._conn.commit()

    def rollback(self):
        """Rollback transaction."""
        if self._conn:
            self._conn.rollback()
'''

            with open(os.path.join(adapters_dir, "sqlite_adapter.py"), 'w') as f:
                f.write(sqlite_adapter)

            # Local cache adapter
            cache_adapter = '''
"""Local cache adapter for dockerless caching."""

import json
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LocalCacheAdapter:
    """Local file-based cache adapter."""

    def __init__(self, cache_path: str):
        self.cache_path = cache_path
        self._cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load cache from file."""
        try:
            with open(self.cache_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"cache": {}, "config": {}, "monitoring": {}}

    def _save_cache(self):
        """Save cache to file."""
        with open(self.cache_path, 'w') as f:
            json.dump(self._cache, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        return self._cache.get(key, default)

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL."""
        self._cache[key] = {
            "value": value,
            "expiry": time.time() + ttl
        }
        self._save_cache()
        return True

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            self._save_cache()
            return True
        return False

    def clear(self) -> bool:
        """Clear all cache entries."""
        self._cache = {"cache": {}, "config": {}, "monitoring": {}}
        self._save_cache()
        return True
'''

            with open(os.path.join(adapters_dir, "cache_adapter.py"), 'w') as f:
                f.write(cache_adapter)

            # Create __init__.py
            with open(os.path.join(adapters_dir, "__init__.py"), 'w') as f:
                f.write('"""Infrastructure adapters for dockerless operation."""\n')

            logger.info(f"✅ Dockerless adapters created: {adapters_dir}")
            return True

        except Exception as e:
            logger.error(f"❌ Dockerless adapters creation failed: {e}")
            return False

    def verify_dockerless_setup(self) -> bool:
        """Verify dockerless infrastructure setup."""
        try:
            logger.info("Verifying dockerless setup...")

            # Check database
            if os.path.exists(self.db_path):
                logger.info("✅ SQLite database exists")
            else:
                logger.error("❌ SQLite database not found")
                return False

            # Check cache
            if os.path.exists(self.cache_path):
                logger.info("✅ Local cache exists")
            else:
                logger.error("❌ Local cache not found")
                return False

            # Test database connection
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM market_data")
                count = cursor.fetchone()[0]
                logger.info(f"✅ Database connection successful (market_data rows: {count})")
                conn.close()
            except Exception as e:
                logger.error(f"❌ Database connection failed: {e}")
                return False

            # Test cache
            try:
                with open(self.cache_path, 'r') as f:
                    cache_data = json.load(f)
                    if cache_data.get("status") == "initialized":
                        logger.info("✅ Cache connection successful")
                    else:
                        logger.error("❌ Cache not properly initialized")
                        return False
            except Exception as e:
                logger.error(f"❌ Cache connection failed: {e}")
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Dockerless setup verification failed: {e}")
            return False

    def run_dockerless_setup(self) -> bool:
        """Run complete dockerless infrastructure setup."""
        logger.info("🚀 Starting Dockerless Infrastructure Setup...")
        logger.info("=" * 70)

        steps = [
            ("setup_sqlite_database", "Setup SQLite database"),
            ("setup_local_cache", "Setup local cache"),
            ("create_dockerless_config", "Create dockerless configuration"),
            ("create_dockerless_adapters", "Create dockerless adapters"),
            ("verify_dockerless_setup", "Verify dockerless setup")
        ]

        results = []
        for method_name, step_name in steps:
            logger.info(f"\n📋 {step_name}...")
            method = getattr(self, method_name)
            result = method()
            results.append((step_name, result))

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 DOCKERLESS SETUP SUMMARY")
        logger.info("=" * 70)

        success_count = sum(1 for _, result in results if result)
        total_count = len(results)

        for step_name, result in results:
            status = "✅ Success" if result else "❌ Failed"
            logger.info(f"{status}: {step_name}")

        logger.info("-" * 70)
        logger.info(f"Total: {success_count}/{total_count} steps successful")

        if success_count == total_count:
            logger.info("\n🎉 Dockerless infrastructure setup completed successfully!")
            logger.info("📝 Using SQLite database and local cache")
            logger.info("🔧 Update .env.dockerless file with your production values")
            return True
        else:
            logger.info("\n⚠️ Dockerless infrastructure setup completed with errors")
            return False


def main():
    """Main function to run dockerless infrastructure setup."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Set up Dockerless infrastructure for DIX VISION"
    )
    parser.add_argument("--path", help="Base path for infrastructure")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing setup")

    args = parser.parse_args()

    setup = DockerlessInfrastructure(base_path=args.path)

    if args.verify_only:
        success = setup.verify_dockerless_setup()
        return 0 if success else 1
    else:
        success = setup.run_dockerless_setup()
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())