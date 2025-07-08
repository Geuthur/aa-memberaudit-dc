"""Custom exceptions for Memberaudit Doctrine Checker."""

# Alliance Auth
from esi.errors import TokenError


class TokenDoesNotExist(TokenError):
    """A token with a specific scope does not exist for a user."""


class NotModifiedError(Exception):
    pass


class HTTPGatewayTimeoutError(Exception):
    pass
