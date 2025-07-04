"""Custom exceptions for Voices of War."""

# Alliance Auth
from esi.errors import TokenError


class TokenDoesNotExist(TokenError):
    """A token with a specific scope does not exist for a user."""


class NotModifiedError(Exception):
    pass


class HTTPGatewayTimeoutError(Exception):
    pass
