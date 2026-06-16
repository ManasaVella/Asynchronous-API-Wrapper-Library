class GitHubError(Exception):
    """Base exception boundary encapsulating all GitHub API payload problems."""
    def __init__(self, message: str, status: int, data: dict | None = None):
        super().__init__(message)
        self.status = status
        self.data = data or {}

class BadRequestError(GitHubError): """Status Code 400 - Validation Faults"""
class UnauthenticatedError(GitHubError): """Status Code 401 - Bad Credentials"""
class ForbiddenError(GitHubError): """Status Code 403 - Protected Resource Restrictions"""
class NotFoundError(GitHubError): """Status Code 404 - Target Missing"""
class RateLimitExceededError(ForbiddenError): """Status Code 403 - Exhausted Allotted API Tokens"""
class ServerError(GitHubError): """Status Code 5xx - Upstream Internal Infrastructure Issues"""

def raise_for_status(status: int, data: dict, headers: dict) -> None:
    """Evaluates network responses and throws contextual structured exceptions."""
    message = data.get("message", "An undocumented exception context occurred.")
    
    if status == 400:
        raise BadRequestError(message, status, data)
    elif status == 401:
        raise UnauthenticatedError(message, status, data)
    elif status == 403:
        # Cross-verifying headers ensures we don't misclassify a general 403 as a rate failure
        if headers.get("X-RateLimit-Remaining") == "0":
            raise RateLimitExceededError("Rate limit ceiling hit! Execution frozen.", status, data)
        raise ForbiddenError(message, status, data)
    elif status == 404:
        raise NotFoundError(message, status, data)
    elif status >= 500:
        raise ServerError(f"GitHub Internal Fault: {message}", status, data)
    elif status >= 400:
        raise GitHubError(message, status, data)