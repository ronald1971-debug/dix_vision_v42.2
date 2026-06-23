"""DYON Research Runtime — Autonomous System Engineering Research (NEW CAPABILITY).

DYON will now autonomously research system engineering topics beyond code:
- System architecture patterns and best practices
- Distributed systems design principles
- Infrastructure and deployment patterns
- Security architecture and patterns
- Performance optimization techniques
- Scalability patterns
- Microservices architecture
- Event-driven systems
- Database design and optimization
- Cloud-native patterns
- Site Reliability Engineering (SRE) practices
- Observability and monitoring patterns
- DevOps and automation practices
- Container orchestration
- Kubernetes patterns
- Service mesh architectures
- API design patterns
- Rate limiting and circuit breaker patterns
- Caching strategies
- Database sharding strategies
- Load balancing algorithms
- Consensus algorithms
- Distributed consensus patterns

This gives DYON true system engineering intelligence, not just code-level intelligence.

Authority (B1): imports only from evolution_engine.* and core.*.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SystemEngineeringResearchTopic:
    """System engineering research topic."""

    topic_id: str
    category: str  # architecture, infrastructure, security, performance, scalability, etc.
    priority: float  # 0.0 to 1.0
    query: str
    sources: tuple[str, ...]  # High-trust engineering sources
    context: str  # Additional context for research
    created_ts_ns: int
    last_accessed_ts_ns: int


@dataclass(frozen=True, slots=True)
class SystemEngineeringFinding:
    """Finding from system engineering research."""

    finding_id: str
    topic_id: str
    title: str
    summary: str
    source: str
    source_url: str
    category: str
    relevance_score: float
    confidence: float
    recommendations: tuple[str, ...]
    ingested_ts_ns: int


class DYONResearchRuntime:
    """DYON's autonomous system engineering research runtime.

    Mirrors INDIRA's autonomous research runtime but focused on system engineering
    topics rather than trading/markets.

    Design:
    * ResearchQueue: priority-ordered queue of SystemEngineeringResearchTopic
    * Background daemon thread: dequeues, runs research, stores findings
    * SourceTrustScorer: deterministic domain → [0, 1] trust tier
    * Knowledge Store: stores system engineering findings for advisory use

    Research Categories:
        * architecture: System design patterns, architectural styles
        * infrastructure: Deployment, orchestration, infrastructure as code
        * security: Security patterns, authentication, authorization
        * performance: Optimization techniques, caching, load balancing
        * scalability: Horizontal/vertical scaling, sharding, replication
        * observability: Monitoring, logging, tracing, alerting
        * devops: CI/CD, automation, GitOps
        * sre: Reliability, incident response, chaos engineering
        * database: Design, optimization, sharding, consistency patterns
        * distributed_systems: Consensus, replication, CAP theorem applications
    """

    # High-trust system engineering sources
    DOMAIN_TRUST: dict[str, float] = {
        # System Architecture & Design
        "martinfowler.com": 0.95,
        "oreilly.com": 0.92,
        "msdn.microsoft.com": 0.90,
        "aws.amazon.com/architecture": 0.92,
        "cloud.google.com/architecture": 0.92,
        "azure.microsoft.com/architecture": 0.92,
        "nginx.org": 0.85,
        "kubernetes.io": 0.90,
        "cloud-native": 0.88,
        # Security
        "owasp.org": 0.95,
        "csrc.nist.gov": 0.95,
        "snyk.io/blog": 0.82,
        "owasp.org/blog": 0.88,
        "portswigger.net": 0.80,
        # Performance & Scalability
        "highscalability.com": 0.95,
        "infoq.com": 0.90,
        "ieee.org": 0.95,
        "acm.org": 0.95,
        "redis.io": 0.85,
        "rabbitmq.com": 0.82,
        # Observability & SRE
        "sre.works": 0.95,
        "prometheus.io": 0.90,
        "grafana.com": 0.88,
        "elastic.co": 0.88,
        "opentelemetry.io": 0.90,
        "datadog.com": 0.85,
        # DevOps & Automation
        "jenkins.io": 0.88,
        "gitlab.com": 0.85,
        "circleci.com": 0.82,
        "travis-ci.org": 0.80,
        "hashicorp.com": 0.90,
        "ansible.com": 0.88,
        "terraform.io": 0.92,
        # Database
        "postgresql.org/docs": 0.92,
        "mysql.com": 0.88,
        "mongodb.com/docs": 0.88,
        "redis.io/docs": 0.85,
        "cassandra.apache.org": 0.82,
        # Distributed Systems
        "databricks.com/blog": 0.88,
        "confluent.io/blog": 0.88,
        "kafka.apache.org/documentation": 0.90,
        "etcd.io": 0.88,
        "zookeeper.apache.org": 0.85,
    }

    # Research categories
    RESEARCH_CATEGORIES = {
        "architecture": [
            "microservices patterns",
            "event-driven architecture",
            "CQRS pattern",
            "saga pattern",
            "hexagonal architecture",
            "clean architecture",
            "domain-driven design",
            "service mesh patterns",
            "API gateway patterns",
            "backend for frontend",
        ],
        "infrastructure": [
            "container orchestration",
            "kubernetes patterns",
            "docker patterns",
            "infrastructure as code",
            "CI/CD patterns",
            "gitops practices",
            "service discovery",
            "configuration management",
            "secret management",
            "deployment strategies",
        ],
        "security": [
            "authentication patterns",
            "authorization patterns",
            "zero-trust architecture",
            "API security",
            "OWASP top 10",
            "defense in depth",
            "security monitoring",
            "incident response",
            "threat modeling",
            "compliance patterns",
        ],
        "performance": [
            "caching strategies",
            "load balancing",
            "rate limiting",
            "circuit breakers",
            "database optimization",
            "query optimization",
            "indexing strategies",
            "connection pooling",
            "async processing",
            "batching strategies",
        ],
        "scalability": [
            "horizontal scaling",
            "vertical scaling",
            "database sharding",
            "read replicas",
            "partitioning strategies",
            "caching layers",
            "CDN strategies",
            "edge computing",
            "auto-scaling",
            "resource allocation",
        ],
        "observability": [
            "monitoring patterns",
            "logging strategies",
            "distributed tracing",
            "metrics collection",
            "alerting patterns",
            "dashboard design",
            "SRE practices",
            "incident management",
            "post-mortem analysis",
            "chaos engineering",
        ],
        "devops": [
            "CI/CD patterns",
            "GitOps workflows",
            "infrastructure automation",
            "configuration management",
            "deployment automation",
            "testing automation",
            "version control strategies",
            "branching strategies",
            "release management",
            "rollback strategies",
        ],
        "database": [
            "data modeling",
            "normalization vs denormalization",
            "index design",
            "query optimization",
            "sharding strategies",
            "replication patterns",
            "consistency patterns",
            "transaction patterns",
            "connection pooling",
            "caching strategies",
        ],
        "distributed_systems": [
            "consensus algorithms",
            "CAP theorem tradeoffs",
            "leader election",
            "replication strategies",
            "eventual consistency",
            "quorum patterns",
            "distributed transactions",
            "message queues",
            "stream processing",
            "service discovery",
        ],
    }

    def __init__(self, *, max_queue_size: int = 100):
        self._lock = threading.RLock()
        self._research_queue: deque[SystemEngineeringResearchTopic] = deque(maxlen=max_queue_size)
        self._findings: dict[str, SystemEngineeringFinding] = {}
        self._thread: threading.Thread | None = None
        self._running = False
        self._repo_root = "."  # Will be set externally

    def set_repo_root(self, repo_root: str):
        """Set repository root for context-aware research."""
        self._repo_root = repo_root

    def add_research_topic(self, topic: SystemEngineeringResearchTopic) -> bool:
        """Add a research topic to the queue."""
        with self._lock:
            self._research_queue.append(topic)
            return True

    def queue_autonomous_research(self, category: str | None = None) -> None:
        """Queue autonomous research topics based on current system state."""
        if category is None:
            # Research all categories
            categories = list(self.RESEARCH_CATEGORIES.keys())
        else:
            categories = [category] if category in self.RESEARCH_CATEGORIES else []

        for cat in categories:
            for subtopic in self.RESEARCH_CATEGORIES.get(cat, []):
                topic = SystemEngineeringResearchTopic(
                    topic_id=f"{cat}_{subtopic}_{int(time.time_ns())}",
                    category=cat,
                    priority=0.7,
                    query=subtopic,
                    sources=self._get_trusted_sources_for_category(cat),
                    context=f"Autonomous research for DYON system engineering in {cat}",
                    created_ts_ns=int(datetime.now(UTC).timestamp() * 1_000_000_000),
                    last_accessed_ts_ns=int(datetime.now(UTC).timestamp() * 1_000_000_000),
                )
                self.add_research_topic(topic)

        LOG.info(f"Queued {len(categories)} categories for autonomous system engineering research")

    def _get_trusted_sources_for_category(self, category: str) -> tuple[str, ...]:
        """Get trusted sources for a research category."""
        # Map categories to appropriate sources
        category_sources = {
            "architecture": (
                "martinfowler.com",
                "oreilly.com",
                "aws.amazon.com/architecture",
                "cloud.google.com/architecture",
            ),
            "infrastructure": (
                "kubernetes.io",
                "ansible.com",
                "terraform.io",
                "gitlab.com",
                "jenkins.io",
            ),
            "security": ("owasp.org", "csrc.nist.gov", "snyk.io/blog", "owasp.org/blog"),
            "performance": ("highscalability.com", "infoq.com", "redis.io", "rabbitmq.com"),
            "scalability": ("highscalability.com", "kubernetes.io", "postgresql.org/docs"),
            "observability": ("sre.works", "prometheus.io", "grafana.com", "opentelemetry.io"),
            "devops": ("gitlab.com", "jenkins.io", "circleci.com", "hashicorp.com"),
            "database": ("postgresql.org/docs", "mysql.com", "mongodb.com/docs", "redis.io/docs"),
            "distributed_systems": (
                "confluent.io/blog",
                "kafka.apache.org/documentation",
                "etcd.io",
            ),
        }
        return category_sources.get(category, ("martinfowler.com", "oreilly.com"))

    def start_background_research(self) -> None:
        """Start background research daemon."""
        if self._running:
            LOG.warning("DYON research runtime already running")
            return

        self._running = True

        def _research_loop():
            while self._running:
                try:
                    with self._lock:
                        if not self._research_queue:
                            time.sleep(5)  # Wait for topics
                            continue
                        topic = self._research_queue.popleft()

                    LOG.info(f"Researching system engineering topic: {topic.topic_id}")
                    findings = self._research_topic(topic)

                    with self._lock:
                        for finding in findings:
                            self._findings[finding.finding_id] = finding

                    LOG.info(f"Completed research for {topic.topic_id}: {len(findings)} findings")

                except Exception as e:
                    LOG.error(f"Error in DYON research loop: {e}")
                    time.sleep(10)  # Back off on error

        self._thread = threading.Thread(
            target=_research_loop, daemon=True, name="dyon-research-loop"
        )
        self._thread.start()
        LOG.info("DYON research runtime started")

    def stop_background_research(self) -> None:
        """Stop background research daemon."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
            self._thread = None
        LOG.info("DYON research runtime stopped")

    def _research_topic(self, topic: SystemEngineeringResearch) -> list[SystemEngineeringFinding]:
        """Research a system engineering topic (placeholder implementation).

        In production, this would:
        1. Fetch content from trusted sources
        2. Parse and extract system engineering knowledge
        3. Generate findings with recommendations
        4. Score relevance and confidence
        """
        # TODO: Implement actual web scraping/research
        # For now, return placeholder findings
        LOG.warning(
            f"System engineering research not yet implemented - returning placeholder for topic: {topic.topic_id}"
        )

        return []

    def get_findings_by_category(self, category: str) -> list[SystemEngineeringFinding]:
        """Get all findings for a category."""
        with self._lock:
            return [f for f in self._findings.values() if f.category == category]

    def get_findings_by_topic(self, topic_id: str) -> list[SystemEngineeringFinding]:
        """Get all findings for a topic."""
        with self._lock:
            return [f for f in self._findings.values() if f.topic_id == topic_id]

    def get_all_findings(self) -> list[SystemEngineeringFinding]:
        """Get all system engineering findings."""
        with self._lock:
            return list(self._findings.values())

    def get_status(self) -> dict[str, Any]:
        """Get DYON research runtime status."""
        with self._lock:
            return {
                "running": self._running,
                "queue_size": len(self._research_queue),
                "findings_count": len(self._findings),
                "thread_alive": (
                    self._thread is not None and self._thread.is_alive() if self._thread else False
                ),
            }


# Singleton instance
_dyon_research_runtime: DYONResearchRuntime | None = None
_runtime_lock = threading.Lock()


def get_dyon_research_runtime() -> DYONResearchRuntime:
    """Get the singleton DYON research runtime instance."""
    global _dyon_research_runtime, _runtime_lock

    with _runtime_lock:
        if _dyon_research_runtime is None:
            _dyon_research_runtime = DYONResearchRuntime()
        return _dyon_research_runtime
