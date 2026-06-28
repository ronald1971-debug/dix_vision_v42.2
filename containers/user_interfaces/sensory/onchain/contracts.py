"""Stub onchain contracts."""

import logging
from typing import Any

LOG = logging.getLogger(__name__)


class OnchainEvent:
    """Stub onchain event."""

    def __init__(self, **kwargs: Any):
        LOG.debug(f"OnchainEvent stub initialized with kwargs: {list(kwargs.keys())}")
        LOG.warning("Using stub OnchainEvent implementation - this is a placeholder")


class HolderShiftAdvisory:
    """Stub holder shift advisory."""

    def __init__(self, **kwargs: Any):
        LOG.debug(f"HolderShiftAdvisory stub initialized with kwargs: {list(kwargs.keys())}")
        LOG.warning("Using stub HolderShiftAdvisory implementation - this is a placeholder")
