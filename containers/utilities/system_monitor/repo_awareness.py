"""Repository Awareness – DYON understands files, modules, dependencies, contracts.

Provides a structural map of the codebase for the evolution engine.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ModuleInfo:
    path: str
    name: str
    package: str
    size_bytes: int = 0
    is_init: bool = False
    imports: list[str] = field(default_factory=list)


@dataclass
class DependencyEdge:
    source: str
    target: str
    import_type: str = "direct"  # direct | transitive


@dataclass
class RepositoryMap:
    """Complete structural map of the repository."""
    root: str = ""
    modules: list[ModuleInfo] = field(default_factory=list)
    dependencies: list[DependencyEdge] = field(default_factory=list)
    packages: list[str] = field(default_factory=list)
    file_count: int = 0
    total_size_bytes: int = 0


class RepoAwareness:
    """Scans and maintains awareness of the repository structure."""

    def __init__(self, repo_root: str) -> None:
        self._root = repo_root
        self._map: RepositoryMap | None = None

    def scan(self) -> RepositoryMap:
        root_path = Path(self._root)
        modules: list[ModuleInfo] = []
        packages: set[str] = set()
        total_size = 0

        for py_file in root_path.rglob("*.py"):
            rel_path = str(py_file.relative_to(root_path))
            if any(part.startswith(".") for part in py_file.parts):
                continue

            size = py_file.stat().st_size
            total_size += size

            package = str(py_file.parent.relative_to(root_path)).replace(os.sep, ".")
            if package == ".":
                package = ""
            else:
                packages.add(package)

            imports = self._extract_imports(py_file)
            modules.append(
                ModuleInfo(
                    path=rel_path,
                    name=py_file.stem,
                    package=package,
                    size_bytes=size,
                    is_init=py_file.name == "__init__.py",
                    imports=imports,
                )
            )

        dependencies = self._build_dependency_graph(modules)

        self._map = RepositoryMap(
            root=self._root,
            modules=modules,
            dependencies=dependencies,
            packages=sorted(packages),
            file_count=len(modules),
            total_size_bytes=total_size,
        )
        return self._map

    def get_map(self) -> RepositoryMap | None:
        return self._map

    def get_module(self, path: str) -> ModuleInfo | None:
        if not self._map:
            return None
        for m in self._map.modules:
            if m.path == path:
                return m
        return None

    def get_package_modules(self, package: str) -> list[ModuleInfo]:
        if not self._map:
            return []
        return [m for m in self._map.modules if m.package == package]

    def _extract_imports(self, filepath: Path) -> list[str]:
        imports: list[str] = []
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from "):
                    module = stripped.split()[1].split(".")[0]
                    if module not in imports:
                        imports.append(module)
        except OSError:
            pass
        return imports

    def _build_dependency_graph(
        self, modules: list[ModuleInfo]
    ) -> list[DependencyEdge]:
        known_packages = {m.package for m in modules if m.package}
        known_packages.update(m.name for m in modules)
        edges: list[DependencyEdge] = []

        for mod in modules:
            for imp in mod.imports:
                if imp in known_packages:
                    edges.append(
                        DependencyEdge(source=mod.path, target=imp)
                    )
        return edges
