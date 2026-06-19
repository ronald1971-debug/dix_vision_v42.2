"""Stub chat module."""

FEATURE_FLAG_ENV_VAR = "COGNITIVE_CHAT_FEATURE_FLAG"


class CognitiveChatFeatureFlag:
    """Stub chat feature flag."""

    def __init__(self, **kwargs: object):
        pass


class AllProvidersFailedError(Exception):
    """Stub error when all providers fail."""
    pass


class CognitiveChatRuntime:
    """Stub chat runtime."""

    def __init__(self, **kwargs: object):
        pass


class ChatTransport:
    """Stub chat transport."""

    def __init__(self, **kwargs: object):
        pass


class CognitiveChatBundle:
    """Stub chat bundle."""

    def __init__(self, **kwargs: object):
        pass


class CognitiveChatDisabledError(Exception):
    """Stub error when chat is disabled."""
    pass


class NoEligibleProviderError(Exception):
    """Stub error when no eligible provider."""
    pass


class ProviderResolver:
    """Stub provider resolver."""

    def __init__(self, **kwargs: object):
        pass


def assemble_cognitive_chat(**kwargs: object):
    """Stub assemble cognitive chat."""
    return None


def get_router(**kwargs: object):
    """Stub router getter."""
    return None


def get_chat(**kwargs: object):
    """Stub chat getter."""
    return None