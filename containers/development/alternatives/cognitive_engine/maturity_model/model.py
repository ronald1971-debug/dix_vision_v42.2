"""Cognitive Maturity Model - tracks understanding maturity levels."""

from __future__ import annotations

import time

from cognitive_engine.maturity_model.levels import DomainMaturity, MaturityDomain, MaturityLevel
from cognitive_engine.maturity_model.report import MaturityReport


class CognitiveMaturityModel:
    """Tracks maturity across cognitive domains.

    Replaces PnL-only maturity measurement with:
    - Market Understanding (Level 1-10)
    - Trader Understanding (Level 1-10)
    - Strategy Understanding (Level 1-10)
    - Execution Understanding (Level 1-10)
    - System Understanding (Level 1-10)
    - Self Understanding (Level 1-10)
    """

    def __init__(self) -> None:
        self._domains: dict[MaturityDomain, DomainMaturity] = {}
        self._reports: list[MaturityReport] = []
        self._initialize_domains()

    def _initialize_domains(self) -> None:
        """Initialize all domains at novice level."""
        for domain in MaturityDomain:
            self._domains[domain] = DomainMaturity(
                domain=domain,
                level=MaturityLevel.NOVICE,
                progress=0.0,
            )

    def update_level(
        self, domain: MaturityDomain, level: MaturityLevel, evidence: str = ""
    ) -> None:
        """Update maturity level for a domain."""
        current = self._domains.get(domain)
        if current:
            self._domains[domain] = DomainMaturity(
                domain=domain,
                level=level,
                progress=current.progress,
                last_assessed=time.time_ns(),
                evidence=(*current.evidence, evidence) if evidence else current.evidence,
            )
        else:
            self._domains[domain] = DomainMaturity(
                domain=domain,
                level=level,
                evidence=(evidence,) if evidence else (),
            )

    def update_progress(self, domain: MaturityDomain, progress: float) -> None:
        """Update progress toward next level."""
        current = self._domains.get(domain)
        if current:
            self._domains[domain] = DomainMaturity(
                domain=domain,
                level=current.level,
                progress=min(1.0, max(0.0, progress)),
                last_assessed=time.time_ns(),
                evidence=current.evidence,
            )

    def advance_level(self, domain: MaturityDomain, evidence: str = "") -> bool:
        """Attempt to advance domain to next level."""
        current = self._domains.get(domain)
        if not current or current.progress < 1.0:
            return False

        next_level = MaturityLevel(min(current.level.value + 1, 10))
        self.update_level(domain, next_level, evidence)
        return True

    def get_level(self, domain: MaturityDomain) -> MaturityLevel:
        """Get current level for a domain."""
        dm = self._domains.get(domain)
        return dm.level if dm else MaturityLevel.NOVICE

    def generate_report(self) -> MaturityReport:
        """Generate comprehensive maturity report."""
        domains = tuple(self._domains.values())

        if domains:
            avg = sum(d.level_value() for d in domains) / len(domains)
            sorted_domains = sorted(domains, key=lambda d: d.level_value())

            highest = sorted_domains[-1].domain.value if sorted_domains else ""
            lowest = sorted_domains[0].domain.value if sorted_domains else ""
            improvement = tuple(d.domain.value for d in sorted_domains[:2])
        else:
            avg = 0.0
            highest = ""
            lowest = ""
            improvement = ()

        report = MaturityReport(
            domains=domains,
            overall_score=avg,
            highest_domain=highest,
            lowest_domain=lowest,
            improvement_areas=improvement,
        )
        self._reports.append(report)
        return report

    def get_report_history(self, limit: int = 10) -> list[MaturityReport]:
        """Get maturity report history."""
        return self._reports[-limit:]
