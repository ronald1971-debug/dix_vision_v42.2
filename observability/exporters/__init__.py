"""observability.exporters — External export targets (Prometheus, OTLP, etc.)."""

from .otlp_exporter import (
    OtlpExporter,
    OtlpExporterConfig,
    OtlpExportResult,
    get_otlp_exporter,
)

__all__ = [
    "OtlpExportResult",
    "OtlpExporter",
    "OtlpExporterConfig",
    "get_otlp_exporter",
]
