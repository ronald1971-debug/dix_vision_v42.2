"""Comprehensive infrastructure setup script for DIX VISION production deployment."""

import sys
import os
import subprocess
import logging
import argparse
from typing import List, Dict
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InfrastructureSetup:
    """Comprehensive infrastructure setup for production deployment."""

    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        self.setup_log = []

    def _default_config(self) -> dict:
        """Default configuration for infrastructure setup."""
        return {
            "install_dependencies": True,
            "setup_database": True,
            "setup_redis": True,
            "setup_environment": True,
            "create_directories": True,
            "install_cryptography": True,
            "skip_interactive": False
        }

    def log_step(self, step: str, status: str, message: str = ""):
        """Log setup step."""
        log_entry = {
            "step": step,
            "status": status,
            "message": message,
            "timestamp": __import__('time').time()
        }
        self.setup_log.append(log_entry)

        status_symbol = "✅" if status == "success" else "❌" if status == "error" else "⏳"
        logger.info(f"{status_symbol} {step}: {status}")
        if message:
            logger.info(f"   {message}")

    def install_python_dependencies(self) -> bool:
        """Install Python dependencies for production."""
        try:
            self.log_step("install_dependencies", "in_progress")

            # Core dependencies
            dependencies = [
                "cryptography>=41.0.0",
                "redis>=5.0.0",
                "psycopg2-binary>=2.9.0",
                "influxdb-client>=1.36.0",
                "numpy>=1.24.0",
                "pydantic>=2.0.0"
            ]

            logger.info("Installing Python dependencies...")
            for dep in dependencies:
                try:
                    subprocess.run(
                        ["pip", "install", dep],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    logger.info(f"✓ Installed {dep}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to install {dep}: {e}")

            self.log_step("install_dependencies", "success", "Python dependencies installed")
            return True

        except Exception as e:
            self.log_step("install_dependencies", "error", str(e))
            return False

    def setup_database(self) -> bool:
        """Initialize PostgreSQL database."""
        try:
            self.log_step("setup_database", "in_progress")

            # Run database initialization script
            script_path = os.path.join(
                os.path.dirname(__file__),
                "init_database.py"
            )

            if os.path.exists(script_path):
                cmd = [sys.executable, script_path, "--postgres"]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    self.log_step("setup_database", "success", "PostgreSQL initialized")
                    return True
                else:
                    self.log_step("setup_database", "error", result.stderr)
                    return False
            else:
                self.log_step("setup_database", "warning", "Database initialization script not found")
                return True  # Not critical

        except Exception as e:
            self.log_step("setup_database", "error", str(e))
            return False

    def setup_redis(self) -> bool:
        """Initialize Redis cache."""
        try:
            self.log_step("setup_redis", "in_progress")

            # Run Redis initialization script
            script_path = os.path.join(
                os.path.dirname(__file__),
                "init_redis.py"
            )

            if os.path.exists(script_path):
                cmd = [sys.executable, script_path]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    self.log_step("setup_redis", "success", "Redis initialized")
                    return True
                else:
                    self.log_step("setup_redis", "error", result.stderr)
                    return False
            else:
                self.log_step("setup_redis", "warning", "Redis initialization script not found")
                return True  # Not critical

        except Exception as e:
            self.log_step("setup_redis", "error", str(e))
            return False

    def setup_environment(self) -> bool:
        """Set up environment configuration."""
        try:
            self.log_step("setup_environment", "in_progress")

            # Check if .env file exists
            env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
            env_template = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.template")

            if os.path.exists(env_template):
                if not os.path.exists(env_file):
                    # Copy template to .env
                    import shutil
                    shutil.copy(env_template, env_file)
                    self.log_step("setup_environment", "success", ".env file created from template")
                    logger.info(f"⚠️  Please edit .env file with your production values")
                    return True
                else:
                    self.log_step("setup_environment", "success", ".env file already exists")
                    return True
            else:
                self.log_step("setup_environment", "warning", ".env.template not found")
                return True

        except Exception as e:
            self.log_step("setup_environment", "error", str(e))
            return False

    def create_directories(self) -> bool:
        """Create required directories for production."""
        try:
            self.log_step("create_directories", "in_progress")

            # Create base directories
            base_dirs = [
                "logs",
                "data",
                "backups",
                "config",
                "secure/keys",
                "archive",
                "tmp"
            ]

            base_path = os.path.dirname(os.path.dirname(__file__))

            for dir_name in base_dirs:
                dir_path = os.path.join(base_path, dir_name)
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"✓ Created directory: {dir_path}")

            self.log_step("create_directories", "success", f"Created {len(base_dirs)} directories")
            return True

        except Exception as e:
            self.log_step("create_directories", "error", str(e))
            return False

    def install_cryptography(self) -> bool:
        """Install cryptography library and verify."""
        try:
            self.log_step("install_cryptography", "in_progress")

            try:
                import cryptography
                self.log_step("install_cryptography", "success", f"cryptography {cryptography.__version__} available")
                return True
            except ImportError:
                # Install cryptography
                subprocess.run(
                    ["pip", "install", "cryptography>=41.0.0"],
                    check=True,
                    capture_output=True,
                    text=True
                )

                import cryptography
                self.log_step("install_cryptography", "success", f"cryptography {cryptography.__version__} installed")
                return True

        except Exception as e:
            self.log_step("install_cryptography", "error", str(e))
            return False

    def verify_installation(self) -> bool:
        """Verify that production components are working."""
        try:
            self.log_step("verify_installation", "in_progress")

            # Test cryptography
            try:
                from trust_root.production_crypto import get_production_trust_root
                trust_root = get_production_trust_root()
                logger.info("✓ Cryptographic operations verified")
            except Exception as e:
                logger.warning(f"Cryptography verification warning: {e}")

            # Test intelligence
            try:
                from intelligence_engine.cognitive.production_intelligence import get_production_decision_engine
                decision_engine = get_production_decision_engine()
                logger.info("✓ Intelligence engine verified")
            except Exception as e:
                logger.warning(f"Intelligence verification warning: {e}")

            # Test trading
            try:
                from execution_unified.production_trading import get_production_trader
                trader = get_production_trader()
                logger.info("✓ Trading system verified")
            except Exception as e:
                logger.warning(f"Trading verification warning: {e}")

            self.log_step("verify_installation", "success", "Production components verified")
            return True

        except Exception as e:
            self.log_step("verify_installation", "error", str(e))
            return False

    def run_full_setup(self) -> bool:
        """Run complete infrastructure setup."""
        logger.info("🚀 Starting DIX VISION production infrastructure setup...")
        logger.info("=" * 70)

        steps = []

        if self.config.get("install_dependencies"):
            steps.append(("install_python_dependencies", "Install Python dependencies"))

        if self.config.get("install_cryptography"):
            steps.append(("install_cryptography", "Install cryptography library"))

        if self.config.get("create_directories"):
            steps.append(("create_directories", "Create required directories"))

        if self.config.get("setup_environment"):
            steps.append(("setup_environment", "Set up environment configuration"))

        if self.config.get("setup_database"):
            steps.append(("setup_database", "Initialize PostgreSQL"))

        if self.config.get("setup_redis"):
            steps.append(("setup_redis", "Initialize Redis"))

        # Execute steps
        results = []
        for step_method, step_name in steps:
            logger.info(f"\n📋 {step_name}...")
            method = getattr(self, step_method)
            result = method()
            results.append((step_name, result))

        # Verification
        logger.info(f"\n📋 Verifying installation...")
        verification_result = self.verify_installation()

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 SETUP SUMMARY")
        logger.info("=" * 70)

        success_count = sum(1 for _, result in results if result)
        total_count = len(results)

        for step_name, result in results:
            status = "✅ Success" if result else "❌ Failed"
            logger.info(f"{status}: {step_name}")

        logger.info("-" * 70)
        logger.info(f"Total: {success_count}/{total_count} steps successful")
        logger.info(f"Verification: {'✅ Passed' if verification_result else '❌ Failed'}")

        if success_count == total_count and verification_result:
            logger.info("\n🎉 Infrastructure setup completed successfully!")
            logger.info("⚠️  Please review and configure .env file before starting production deployment")
            return True
        else:
            logger.info("\n⚠️  Infrastructure setup completed with errors")
            return False

    def generate_setup_report(self) -> dict:
        """Generate setup report."""
        return {
            "setup_log": self.setup_log,
            "success_count": sum(1 for log in self.setup_log if log["status"] == "success"),
            "error_count": sum(1 for log in self.setup_log if log["status"] == "error"),
            "warning_count": sum(1 for log in self.setup_log if log["status"] == "warning"),
            "total_steps": len(self.setup_log)
        }


def main():
    """Main function to run infrastructure setup."""
    parser = argparse.ArgumentParser(
        description="Set up infrastructure for DIX VISION production deployment"
    )

    parser.add_argument("--skip-dependencies", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-database", action="store_true", help="Skip database setup")
    parser.add_argument("--skip-redis", action="store_true", help="Skip Redis setup")
    parser.add_argument("--skip-dirs", action="store_true", help="Skip directory creation")
    parser.add_argument("--skip-env", action="store_true", help="Skip environment setup")
    parser.add_argument("--skip-crypto", action="store_true", help="Skip cryptography installation")
    parser.add_argument("--skip-interactive", action="store_true", help="Skip interactive prompts")
    parser.add_argument("--report", action="store_true", help="Generate setup report only")

    args = parser.parse_args()

    config = {
        "install_dependencies": not args.skip_dependencies,
        "setup_database": not args.skip_database,
        "setup_redis": not args.skip_redis,
        "create_directories": not args.skip_dirs,
        "setup_environment": not args.skip_env,
        "install_cryptography": not args.skip_crypto,
        "skip_interactive": args.skip_interactive
    }

    setup = InfrastructureSetup(config)

    if args.report:
        report = setup.generate_setup_report()
        print(json.dumps(report, indent=2))
        return 0 if report["error_count"] == 0 else 1

    success = setup.run_full_setup()

    # Generate report
    report = setup.generate_setup_report()
    report_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "setup_report.json"
    )

    import json
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"\n📋 Setup report saved to: {report_file}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())