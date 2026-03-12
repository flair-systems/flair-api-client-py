# Backward compatibility module
# This allows users to import as: from flair_client import make_client
# while the actual implementation is in flair_api

try:
    from flair_api import (
        make_client,
        Resource,
        ApiError,
        EmptyBodyException,
        AuthenticationError
    )
except ImportError:
    # Fallback for when flair_api is not available
    raise ImportError(
        "Could not import from flair_api. Please ensure the package is properly installed."
    )

__all__ = [
    'make_client',
    'Resource',
    'ApiError',
    'EmptyBodyException',
    'AuthenticationError'
]