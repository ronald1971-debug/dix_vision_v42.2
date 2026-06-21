"""
DYON Engineering Intelligence - Entry Point Script
Proper entry point for running DYON functionality
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from containers.engineering_intelligence.dyon import (
    RepositoryUnderstanding,
    ArchitectureAnalysis,
    DependencyMapping,
    TechnicalDebtAnalysis
)


def main():
    """Main entry point for DYON Engineering Intelligence"""
    print("DYON Engineering Intelligence")
    print("=" * 50)
    
    # Initialize components
    repo_understanding = RepositoryUnderstanding()
    architecture_analysis = ArchitectureAnalysis()
    dependency_mapping = DependencyMapping()
    technical_debt_analysis = TechnicalDebtAnalysis()
    
    print("Components initialized:")
    print("- Repository Understanding")
    print("- Architecture Analysis")
    print("- Dependency Mapping")
    print("- Technical Debt Analysis")
    print("\nDYON Engineering Intelligence is ready for use.")
    
    # Example usage (commented out to prevent actual execution)
    # analysis_result = repo_understanding.analyze_repository("path/to/repo")
    # print(f"Analysis result: {analysis_result}")


if __name__ == "__main__":
    main()