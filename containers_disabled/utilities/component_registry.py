"""
Unified Component Registry System
Phase 4: Component Registration and Activation - FULL ACTIVATION, NO LAZY LOADING
"""

import importlib
import os
from typing import Any, Dict, List, Optional


class UnifiedComponentRegistry:
    """Registry for all 621 system components with full activation - NO LAZY LOADING"""

    def __init__(self):
        self.components: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.active_components: set = set()
        self.component_sources: Dict[str, str] = {}

    def register_component(
        self,
        component_name: str,
        module_path: str,
        component_class_name: str,
        dependencies: List[str] = None,
    ):
        """Register a component with full import path - NO LAZY LOADING"""
        self.components[component_name] = {
            "module_path": module_path,
            "class_name": component_class_name,
            "dependencies": dependencies or [],
            "status": "registered",
        }
        self.component_sources[component_name] = module_path
        if dependencies:
            self.dependencies[component_name] = dependencies

    def activate_component(self, component_name: str) -> bool:
        """Activate a component with full import - NO LAZY LOADING"""
        if component_name not in self.components:
            return False

        component_info = self.components[component_name]

        try:
            # Full import - NO LAZY LOADING
            module = importlib.import_module(component_info["module_path"])
            component_class = getattr(module, component_info["class_name"])

            self.components[component_name]["instance"] = component_class
            self.components[component_name]["status"] = "active"
            self.active_components.add(component_name)

            return True

        except Exception as e:
            print(f"Failed to activate {component_name}: {e}")
            self.components[component_name]["status"] = "failed"
            return False

    def get_component(self, component_name: str) -> Optional[Any]:
        """Get an activated component instance"""
        if component_name in self.active_components:
            return self.components[component_name].get("instance")
        return None

    def register_all_archival_components(self):
        """Register all archival components systematically"""
        print("Registering all archival components...")

        # Execution archival components
        execution_components = self._scan_execution_archival()
        for component_name, info in execution_components.items():
            self.register_component(
                component_name, info["module"], info["class"], info.get("dependencies")
            )

        # Governance archival components
        governance_components = self._scan_governance_archival()
        for component_name, info in governance_components.items():
            self.register_component(
                component_name, info["module"], info["class"], info.get("dependencies")
            )

        print(f"Registered {len(self.components)} total components")
        return len(self.components)

    def _scan_execution_archival(self) -> Dict[str, Dict]:
        """Scan and categorize execution archival components"""
        components = {}

        # Scan execution_unified archival directories
        for root, dirs, files in os.walk("execution_unified"):
            if "archive" in root.lower():
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, "execution_unified")

                        # Extract component info
                        component_name = file.replace(".py", "").replace("_archive", "")
                        module_path = relative_path.replace(".py", "").replace("\\", ".")
                        class_name = component_name.replace("_", " ").title().replace(" ", "")

                        components[component_name] = {
                            "module": f"execution_unified.{module_path}",
                            "class": class_name,
                            "dependencies": [],
                        }

        return components

    def _scan_governance_archival(self) -> Dict[str, Dict]:
        """Scan and categorize governance archival components"""
        components = {}

        # Scan governance_unified archival directories
        for root, dirs, files in os.walk("governance_unified"):
            if "archive" in root.lower() or "legacy" in root.lower():
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, "governance_unified")

                        # Extract component info
                        component_name = file.replace(".py", "").replace("_archive", "")
                        module_path = relative_path.replace(".py", "").replace("\\", ".")
                        class_name = component_name.replace("_", " ").title().replace(" ", "")

                        components[component_name] = {
                            "module": f"governance_unified.{module_path}",
                            "class": class_name,
                            "dependencies": [],
                        }

        return components

    def activate_all_components(self) -> Dict[str, bool]:
        """Activate all registered components - FULL ACTIVATION, NO LAZY LOADING"""
        results = {}

        for component_name in self.components:
            success = self.activate_component(component_name)
            results[component_name] = success

        successful = sum(1 for s in results.values() if s)
        print(f"Activated {successful}/{len(self.components)} components successfully")

        return results


def main():
    """Main execution function"""
    print("=" * 80)
    print("PHASE 4: COMPONENT REGISTRATION AND ACTIVATION SYSTEM")
    print("FULL ACTIVATION - NO LAZY LOADING")
    print("=" * 80)

    registry = UnifiedComponentRegistry()

    # Register all archival components
    print("\nRegistering all archival components...")
    total_registered = registry.register_all_archival_components()

    # Activate all components systematically
    print("\nActivating all components...")
    activation_results = registry.activate_all_components()

    # Report results
    successful = sum(1 for s in activation_results.values() if s)
    print(f"\nSuccessful activations: {successful}/{total_registered}")

    print("\n" + "=" * 80)
    print("COMPONENT REGISTRATION COMPLETE")
    print("ALL COMPONENTS ATTEMPTED FOR FULL ACTIVATION")
    print("=" * 80)

    return {"registered": total_registered, "successful": successful, "registry": registry}


if __name__ == "__main__":
    result = main()
