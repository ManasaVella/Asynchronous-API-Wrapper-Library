from .client import AsyncClient
from .models import Repository, GitHubUser
from .exceptions import (
    GitHubError,
    RateLimitExceededError,
    NotFoundError,
    UnauthenticatedError
)

# Explicitly defining public exports for structural package safety
__all__ = [
    "AsyncClient",
    "Repository",
    "GitHubUser",
    "GitHubError",
    "RateLimitExceededError",
    "NotFoundError",
    "UnauthenticatedError"
]