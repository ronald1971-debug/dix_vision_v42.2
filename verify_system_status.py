"""
DIX VISION Desktop AgentOS - System Status Verification

Verifies that all components are properly installed and configured
for the DIX VISION Desktop AgentOS system.
"""

import sys
import os
import asyncio
import logging
import subprocess
from pathlib import Path
import importlib.util

# Add project root to path
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)
os.chdir(project_root)

# Set Python path environment variable
os.environ['PYTHONPATH'] = project_root

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class SystemVerifier:
    """Verifies system status and configuration."""
    
    def __init__(self):
        """Initialize verifier."""
        self.checks = []
        self.warnings = []
        self.errors = []
        
    def check_python_version(self) -> dict:
        """Check Python version."""
        version = sys.version_info
        result = {
            "component": "Python Version",
            "status": "PASS" if version.major >= 3 and version.minor >= 8 else "FAIL",
            "version": f"{version.major}.{version.minor}.{version.micro}",
            "details": f"Requires Python 3.8+, found {version.major}.{version.minor}.{version.micro}"
        }
        self.checks.append(result)
        if result["status"] == "FAIL":
            self.errors.append(result["details"])
        return result
        
    def check_directory_structure(self) -> dict:
        """Check that all required directories exist."""
        required_dirs = [
            "desktop_agent",
            "desktop_agent/runtime",
            "desktop_agent/agents", 
            "desktop_agent/browser",
            "desktop_agent/desktop",
            "desktop_agent/voice",
            "desktop_agent/memory",
            "desktop_agent/governance",
            "desktop_agent/skills",
            "desktop_agent/hud",
            "desktop_agent/telemetry",
            "desktop_agent/environment",
            "dix_desktop",
            "custom_skills",
            "models",
            "voices",
        ]
        
        missing_dirs = []
        existing_dirs = []
        
        for dir_path in required_dirs:
            full_path = Path(dir_path)
            if full_path.exists():
                existing_dirs.append(dir_path)
            else:
                missing_dirs.append(dir_path)
                
        result = {
            "component": "Directory Structure",
            "status": "PASS" if not missing_dirs else "FAIL",
            "existing": len(existing_dirs),
            "required": len(required_dirs),
            "missing": missing_dirs,
            "details": f"{len(existing_dirs)}/{len(required_dirs)} directories exist"
        }
        
        self.checks.append(result)
        if missing_dirs:
            self.errors.extend([f"Missing directory: {dir}" for dir in missing_dirs])
            
        return result
        
    def check_module_imports(self) -> dict:
        """Check that core modules can be imported."""
        modules_to_check = [
            "desktop_agent.runtime",
            "desktop_agent.agents",
            "desktop_agent.browser", 
            "desktop_agent.desktop",
            "desktop_agent.environment",
            "desktop_agent.memory",
            "desktop_agent.governance",
            "desktop_agent.skills",
            "desktop_agent.hud",
            "desktop_agent.telemetry",
        ]
        
        importable = []
        failed = []
        
        for module_name in modules_to_check:
            try:
                importlib.import_module(module_name)
                importable.append(module_name)
            except ImportError as e:
                failed.append((module_name, str(e)))
                
        result = {
            "component": "Module Imports",
            "status": "PASS" if not failed else "FAIL",
            "importable": len(importable),
            "total": len(modules_to_check),
            "failed": [m[0] for m in failed],
            "details": f"{len(importable)}/{len(modules_to_check)} modules import successfully"
        }
        
        self.checks.append(result)
        if failed:
            self.errors.extend([f"Import failed: {m[0]} - {m[1]}" for m in failed])
            
        return result
        
    def check_dependencies(self) -> dict:
        """Check Python dependencies."""
        packages_to_check = [
            ("selenium", "Browser automation (Selenium)"),
            ("playwright", "Browser automation (Playwright)"),
            ("psutil", "System monitoring"),
            ("asyncio", "Async support"),
            ("pathlib", "Path handling"),
        ]
        
        installed = []
        missing = []
        
        for package, description in packages_to_check:
            try:
                __import__(package)
                installed.append((package, description))
            except ImportError:
                missing.append((package, description))
                
        result = {
            "component": "Python Dependencies",
            "status": "PASS" if not missing else "WARNING",
            "installed": [p[1] for p in installed],
            "missing": [p[1] for p in missing],
            "details": f"{len(installed)}/{len(packages_to_check)} packages installed"
        }
        
        self.checks.append(result)
        if missing:
            self.warnings.extend([f"Missing package: {p[1]} - install with: pip install {p[0]}" for p in missing])
            
        return result
        
    def check_dix_desktop(self) -> dict:
        """Check DIX DESKTOP frontend configuration."""
        dix_desktop_path = Path("dix_desktop")
        
        checks = {
            "directory_exists": dix_desktop_path.exists(),
            "package_json": (dix_desktop_path / "package.json").exists(),
            "tauri_conf": (dix_desktop_path / "src-tauri" / "tauri.conf.json").exists(),
            "node_modules": (dix_desktop_path / "node_modules").exists(),
        }
        
        result = {
            "component": "DIX DESKTOP Frontend",
            "status": "PASS" if all(checks.values()) else "WARNING",
            "checks": checks,
            "details": f"{sum(checks.values())}/{len(checks)} checks passed"
        }
        
        self.checks.append(result)
        if not all(checks.values()):
            for check, passed in checks.items():
                if not passed:
                    self.warnings.append(f"DIX DESKTOP check failed: {check}")
                    
        return result
        
    def check_desktop_shortcut(self) -> dict:
        """Check desktop shortcut."""
        desktop = Path.home() / "OneDrive" / "Desktop" / "DIX DESKTOP.lnk"
        
        result = {
            "component": "Desktop Shortcut",
            "status": "PASS" if desktop.exists() else "WARNING",
            "exists": desktop.exists(),
            "path": str(desktop),
            "details": f"Desktop shortcut { 'exists' if desktop.exists() else 'not found'} at {desktop}"
        }
        
        self.checks.append(result)
        if not desktop.exists():
            self.warnings.append("Desktop shortcut not found")
            
        return result
        
    def check_custom_skills(self) -> dict:
        """Check custom skills."""
        custom_skills_path = Path("custom_skills")
        
        if custom_skills_path.exists():
            skill_files = list(custom_skills_path.glob("*.py"))
            skill_files = [f for f in skill_files if f.name != "__init__.py"]
            
            result = {
                "component": "Custom Skills",
                "status": "PASS",
                "count": len(skill_files),
                "skills": [f.name for f in skill_files],
                "details": f"{len(skill_files)} custom skills found"
            }
        else:
            result = {
                "component": "Custom Skills",
                "status": "WARNING",
                "count": 0,
                "skills": [],
                "details": "Custom skills directory not found"
            }
            
        self.checks.append(result)
        return result
        
    def print_report(self):
        """Print verification report."""
        logger.info("=" * 60)
        logger.info("DIX VISION Desktop AgentOS - System Verification Report")
        logger.info("=" * 60)
        logger.info("")
        
        # Overall status
        has_errors = any(check["status"] == "FAIL" for check in self.checks)
        has_warnings = any(check["status"] in ["WARNING", "FAIL"] for check in self.checks)
        
        overall_status = "✓ PASS" if not has_errors else "✗ FAIL"
        if has_warnings and not has_errors:
            overall_status = "⚠ PASS (with warnings)"
        
        logger.info(f"Overall Status: {overall_status}")
        logger.info("")
        
        # Component checks
        for check in self.checks:
            status_icon = "✓" if check["status"] == "PASS" else "⚠" if check["status"] == "WARNING" else "✗"
            logger.info(f"{status_icon} {check['component']}: {check['status']}")
            logger.info(f"  {check['details']}")
            
        logger.info("")
        
        # Errors
        if self.errors:
            logger.info("=" * 60)
            logger.info("ERRORS:")
            logger.info("=" * 60)
            for error in self.errors:
                logger.error(f"  ✗ {error}")
            logger.info("")
            
        # Warnings
        if self.warnings:
            logger.info("=" * 60)
            logger.info("WARNINGS:")
            logger.info("=" * 60)
            for warning in self.warnings:
                logger.warning(f"  ⚠ {warning}")
            logger.info("")
            
        # Recommendations
        if self.errors or self.warnings:
            logger.info("=" * 60)
            logger.info("RECOMMENDATIONS:")
            logger.info("=" * 60)
            
            if self.errors:
                logger.info("Critical issues must be resolved:")
                for error in self.errors:
                    logger.info(f"  • Fix: {error}")
                    
            if self.warnings:
                logger.info("Optional improvements:")
                for warning in self.warnings:
                    logger.info(f"  • {warning}")
            logger.info("")
            
        logger.info("=" * 60)
        logger.info("Verification Complete")
        logger.info("=" * 60)
        
        return not has_errors


def main():
    """Main verification entry point."""
    verifier = SystemVerifier()
    
    # Run all checks
    logger.info("Running system verification...")
    verifier.check_python_version()
    verifier.check_directory_structure()
    verifier.check_module_imports()
    verifier.check_dependencies()
    verifier.check_dix_desktop()
    verifier.check_desktop_shortcut()
    verifier.check_custom_skills()
    
    # Print report
    verifier.print_report()
    
    # Return status
    return 0 if not verifier.errors else 1


if __name__ == "__main__":
    sys.exit(main())
